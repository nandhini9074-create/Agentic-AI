import { FinalProfile } from "./types/agent";

export const mockProfile: FinalProfile = {
  profile: {
    name: "Dr. Elena Vance",
    bio: "Senior AI Researcher and Lead Systems Architect with over 15 years of experience in autonomous robotics and neural-symbolic reasoning. Currently pioneering 'Project White-Forest' for sustainable urban infrastructure.",
    location: "Stockholm, Sweden",
    skills: ["PyTorch", "Rust", "LLMs", "Robotics", "Systems Design", "Graph Neural Networks"],
    experience: [
      {
        title: "Lead AI Scientist",
        company: "Aether Dynamics",
        period: "2018 - Present",
        description: "Leading a team of 40 researchers to develop decentralized intelligence for smart cities."
      },
      {
        title: "Senior Software Engineer",
        company: "Nebula Systems",
        period: "2014 - 2018",
        description: "Developed the core real-time operating system for industrial autonomous drones."
      }
    ],
    projects: [
      {
        name: "LumenCore",
        description: "An open-source library for distributed neural network training on edge devices.",
        technologies: ["Rust", "WASM", "WebGPU"]
      },
      {
        name: "EcoMesh",
        description: "Autonomous mesh network for monitoring biodiversity in remote rainforest regions.",
        technologies: ["Python", "LoRaWAN", "TensorFlow"]
      }
    ],
    certifications: [
      { name: "Deep Learning Specialization", issuer: "DeepLearning.AI" }
    ],
    social_links: ["https://github.com", "https://linkedin.com", "https://x.com"],
    external_mentions: ["Wired Magazine Feature", "Keynote at AI Summit 2025"],
    recent_posts: [
      {
        content: "Excited to share our latest research on neural-symbolic reasoning at #NeurIPS2025. We've achieved a 40% reduction in training compute while maintaining logic consistency.",
        summary: "Dr. Vance announces a significant breakthrough in AI efficiency, reducing training compute by 40% while preserving logical reasoning capabilities.",
        date: "2 days ago",
        link: "https://linkedin.com/posts/evance_ai_research"
      },
      {
        content: "Sustainability in urban infrastructure isn't just about better materials; it's about better intelligence. Project White-Forest is officially entering Phase 2.",
        summary: "Announcement of Phase 2 for Project White-Forest, focusing on intelligent systems as the core driver for sustainable urban development.",
        date: "1 week ago"
      }
    ]
  },
  insights: {
    summary: "Elena Vance is a high-impact technical leader bridging the gap between cutting-edge AI research and practical industrial implementation.",
    key_strengths: ["Architecture Design", "Strategic Innovation", "Cross-disciplinary Leadership"],
    expertise_areas: ["Autonomous Systems", "Edge Computing", "MLOps"],
    online_presence: "Strong professional presence in research communities and GitHub."
  },
  confidence: {
    score: 0.94,
    justification: "Profile data corroborated across LinkedIn, GitHub, and multiple research paper repositories."
  }
};
