import os
import json
# from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.services.scraper import scraper_service
from app.services.search import search_service
from app.services.url_processor import url_processor
from app.utils.logger import logger

class EntityDiscoveryService:
    def __init__(self):
        # Initialize Groq LLM setup (Commented out for Gemini migration)
        # self.llm = ChatGroq(
        #     api_key=os.getenv("GROQ_API_KEY"),
        #     model_name="llama-3.1-8b-instant",
        #     temperature=0,
        #     max_tokens=2048
        # ).bind(response_format={"type": "json_object"})

        # Initialize Google Gemini API
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "DUMMY_KEY",
            model="gemini-2.5-flash",
            temperature=0,
            max_output_tokens=8192
        )

    async def discover(self, url: str) -> dict:
        logger.info(f"Entity Discovery requested for URL: {url}")
        
        # STEP 1: Extract Identity & directly mentioned URLs
        primary_result = await scraper_service.scrape(url)
        if not isinstance(primary_result, dict) or "error" in primary_result:
            err_msg = primary_result.get("error") if isinstance(primary_result, dict) else str(primary_result)
            return {
                "error": f"Failed to scrape seed URL: {err_msg}",
                "person": None,
                "confidence_score": 0.0
            }
            
        visible_text = primary_result.get("visible_text", "")
        title = primary_result.get("title", "")
        extracted_links = primary_result.get("discovered_links", [])
        
        # Filter outbound links using classify_url to identify direct profiles
        direct_profile_links = []
        for l in extracted_links:
            l_type = url_processor.classify_url(l)
            if l_type in ("linkedin", "twitter", "facebook", "youtube", "github", "portfolio", "blog"):
                direct_profile_links.append(l)
                
        # STEP 2 & 3: Extract Identity & Generate Search Queries using LLM
        identity_prompt = ChatPromptTemplate.from_template("""
        You are an expert Information Extraction Agent.
        Analyze this web page title and raw text content to identify the primary person.
        
        Title: {title}
        Page Text: {text}
        
        Extract the following:
        1. Name (Full name of the person)
        2. Aliases or usernames
        3. Job title / role
        4. Organization (if available)
        5. Strong keywords or context about them (location, industry)
        6. A set of 5 targeted search queries to find their other profiles (e.g. "Name GitHub", "Name Twitter", etc.)
        
        If the page does not clearly identify a person, set the "person_found" flag to false.
        
        Respond in JSON format:
        {{
            "person_found": true,
            "person": {{
                "name": "Full Name",
                "aliases": ["alias1", "alias2"],
                "role": "Role",
                "organization": "Organization"
            }},
            "keywords": ["keyword1", "keyword2"],
            "search_queries": ["query1", "query2"]
        }}
        """)
        
        chain = identity_prompt | self.llm
        try:
            res_identity = chain.invoke({
                "title": title,
                "text": visible_text[:25000] # Limit size to fit within window
            })
            # Clean possible markdown fences in Gemini response
            raw_content = res_identity.content.strip()
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:].strip()
            elif raw_content.startswith("```"):
                raw_content = raw_content[3:].strip()
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3].strip()
            
            first_brace = raw_content.find("{")
            last_brace = raw_content.rfind("}")
            if first_brace != -1 and last_brace != -1:
                raw_content = raw_content[first_brace:last_brace+1]
                
            identity_data = json.loads(raw_content)
        except Exception as e:
            logger.error(f"Error during LLM identity extraction: {str(e)}")
            return {"error": "Failed to parse identity from seed URL", "confidence_score": 0.0}
            
        if not identity_data.get("person_found", True):
            return {"error": "PERSON_NOT_FOUND", "confidence_score": 0.0}
            
        person = identity_data.get("person", {})
        queries = identity_data.get("search_queries", [])
        
        # STEP 4: Web Expansion via simulated search queries
        expanded_links = []
        for query in queries[:5]: # execute the top 5 high-value queries to bypass rates
            try:
                search_res = search_service.search(query)
                if isinstance(search_res, list):
                    for item in search_res:
                        url_item = item.get("url")
                        if url_item and url_item not in expanded_links:
                            expanded_links.append(url_item)
            except Exception as search_err:
                logger.error(f"Search failed for query '{query}': {str(search_err)}")
                
        # STEP 5 & 6: Verification & Deduplication
        verification_prompt = ChatPromptTemplate.from_template("""
        You are an expert Web Entity Verification Agent.
        
        Target Person:
        Name: {name}
        Aliases: {aliases}
        Role: {role}
        Organization: {organization}
        
        We have discovered some candidate profile URLs for this target person.
        Candidate URLs: {candidate_urls}
        Direct URLs from Seed Page: {direct_urls}
        
        Your task:
        1. Verify each URL to ensure it belongs to the EXACT same person.
        2. Categorize verified URLs into: linkedin, twitter, instagram, github, youtube, personal_website, blog.
        3. Reject fan pages, companies, or other people with similar names.
        4. Calculate a confidence score between 0.0 and 1.0.
        
        Respond in JSON format:
        {{
            "verified_profiles": {{
                "linkedin": "url or empty string",
                "twitter": "url or empty string",
                "instagram": "url or empty string",
                "github": "url or empty string",
                "youtube": "url or empty string",
                "personal_website": "url or empty string",
                "blog": "url or empty string"
            }},
            "discovered_urls": ["list of other verified non-social URLs"],
            "confidence_score": 0.95
        }}
        """)
        
        all_candidates = list(set(direct_profile_links + expanded_links))
        
        chain_verify = verification_prompt | self.llm
        try:
            res_verify = chain_verify.invoke({
                "name": person.get("name"),
                "aliases": person.get("aliases", []),
                "role": person.get("role"),
                "organization": person.get("organization"),
                "candidate_urls": all_candidates,
                "direct_urls": direct_profile_links
            })
            # Clean possible markdown fences in Gemini response
            raw_content = res_verify.content.strip()
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:].strip()
            elif raw_content.startswith("```"):
                raw_content = raw_content[3:].strip()
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3].strip()
            
            first_brace = raw_content.find("{")
            last_brace = raw_content.rfind("}")
            if first_brace != -1 and last_brace != -1:
                raw_content = raw_content[first_brace:last_brace+1]
                
            verify_data = json.loads(raw_content)
        except Exception as e:
            logger.error(f"Error during verification step: {str(e)}")
            return {
                "person": person,
                "direct_urls": direct_profile_links,
                "discovered_urls": [],
                "verified_profiles": {},
                "confidence_score": 0.5
            }
            
        return {
            "person": person,
            "direct_urls": direct_profile_links,
            "discovered_urls": verify_data.get("discovered_urls", []),
            "verified_profiles": verify_data.get("verified_profiles", {}),
            "confidence_score": verify_data.get("confidence_score", 0.0)
        }

entity_discovery_service = EntityDiscoveryService()
