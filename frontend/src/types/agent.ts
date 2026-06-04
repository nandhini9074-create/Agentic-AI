export type Phase = "IDLE" | "REASON" | "ACT" | "OBSERVE" | "REFLECT" | "FINAL";

export interface AgentStep {
  phase: Phase;
  thought?: string;
  action?: string;
  action_input?: any;
  observation?: any;
  reflection?: string;
  timestamp: string;
}

export interface Experience {
  title: string;
  company: string;
  period: string;
  description?: string;
  source_url?: string;
}

export interface Project {
  name: string;
  description: string;
  link?: string;
  technologies: string[];
  source_url?: string;
}

export interface Certification {
  name: string;
  issuer: string;
  date?: string;
  source_url?: string;
}

export interface Post {
  content: string;
  summary?: string;
  date?: string;
  link?: string;
  source_url?: string;
}

export interface ProfileData {
  name: string;
  bio?: string;
  location?: string;
  skills: string[];
  experience: Experience[];
  projects: Project[];
  certifications: Certification[];
  social_links: string[];
  external_mentions: string[];
  recent_posts: Post[];
  
  // Extended multi-source fields
  headline?: string;
  basic_info?: {
    full_name: string;
    headline?: string;
    location?: string;
    bio?: string;
    source_url?: string;
  };
  education?: Array<{ school: string; degree: string; period: string; source_url?: string }>;
  social_profiles?: string[];
  verified_profiles?: {
    linkedin?: string;
    twitter?: string;
    instagram?: string;
    github?: string;
    youtube?: string;
    facebook?: string;
    personal_website?: string;
    blog?: string;
  };
  github_data?: {
    repositories_count?: number;
    stars_received?: number;
    top_repositories?: Array<{ name: string; stars: number; link?: string }>;
  };
  articles?: Array<{ title: string; publisher: string; date?: string; summary?: string; source_url?: string }>;
  achievements?: string[];
  tech_stack?: string[];
  communities?: string[];
  contact_info?: { email?: string; phone?: string };
  sources_used?: string[];
}

export interface Insights {
  summary: string;
  key_strengths: string[];
  expertise_areas: string[];
  online_presence: string;
}

export interface FinalProfile {
  profile: ProfileData;
  insights: Insights;
  confidence: {
    score: number;
    justification: string;
  };
}
