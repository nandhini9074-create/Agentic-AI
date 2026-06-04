from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator
import json
import os
import asyncio
from langgraph.graph import StateGraph, END
# from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.services.scraper import scraper_service
from app.services.search import search_service
from app.services.url_processor import url_processor
from app.utils.logger import logger, log_execution_time
from app.utils.job_store import jobs

class AgentState(TypedDict):
    name: str
    email: Optional[str]
    phone: Optional[str]
    skills: Optional[str]
    age: Optional[str]
    gender: Optional[str]
    dob: Optional[str]
    location: Optional[str]
    language: Optional[str]
    query: Optional[str]
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
        # Initialize LLM with Groq API (Commented out for Gemini migration)
        # self.api_key = os.getenv("GROQ_API_KEY")
        # self.model_name = "llama-3.1-8b-instant"
        # self.llm = ChatGroq(
        #     api_key=self.api_key,
        #     model_name=self.model_name,
        #     temperature=0,
        #     max_tokens=2048
        # ).bind(response_format={"type": "json_object"})

        # Initialize LLM with Google Gemini API
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = "gemini-2.5-flash"
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=self.api_key or "DUMMY_KEY",
            model=self.model_name,
            temperature=0,
            max_output_tokens=8192
        )

        self.setup_graph()

    def safe_invoke(self, chain, inputs, max_retries=5, model_name: str = None, fallback_chain=None, job_id: str = None):
        import time
        model_label = model_name or self.model_name
        delay = 5.0
        
        # Log estimated input character length for visibility
        est_chars = sum(len(str(v)) for v in inputs.values()) if isinstance(inputs, dict) else len(str(inputs))
        logger.info(f"LLM Invoke: Preparing call to model '{model_label}' (Estimated input size: ~{est_chars} chars)")
        
        for attempt in range(max_retries):
            try:
                response = chain.invoke(inputs)
                
                # Check response_metadata for actual token counts returned by the LLM provider
                token_usage = getattr(response, "response_metadata", {}).get("token_usage", {})
                p_tok, c_tok, t_tok = 0, 0, 0
                if token_usage:
                    p_tok = token_usage.get("prompt_tokens") or token_usage.get("input_tokens") or 0
                    c_tok = token_usage.get("completion_tokens") or token_usage.get("output_tokens") or 0
                    t_tok = token_usage.get("total_tokens") or (p_tok + c_tok)
                    logger.info(f"LLM Token Usage Metrics: model={model_label} | Prompt/Input Tokens: {p_tok} | Completion/Output Tokens: {c_tok} | Total Tokens: {t_tok}")
                else:
                    # Fallback token estimation
                    p_tok = est_chars // 4
                    res_text = getattr(response, "content", "") if response else ""
                    c_tok = len(str(res_text)) // 4
                    t_tok = p_tok + c_tok
                    logger.info(f"LLM Token Usage (Estimated): model={model_label} | Prompt/Input Tokens: ~{p_tok} | Completion/Output Tokens: ~{c_tok} | Total Tokens: ~{t_tok}")
                
                # Accumulate tokens globally if job_id is provided
                if job_id and job_id in jobs:
                    if "token_usage" not in jobs[job_id]:
                        jobs[job_id]["token_usage"] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                    jobs[job_id]["token_usage"]["prompt_tokens"] += p_tok
                    jobs[job_id]["token_usage"]["completion_tokens"] += c_tok
                    jobs[job_id]["token_usage"]["total_tokens"] += t_tok
                
                return response
            except Exception as e:
                err_str = str(e)
                err_lower = err_str.lower()
                is_transient = any(x in err_lower for x in ["429", "503", "500", "504", "rate limit", "unavailable", "high demand", "temporary", "overloaded", "server error"])
                if is_transient:
                    # Try fallback chain (alternate key) immediately before sleeping
                    if fallback_chain and attempt == 0:
                        logger.warning(f"Groq 429 on {model_label} (key 1) — trying fallback key immediately...")
                        try:
                            fallback_res = fallback_chain.invoke(inputs)
                            token_usage = getattr(fallback_res, "response_metadata", {}).get("token_usage", {})
                            p_tok_fb, c_tok_fb, t_tok_fb = 0, 0, 0
                            if token_usage:
                                p_tok_fb = token_usage.get("prompt_tokens") or token_usage.get("input_tokens") or 0
                                c_tok_fb = token_usage.get("completion_tokens") or token_usage.get("output_tokens") or 0
                                t_tok_fb = token_usage.get("total_tokens") or (p_tok_fb + c_tok_fb)
                                logger.info(f"LLM Token Usage Metrics (Fallback): model={model_label} | Prompt/Input Tokens: {p_tok_fb} | Completion/Output Tokens: {c_tok_fb} | Total Tokens: {t_tok_fb}")
                            else:
                                p_tok_fb = est_chars // 4
                                fb_text = getattr(fallback_res, "content", "") if fallback_res else ""
                                c_tok_fb = len(str(fb_text)) // 4
                                t_tok_fb = p_tok_fb + c_tok_fb
                                logger.info(f"LLM Token Usage (Estimated Fallback): model={model_label} | Prompt/Input Tokens: ~{p_tok_fb} | Completion/Output Tokens: ~{c_tok_fb} | Total Tokens: ~{t_tok_fb}")
                            
                            if job_id and job_id in jobs:
                                if "token_usage" not in jobs[job_id]:
                                    jobs[job_id]["token_usage"] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                                jobs[job_id]["token_usage"]["prompt_tokens"] += p_tok_fb
                                jobs[job_id]["token_usage"]["completion_tokens"] += c_tok_fb
                                jobs[job_id]["token_usage"]["total_tokens"] += t_tok_fb
                            
                            return fallback_res
                        except Exception:
                            pass  # fallback also rate-limited, proceed with backoff
                    sleep_time = delay + (attempt * 8.0)
                    logger.warning(f"Transient LLM Error detected ({type(e).__name__}) during LLM invoke on {model_label}. Retrying attempt {attempt+1}/{max_retries} after sleeping {sleep_time}s... Error: {err_str[:250]}")
                    time.sleep(sleep_time)
                else:
                    raise e
        
        final_res = chain.invoke(inputs)
        token_usage = getattr(final_res, "response_metadata", {}).get("token_usage", {})
        p_tok, c_tok, t_tok = 0, 0, 0
        if token_usage:
            p_tok = token_usage.get("prompt_tokens") or token_usage.get("input_tokens") or 0
            c_tok = token_usage.get("completion_tokens") or token_usage.get("output_tokens") or 0
            t_tok = token_usage.get("total_tokens") or (p_tok + c_tok)
            logger.info(f"LLM Token Usage Metrics: model={model_label} | Prompt/Input Tokens: {p_tok} | Completion/Output Tokens: {c_tok} | Total Tokens: {t_tok}")
        else:
            p_tok = est_chars // 4
            fr_text = getattr(final_res, "content", "") if final_res else ""
            c_tok = len(str(fr_text)) // 4
            t_tok = p_tok + c_tok
            logger.info(f"LLM Token Usage (Estimated Final): model={model_label} | Prompt/Input Tokens: ~{p_tok} | Completion/Output Tokens: ~{c_tok} | Total Tokens: ~{t_tok}")
        
        if job_id and job_id in jobs:
            if "token_usage" not in jobs[job_id]:
                jobs[job_id]["token_usage"] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            jobs[job_id]["token_usage"]["prompt_tokens"] += p_tok
            jobs[job_id]["token_usage"]["completion_tokens"] += c_tok
            jobs[job_id]["token_usage"]["total_tokens"] += t_tok
            
        return final_res

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

    def is_sports_target(self, name: str, skills: str = "", query: str = "", urls: List[str] = None) -> bool:
        """Determines if the target name, skills, custom query, or source URLs represent a sports person."""
        # Single tokens for exact matching (prevents substring issues for small abbreviations like ca, atp, f1)
        sports_tokens = {
            # 1. Sports Roles & Positions
            "cricketer", "footballer", "athlete", "batsman", "bowler", "wicketkeeper", "all-rounder", 
            "spinner", "pacer", "opener", "finisher", "captain", "coach", "manager", "selector", 
            "scout", "analyst", "commentator", "referee", "umpire", "striker", "winger", "midfielder", 
            "defender", "goalkeeper", "sweeper", "forward", "playmaker", "quarterback", "boxer", 
            "wrestler", "swimmer", "runner", "cyclist", "racer", "driver", "shooter", "archer", 
            "gymnast", "judoka", "karateka", "gamer",
            # 2. Sports & Games
            "cricket", "football", "soccer", "basketball", "baseball", "rugby", "tennis", "badminton", 
            "squash", "hockey", "volleyball", "kabaddi", "kho", "chess", "golf", "swimming", "athletics", 
            "marathon", "cycling", "motorsport", "f1", "mma", "ufc", "wrestling", "boxing", "karate", 
            "judo", "taekwondo", "fencing", "archery", "shooting", "gymnastics", "rowing", "sailing", "esports",
            # 3. Tournaments, Leagues & Events
            "olympics", "paralympics", "championship", "tournament", "wimbledon", "ipl", "wpl", "tnpl", 
            "psl", "bbl", "cpl", "sa20", "isl", "motogp", "nascar",
            # 4. Sports Organizations & Governing Bodies
            "fifa", "uefa", "afc", "icc", "bcci", "ecb", "pcb", "ca", "aiff", "ioc", "atp", "wta", 
            "fide", "bwf", "ittf", "nba", "nfl", "mlb", "nhl", "ufc", "wwe", "fia", "fih", "tnca",
            # 5. Sports Data, Analytics & News Platforms
            "transfermarkt", "sofascore", "flashscore", "livescore", "fotmob", "statbunker", "fbref", 
            "understat", "whoscored", "soccerway", "espn", "cricbuzz", "lichess", "sportstar", "statmuse", "rotowire",
            # 6. Sports Statistics & Search Terms
            "standings", "rankings", "fixtures", "lineup", "squad", "roster", "stats", "highlights", 
            "assist", "century", "fifty", "possession", "mvp", "prediction", "odds", "playoffs", 
            "knockout", "final", "medal", "qualification", "debut", "retirement", "contract", 
            "auction", "draft", "trade", "academy",
            # Nicknames & Stars
            "messi", "kohli", "ronaldo", "dhoni", "sachin", "tendulkar", "leomessi", "virat", "neymar", "mbappe"
        }

        # Multi-word exact phrases for substring search
        sports_phrases = [
            "vice-captain", "head coach", "assistant coach", "wing back", "center back", 
            "running back", "point guard", "shooting guard", "martial artist", "esports player",
            "table tennis", "formula 1", "weightlifting", "bodybuilding",
            "world cup", "fifa world cup", "champions league", "europa league", "premier league", 
            "la liga", "bundesliga", "serie a", "ligue 1", "copa america", "euro cup", "asia cup", 
            "grand slam", "french open", "australian open", "us open", "icc world cup", "champions trophy", 
            "t20 world cup", "ranji trophy", "pro kabaddi league", "nba finals", "super bowl", 
            "ufc fight night", "wrestlemania", "royal rumble", "asian games", "commonwealth games",
            "world athletics", "espn cricinfo", "cricinfo.com", "cricbuzz.com", "sofascore.com", 
            "transfermarkt.com", "olympics.com", "fifa.com", "uefa.com", "nba.com", "nfl.com", 
            "mlb.com", "nhl.com", "fide.com", "formula1.com", "motorsport.com", "sky sports", 
            "the athletic", "goal.com", "onefootball", "live score", "scorecard", "transfer news", 
            "injury update", "clean sheet", "hat trick", "goal difference", "fantasy league", 
            "player rating", "semi final", "youth team"
        ]

        import re
        def check_text(text: str) -> bool:
            if not text:
                return False
            text_lower = text.lower().strip()
            # 1. Match exact phrases as substrings
            if any(phrase in text_lower for phrase in sports_phrases):
                return True
            # 2. Tokenize and check exact single keyword overlap
            tokens = set(re.findall(r"\b[a-z0-9\-]+\b", text_lower))
            if tokens.intersection(sports_tokens):
                return True
            return False

        if check_text(name) or check_text(skills) or check_text(query):
            return True

        if urls:
            for url in urls:
                if check_text(url):
                    return True

        return False

    def extract_username_from_url(self, url: str) -> str:
        """Extracts username/handle from common social media URLs."""
        if not url:
            return ""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            path = parsed.path.strip("/")
            parts = [p for p in path.split("/") if p]
            domain = parsed.netloc.lower()
            
            if any(d in domain for d in ["instagram.com", "github.com", "twitter.com", "x.com", "facebook.com"]):
                if parts:
                    return parts[0]
            elif "linkedin.com" in domain:
                if len(parts) >= 2 and parts[0] == "in":
                    return parts[1]
                elif parts:
                    return parts[0]
            elif "youtube.com" in domain or "youtu.be" in domain:
                if parts:
                    user = parts[0]
                    if user.startswith("@"):
                        return user[1:]
                    return user
        except Exception:
            pass
        return ""

    def verify_search_result(self, item: dict, target_name: str, seed_urls: List[str] = None, skills: str = "", query: str = "") -> bool:
        """
        Strict identity validation function to filter out unrelated namesake or company pages.
        Verifies if search results contain first name and last name, or match username handles,
        with smart fuzzy matching for name variations when strong skill/domain indicators match.
        """
        title = item.get("title", "").lower()
        snippet = item.get("content", "").lower()
        url = item.get("url", "").lower()
        
        # Clean target_name to split on both spaces, dots, and underscores
        clean_target_name = target_name.replace(".", " ").replace("_", " ").lower()
        name_parts = [p.strip() for p in clean_target_name.split() if len(p.strip()) > 1]
        if not name_parts:
            return True
            
        # Extract seed handles to use as absolute anchors
        seed_handles = []
        if seed_urls:
            for s_url in seed_urls:
                handle = self.extract_username_from_url(s_url)
                if handle:
                    seed_handles.append(handle.lower())
                    
        # Extract candidate handle
        cand_handle = self.extract_username_from_url(url)
        
        # Rule 1: Instant match if the candidate handle matches any seed handle
        if cand_handle and cand_handle.lower() in seed_handles:
            logger.info(f"Identity Verification: Instant handle match for URL {url} against seed handles {seed_handles}")
            return True
            
        # Rule 2: Social media handle alignment
        is_social = any(domain in url for domain in ["linkedin.com", "github.com", "twitter.com", "x.com", "instagram.com", "youtube.com", "facebook.com"])
        if is_social and cand_handle and seed_handles:
            handle_match = False
            for sh in seed_handles:
                if sh in cand_handle.lower() or cand_handle.lower() in sh:
                    handle_match = True
                    break
            
            if not handle_match:
                name_in_handle = all(part in cand_handle.lower() for part in name_parts)
                if not name_in_handle:
                    logger.warning(f"Identity Verification: REJECTED URL {url} - Social handle '{cand_handle}' mismatch against seed handles {seed_handles}")
                    return False

        # Case 1: URL holds target's combined full name or name parts
        joined_name = "".join(name_parts)
        if joined_name in url or "-".join(name_parts) in url or "_".join(name_parts) in url:
            return True
            
        # Case 2: Title or snippet has all parts of the candidate's name (strict relevance match)
        matches_all_parts = all(part in title or part in snippet or part in url for part in name_parts)
        if matches_all_parts:
            return True
            
        # Case 3: Direct social media profiles containing any part of the name
        matches_any_part = any(part in title or part in url for part in name_parts)
        if is_social and matches_any_part:
            return True
            
        # Case 4: Smart Fuzzy Name & Skill Match (highly useful for slight surname changes like Narayanan vs Narayanasamy)
        # Check if the first name is clearly present
        first_name = name_parts[0]
        if first_name in title or first_name in url or first_name in snippet:
            # Check if any other name part shares a significant common prefix (>= 5 chars) with a word in the text/title
            has_fuzzy_surname = False
            all_text = f"{title} {snippet} {url}".lower()
            import re
            words = re.findall(r'[a-z]{4,}', all_text)
            
            for part in name_parts[1:]:
                for w in words:
                    # Find common prefix length
                    prefix_len = 0
                    for c1, c2 in zip(part, w):
                        if c1 == c2:
                            prefix_len += 1
                        else:
                            break
                    if prefix_len >= 5:
                        has_fuzzy_surname = True
                        break
                if has_fuzzy_surname:
                    break
                    
            if has_fuzzy_surname:
                # Check for explicit skill/specialty matches
                skill_keywords = []
                if skills:
                    skill_keywords.extend([s.strip().lower() for s in skills.replace(",", " ").split() if len(s.strip()) > 2])
                if query:
                    skill_keywords.extend([q.strip().lower() for q in query.replace(",", " ").split() if len(q.strip()) > 3])
                
                # Filter out extremely common search terms
                stop_words = {"find", "career", "profile", "stats", "trophies", "social", "media", "handles", "sports", "person", "with", "skills", "extract", "details", "accomplishments", "data", "athlete", "full", "name", "biography", "current", "club", "team", "position", "role", "history"}
                skill_keywords = [k for k in skill_keywords if k not in stop_words]
                
                # If there are skill keywords, verify if at least one matches
                if skill_keywords:
                    matching_skills = [k for k in skill_keywords if k in all_text]
                    if matching_skills:
                        logger.info(f"Identity Verification: FUZZY MATCH ACCEPTED for URL {url} (First name '{first_name}' + fuzzy surname + matching skills {matching_skills})")
                        return True
            
        return False

    @log_execution_time
    def reason_node(self, state: AgentState):
        # -------------------------------------------------------------
        # STEP 1: Perform Tavily search using name & user details.
        # Updates temp_search_data.json.
        # -------------------------------------------------------------
        logger.info(f"Phase: REASON (Search) | Target: {state['name']}")
        
        name = state["name"]
        email = state.get("email") or ""
        phone = state.get("phone") or ""
        skills = state.get("skills") or ""
        location = state.get("location") or ""
        language = state.get("language") or ""
        age = state.get("age") or ""
        gender = state.get("gender") or ""
        dob = state.get("dob") or ""
        custom_query = state.get("query") or ""
        urls = state.get("urls", [])
        job_id = state.get("job_id", "")
        
        # Build precise natural language search query dynamically using full user-entered details to locate multiple profiles
        is_sports = self.is_sports_target(name, skills, custom_query, urls)
        
        details_list = []
        if skills:
            details_list.append(f"skills: {skills}")
        if location:
            details_list.append(f"location: {location}")
        if age:
            details_list.append(f"age: {age}")
        if dob:
            details_list.append(f"DOB: {dob}")
        if gender:
            details_list.append(f"gender: {gender}")
        if language:
            details_list.append(f"language: {language}")
            
        extra_info = []
        if email:
            extra_info.append(f"email: {email}")
        if phone:
            extra_info.append(f"phone: {phone}")
            
        details_str = f" [{', '.join(details_list)}]" if details_list else ""
        extra_str = f" ({', '.join(extra_info)})" if extra_info else ""
        
        if custom_query and custom_query.strip() != "":
            base_query = custom_query.strip()
            # Ensure name is in the custom query so that search is relevant
            if name.lower() not in base_query.lower():
                base_query = f"'{name}' {base_query}"
            query = f"{base_query}{details_str}{extra_str}"
        else:
            if is_sports:
                query = f"Find career profile, stats, trophies, and social media handles for sports person '{name}'{details_str}{extra_str}"
            else:
                query = f"Find professional profiles, linkedin, github, portfolio websites, and resume URLs for '{name}'{details_str}{extra_str}"
        
        logger.warning("================================================================================")
        logger.warning(f"STEP 1: SEARCHING WEB VIA SEARCH SERVICE (IS SPORTS = {is_sports})")
        logger.warning(f"QUERY: {query}")
        logger.warning("================================================================================")
        
        # Perform Search
        search_results = search_service.search(query)
        if isinstance(search_results, str) and search_results.startswith("Error"):
            logger.error(f"Search returned error: {search_results}. Falling back to default search.")
            search_results = search_service.search(name)
            
        if not isinstance(search_results, list):
            search_results = []
            
        # Extract concise details suffix for specialized search engine queries
        concise_details = []
        if skills:
            concise_details.append(skills.split(',')[0].strip())
        if location:
            concise_details.append(location.split(',')[0].strip())
        db_suffix = f" {' '.join(concise_details)}" if concise_details else ""
        
        # Specialized database search expansion depending on target type
        if is_sports:
            db_query = f"'{name}'{db_suffix} site:wikidata.org OR site:wikipedia.org OR site:espncricinfo.com OR site:transfermarkt.com OR site:sofascore.com"
            logger.warning(f"SPORTS OSINT SPECIALIZED EXPANSION: {db_query}")
            db_results = search_service.search(db_query)
            if isinstance(db_results, list):
                existing_urls = {item.get("url") for item in search_results if item.get("url")}
                for item in db_results:
                    if item.get("url") not in existing_urls:
                        search_results.append(item)
                logger.warning(f"Successfully integrated sports DB results. Total search results is now {len(search_results)}")
        else:
            tech_query = f"'{name}'{db_suffix} site:github.com OR site:facebook.com OR site:linkedin.com OR 'portfolio' OR 'personal website'"
            logger.warning(f"TECH/NORMAL OSINT SPECIALIZED EXPANSION: {tech_query}")
            tech_results = search_service.search(tech_query)
            if isinstance(tech_results, list):
                existing_urls = {item.get("url") for item in search_results if item.get("url")}
                for item in tech_results:
                    if item.get("url") not in existing_urls:
                        search_results.append(item)
                logger.warning(f"Successfully integrated tech/normal DB results. Total search results is now {len(search_results)}")
        # Limit total consolidated search results to 20 high-signal items
        search_results = search_results[:20]
            
        # Log to temp_search_data.json
        import time
        temp_search_path = "d:\\Agentic-AI\\temp_search_data.json"
        
        scraped_payload = []
        total_words = 0
        for item in search_results:
            content_str = item.get("content", "")
            words = len(str(content_str).split())
            total_words += words
            scraped_payload.append({
                "title": item.get("title", "No Title"),
                "url": item.get("url", ""),
                "content": content_str,
                "word_count": words
            })
            
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "job_id": job_id,
            "target_name": name,
            "action": "web_search",
            "action_input": {"query": query},
            "word_count": total_words,
            "scraped_payload": scraped_payload
        }
        
        try:
            temp_data = []
            if os.path.exists(temp_search_path):
                with open(temp_search_path, "r", encoding="utf-8") as f:
                    try:
                        temp_data = json.load(f)
                        if not isinstance(temp_data, list):
                            temp_data = []
                    except:
                        temp_data = []
            temp_data.append(log_entry)
            with open(temp_search_path, "w", encoding="utf-8") as f:
                json.dump(temp_data, f, indent=4, ensure_ascii=False)
            logger.info(f"Successfully cached Tavily search data to: {temp_search_path}")
        except Exception as e:
            logger.error(f"Failed to write search logs to temp file: {str(e)}")
            
        # Update State
        return {
            "phase": "REASON",
            "thought": f"Executed Tavily search with {len(search_results)} results.",
            "next_action": "web_search",
            "action_input": {"query": query},
            "observation": f"Discovered {len(search_results)} search results.",
            "data": {
                "search_results": search_results
            },
            "history": [log_entry],
            "step_count": 1
        }

    @log_execution_time
    async def act_node(self, state: AgentState):
        # -------------------------------------------------------------
        # STEP 2: Convert Tavily search results directly to vector embeddings.
        # Index in Qdrant, similarity search, and Cross-Encoder rerank.
        # Saves top 3 matched URLs to temp_rag_matched_data.json.
        # -------------------------------------------------------------
        logger.info(f"Phase: ACT (Embed & Rerank) | Target: {state['name']}")
        
        name = state["name"]
        job_id = state.get("job_id", "")
        search_results = state.get("data", {}).get("search_results", [])
        seed_urls = state.get("urls", [])
        
        # Strictly verify search results against the seed target's identity
        skills_val = state.get("skills") or ""
        custom_query_val = state.get("query") or ""
        
        verified_results = []
        for item in search_results:
            if self.verify_search_result(item, name, seed_urls, skills=skills_val, query=custom_query_val):
                verified_results.append(item)
            else:
                logger.warning(f"ACT: Filtering out unrelated namesake URL: {item.get('url')} (Title: {item.get('title')})")
                
        if not verified_results and search_results:
            logger.warning("ACT: All search results were filtered by strict identity checks. Falling back to original list to prevent blank profile.")
            verified_results = search_results

        logger.warning("================================================================================")
        logger.warning(f"STEP 2: VECTORIZING SEARCH SNIPPETS AND RERANKING CANDIDATES")
        logger.warning(f"TOTAL SEARCH RESULTS DISCOVERED: {len(search_results)} | VERIFIED: {len(verified_results)}")
        logger.warning("================================================================================")
        
        # Erase old temp_rag_matched_data.json
        temp_rag_path = "d:\\Agentic-AI\\temp_rag_matched_data.json"
        if os.path.exists(temp_rag_path):
            try:
                os.remove(temp_rag_path)
                logger.info(f"ACT: Erased legacy matched RAG context file: {temp_rag_path}")
            except Exception as e:
                logger.error(f"ACT: Failed to erase old RAG matched data file: {str(e)}")
                
        # Clear legacy vectors
        from app.core.vectordb import vectordb_service
        try:
            vectordb_service.delete_target_chunks(name)
            logger.info(f"ACT: Cleared legacy vector database entries for target '{name}'")
        except Exception as e:
            logger.warning(f"ACT: Could not clear existing chunks: {str(e)}")
            
        # Convert verified search results to chunks
        import uuid
        chunks = []
        for idx, item in enumerate(verified_results):
            content_str = item.get("content", "")
            title = item.get("title", "No Title")
            url = item.get("url", "")
            chunks.append({
                "chunk_id": f"search_{idx}_{uuid.uuid4().hex[:6]}",
                "source_url": url,
                "content": f"Title: {title}\nSnippet: {content_str}",
                "metadata": {
                    "title": title,
                    "target_name": name
                }
            })
            
        if chunks:
            vectordb_service.add_chunks(chunks)
            
        # Perform similarity search using dynamic target-type optimized queries
        skills_val = state.get("skills") or ""
        custom_query_val = state.get("query") or ""
        location_val = state.get("location") or ""
        age_val = state.get("age") or ""
        dob_val = state.get("dob") or ""
        gender_val = state.get("gender") or ""
        language_val = state.get("language") or ""
        email_val = state.get("email") or ""
        phone_val = state.get("phone") or ""
        
        details = []
        if skills_val:
            details.append(f"skills: '{skills_val}'")
        if location_val:
            details.append(f"location: '{location_val}'")
        if age_val:
            details.append(f"age: '{age_val}'")
        if dob_val:
            details.append(f"DOB: '{dob_val}'")
        if gender_val:
            details.append(f"gender: '{gender_val}'")
        if language_val:
            details.append(f"languages: '{language_val}'")
        if email_val:
            details.append(f"email: '{email_val}'")
        if phone_val:
            details.append(f"phone: '{phone_val}'")
        if custom_query_val:
            details.append(f"focus: '{custom_query_val}'")
            
        details_str = f" ({', '.join(details)})" if details else ""
        
        if self.is_sports_target(name, skills=state.get("skills") or "", query=state.get("query") or "", urls=seed_urls):
            rag_query = f"Extract professional sports details, stats, accomplishments, and career data for athlete {name}{details_str}: full name, biography, current club/team, position/role, career history (past clubs/teams, years), athletic skills/attributes, tournament achievements, cups/trophies, awards, certifications, and posts."
        else:
            rag_query = f"Extract professional career details, skills, projects, and work history for {name}{details_str}: biography, current job title, company, core skills, work history (past roles, companies, years), projects built, open-source repos, education, and recent posts."
        candidate_chunks = vectordb_service.similarity_search(rag_query, k=50, where={"target_name": name})
        
        if not candidate_chunks:
            logger.warning("ACT: No chunks returned under target name filter. Querying globally.")
            candidate_chunks = vectordb_service.similarity_search(rag_query, k=50)
            
        # Rerank to select top 3
        from app.core.reranker import reranker_service
        top_3_chunks = []
        if candidate_chunks:
            top_3_chunks = reranker_service.rerank(query=rag_query, chunks=candidate_chunks, top_n=3)
            
        # Log to temp_rag_matched_data.json
        formatted_rag = []
        top_urls = []
        for rank_idx, chunk in enumerate(top_3_chunks, 1):
            source_url = chunk.get("source_url", "")
            if source_url and source_url not in top_urls:
                top_urls.append(source_url)
            formatted_rag.append({
                "rank": rank_idx,
                "target_name": name,
                "query": rag_query,
                "chunk_id": chunk.get("chunk_id"),
                "source_url": source_url,
                "rerank_score": chunk.get("rerank_score", 0.0),
                "content": chunk.get("content"),
                "metadata": chunk.get("metadata", {})
            })
            
        try:
            with open(temp_rag_path, "w", encoding="utf-8") as f:
                json.dump(formatted_rag, f, indent=4, ensure_ascii=False)
            logger.info(f"ACT: Logged top 3 matched search chunks to: {temp_rag_path}")
        except Exception as e:
            logger.error(f"ACT: Failed to log matched RAG chunks: {str(e)}")
            
        # If fewer than 3 unique URLs in top_3_chunks, append other verified URLs to have 3 to scrape
        for item in verified_results:
            url = item.get("url")
            if url and url not in top_urls and len(top_urls) < 3:
                top_urls.append(url)
                
        logger.warning("================================================================================")
        logger.warning(f"TOP 3 SELECT CANDIDATE URLS RERANKED:")
        for idx, url in enumerate(top_urls, 1):
            logger.warning(f"   [{idx}] {url}")
        logger.warning("================================================================================")
        
        # Update State
        return {
            "phase": "ACT",
            "thought": f"Selected top {len(top_urls)} URLs based on search result semantic relevance and identity checks.",
            "next_action": "embed_and_rerank",
            "action_input": {"top_urls": top_urls},
            "observation": f"Identified top URLs for scraping: {top_urls}",
            "data": {
                "search_results": search_results,
                "top_urls": top_urls
            },
            "history": state["history"] + [{
                "phase": "ACT",
                "action": "embed_and_rerank",
                "action_input": {"top_urls": top_urls}
            }],
            "step_count": 1
        }

    @log_execution_time
    async def observe_node(self, state: AgentState):
        # -------------------------------------------------------------
        # STEP 3: Scrape the entire page contents from the top 3 URLs.
        # Saves to temp_scraped_data.json.
        # -------------------------------------------------------------
        logger.info(f"Phase: OBSERVE (Scrape Top 3) | Target: {state['name']}")
        
        name = state["name"]
        job_id = state.get("job_id", "")
        top_urls = state.get("data", {}).get("top_urls", [])
        
        logger.warning("================================================================================")
        logger.warning(f"STEP 3: CRAWLING ENTIRE DATA FROM ALL TOP {len(top_urls)} URLS")
        logger.warning("================================================================================")
        
        # Scrape all top 3 URLs in parallel
        tasks = [scraper_service.scrape(url) for url in top_urls]
        scraped_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        scraped_pages = []
        for url, page_data in zip(top_urls, scraped_results):
            if isinstance(page_data, Exception):
                logger.error(f"Failed to scrape {url}: {str(page_data)}")
                scraped_pages.append({
                    "source_url": url,
                    "error": f"Scrape failed: {str(page_data)}"
                })
                continue
                
            if not isinstance(page_data, dict):
                scraped_pages.append({
                    "source_url": url,
                    "error": str(page_data)
                })
                continue
                
            if "source_url" not in page_data:
                page_data["source_url"] = url
            
            # Check if the scraped page has very thin content (e.g. < 350 words)
            text_content = page_data.get("visible_text") or ""
            words = len(text_content.split())
            discovered_links = page_data.get("discovered_links", [])
            
            # Dynamic Deep Crawling: If content is low, follow the top 2-3 high-value internal sub-links
            if words < 350 and discovered_links:
                logger.warning(f"CRAWL COMPROMISE: '{url}' has very thin content ({words} words). Crawling sub-links to enrich...")
                
                from urllib.parse import urlparse
                base_domain = urlparse(url).netloc
                
                sub_urls_to_scrape = []
                for link in discovered_links:
                    parsed_link = urlparse(link)
                    # Ensure it's the same domain, has a path, and isn't a static social/utility page
                    if parsed_link.netloc == base_domain and len(parsed_link.path) > 2:
                        if not any(x in parsed_link.path.lower() for x in ["privacy", "terms", "abuse", "report", "subscribe", "contact", "about-us"]):
                            if link not in sub_urls_to_scrape and link != url:
                                sub_urls_to_scrape.append(link)
                                if len(sub_urls_to_scrape) >= 2: # limit to top 2 sub-pages to fit within TPM limits
                                    break
                                    
                # Scrape internal articles/sub-pages to extract deep bios
                sub_contents = []
                for s_url in sub_urls_to_scrape:
                    logger.warning(f"   -> DYNAMICALLY DEEP CRAWLING SUB-URL: {s_url}")
                    try:
                        sub_page = await scraper_service.scrape(s_url)
                        if isinstance(sub_page, dict) and sub_page.get("visible_text"):
                            sub_text = sub_page["visible_text"]
                            sub_words = len(sub_text.split())
                            logger.info(f"      Successfully fetched {sub_words} words from {s_url}")
                            sub_contents.append(f"\n\n--- Sub-Page Article [{s_url}] ---\n{sub_text}")
                    except Exception as sub_err:
                        logger.warning(f"      Failed to scrape sub-url {s_url}: {str(sub_err)}")
                        
                if sub_contents:
                    page_data["visible_text"] += "\n" + "\n".join(sub_contents)
                    logger.warning(f"CRAWL ENRICHED: Added sub-pages. Total word count is now: {len(page_data['visible_text'].split())} words!")
                    
            scraped_pages.append(page_data)
                
        # Log to temp_scraped_data.json
        import time
        temp_scraped_path = "d:\\Agentic-AI\\temp_scraped_data.json"
        
        scraped_entries = []
        for page in scraped_pages:
            content_str = page.get("visible_text") or page.get("content") or page.get("text") or ""
            words = len(str(content_str).split())
            entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "job_id": job_id,
                "target_name": name,
                "action": "scraper",
                "action_input": {"url": page.get("source_url")},
                "word_count": words,
                "scraped_payload": page
            }
            scraped_entries.append(entry)
            
        try:
            with open(temp_scraped_path, "w", encoding="utf-8") as f:
                json.dump(scraped_entries, f, indent=4, ensure_ascii=False)
            logger.info(f"Successfully cached scraped data to: {temp_scraped_path}")
        except Exception as e:
            logger.error(f"Failed to write scraped logs: {str(e)}")
            
        # Update State
        return {
            "phase": "OBSERVE",
            "observation": f"Scraped full content of top {len(scraped_pages)} URLs.",
            "data": {
                "search_results": state.get("data", {}).get("search_results", []),
                "top_urls": top_urls,
                "scraped_pages": scraped_pages
            },
            "history": state["history"] + [{
                "phase": "OBSERVE",
                "observation": f"Successfully scraped full contents of {len(scraped_pages)} URLs."
            }],
            "step_count": 1
        }

    @log_execution_time
    def reflect_node(self, state: AgentState):
        # -------------------------------------------------------------
        # Transitions directly to final node.
        # -------------------------------------------------------------
        logger.info(f"Phase: REFLECT | Completed pipeline steps.")
        return {
            "phase": "REFLECT",
            "reflection": "Completed search, RAG reranking, and full scraping. Compiling final LLM profile...",
            "complete": True,
            "history": state["history"] + [{
                "phase": "REFLECT",
                "reflection": "All data collected. Starting final profile generation."
            }],
            "step_count": 1
        }

    def should_continue(self, state: AgentState):
        if state.get("complete"):
            return "end"
        return "continue"

    @log_execution_time
    def final_node(self, state: AgentState):
        # -------------------------------------------------------------
        # STEP 4: Send the scraped entire contents from the top 3 URLs to LLM.
        # Synthesizes the structured professional profile.
        # -------------------------------------------------------------
        logger.info(f"Phase: FINAL | Generating structured profile for {state['name']}")
        
        name = state["name"]
        scraped_pages = state.get("data", {}).get("scraped_pages", [])
        
        logger.warning("================================================================================")
        logger.warning(f"STEP 4: SEMANTIC CHUNKING, INDEXING & RERANKING FULL SCRAPED PAGES")
        logger.warning(f"TOTAL SOURCE PAGES: {len(scraped_pages)}")
        logger.warning("================================================================================")
        
        # 1. Chunk and Vectorize all scraped page content
        import uuid
        import re as re_mod
        from app.core.vectordb import vectordb_service
        from app.core.reranker import reranker_service
        
        scraped_chunks = []
        crawled_urls = []
        for idx, page in enumerate(scraped_pages, 1):
            url = page.get("source_url") or "Unknown URL"
            crawled_urls.append(url)
            text = page.get("visible_text") or page.get("content") or page.get("text") or ""
            title = page.get("title") or "Web Page"
            
            # Algorithmic Noise Stripping: strip redundant whitespace, long repeating symbols
            text = re_mod.sub(r'[\-\=\*\_\#\@\+\:\/\.\,\;\!\?]{4,}', ' ', text)
            text = re_mod.sub(r'\s+', ' ', text).strip()
            
            # Split cleaned text into 500-char blocks with 100-char overlap
            chunk_size = 500
            overlap = 100
            start = 0
            chunk_idx = 0
            while start < len(text):
                end = start + chunk_size
                chunk_content = text[start:end]
                scraped_chunks.append({
                    "chunk_id": f"scraped_{idx}_{chunk_idx}_{uuid.uuid4().hex[:6]}",
                    "source_url": url,
                    "content": f"Title: {title}\nContent:\n{chunk_content}",
                    "metadata": {
                        "title": title,
                        "target_name": name,
                        "type": "scraped_page"
                    }
                })
                start += (chunk_size - overlap)
                chunk_idx += 1
                
        # 2. Add scraped chunks to Qdrant (in addition to search chunks)
        if scraped_chunks:
            try:
                vectordb_service.add_chunks(scraped_chunks)
                logger.info(f"FINAL: Vectorized and added {len(scraped_chunks)} scraped chunks to local database.")
            except Exception as e:
                logger.error(f"FINAL: Failed to add scraped chunks to Qdrant: {str(e)}")
                
        # 3. Retrieve top semantically relevant chunks
        skills_val = state.get("skills") or ""
        custom_query_val = state.get("query") or ""
        location_val = state.get("location") or ""
        age_val = state.get("age") or ""
        dob_val = state.get("dob") or ""
        gender_val = state.get("gender") or ""
        language_val = state.get("language") or ""
        email_val = state.get("email") or ""
        phone_val = state.get("phone") or ""
        
        details = []
        if skills_val:
            details.append(f"skills: '{skills_val}'")
        if location_val:
            details.append(f"location: '{location_val}'")
        if age_val:
            details.append(f"age: '{age_val}'")
        if dob_val:
            details.append(f"DOB: '{dob_val}'")
        if gender_val:
            details.append(f"gender: '{gender_val}'")
        if language_val:
            details.append(f"languages: '{language_val}'")
        if email_val:
            details.append(f"email: '{email_val}'")
        if phone_val:
            details.append(f"phone: '{phone_val}'")
        if custom_query_val:
            details.append(f"focus: '{custom_query_val}'")
            
        details_str = f" ({', '.join(details)})" if details else ""
        
        rag_query = f"Extract professional career summary, jobs/experience, technical or athletic skills, key initiatives/projects, social footprint, and achievements/accolades for {name}{details_str}."
        candidate_chunks = vectordb_service.similarity_search(rag_query, k=60, where={"target_name": name})
        
        # 4. Rerank down to top 5 chunks to strictly enforce our token budgets
        top_5_chunks = []
        if candidate_chunks:
            try:
                top_5_chunks = reranker_service.rerank(query=rag_query, chunks=candidate_chunks, top_n=5)
                logger.info(f"FINAL: Reranked down to top {len(top_5_chunks)} highly relevant chunks for synthesis.")
            except Exception as re_err:
                logger.error(f"FINAL: Reranker failed: {str(re_err)}. Falling back to top 5 candidate chunks.")
                top_5_chunks = candidate_chunks[:5]
                
        # 5. Serialize context using Flat-Pipe TOON format for optimal token compression
        from app.utils.toon import serialize_rag_context_to_toon
        rag_data_context = serialize_rag_context_to_toon(
            name=name,
            query=rag_query,
            chunks=top_5_chunks
        ) if top_5_chunks else "No scraped context available."
        
        prompt = ChatPromptTemplate.from_template("""
        You are a highly advanced OSINT (Open Source Intelligence) Analysis Engine.
        Your job is to build a complete, highly-structured, classified public profile of the target individual using ONLY the provided retrieved context (RAG data in Flat-Pipe TOON format).
        
        Target Person Name: {name}
        Context (TOON Format):
        {data}
        
        📌 USER-SUPPLIED BASELINE DETAILS (TRUTH ANCHORS):
        These are the exact verified baseline details provided by the user. You MUST pre-populate or integrate them directly into your response fields, and resolve/enrich them with the scraped context:
        - Full Name / Name: {name}
        - Email: {user_email}
        - Phone: {user_phone}
        - Skills/Specialties: {user_skills}
        - Age: {user_age}
        - Gender: {user_gender}
        - Date of Birth: {user_dob}
        - Location: {user_location}
        - Preferred Language: {user_language}
        - Search Query Context: {user_query}
        
        Ensure that these user-supplied values are integrated into the output JSON fields (e.g., email and phone in 'contact_info', skills in 'skills', age, gender, and dob in 'basic_info' and biographical intelligence, location in 'location', preferred language in languages/description, etc.). Do not ignore or drop them unless they are empty.
             ---
        🚨 CRITICAL PROFILE CLASSIFICATION RULE:
        You must autonomously analyze the scraped data and classify the target into exactly one of four profile types:
        1. "sports": If the target is an athlete, sports professional, player, coach, or sports executive (e.g. cricketer, footballer, tennis player, etc.).
        2. "tech": If the target is a pure hardcore developer, programmer, systems engineer, software engineer, or hacker.
        3. "tech_normal": If the target is a hybrid technical professional, tech product manager, solutions architect, dev advocate, tech executive, or designer.
        4. "general": For all other general professionals, business executives, managers, entrepreneurs, marketers, writers, doctors, academics, or normal people.
        
        Set this classification in the "profile_type" JSON field.
        
        ---
        🚨 STRICT CONCISENESS & TOKEN CONSTRAINTS (PREVENT TRUNCATION):
        To fit within output length limits, you must keep all descriptions and dossiers extremely brief:
        - Bio / Summary / Descriptions: maximum 1-2 dense sentences per block.
        - Experience / Projects / Education lists: Limit to the top 3-4 entries.
        - Markdown table in the dossier: maximum 3-5 rows.
        - Do not include large paragraphs or fluff. Be concise, direct, and factual.
        
        ---
        🧠 INSTRUCTIONS & GUIDELINES:
        1. NO HALLUCINATION: Do NOT assume or invent missing facts, projects, or numbers. Only state what is verified in the context.
        2. RESOLVE CONFLICTS: If there are conflicting facts, resolve them using strict source priority: Wikidata > Wikipedia > Official Sites > News/Articles.
        3. SOURCE AUDITABILITY: Assign the correct 'source_url' to each list item in experience, projects, articles, achievements, and education. Match it from the 'source' attribute of 'ctx' entities.
        4. TOON PARSING: The data is in token-optimized Flat-Pipe TOON format (entity|key=value). 'ctx' represents a chunk of scraped context. 'source' is the URL, and 'content' is the text.
        5. FIELD MAPPINGS:
           - For "sports": Map club/team history to 'experience' (title=Position/Role, company=Club/Team, description=Appearances/Stats). Map tournaments/seasons to 'projects' (name=Tournament name, technologies=athletic stats like Goals, Runs, Wickets, Assists). Map athletic attributes to 'skills'. Map cups/medals to 'achievements'.
           - For "tech": Map software/programming skills to 'skills'. Map programming languages/frameworks to 'tech_stack' (and also duplicate under 'skills'). Map coding projects and repositories to 'projects'. Map open-source achievements to 'achievements'.
           - For "tech_normal": Map jobs/titles to 'experience'. Map product initiatives, repositories, or technical platforms to 'projects'. Map professional expertise to 'skills'. Map certifications or business milestones to 'achievements'.
           - For "general": Map jobs/titles to 'experience'. Map business initiatives, publications, or campaigns to 'projects'. Map professional expertise to 'skills'. Map leadership indices or business milestones to 'achievements'.
         
        6. CUSTOM OSINT DOSSIER COMPILATION:
           You MUST compile a stunning plain-text markdown document in the "osint_dossier_markdown" field, customized precisely to the target's "profile_type". Do NOT use raw JSON or TOON syntax inside this markdown.
           
           Use the following exact layout structures depending on the classified "profile_type":
           
           👉 IF PROFILE TYPE IS "sports":
           ⚡ CLASSIFIED SPORTS OSINT DOSSIER: {name}
           ======================================================================
           SECURITY LEVEL: CONFIDENTIAL // AGENTIC EYE ONLY // SPORTS OSINT DIVISION
           
           👤 BIOGRAPHICAL INTEL
           ---------------------------
           * Full Name: [Full Name]
           * Place of Birth: [Birthplace]
           * Date of Birth: [DOB]
           * Age: [Age]
           * Gender: [Gender]
           * Nationality: [Nationality]
           * Playing Years: [Active Career Years]
           * Height/Weight: [Height & Weight]
           
           ⚡ ATHLETIC SPECIALTIES & PLAY STYLE
           ----------------------------------
           [Brief analysis of athletic specialties, attributes, style of play, strengths.]
           
           📊 CAREER STATS & CLUB HISTORY
           ------------------------------
           [Markdown table summarizing club history/stats, max 3-5 rows:
           | Years | Club/Team | Appearances | Goals/Runs/Wickets | Assists/Role |
           |-------|-----------|-------------|--------------------|--------------|]
           
           🏆 CLASSIFIED HONOURS & ACHIEVEMENTS
           ------------------------------------
           * [List of verified cups, trophies, records, or accolades.]
           
           🌐 VERIFIED SOCIAL & PUBLIC FOOTPRINT
           ------------------------------------
           * [Verified social handles or profiles found in the data.]
           
           🔒 OSINT THREAT ANALYSIS & ENGINE CLASSIFICATION
           -----------------------------------------------
           * OSINT Engine Confidence: [Confidence Score]
           * Audit Justification: [Brief justification of credibility and source analysis.]
           
           👉 IF PROFILE TYPE IS "tech":
           💻 CLASSIFIED TECH OSINT DOSSIER: {name}
           ======================================================================
           SECURITY LEVEL: CONFIDENTIAL // AGENTIC EYE ONLY // TECH OSINT DIVISION
           
           👤 CORE DEVELOPER PROFILE
           ---------------------------
           * Full Name: [Full Name]
           * Core Title: [Primary Developer Title]
           * Focus Area: [e.g. Frontend, Backend, ML, DevOps]
           * Location: [Location]
           * Active Years: [Active Career Years]
           * Preferred Tech: [Primary Programming Languages]
           
           🛠️ TECH MATRIX & SPECIFICATION
           ----------------------------------
           [Brief technical write-up detailing their tech stack, expertise, framework preferences.]
           
           📦 REPOSITORY FOOTPRINT & PROJECTS
           ------------------------------
           [Markdown table summarizing contributions or repositories, max 3-5 rows:
           | Repository / Project | Role | Stars | Key Tech Used | Impact Summary |
           |----------------------|------|-------|----------------|----------------|]
           
           🏆 CERTIFICATIONS & OPEN SOURCE CONTRIBUTIONS
           ------------------------------------
           * [List of verified contributions, commits, certs, or technical accomplishments.]
           
           🌐 VERIFIED SOCIAL & DEVELOPER FOOTPRINT
           ------------------------------------
           * [Verified GitHub, LinkedIn, StackOverflow, or portfolio handles.]
           
           🔒 OSINT THREAT ANALYSIS & ENGINE CLASSIFICATION
           -----------------------------------------------
           * OSINT Engine Confidence: [Confidence Score]
           * Audit Justification: [Brief justification of credibility and source analysis.]

           👉 IF PROFILE TYPE IS "tech_normal":
           📁 SECURE TECH-NORMAL DOSSIER // PROFESSIONAL BRIEFING: {name}
           ======================================================================
           SECURITY LEVEL: CONFIDENTIAL // AGENTIC EYE ONLY // TECH-NORMAL DIVISION
           
           👤 PROFESSIONAL PROFILE
           ---------------------------
           * Full Name: [Full Name]
           * Title/Role: [Lead Tech Title]
           * Tech Focus: [e.g. Enterprise AI, Cloud Strategy, Developer Systems]
           * Location: [Location]
           * Active Career Span: [Active Years]
           * Core Tech Matrix: [Top programming languages/technologies]
           
           💼 KEY INITIATIVES & IMPACT
           ----------------------------------
           [Brief analysis of product-technical expertise, systems design, and cross-functional leadership.]
           
           📊 STRATEGIC PROJECTS & PRODUCTS
           ------------------------------
           [Markdown table summarizing key product initiatives or repositories, max 3-5 rows:
           | Product / Project | Tech Stack | Role | Business & Technical Impact |
           |-------------------|------------|------|----------------------------|]
           
           🏆 ACCOLADES & COMMUNITY FOOTPRINT
           ------------------------------------
           * [List of certifications, community speaking, speaking engagements, or technical contributions.]
           
           🌐 VERIFIED PUBLIC FOOTPRINT
           ------------------------------------
           * [Verified LinkedIn, GitHub, personal portfolio, or corporate bio profiles.]
           
           🔒 OSINT THREAT ANALYSIS & ENGINE CLASSIFICATION
           -----------------------------------------------
           * OSINT Engine Confidence: [Confidence Score]
           * Audit Justification: [Brief justification of source credibility.]
           
           👉 IF PROFILE TYPE IS "general":
           💼 EXECUTIVE BRIEFING & OSINT DOSSIER: {name}
           ======================================================================
           SECURITY LEVEL: CONFIDENTIAL // AGENTIC EYE ONLY // GENERAL OSINT DIVISION
           
           👤 EXECUTIVE PROFILE
           ---------------------------
           * Full Name: [Full Name]
           * Title/Position: [Primary Job Title]
           * Industry: [Industry Sector]
           * Location: [Location]
           * Career Span: [Active Career Years]
           * Key Expertise: [Top 3-4 professional specialties]
           
           💼 PROFESSIONAL FOOTPRINT & BIOGRAPHY
           ----------------------------------
           [Brief biography summarizing professional trajectory, business leadership, or achievements.]
           
           📈 STRATEGIC IMPACT & HISTORY
           ------------------------------
           [Markdown table summarizing professional history, max 3-5 rows:
           | Years | Organization | Position | Business/Operational Impact |
           |-------|--------------|----------|-----------------------------|]
           
           🏆 PUBLICATIONS, PAPERS & RECOGNITIONS
           ------------------------------------
           * [List of verified articles, papers, presentations, patents, or honors.]
           
           🌐 VERIFIED PUBLIC FOOTPRINT
           ------------------------------------
           * [Verified LinkedIn, company bios, personal websites, or public handles.]
           
           🔒 OSINT THREAT ANALYSIS & ENGINE CLASSIFICATION
           -----------------------------------------------
           * OSINT Engine Confidence: [Confidence Score]
           * Audit Justification: [Brief justification of credibility and source analysis.]
         
        Respond in STRICT JSON format with this exact structure:
        {{
            "profile_type": "sports | tech | tech_normal | general",
            "osint_dossier_markdown": "string (custom category markdown)",
            "profile": {{
                "name": "{name}",
                "bio": "string (maximum 2 dense sentences)",
                "location": "string",
                "skills": ["string"],
                "experience": [{{ "title": "string", "company": "string", "period": "string", "description": "string (max 1 sentence)", "source_url": "string" }}],
                "projects": [{{ "name": "string", "description": "string (max 1 sentence)", "technologies": ["string"], "source_url": "string" }}],
                "social_links": ["string"],
                "recent_posts": [{{ "content": "string", "summary": "string", "date": "string (e.g. 'May 18, 2026 at 10:30 AM')", "link": "string", "source_url": "string" }}],
                
                "basic_info": {{
                    "full_name": "{name}",
                    "headline": "string (max 1 sentence)",
                    "location": "string",
                    "bio": "string (max 2 dense sentences)",
                    "source_url": "string"
                }},
                "education": [{{ "school": "string", "degree": "string", "period": "string", "source_url": "string" }}],
                "social_profiles": ["string"],
                "verified_profiles": {{
                    "linkedin": "string or empty",
                    "twitter": "string or empty",
                    "instagram": "string or empty",
                    "github": "string or empty",
                    "youtube": "string or empty",
                    "facebook": "string or empty",
                    "personal_website": "string or empty",
                    "blog": "string or empty"
                }},
                "github_data": {{
                    "repositories_count": 0,
                    "stars_received": 0,
                    "top_repositories": [{{ "name": "string", "stars": 0, "link": "string" }}]
                }},
                "articles": [{{ "title": "string", "publisher": "string", "date": "string", "summary": "string", "source_url": "string" }}],
                "achievements": ["string"],
                "tech_stack": ["string"],
                "communities": ["string"],
                "contact_info": {{ "email": "string", "phone": "string" }},
                "sources_used": ["string"]
            }},
            "insights": {{
                "summary": "string (max 2 dense sentences)",
                "key_strengths": ["string"],
                "expertise_areas": ["string"],
                "online_presence": "string (max 1 sentence)"
            }},
            "confidence": {{
                "score": float (0-1),
                "justification": "string"
            }}
        }}
        """)
        
        job_id = state.get("job_id", "")
        chain = prompt | self.llm
        response = self.safe_invoke(
            chain, 
            {
                "name": name, 
                "data": rag_data_context,
                "user_email": state.get("email") or "",
                "user_phone": state.get("phone") or "",
                "user_skills": state.get("skills") or "",
                "user_age": state.get("age") or "",
                "user_gender": state.get("gender") or "",
                "user_dob": state.get("dob") or "",
                "user_location": state.get("location") or "",
                "user_language": state.get("language") or "",
                "user_query": state.get("query") or ""
            }, 
            job_id=job_id
        )
        res = self.safe_json_load(response.content)
        
        # Populate backward compatibility keys
        if isinstance(res, dict):
            profile_type = res.get("profile_type") or "general"
            dossier_md = res.get("osint_dossier_markdown") or ""
            res["profile_type"] = profile_type
            res["osint_dossier_markdown"] = dossier_md
            res["sports_profile_markdown"] = dossier_md
            
            if "profile" in res and isinstance(res["profile"], dict):
                res["profile"]["profile_type"] = profile_type
                res["profile"]["osint_dossier_markdown"] = dossier_md
                res["profile"]["sports_profile_markdown"] = dossier_md
        
        # --- HARD HALLUCINATION FILTER (POST-PROCESSING) ---
        if isinstance(res, dict) and "profile" in res:
            posts = res["profile"].get("recent_posts", [])
            filtered_posts = []
            for post in posts:
                content = post.get("content", "").lower()
                date = post.get("date", "")
                is_hallucinated = any(phrase in content for phrase in [
                    "revolutionizing", "leveraging machine learning", "chatbot", 
                    "24/7", "personalized support", "search engine is getting smarter", 
                    "ai-powered search", "google's ai"
                ])
                is_old = any(year in date for year in ["2020", "2021", "2022", "2023"])
                if not (is_hallucinated or is_old):
                    filtered_posts.append(post)
            res["profile"]["recent_posts"] = filtered_posts[:3]
            res["profile"]["sources_used"] = crawled_urls
            
            # Retrieve accumulated tokens
            token_log = "Prompt: 0 | Completion: 0 | Total: 0"
            if job_id and job_id in jobs and "token_usage" in jobs[job_id]:
                usage = jobs[job_id]["token_usage"]
                token_log = f"Prompt/Input Tokens: {usage['prompt_tokens']} | Completion/Output Tokens: {usage['completion_tokens']} | Total Tokens: {usage['total_tokens']}"
                res["token_usage"] = usage

            logger.warning("================================================================================")
            logger.warning(f"CONSOLIDATED PROFILE COMPLETED FOR: {name} (TYPE: {profile_type})")
            logger.warning(f"TOTAL TOKENS CONSUMED: {token_log}")
            logger.warning(f"BIO: {res['profile'].get('bio', '')[:120]}...")
            logger.warning(f"VERIFIED SOURCES USED ({len(crawled_urls)} sources integrated):")
            for idx, src_url in enumerate(crawled_urls, 1):
                logger.warning(f"   [{idx}] {src_url}")
            logger.warning("================================================================================")
            
        return {
            "phase": "FINAL",
            "data": res,
            "history": state["history"] + [res]
        }

    def repair_truncated_json(self, text: str) -> str:
        text = text.strip()
        if not text:
            return "{}"
        
        start_idx = text.find('{')
        if start_idx == -1:
            return "{}"
        
        text = text[start_idx:]
        
        state = "normal"  # normal, string, escape
        stack = []
        clean_up_to = 0
        
        i = 0
        while i < len(text):
            char = text[i]
            
            if state == "escape":
                state = "string"
                i += 1
                continue
                
            if state == "string":
                if char == "\\":
                    state = "escape"
                elif char == '"':
                    state = "normal"
                    clean_up_to = i + 1
                i += 1
                continue
                
            # normal state
            if char == '"':
                state = "string"
            elif char in ('{', '['):
                stack.append(char)
                clean_up_to = i + 1
            elif char in ('}', ']'):
                if stack:
                    stack.pop()
                clean_up_to = i + 1
            elif char in (',', ':', ' ', '\n', '\r', '\t'):
                pass
            elif char.isalnum() or char in ('-', '.', 't', 'f', 'n'):
                clean_up_to = i + 1
                
            i += 1
            
        truncated_text = text[:clean_up_to].strip()
        
        while truncated_text and truncated_text[-1] in (',', ':', ' '):
            truncated_text = truncated_text[:-1].strip()
            
        open_stack = []
        i = 0
        state = "normal"
        while i < len(truncated_text):
            char = truncated_text[i]
            if state == "escape":
                state = "string"
                i += 1
                continue
            if state == "string":
                if char == "\\":
                    state = "escape"
                elif char == '"':
                    state = "normal"
                i += 1
                continue
            if char == '"':
                state = "string"
            elif char == '{':
                open_stack.append('{')
            elif char == '[':
                open_stack.append('[')
            elif char == '}':
                if open_stack and open_stack[-1] == '{':
                    open_stack.pop()
            elif char == ']':
                if open_stack and open_stack[-1] == '[':
                    open_stack.pop()
            i += 1
            
        closing_chars = []
        for op in reversed(open_stack):
            if op == '{':
                closing_chars.append('}')
            elif op == '[':
                closing_chars.append(']')
                
        return truncated_text + "".join(closing_chars)

    def clean_json(self, text: str):
        # Robustly extract JSON block from raw LLM text response
        text = text.strip()
        
        # Remove markdown fences at the start/end if present
        if text.startswith("```json"):
            text = text[7:].strip()
        elif text.startswith("```"):
            text = text[3:].strip()
            
        if text.endswith("```"):
            text = text[:-3].strip()
            
        # Extract content between first '{' and last '}'
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1:
            text = text[first_brace:last_brace+1]
            
        return text.strip()

    def safe_json_load(self, text: str, fallback_type: str = "dict"):
        # Safely parse JSON strings with fallbacks to avoid application crashes
        """Safely parse JSON with fallbacks."""
        cleaned = self.clean_json(text)
        try:
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"Initial JSON parse failed. Attempting state-machine repair... Error: {str(e)}")
            try:
                repaired = self.repair_truncated_json(cleaned)
                logger.info("JSON repaired successfully. Attempting second parse...")
                return json.loads(repaired)
            except Exception as e_repair:
                logger.error(f"State-machine repair also failed. Error: {str(e_repair)}")
                if fallback_type == "dict":
                    return {"error": "Failed to parse JSON", "raw": text}
                return []

orchestrator = Orchestrator()
