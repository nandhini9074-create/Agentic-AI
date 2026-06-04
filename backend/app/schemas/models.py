from pydantic import BaseModel, Field
from typing import List, Optional

class RAGProfileRequest(BaseModel):
    name: str = Field(..., description="Target name of the person")
    urls: List[str] = Field(..., description="Seed URLs to scrape information from")
    query: str = Field(..., description="Semantic query specifying the profile details needed")

class ExperienceItem(BaseModel):
    title: str = Field(default="", description="Job title")
    company: str = Field(default="", description="Company name")
    period: str = Field(default="", description="Employment period")
    description: str = Field(default="", description="Role description and achievements")
    source_url: str = Field(default="", description="URL source where this was crawled")

class ProjectItem(BaseModel):
    name: str = Field(default="", description="Project name")
    description: str = Field(default="", description="Project description")
    technologies: List[str] = Field(default_factory=list, description="Technologies and stack used")
    source_url: str = Field(default="", description="URL source where this was crawled")

class CertificationItem(BaseModel):
    name: str = Field(default="", description="Certification name")
    issuer: str = Field(default="", description="Issuing organization")
    date: str = Field(default="", description="Date issued")
    source_url: str = Field(default="", description="URL source where this was crawled")

class RecentActivityItem(BaseModel):
    content: str = Field(default="", description="Social media post content or activity detail")
    platform: str = Field(default="", description="Platform name (LinkedIn, Twitter, GitHub)")
    date: str = Field(default="", description="Date of the activity")

class StructuredProfile(BaseModel):
    name: str = Field(default="", description="Full name of the person")
    headline: str = Field(default="", description="Professional headline/title")
    bio: str = Field(default="", description="Extensive career summary bio")
    skills: List[str] = Field(default_factory=list, description="List of professional skills")
    experience: List[ExperienceItem] = Field(default_factory=list, description="Employment experience")
    projects: List[ProjectItem] = Field(default_factory=list, description="Projects and showcases")
    certifications: List[CertificationItem] = Field(default_factory=list, description="Certifications and achievements")
    social_links: List[str] = Field(default_factory=list, description="Social profile URLs found")
    achievements: List[str] = Field(default_factory=list, description="Achievements and awards")
    recent_activity: List[RecentActivityItem] = Field(default_factory=list, description="Recent posts and online activity")
    confidence_score: float = Field(default=0.0, description="Verification confidence score (0.0 to 1.0)")
