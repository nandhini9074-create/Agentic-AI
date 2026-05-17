from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Experience(BaseModel):
    title: str
    company: str
    period: str
    description: Optional[str] = None

class Project(BaseModel):
    name: str
    description: str
    link: Optional[str] = None
    technologies: List[str] = []

class Certification(BaseModel):
    name: str
    issuer: str
    date: Optional[str] = None

class Post(BaseModel):
    content: str
    summary: Optional[str] = None
    date: Optional[str] = None
    link: Optional[str] = None

class Profile(BaseModel):
    name: str
    bio: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = []
    experience: List[Experience] = []
    projects: List[Project] = []
    certifications: List[Certification] = []
    social_links: List[str] = []
    external_mentions: List[str] = []
    recent_posts: List[Post] = []

class Insights(BaseModel):
    summary: str
    key_strengths: List[str]
    expertise_areas: List[str]
    online_presence: str

class Confidence(BaseModel):
    score: float
    justification: str

class FinalOutput(BaseModel):
    phase: str = "FINAL"
    profile: Profile
    insights: Insights
    confidence: Confidence

class AgentResponse(BaseModel):
    phase: str
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    reflection: Optional[str] = None
