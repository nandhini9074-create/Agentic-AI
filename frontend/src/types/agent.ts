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
}

export interface Project {
  name: string;
  description: string;
  link?: string;
  technologies: string[];
}

export interface Certification {
  name: string;
  issuer: string;
  date?: string;
}

export interface Post {
  content: string;
  summary?: string;
  date?: string;
  link?: string;
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
