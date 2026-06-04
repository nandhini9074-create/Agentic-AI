from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import sys
import uvicorn

# Windows-specific event loop policy for Playwright/Subprocesses
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from app.agents.orchestrator import orchestrator, AgentState
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import logger
from app.db.database import SessionLocal, ProfileDB
from app.utils.job_store import jobs
import uuid
from app.services.entity_discovery import entity_discovery_service
from app.api.routes import router as rag_router

app = FastAPI(title="Agentic AI Profiler")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the new RAG Profile Generation routes
app.include_router(rag_router, prefix="/api/rag", tags=["RAG Profile"])


class ProfileRequest(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None
    query: Optional[str] = None
    urls: Optional[List[str]] = []

class GenerateProfileRequest(BaseModel):
    name: str
    url: str

class DiscoverEntityRequest(BaseModel):
    url: str

@app.post("/generate-profile")
async def generate_profile(request: GenerateProfileRequest, background_tasks: BackgroundTasks):
    # Entry point for single-URL requests as specified in Step 1. Maps seamlessly to the multi-source pipeline.
    profile_req = ProfileRequest(
        name=request.name,
        email="unknown@email.com",
        phone="unknown",
        skills="Software Engineering",
        urls=[request.url]
    )
    return await build_profile(profile_req, background_tasks)

@app.post("/discover-entity")
async def discover_entity(request: DiscoverEntityRequest):
    # Step-by-step single-URL entity discovery and verification endpoint
    return await entity_discovery_service.discover(request.url)

@app.post("/build-profile")
async def build_profile(request: ProfileRequest, background_tasks: BackgroundTasks):
    # Entry point to start a new profile synthesis job in the background
    # Auto-cleanup: keep only the last 20 jobs to prevent memory bloat
    if len(jobs) > 20:
        logger.info("Cleaning up old jobs to maintain server health")
        oldest_jobs = sorted(jobs.keys(), key=lambda k: k)[:10]
        for k in oldest_jobs:
            if jobs[k].get("status") != "running":
                del jobs[k]

    job_id = str(uuid.uuid4())
    logger.info(f"Starting new profile build job: {job_id} for {request.name}")
    jobs[job_id] = {"status": "running", "steps": []} #Store Job State
    
    background_tasks.add_task(
        run_agent, 
        job_id, 
        request.name, 
        request.email,
        request.phone,
        request.skills,
        request.age,
        request.gender,
        request.dob,
        request.location,
        request.language,
        request.query,
        request.urls or []
    )
    
    return {"job_id": job_id}

@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    # Retrieve the current status and execution steps of a specific job
    logger.info(f"Checking status for job: {job_id}")
    return jobs.get(job_id, {"error": "Job not found"})

@app.post("/job/{job_id}/cancel")
async def cancel_job(job_id: str):
    # Request immediate cancellation of a running background job
    if job_id in jobs:
        logger.warning(f"Cancelling job: {job_id}")
        jobs[job_id]["status"] = "cancelled"
        return {"message": "Job cancellation requested"}
    return {"error": "Job not found"}, 404

async def run_agent(
    job_id: str,
    name: str,
    email: Optional[str],
    phone: Optional[str],
    skills: Optional[str],
    age: Optional[str],
    gender: Optional[str],
    dob: Optional[str],
    location: Optional[str],
    language: Optional[str],
    query: Optional[str],
    urls: List[str]
):
    # Main background execution loop that orchestrates the agentic workflow and saves the final result
    logger.info(f"Agent thread started for job {job_id}")
    
    # Automatically clean up old temporary scraping and RAG logs on new trigger
    import os
    temp_file_path = "d:\\Agentic-AI\\temp_scraped_data.json"
    temp_rag_path = "d:\\Agentic-AI\\temp_rag_matched_data.json"
    temp_search_path = "d:\\Agentic-AI\\temp_search_data.json"
    
    for path in [temp_file_path, temp_rag_path, temp_search_path]:
        if os.path.exists(path):
            try:
                os.remove(path)
                logger.info(f"Successfully cleaned up old temporary cache: {path}")
            except Exception as e:
                logger.error(f"Failed to clear cache file {path}: {str(e)}")
            
    try:
        initial_state = {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "age": age,
            "gender": gender,
            "dob": dob,
            "location": location,
            "language": language,
            "query": query,
            "urls": urls,
            "data": {},
            "next_action": None,
            "action_input": None,
            "observation": None,
            "reflection": None,
            "history": [],
            "phase": "REASON",
            "complete": False,
            "job_id": job_id,
            "step_count": 0
        }
        
        async for output in orchestrator.app.astream(initial_state):
            # Check for cancellation
            if jobs.get(job_id, {}).get("status") == "cancelled":
                logger.info(f"Agent job {job_id} stopping due to cancellation")
                return

            for node, state in output.items():
                logger.info(f"Job {job_id} reached node: {node}")
                jobs[job_id]["steps"].append({
                    "node": node,
                    "phase": state.get("phase"),
                    "thought": state.get("thought"),
                    "action": state.get("next_action"),
                    "action_input": state.get("action_input"),
                    "observation": state.get("observation"),
                    "reflection": state.get("reflection"),
                    "data": state.get("data") if node == "final" else None
                })
        
        logger.info(f"Agent job {job_id} completed successfully")
        jobs[job_id]["status"] = "completed"
        
        final_step = next((s for s in jobs[job_id]["steps"] if s["node"] == "final"), None)
        if final_step and final_step.get("data"):
            logger.info(f"Saving job {job_id} to database")
            db = SessionLocal()
            try:
                data = final_step.get("data", {})
                if not isinstance(data, dict):
                    data = {}
                
                profile_info = data.get("profile", {})
                if not isinstance(profile_info, dict):
                    profile_info = {"name": name, "bio": "Data extraction failed", "location": "Unknown"}

                profile_db = ProfileDB(
                    name=name,
                    profile_data=profile_info,
                    insights=data.get("insights", {"summary": "No summary available"}),
                    confidence=data.get("confidence", {"score": 0.0, "justification": "Extraction failed"})
                )
                db.add(profile_db)
                db.commit()
                logger.info(f"Successfully saved profile for {name} to Postgres")
            except Exception as db_err:
                logger.error(f"Failed to save to Postgres: {str(db_err)}")
                db.rollback()
            finally:
                db.close()
        
    except Exception as e:
        logger.error(f"FATAL ERROR in job {job_id}: {str(e)}", exc_info=True)
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)

if __name__ == "__main__":
   
    uvicorn.run(app, host="0.0.0.0", port=8000)
