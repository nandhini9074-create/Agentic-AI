import asyncio
import os
import json
from app.core.scraper import RAGScraper
from app.core.extractor import RAGExtractor
from app.core.chunker import RAGChunker
from app.core.vectordb import vectordb_service
from app.core.retriever import RAGRetriever
from app.core.reranker import reranker_service
from app.core.llm_engine import llm_engine
from app.utils.logger import logger

class RAGPipeline:
    @staticmethod
    async def run_pipeline(name: str, urls: list[str], query: str) -> dict:
        """
        Coordinates the entire streaming RAG pipeline:
        Scrapes a URL -> Normalizes -> Vectors -> Semantic Match -> LLM Synthesis.
        Simultaneously in the background, pre-fetches/scrapes the next URL so 
        scraping and vectorization occur concurrently, looping until all URLs are merged.
        """
        logger.info(f"RAGPipeline: Commencing streaming RAG profile builder for '{name}'...")
        logger.info(f"RAGPipeline: Query: '{query}' | URLs: {urls}")

        if not urls:
            return {}

        # If query is empty or too generic, enrich it to target the full Pydantic profile model fields
        if not query or query.strip().lower() in ["", "generate", "profile", "default"]:
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
            logger.info(f"RAGPipeline: Enriched RAG query to mirror profile.py fields: {query}")

        # Step 0: Erase/remove old temp_rag_matched_data.json when a new search starts
        temp_file_path = "d:\\Agentic-AI\\temp_rag_matched_data.json"
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"RAGPipeline: Erased legacy matched RAG context file: {temp_file_path}")
            except Exception as e:
                logger.error(f"RAGPipeline: Failed to erase old RAG matched data file: {str(e)}")

        # Clear any old vector chunks for this specific target name to guarantee a clean starting state
        try:
            vectordb_service.delete_target_chunks(name)
            logger.info(f"RAGPipeline: Cleared legacy vector database entries for target '{name}'")
        except Exception as e:
            logger.warning(f"RAGPipeline: Could not clear existing chunks for target: {str(e)}")

        final_profile_json = {}
        top_5_chunks = []

        # Start scraping the very first URL in the background
        logger.info(f"RAGPipeline: Launching background scrape for first URL: {urls[0]}")
        current_scrape_task = asyncio.create_task(RAGScraper.scrape_url(urls[0]))

        for idx, url in enumerate(urls):
            logger.info(f"RAGPipeline: Iteration [{idx + 1}/{len(urls)}] | Waiting for scrape on: {url}")
            
            # 1. Wait for current scraping task to finish
            raw_result = await current_scrape_task
            
            # 2. Concurrently trigger/pre-fetch the next URL scraping task in the background (if it exists)
            next_scrape_task = None
            if idx + 1 < len(urls):
                next_url = urls[idx + 1]
                logger.info(f"RAGPipeline: Concurrently launching background pre-fetch scrape for next URL: {next_url}")
                next_scrape_task = asyncio.create_task(RAGScraper.scrape_url(next_url))

            # 3. Clean, normalize, and semantic chunk the crawled URL content
            cleaned_result = RAGExtractor.extract_and_clean(raw_result)
            chunks = RAGChunker.chunk_content(cleaned_result)
            
            # Stamp target name for strict context database isolation
            for chunk in chunks:
                if "metadata" not in chunk:
                    chunk["metadata"] = {}
                chunk["metadata"]["target_name"] = name

            # 4. Generate Embeddings and Save chunks to persistent vector store
            if chunks:
                vectordb_service.add_chunks(chunks)

            # 5. Hybrid Semantic Retrieval (Top 10 candidate chunks accumulated so far)
            candidate_chunks = RAGRetriever.retrieve_chunks(
                query=query, 
                k=10, 
                use_hybrid=True, 
                where={"target_name": name}
            )
            
            if not candidate_chunks:
                logger.warning("RAGPipeline: No chunks retrieved under target filter. Querying globally.")
                candidate_chunks = RAGRetriever.retrieve_chunks(query=query, k=10, use_hybrid=True)

            # 6. Cross-Encoder Reranking to pull top 5 chunks
            if candidate_chunks:
                top_5_chunks = reranker_service.rerank(query=query, chunks=candidate_chunks, top_n=5)

                # 7. Write matched chunks to temp_rag_matched_data.json for observability
                try:
                    formatted_context = []
                    for rank_idx, chunk in enumerate(top_5_chunks, 1):
                        formatted_context.append({
                            "rank": rank_idx,
                            "target_name": name,
                            "query": query,
                            "chunk_id": chunk.get("chunk_id"),
                            "source_url": chunk.get("source_url"),
                            "rerank_score": chunk.get("rerank_score"),
                            "content": chunk.get("content"),
                            "metadata": chunk.get("metadata", {})
                        })
                    with open(temp_file_path, "w", encoding="utf-8") as f:
                        json.dump(formatted_context, f, indent=4, ensure_ascii=False)
                        f.flush()
                        os.fsync(f.fileno()) # Force write to physical disk immediately
                    logger.info(f"RAGPipeline: Logged intermediate matched chunks to: {temp_file_path}")
                except Exception as e:
                    logger.error(f"RAGPipeline: Failed to log matched RAG chunks: {str(e)}")

                # 8. Feed to LLM for intermediate structured profile compilation/merging
                final_profile_json = llm_engine.generate_profile(
                    name=name,
                    query=query,
                    top_chunks=top_5_chunks
                )
            else:
                logger.warning("RAGPipeline: No content available for LLM matching on this iteration.")

            # Bind pre-fetching task to current task for next iteration
            if next_scrape_task:
                current_scrape_task = next_scrape_task

        # Append overall sources integrated in the final session
        if top_5_chunks:
            sources_used = list(set([chunk["source_url"] for chunk in top_5_chunks]))
            if "profile" in final_profile_json:
                final_profile_json["profile"]["sources_used"] = sources_used
            else:
                final_profile_json["sources_used"] = sources_used

        logger.info(f"RAGPipeline: Streaming loop completed successfully for '{name}'.")
        return final_profile_json

# Global instance for pipeline execution
rag_pipeline = RAGPipeline()
