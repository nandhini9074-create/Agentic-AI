from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# ==========================================
# 14. Confidence & Source Attribution Model
# ==========================================
class FieldAttribution(BaseModel):
    confidence_score: float = Field(default=1.0, description="AI extraction confidence score between 0 and 1")
    source_urls: List[str] = Field(default=[], description="Source URLs from which this information was obtained")
    extraction_method: str = Field(default="AI Extraction", description="Extraction method used (e.g. static search, dynamic playwright, tavily)")

# ==========================================
# 1. Basic Professional Identity
# ==========================================
class BasicIdentity(BaseModel):
    full_name: str = Field(..., description="Target's full legal or professional name")
    headline: Optional[str] = Field(default=None, description="Professional headline or title")
    current_role: Optional[str] = Field(default=None, description="Current job title / position")
    current_company: Optional[str] = Field(default=None, description="Current employer company")
    profile_tagline: Optional[str] = Field(default=None, description="Short personal tagline")
    profile_image: Optional[str] = Field(default=None, description="Public profile photo URL")
    cover_image: Optional[str] = Field(default=None, description="Public cover photo URL")
    gender: Optional[str] = Field(default=None, description="Public gender identification")
    pronouns: Optional[str] = Field(default=None, description="Preferred public pronouns")
    languages_known: List[str] = Field(default=[], description="Languages spoken by the candidate")
    attribution: Optional[FieldAttribution] = None

# ==========================================
# 2. Contact & Public Presence
# ==========================================
class ContactPresence(BaseModel):
    email: Optional[str] = Field(default=None, description="Public professional email address")
    phone: Optional[str] = Field(default=None, description="Public contact number")
    portfolio_url: Optional[str] = Field(default=None, description="Personal portfolio or website link")
    github_url: Optional[str] = Field(default=None, description="GitHub profile URL")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    twitter_url: Optional[str] = Field(default=None, description="Twitter / X profile URL")
    medium_url: Optional[str] = Field(default=None, description="Medium blog profile link")
    kaggle_url: Optional[str] = Field(default=None, description="Kaggle profile link")
    youtube_url: Optional[str] = Field(default=None, description="YouTube channel URL")
    personal_website: Optional[str] = Field(default=None, description="Personal website link")
    public_resume_url: Optional[str] = Field(default=None, description="Link to public resume / CV")
    attribution: Optional[FieldAttribution] = None

# ==========================================
# 3. Education Details
# ==========================================
class EducationDetails(BaseModel):
    institution: str = Field(..., description="Name of the university, college, or school")
    degree: Optional[str] = Field(default=None, description="Degree or certificate level (e.g. BS, MS, PhD)")
    specialization: Optional[str] = Field(default=None, description="Field of study or major")
    start_year: Optional[str] = Field(default=None, description="Start year of study")
    end_year: Optional[str] = Field(default=None, description="End year of study")
    grade: Optional[str] = Field(default=None, description="GPA or grade classification")
    achievements: List[str] = Field(default=[], description="Academic achievements, honors, or scholarships")
    activities: List[str] = Field(default=[], description="Extra-curricular activities or student societies")
    source_url: Optional[str] = Field(default=None, description="Source URL where this education was found")
    attribution: Optional[FieldAttribution] = None

# ==========================================
# 4. Skills Intelligence
# ==========================================
class SkillIntelligence(BaseModel):
    skill_name: str = Field(..., description="Name of the skill")
    proficiency_level: str = Field(default="Intermediate", description="Proficiency level (e.g. Beginner, Intermediate, Advanced, Expert)")
    years_of_experience: Optional[float] = Field(default=None, description="Estimated years of experience in this skill")
    confidence_score: float = Field(default=1.0, description="AI extraction confidence score")
    source: Optional[str] = Field(default=None, description="Primary source URL for this skill")

# ==========================================
# 5. Work Experience Enhancements
# ==========================================
class WorkExperienceEnhanced(BaseModel):
    title: str = Field(..., description="Role title")
    company: str = Field(..., description="Employer company name")
    period: str = Field(..., description="Duration or period of employment")
    description: Optional[str] = Field(default=None, description="Job summary description")
    employment_type: Optional[str] = Field(default=None, description="Type of employment (e.g. Full-time, Part-time, Contract, Internship)")
    location: Optional[str] = Field(default=None, description="Job location")
    technologies_used: List[str] = Field(default=[], description="Tech stack used in this role")
    achievements: List[str] = Field(default=[], description="Major accomplishments or key projects in this role")
    responsibilities: List[str] = Field(default=[], description="List of regular job responsibilities")
    team_size: Optional[int] = Field(default=None, description="Size of the team managed or worked with")
    impact_metrics: List[str] = Field(default=[], description="Quantifiable business or engineering metrics")
    source_url: Optional[str] = Field(default=None, description="Source URL where this experience was found")
    attribution: Optional[FieldAttribution] = None

