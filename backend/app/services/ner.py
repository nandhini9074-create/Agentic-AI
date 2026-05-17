from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from dotenv import load_dotenv
from app.utils.logger import logger, log_execution_time

load_dotenv()
# llm returned data format
class ExtractedEntities(BaseModel):
    skills: List[str] = Field(default_factory=list, description="Professional skills and technologies")
    organizations: List[str] = Field(default_factory=list, description="Companies, institutions, or organizations")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications or licenses")
    projects: List[str] = Field(default_factory=list, description="Notable projects or initiatives")

class NERService:
    def __init__(self):
        # Initialize the Groq LLM with structured output capabilities for entity extraction
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant", # Switched to 8b for better rate limits
            temperature=0
        )
        self.structured_llm = self.llm.with_structured_output(ExtractedEntities)

    @log_execution_time
    def extract_entities(self, text: str):
        # Use LLM to identify and extract structured professional entities (skills, organizations, etc.) from raw text
        logger.info(f"Extracting entities from text (length: {len(text)})")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at extracting professional entities from text. Extract skills, organizations, certifications, and projects as a structured object."),
            ("human", "Extract entities from this text: {text}")
        ])
        
        chain = prompt | self.structured_llm
        
        try:
            result = chain.invoke({"text": text})
            return result.dict()
        except Exception as e:
            # Fallback for models or cases where structured output fails
            print(f"Structured output error: {e}")
            return {
                "skills": [],
                "organizations": [],
                "certifications": [],
                "projects": [],
                "error": str(e)
            }

ner_service = NERService()
