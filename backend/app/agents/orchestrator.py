from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator
import json
import os
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.services.scraper import scraper_service
from app.services.search import search_service
from app.services.ner import ner_service
from app.services.memory import memory_service
from app.services.enrichment import enrichment_service
from app.utils.logger import logger, log_execution_time
from app.utils.job_store import jobs
#scrapling
class AgentState(TypedDict):
    name: str
    urls: List[str]
    data: Dict[str, Any]
    next_action: Optional[str]
    action_input: Optional[Dict[str, Any]]
    observation: Optional[str]
    reflection: Optional[str]
    history: Annotated[List[Dict[str, Any]], operator.add]
    phase: str
    complete: bool
    job_id: str
    step_count: Annotated[int, operator.add]

class Orchestrator:
    def __init__(self):
        # Initialize LLM with Groq API and setup the LangGraph workflow
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant", # Switched to 8b to resolve 429 Rate Limit
            temperature=0
        ).bind(response_format={"type": "json_object"})
        self.setup_graph()

    def setup_graph(self):
        # Define the state machine nodes, edges, and conditional logic for the agentic loop
        workflow = StateGraph(AgentState)

        workflow.add_node("reason", self.reason_node)
        workflow.add_node("act", self.act_node)
        workflow.add_node("observe", self.observe_node)
        workflow.add_node("reflect", self.reflect_node)
        workflow.add_node("final", self.final_node)

        workflow.set_entry_point("reason")

        workflow.add_edge("reason", "act")
        workflow.add_edge("act", "observe")
        workflow.add_edge("observe", "reflect")
        
        workflow.add_conditional_edges(
            "reflect",
            self.should_continue,
            {
                "continue": "reason",
                "end": "final"
            }
        )
        workflow.add_edge("final", END)

        self.app = workflow.compile()

    @log_execution_time
    def reason_node(self, state: AgentState):
        # Analyze current state and decide which tool to use next (Scraper, Search, or NER)
        if state.get("step_count", 0) >= 20:
            return {"complete": True, "phase": "REASON", "step_count": 1}
            
        logger.info(f"Phase: REASON | Target: {state['name']} | Steps: {state.get('step_count', 0)}")
        prompt = ChatPromptTemplate.from_template("""
        You are an Agentic AI Profiler. 
        Target: {name}
        Seed URLs: {urls}
        Current Data: {data}
        History: {history}
        
        STRICT RULES:
        1. SOURCE-FIRST: You MUST use the `scraper` tool on ALL provided Seed URLs before doing any `web_search`.
        2. NO GENERIC SEARCH: DO NOT search for "{name}" generically.
        3. IDENTIFIER EXTRACTION: Extract UNIQUE details (username, location, role) from the Seed URLs.
        4. TARGETED SEARCH: Use the extracted identifiers for any subsequent cross-platform searches.
        5. ACCURACY: Focus on accuracy over quantity.
        
        Identify missing components and decide the next action.
        
        AVAILABLE TOOLS:
        - `scraper`: Requires {{"url": "string"}}. Use for Seed URLs first.
        # - `apify_extract`: Requires {{"url": "string"}}. (DISABLED - Do not use)
        - `web_search`: Requires {{"query": "string"}}. Use for finding new info via Tavily.
        - `clay_enrich`: Requires {{"query": "string"}}. Use to find deep professional enrichment info (emails, skills).
        - `ner_extract`: Requires {{"text": "string"}}. Use to pull entities from raw text.
        
        Respond in JSON format:
        {{
            "phase": "REASON",
            "thought": "your reasoning",
            "action": "scraper" | "web_search" | "clay_enrich" | "ner_extract",
            "action_input": {{ "url": "..." }} OR {{ "query": "..." }}
        }}
        """)
        
        chain = prompt | self.llm
        response = chain.invoke({
            "name": state["name"],
            "urls": state["urls"],
            "data": state["data"],
            "history": state["history"]
        })
        
        res = self.safe_json_load(response.content)
        action = res.get("action", "scraper" if not state["data"] else "web_search")
        action_input = res.get("action_input", {})
        
        # Smart Fallback: Generate query if missing for web_search
        if action == "web_search" and not action_input.get("query"):
            action_input["query"] = f"{state['name']} professional profile"
            
        return {
            "phase": "REASON",
            "thought": res.get("thought", "Searching for more professional details..."),
            "next_action": action,
            "action_input": action_input,
            "history": [res],
            "step_count": 1
        }

    @log_execution_time
    async def act_node(self, state: AgentState):
        # Execute the tool selected in the reasoning phase (e.g., scrape a URL or search the web)
        if state.get("complete") or state.get("step_count", 0) >= 20:
            return {"phase": "ACT", "observation": "Skipping action due to limit", "step_count": 1}
            
        job_id = state.get("job_id")
        # Check for cancellation before starting
        if job_id and jobs.get(job_id, {}).get("status") == "cancelled":
            logger.info(f"ACT phase aborted for job {job_id} due to cancellation")
            return {"phase": "ACT", "observation": "CANCELLED", "history": state["history"]}

        action = state["next_action"]
        inp = state["action_input"]
        logger.info(f"Phase: ACT | Tool: {action} | Input: {inp}")
        observation = ""

        if action == "scraper":
            url = inp.get("url")
            if url:
                observation = await scraper_service.scrape(url)
            else:
                observation = "Error: No URL provided for scraper"
        elif action == "web_search":
            query = inp.get("query")
            if query:
                observation = search_service.search(query)
            else:
                observation = "Error: No query provided for web_search"
        elif action == "apify_extract":
            observation = "Error: Apify extraction is currently disabled."
            # url = inp.get("url")
            # if url:
            #     observation = enrichment_service.apify_extract(url)
            # else:
            #     observation = "Error: No URL provided for apify_extract"
        elif action == "clay_enrich":
            query = inp.get("query")
            if query:
                observation = enrichment_service.clay_enrich(query)
            else:
                observation = "Error: No query provided for clay_enrich"
        elif action == "ner_extract":
            text = inp.get("text") or state.get("observation")
            if text:
                observation = ner_service.extract_entities(text)
            else:
                observation = "Error: No text provided for ner_extract"
        elif action == "memory_write":
            key = inp.get("key")
            value = inp.get("value")
            if key and value:
                memory_service.write(key, value)
                observation = "Data written to memory"
            else:
                observation = "Error: Missing key or value for memory_write"
        elif action == "memory_read":
            query = inp.get("query")
            if query:
                observation = memory_service.read(query)
            else:
                observation = "Error: No query provided for memory_read"
        
        return {
            "phase": "ACT",
            "observation": str(observation),
            "history": [{
                "phase": "ACT",
                "action": action,
                "action_input": inp
            }],
            "step_count": 1
        }

    @log_execution_time
    def observe_node(self, state: AgentState):
        # Use LLM to integrate raw tool output into the consolidated knowledge base
        logger.info(f"Phase: OBSERVE | Updating knowledge with latest observation")
        
        # We use the LLM to merge the new observation into the existing consolidated data
        prompt = ChatPromptTemplate.from_template("""
        You are a Knowledge Integrator.
        Existing Data: {data}
        New Observation: {observation}
        
        Merge the New Observation into the Existing Data. 
        
        STRICT RULES:
        1. IF New Observation contains "Error scraping", "LinkedIn is blocking", "404/Not Found", "Agree & Join", "Join LinkedIn", or "Sign in to LinkedIn", it means we hit an Auth Wall. IGNORE IT COMPLETELY and return the Existing Data.
        2. DO NOT make up or hallucinate any information. Only use facts present in the New Observation.
        3. POST EXTRACTION: Identify and extract the 3 most recent posts. Note the content and any posting dates/times (e.g., "2 hours ago", "Yesterday").
        4. BIO SUMMARY: Synthesize a brief but detailed professional bio based on the user's headline, about section, and experience.
        5. If no new valid data is found, return the Existing Data as is.
        6. Keep all existing valid data.
        7. Add new information (Bio, Skills, Experience, Education, Projects).
        8. If there is a conflict, prefer the more detailed/recent data.
        9. Focus heavily on Education and Experience.
        
        OUTPUT FORMAT: RAW JSON ONLY. DO NOT OUTPUT PYTHON CODE. DO NOT OUTPUT MARKDOWN.
        Respond ONLY with a JSON object. Ensure it has these exact top-level keys: "profile", "insights", "confidence".
        "profile" must contain: name, bio, location, skills, experience, projects, social_links, recent_posts.
        "insights" must contain: summary, key_strengths.
        "confidence" must contain: score, justification.
        For each post in recent_posts, analyze the content and provide a concise summary.
        
        Respond ONLY with the updated consolidated JSON data.
        """)
        
        # Truncate observation to avoid overloading the 8B model's context window
        obs_text = str(state['observation'])
        if len(obs_text) > 5000:
            obs_text = obs_text[:5000] + "... [Truncated for processing]"

        chain = prompt | self.llm

        response = chain.invoke({
            "data": state["data"],
            "observation": obs_text
        })
        
        parsed_data = self.safe_json_load(response.content)
        # Fallback to existing data if parsing failed or returned empty/error
        updated_data = parsed_data if isinstance(parsed_data, dict) and "error" not in parsed_data else state["data"]
        
        return {
            "phase": "OBSERVE",
            "data": updated_data,
            "history": [{
                "phase": "OBSERVE",
                "observation": f"Integrated {len(str(state['observation']))} chars into knowledge base"
            }],
            "step_count": 1
        }

    @log_execution_time
    def reflect_node(self, state: AgentState):
        # Evaluate profile completeness and decide whether to stop or continue the loop
        # Count web searches and total history length
        search_count = sum(1 for h in state["history"] if h.get("action") == "web_search")
        total_steps = len(state["history"])
        
        logger.info(f"Phase: REFLECT | Search count: {search_count} | Total steps: {total_steps}")
        
        prompt = ChatPromptTemplate.from_template("""
        Evaluate the completeness of the profile for {name}.
        Data: {data}
        Recent Observation: {observation}
        Current Search Count: {search_count}
        
        CRITICAL RULES:
        1. If Current Search Count >= 5 OR Total Steps >= 20, you MUST set "complete": true.
        2. If you have enough info (Bio, Skills, Experience), set "complete": true.
        3. Otherwise, set "complete": false to continue gathering.
        
        Respond in JSON format:
        {{
            "phase": "REFLECT",
            "thought": "evaluation of data and limits",
            "reflection": "detailed analysis",
            "complete": true/false
        }}
        """)
        
        chain = prompt | self.llm
        response = chain.invoke({
            "name": state["name"],
            "data": state["data"],
            "observation": state["observation"],
            "search_count": search_count,
            "total_steps": total_steps
        })
        
        res = self.safe_json_load(response.content)
        if not isinstance(res, dict):
            res = {"complete": search_count >= 5 or total_steps >= 20, "reflection": "Limit reached"}
        
        # Force completion if ANY limit is reached
        is_complete = res.get("complete", False) or search_count >= 5 or total_steps >= 20
        
        return {
            "phase": "REFLECT",
            "reflection": res.get("reflection", "No reflection available"),
            "complete": is_complete,
            "history": [res],
            "step_count": 1
        }

    def should_continue(self, state: AgentState):
        # Control flow logic to determine if the graph should transition to 'final' or 'reason'
        if state["complete"]:
            return "end"
        return "continue"

    @log_execution_time
    def final_node(self, state: AgentState):
        # Generate the final structured JSON profile from the consolidated knowledge
        logger.info(f"Phase: FINAL | Generating profile for {state['name']}")
        prompt = ChatPromptTemplate.from_template("""
        Generate the final structured profile for {name}.
        Data: {data}
        
        STRICT RULES:
        1. NO HALLUCINATION: DO NOT invent names, companies, or roles.
        2. BIO: Generate an extensive, detailed professional bio summary covering their full career trajectory. DO NOT make it brief.
        3. PROJECTS: If explicit projects are not found, INFER their major initiatives or repositories from their "experience" section and list them under "projects".
        4. POSTS (CRITICAL): Only extract genuine social media posts or activity made by the person. 
           - DO NOT extract generic news snippets or search engine descriptions (e.g. "Google's AI-powered search engine").
           - REJECT any post containing "2022" or "2023" (2024 and newer are OK).
           - If no actual recent posts by the user are found in the Data, YOU MUST return an empty list `[]` for `recent_posts`. DO NOT hallucinate.
        5. DATA-DRIVEN: Only use information explicitly found or safely inferred from the provided Data.
        5. FALLBACK: If a field is missing, use "Unknown".
        6. VERACITY: If the Data contains error messages, ignore them.
        
        Respond in STRICT JSON format with this exact structure:
        {{
            "profile": {{
                "name": "{name}",
                "bio": "string",
                "location": "string",
                "skills": ["string"],
                "experience": [{{ "title": "string", "company": "string", "period": "string", "description": "string" }}],
                "projects": [{{ "name": "string", "description": "string", "technologies": ["string"] }}],
                "social_links": ["string"],
                "recent_posts": [{{ "content": "string", "summary": "AI generated analysis of the post", "date": "string", "link": "string" }}]
            }},
            "insights": {{
                "summary": "string",
                "key_strengths": ["string"]
            }},
            "confidence": {{
                "score": float (0-1),
                "justification": "string"
            }}
        }}
        """)
        
        chain = prompt | self.llm
        response = chain.invoke({"name": state["name"], "data": state["data"]})
        
        res = self.safe_json_load(response.content)
        
        # --- HARD HALLUCINATION FILTER (POST-PROCESSING) ---
        if isinstance(res, dict) and "profile" in res:
            posts = res["profile"].get("recent_posts", [])
            filtered_posts = []
            for post in posts:
                content = post.get("content", "").lower()
                date = post.get("date", "")
                
                # Reject generic AI hallucinations or search engine snippets
                is_hallucinated = any(phrase in content for phrase in [
                    "revolutionizing", "leveraging machine learning", "chatbot", 
                    "24/7", "personalized support", "search engine is getting smarter", 
                    "ai-powered search", "google's ai"
                ])
                # Reject old dates (allow 2024+)
                is_old = any(year in date for year in ["2020", "2021", "2022", "2023"])
                
                if not (is_hallucinated or is_old):
                    filtered_posts.append(post)
            
            res["profile"]["recent_posts"] = filtered_posts[:3]
        # ----------------------------------------------------

        return {
            "phase": "FINAL",
            "data": res,
            "history": state["history"] + [res]
        }

    def clean_json(self, text: str):
        # Robustly extract JSON block from raw LLM text response
        """Robustly extract JSON from LLM response."""
        import re
        # Try to find JSON block
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if json_match:
            return json_match.group(1).strip()
            
        # Try to find any triple backtick block
        any_code_match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if any_code_match:
            return any_code_match.group(1).strip()
            
        # Try to find content between first { and last }
        curly_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if curly_match:
            return curly_match.group(1).strip()
            
        return text.strip()

    def safe_json_load(self, text: str, fallback_type: str = "dict"):
        # Safely parse JSON strings with fallbacks to avoid application crashes
        """Safely parse JSON with fallbacks."""
        cleaned = self.clean_json(text)
        try:
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Failed to parse JSON: {cleaned}. Error: {str(e)}")
            if fallback_type == "dict":
                return {"error": "Failed to parse JSON", "raw": text}
            return []

orchestrator = Orchestrator()