# ==========================================
# 6. Project Enhancements
# ==========================================
class ProjectEnhanced(BaseModel):
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project summary description")
    link: Optional[str] = Field(default=None, description="Public link or homepage of the project")
    technologies: List[str] = Field(default=[], description="Technologies and packages used")
    github_link: Optional[str] = Field(default=None, description="Repository link")
    live_demo: Optional[str] = Field(default=None, description="Live interactive demo URL")
    role: Optional[str] = Field(default=None, description="Candidate's role in this project (e.g. Lead, Contributor)")
    category: Optional[str] = Field(default=None, description="Project category (e.g. Web, AI/ML, DevOps)")
    project_status: Optional[str] = Field(default=None, description="Status (e.g. Completed, Ongoing, Inactive)")
    screenshots: List[str] = Field(default=[], description="Links to screenshots or wireframes")
    architecture_summary: Optional[str] = Field(default=None, description="Brief description of the system architecture")
    ai_features: List[str] = Field(default=[], description="Integrated AI features or models used")
    challenges_faced: List[str] = Field(default=[], description="Key technical challenges overcome")
    outcomes: List[str] = Field(default=[], description="Quantifiable outcomes or project impact")
    source_url: Optional[str] = Field(default=None, description="Source URL where this project was found")
    attribution: Optional[FieldAttribution] = None

# ==========================================
# 7. Open Source Contributions
# ==========================================
class OpenSourceContribution(BaseModel):
    repository_name: str = Field(..., description="Contributed repository name")
    stars: int = Field(default=0, description="Stars count of the repository")
    forks: int = Field(default=0, description="Forks count of the repository")
    commits: int = Field(default=0, description="Total commits contributed")
    pull_requests: int = Field(default=0, description="Total pull requests submitted")
    contribution_summary: Optional[str] = Field(default=None, description="Brief summary of candidate's contributions")
    source_url: Optional[str] = Field(default=None, description="Source URL where this contribution was found")
    attribution: Optional[FieldAttribution] = None

# ==========================================
# 8. Technical Profile Analytics
# ==========================================
class TechnicalProfileAnalytics(BaseModel):
    primary_domain: Optional[str] = Field(default=None, description="Primary technical domain (e.g. Backend, Frontend, ML Engineering, Cloud)")
    secondary_domains: List[str] = Field(default=[], description="Secondary domain capabilities")
    tech_stack: List[str] = Field(default=[], description="Core tech stack names")
    preferred_languages: List[str] = Field(default=[], description="Preferred coding languages")
    frameworks: List[str] = Field(default=[], description="Familiar frameworks and tools")
    cloud_platforms: List[str] = Field(default=[], description="Preferred cloud platforms (e.g. AWS, GCP, Azure)")
    databases: List[str] = Field(default=[], description="Preferred database systems")
    devops_tools: List[str] = Field(default=[], description="CI/CD and DevOps technologies")
    ai_tools: List[str] = Field(default=[], description="Generative AI models and tools utilized")
    attribution: Optional[FieldAttribution] = None

# ==========================================
# 9. Social & Community Presence
# ==========================================
class SocialCommunityPresence(BaseModel):
    communities: List[str] = Field(default=[], description="Involvement in developer communities")
    hackathons: List[str] = Field(default=[], description="Hackathons participated in")
    conferences: List[str] = Field(default=[], description="Conferences attended or spoken at")
    speaking_sessions: List[str] = Field(default=[], description="Speaking presentations or panels")
    workshops: List[str] = Field(default=[], description="Workshops conducted or attended")
    mentoring: List[str] = Field(default=[], description="Mentoring activities")
    volunteering: List[str] = Field(default=[], description="Volunteering initiatives")
    attribution: Optional[FieldAttribution] = None

# ==========================================
# 10. Content & Thought Leadership
# ==========================================
class ContentThoughtLeadership(BaseModel):
    blogs_written: List[str] = Field(default=[], description="Titles of written blogs")
    articles: List[Dict[str, Any]] = Field(default=[], description="List of articles with publication details")
    newsletters: List[str] = Field(default=[], description="Newsletters managed or authored")
    topics_of_interest: List[str] = Field(default=[], description="Topics of regular writing/discussion")
    writing_categories: List[str] = Field(default=[], description="Categories written in")
    social_engagement_metrics: Dict[str, Any] = Field(default={}, description="Metrics of engagement (likes, views, shares)")
    attribution: Optional[FieldAttribution] = None

