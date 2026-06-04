import os
import json
# from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.utils.logger import logger

class RAGLLMEngine:
    def __init__(self):
        # Initialize Groq LLM setup (Commented out for Gemini migration)
        # self.api_key = os.getenv("GROQ_API_KEY")
        # if not self.api_key:
        #     logger.warning("GROQ_API_KEY is not configured in env!")
        # 
        # self.llm = ChatGroq(
        #     api_key=self.api_key,
        #     model_name="llama-3.1-8b-instant", # Switched to 8b to match orchestrator.py rate limit guidelines
        #     temperature=0.1,
        #     max_tokens=2048
        # ).bind(response_format={"type": "json_object"})

        # Initialize Google Gemini API
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=self.api_key or "DUMMY_KEY",
            model="gemini-2.5-flash",
            temperature=0.1,
            max_output_tokens=8192
        )

    def generate_profile(self, name: str, query: str, top_chunks: list[dict]) -> dict:
        """
        Takes the query and top 3 reranked chunks, pushes them to the LLM, 
        and extracts the final unified structured profile JSON.
        """
        logger.info(f"RAGLLMEngine: Generating query-aware profile for target: {name}...")

        # Serialize context using Flat-Pipe TOON format for optimal token compression
        from app.utils.toon import serialize_rag_context_to_toon
        context_text = serialize_rag_context_to_toon(
            name=name,
            query=query,
            chunks=top_chunks
        ) if top_chunks else "No relevant context chunks found."

        prompt = ChatPromptTemplate.from_template("""
        You are a Senior Professional Intelligence Synthesis Agent.
        Your task is to generate a comprehensive, highly accurate, query-aware structured professional profile for the Target Person based ONLY on the provided relevant chunks of text retrieved from their online profiles/websites.

        Target Person Name: {name}
        User Specific Request/Query: {query}

        Context Chunks (Flat-Pipe TOON formatted):
        {context}

        STRICT RECONCILIATION AND DATA INTEGRITY RULES:
        1. QUERY INTEGRITY: Focus your synthesis primarily on answering the user's specific request/query. For example, if they query "Show technical skills", make sure the 'skills' and 'bio' sections reflect detailed context on skills.
        2. DEDUPLICATION: Merge repeating details, unify repeated experiences, and eliminate any conflicting namesake data.
        3. STRICT SOURCE TRACEABILITY: For every single item inside 'experience', 'projects', and 'certifications', you MUST assign the correct 'source_url' (taken from the 'source' attribute of a matching 'ctx' entity in the data) corresponding to the specific chunk it was extracted from.
        4. RECENT ACTIVITY: If there are posts or online activities by the target person found in the chunks, capture them in the 'recent_activity' list (containing: content, platform, date). Otherwise, leave it as an empty list [].
        5. FALLBACK VALUES: If information for a field is not found anywhere in the context chunks, set the field to an empty string "" or an empty list [] so it can be cleanly parsed. Under no circumstances should you invent or hallucinate information.
        6. CONFIDENCE SCORE: Evaluate the overall richness, alignment, and authority of the retrieved context and output a float confidence score between 0.0 and 1.0.
        7. SPORTS PERSON / ATHLETE SUPPORT (CRITICAL):
           If the target person is identified as a sports person, athlete, footballer, cricketer, coach, or similar:
           - Map their club/team history to 'experience' (with title as Position/Role played, company as Club/Team, and description as performance stats/appearances).
           - Map their key tournaments, seasons, or championships to 'projects' (with name as Tournament/Competition name, and technologies as key athletic stats like Goals, Assists, Wins, MVPs).
           - Map their athletic skills, attributes, or specialties (e.g. Speed, Stamina, Agility, Dribbling, Tackling, Shooting) to 'skills'.
           - Map their cups, trophies, medals, records, or personal awards to 'certifications' / 'achievements'.
        8. DATA FORMAT: The provided Context Chunks are in token-optimized Flat-Pipe TOON format. 
           - 'ctx' represents a semantic context chunk containing 'source' (the source URL) and 'content' (the text data).
           - Map all experiences and projects to their corresponding 'source' URL.

        You MUST respond with a RAW JSON object matching this exact structure:
        {{
            "name": "{name}",
            "headline": "string (professional headline/title)",
            "bio": "string (career summary/biography)",
            "skills": ["string"],
            "experience": [
                {{
                    "title": "string",
                    "company": "string",
                    "period": "string",
                    "description": "string",
                    "source_url": "string"
                }}
            ],
            "projects": [
                {{
                    "name": "string",
                    "description": "string",
                    "technologies": ["string"],
                    "source_url": "string"
                }}
            ],
            "certifications": [
                {{
                    "name": "string",
                    "issuer": "string",
                    "date": "string",
                    "source_url": "string"
                }}
            ],
            "social_links": ["string (discovered social links)"],
            "achievements": ["string (notable awards/achievements)"],
            "recent_activity": [
                {{
                    "content": "string",
                    "platform": "string",
                    "date": "string"
                }}
            ],
            "confidence_score": 0.95
        }}

        Do NOT output markdown. Do NOT output code blocks. Respond ONLY with a valid stringified JSON object.
        """)

        # Chain prompt and LLM
        chain = prompt | self.llm
        
        try:
            logger.info("RAGLLMEngine: Invoking Gemini LLM chain...")
            response = chain.invoke({
                "name": name,
                "query": query,
                "context": context_text
            })
            
            # Parse the clean JSON object returned by Gemini (handling code fences robustly)
            raw_text = response.content.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:].strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:].strip()
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3].strip()
                
            first_brace = raw_text.find("{")
            last_brace = raw_text.rfind("}")
            if first_brace != -1 and last_brace != -1:
                raw_text = raw_text[first_brace:last_brace+1]

            parsed_profile = json.loads(raw_text)
            logger.info("RAGLLMEngine: Structured profile successfully synthesized.")
            return parsed_profile
            
        except Exception as e:
            logger.error(f"RAGLLMEngine: LLM compilation failed: {str(e)}")
            # Graceful fallback response matching structure
            return {
                "name": name,
                "headline": "Failed to compile headline",
                "bio": f"Profile synthesis aborted due to error: {str(e)}",
                "skills": [],
                "experience": [],
                "projects": [],
                "certifications": [],
                "social_links": [],
                "achievements": [],
                "recent_activity": [],
                "confidence_score": 0.0
            }

# Global instance for workspace reuse
llm_engine = RAGLLMEngine()
