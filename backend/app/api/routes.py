from fastapi import APIRouter, HTTPException
from app.schemas.models import RAGProfileRequest, StructuredProfile
from app.core.pipeline import rag_pipeline
from app.utils.logger import logger

router = APIRouter()

@router.post("/profile", response_model=StructuredProfile)
async def generate_rag_profile(request: RAGProfileRequest):
    """
    RAG-based Semantic Profile Generation endpoint.
    Scrapes URLs, cleans & chunks, stores to Vector DB, retrieves semantically relevant text, 
    reranks via ms-marco cross-encoder, and synthesizes a high-fidelity query-aware profile.
    """
    logger.info(f"API: Received RAG Profile request for {request.name}")
    try:
        profile_response = await rag_pipeline.run_pipeline(
            name=request.name,
            urls=request.urls,
            query=request.query
        )
        
        # If the LLM returned a nested "profile" key (common in our schemas), extract it directly
        if "profile" in profile_response and isinstance(profile_response["profile"], dict):
            extracted_profile = profile_response["profile"]
            # Ensure top-level fields like confidence_score are copied over if missing
            if "confidence_score" not in extracted_profile and "confidence" in profile_response:
                extracted_profile["confidence_score"] = profile_response["confidence"].get("score", 0.0)
            elif "confidence_score" not in extracted_profile:
                extracted_profile["confidence_score"] = profile_response.get("confidence_score", 0.95)
            
            return extracted_profile
            
        return profile_response
    except Exception as e:
        logger.error(f"API Error during RAG generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during RAG profile synthesis: {str(e)}"
        )

@router.get("/inspect")
async def inspect_qdrant_database(limit: int = 100):
    """
    Lightweight local inspector for Qdrant database contents.
    Exposes stored vectors, chunks, and metadata directly to browser users!
    """
    from app.core.vectordb import vectordb_service
    points = vectordb_service.list_all_points(limit=limit)
    return {
        "status": "success",
        "total_points_loaded": len(points),
        "database_engine": "Qdrant (Embedded Local File Mode)",
        "storage_path": "./backend/storage/qdrant_rag",
        "points": points
    }

@router.get("/test-search")
async def test_search_retrieval(name: str = "Sundar Pichai"):
    """
    Diagnostic endpoint to run semantic search and reranking on the active server.
    """
    from app.core.retriever import RAGRetriever
    from app.core.reranker import reranker_service
    
    query = (
        f"Extract all professional details for {name} to populate: "
        f"Basic Identity & Branding (full name, headline, tagline, current role, company, language skills, gender, pronouns), "
        f"Contact & Web Presence (email, phone, portfolio URL, github, linkedin, twitter, medium, kaggle, youtube, resume, personal website), "
        f"Education & Academic History (institutions, degree, specialization, years, grade GPAs, honors, activities), "
        f"Skills & Domain Analytics (primary domain, stack, languages, frameworks, cloud platforms, databases, devops, AI tools), "
        f"Enhanced Work Experience (job title, employer, period, location, employment type, tech used, responsibilities, team size, achievements, impact metrics), "
        f"Enhanced Projects (name, description, status, link, github repository, role, tech stack, AI features, architecture, challenges, outcomes), "
        f"Open Source Contributions (repos, stars, forks, commits, pull requests, summaries), "
        f"Social & Developer Communities (hackathons, speaking, mentoring, conferences, volunteering, workshops), "
        f"Content & Thought Leadership (blogs, articles, newsletters, writing topics, social engagement metrics), "
        f"Achievements & Recognition (awards, platform rankings, scholarships, featured media, testimonials), "
        f"Resume Intelligence (years of experience, seniority level, growth and leadership depth, communication scores)."
    )
    
    # 1. Similarity search direct
    from app.core.vectordb import vectordb_service
    direct_search = vectordb_service.similarity_search(query, k=10, where={"target_name": name})
    
    # 2. Similarity search no filter
    direct_search_no_filter = vectordb_service.similarity_search(query, k=10)
    
    # 3. Retrieve chunks with hybrid
    candidate_chunks = RAGRetriever.retrieve_chunks(
        query=query,
        k=10,
        use_hybrid=True,
        where={"target_name": name}
    )
    
    # 4. Rerank
    top_3_chunks = reranker_service.rerank(query=query, chunks=candidate_chunks, top_n=3)
    
    return {
        "name_queried": name,
        "direct_search_count": len(direct_search),
        "direct_search_no_filter_count": len(direct_search_no_filter),
        "candidate_chunks_count": len(candidate_chunks),
        "top_3_chunks_count": len(top_3_chunks),
        "top_3_chunks": [{
            "rank": idx,
            "source_url": c.get("source_url"),
            "score": c.get("rerank_score"),
            "content": c.get("content")
        } for idx, c in enumerate(top_3_chunks, 1)]
    }