# ==========================================
# 11. Achievements & Recognition
# ==========================================
class AchievementsRecognition(BaseModel):
    awards: List[str] = Field(default=[], description="Awards received")
    rankings: List[str] = Field(default=[], description="Competitive programming or platform rankings")
    scholarships: List[str] = Field(default=[], description="Scholarships received")
    recognitions: List[str] = Field(default=[], description="Public honors or recognitions")
    featured_in: List[str] = Field(default=[], description="Media articles or features")
    testimonials: List[str] = Field(default=[], description="Public recommendations / testimonials")
    attribution: Optional[FieldAttribution] = None

# ==========================================
# 12. Resume Intelligence
# ==========================================
class ResumeIntelligence(BaseModel):
    total_years_experience: float = Field(default=0.0, description="Total years of work experience")
    current_seniority_level: Optional[str] = Field(default=None, description="Seniority classification (e.g. Junior, Mid, Senior, Lead, Executive)")
    career_growth_score: float = Field(default=1.0, description="AI-calculated career progression score")
    leadership_score: float = Field(default=1.0, description="AI-calculated leadership capabilities score")
    technical_depth_score: float = Field(default=1.0, description="AI-calculated engineering depth score")
    communication_score: float = Field(default=1.0, description="AI-calculated communication and thought-leadership score")
    attribution: Optional[FieldAttribution] = None

# ==========================================
# 15. Metadata & Tracking
# ==========================================
class MetadataTracking(BaseModel):
    generated_at: str = Field(..., description="Timestamp when the profile was generated")
    updated_at: str = Field(..., description="Timestamp when the profile was last updated")
    processing_time: float = Field(default=0.0, description="Total pipeline execution time in seconds")
    data_sources_count: int = Field(default=0, description="Count of parsed sources")
    urls_processed: List[str] = Field(default=[], description="List of successfully parsed URLs")
    failed_urls: List[str] = Field(default=[], description="List of failed URLs")
    enrichment_steps: List[str] = Field(default=[], description="AI enrichment steps executed")

# ==========================================
# Backward-Compatible Legacy Experience
# ==========================================
class Experience(BaseModel):
    title: str
    company: str
    period: str
    description: Optional[str] = None
    source_url: Optional[str] = None

class Project(BaseModel):
    name: str
    description: str
    link: Optional[str] = None
    technologies: List[str] = []
    source_url: Optional[str] = None

class Certification(BaseModel):
    name: str
    issuer: str
    date: Optional[str] = None
    source_url: Optional[str] = None

class Post(BaseModel):
    content: str
    summary: Optional[str] = None
    date: Optional[str] = None
    link: Optional[str] = None
    source_url: Optional[str] = None

class BasicInfo(BaseModel):
    full_name: str
    headline: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    source_url: Optional[str] = None

# ==========================================
# Core Professional Profile Model
# ==========================================
class Profile(BaseModel):
    # --- Backward-Compatible Legacy Fields ---
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
    basic_info: Optional[BasicInfo] = None
    education: Optional[List[Dict[str, Any]]] = []
    social_profiles: Optional[List[str]] = []
    verified_profiles: Optional[Dict[str, str]] = {}
    github_data: Optional[Dict[str, Any]] = {}
    articles: Optional[List[Dict[str, Any]]] = []
    achievements: Optional[List[str]] = []
    tech_stack: Optional[List[str]] = []
    communities: Optional[List[str]] = []
    contact_info: Optional[Dict[str, str]] = {}
    sources_used: Optional[List[str]] = []

    # --- Extended Production-Grade Fields ---
    basic_identity: Optional[BasicIdentity] = None
    contact_presence: Optional[ContactPresence] = None
    education_details: List[EducationDetails] = []
    skills_intelligence: List[SkillIntelligence] = []
    work_experience_enhanced: List[WorkExperienceEnhanced] = []
    project_enhanced: List[ProjectEnhanced] = []
    open_source_contributions: List[OpenSourceContribution] = []
    technical_analytics: Optional[TechnicalProfileAnalytics] = None
    social_community: Optional[SocialCommunityPresence] = None
    content_leadership: Optional[ContentThoughtLeadership] = None
    achievements_recognition: Optional[AchievementsRecognition] = None
    resume_intelligence: Optional[ResumeIntelligence] = None
    metadata_tracking: Optional[MetadataTracking] = None

# ==========================================
# 13. AI-Generated Insights
# ==========================================
class Insights(BaseModel):
    summary: str
    key_strengths: List[str] = []
    expertise_areas: List[str] = []
    online_presence: str = "Active"
    
    # Enhanced traits
    personality_traits: List[str] = []
    learning_style: Optional[str] = None
    collaboration_style: Optional[str] = None
    engineering_strengths: List[str] = []
    probable_interests: List[str] = []
    recommended_roles: List[str] = []
    hiring_recommendation: Optional[str] = None
    growth_areas: List[str] = []
    attribution: Optional[FieldAttribution] = None

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
