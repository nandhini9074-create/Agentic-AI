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
        date: "2 days ago (May 16, 2026 at 10:15 AM)",
        link: "https://linkedin.com/posts/evance_ai_research"
      },
      {
        content: "Sustainability in urban infrastructure isn't just about better materials; it's about better intelligence. Project White-Forest is officially entering Phase 2.",
        summary: "Announcement of Phase 2 for Project White-Forest, focusing on intelligent systems as the core driver for sustainable urban development.",
        date: "1 week ago (May 11, 2026 at 02:45 PM)"
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

export const mockSportsProfile: FinalProfile = {
  profile: {
    name: "Lionel Messi",
    bio: "Widely regarded as one of the greatest football players of all time. Captain of the Argentina National Team and Forward for Inter Miami CF. Winner of 8 Ballon d'Or awards and the 2022 FIFA World Cup.",
    location: "Miami, Florida, USA",
    skills: ["Dribbling", "Playmaking", "Free-kick Accuracy", "Acceleration", "Finishing", "Tactical Vision"],
    experience: [
      {
        title: "Forward / Captain",
        company: "Inter Miami CF",
        period: "2023 - Present",
        description: "Leading the team in MLS. Winner of the 2023 Leagues Cup, scoring 10 goals in 7 appearances."
      },
      {
        title: "Forward",
        company: "Paris Saint-Germain (PSG)",
        period: "2021 - 2023",
        description: "Scored 32 goals in 75 matches. Winner of Ligue 1 twice and Trophée des Champions."
      },
      {
        title: "Forward",
        company: "FC Barcelona",
        period: "2004 - 2021",
        description: "Club's all-time top scorer with 672 goals in 778 matches. Winner of 10 La Liga titles, 7 Copa del Rey titles, and 4 UEFA Champions Leagues."
      }
    ],
    projects: [
      {
        name: "FIFA World Cup Qatar 2022",
        description: "Champion of the world with Argentina. Awarded the Golden Ball as the tournament's best player, scoring 7 goals.",
        technologies: ["G: 7", "A: 3", "Matches: 7", "Golden Ball MVP"]
      },
      {
        name: "Copa América 2021 & 2024",
        description: "Led Argentina to historic consecutive Copa América trophies, ending a 28-year senior title drought.",
        technologies: ["G: 4 (2021)", "A: 5 (2021)", "Golden Boot MVP"]
      }
    ],
    certifications: [
      { name: "Ballon d'Or (8-time Winner)", issuer: "France Football" },
      { name: "Laureus World Sportsman of the Year", issuer: "Laureus" }
    ],
    social_links: ["https://instagram.com/leomessi", "https://facebook.com/leomessi", "https://x.com"],
    external_mentions: ["FIFA World Cup Golden Ball 2022", "Guinness World Record for goals in a calendar year (91 goals)"],
    recent_posts: [
      {
        content: "Increíble noche en Miami. Gracias a todos por el apoyo constante. ¡Seguimos trabajando fuerte por más victorias! ⚽️🔥",
        summary: "Messi expresses gratitude to Inter Miami fans after a successful match night, looking forward to future wins.",
        date: "1 day ago (May 19, 2026 at 11:30 PM)",
        link: "https://instagram.com/p/leomessi_post"
      },
      {
        content: "Agradecido por estar nominado otra vez al premio Laureus. Es un honor estar entre tan grandes deportistas.",
        summary: "Lionel Messi expresses gratitude for his nomination for the Laureus World Sports Award.",
        date: "2 weeks ago (May 06, 2026 at 04:00 PM)"
      }
    ]
  },
  insights: {
    summary: "Lionel Messi is a legendary playmaker and clinical finisher who has defined a generation of modern football through unparalleled ball control, visual field scanning, and set-piece accuracy.",
    key_strengths: ["Unmatched Dribbling", "Elite Set-piece Accuracy", "Playmaking Vision"],
    expertise_areas: ["Attacking Midfielder", "Second Striker", "Winger"],
    online_presence: "Massive global social media footprint, followed by hundreds of millions worldwide."
  },
  confidence: {
    score: 0.99,
    justification: "Verified international match records, official club registries, and verified public channels."
  }
};

export const mockTechNormalProfile: FinalProfile = {
  profile: {
    name: "Nandhini S",
    bio: "Lead Technical Product Manager & Enterprise Solutions Architect with a passion for designing scalable developer platforms and orchestrating high-fidelity enterprise AI applications.",
    location: "Bengaluru, Karnataka, India",
    skills: ["Product Strategy", "System Architecture", "React", "Node.js", "Docker", "Agile Leadership", "API Design", "GraphQL"],
    experience: [
      {
        title: "Lead Technical Product Manager",
        company: "SynthAI Systems",
        period: "2022 - Present",
        description: "Orchestrating high-scale enterprise AI API deployments and developer portals, reducing integration latency by 35%."
      },
      {
        title: "Senior Solutions Architect",
        company: "Nexus Cloud",
        period: "2018 - 2022",
        description: "Designed and scaled hybrid multi-cloud infrastructure and developer sandboxes for Fortune 500 digital transformations."
      }
    ],
    projects: [
      {
        name: "DevForge Platform",
        description: "An enterprise developer platform unifying API management, telemetry, and automated sandbox environments.",
        technologies: ["React", "GraphQL", "Kubernetes", "OpenAPI"]
      },
      {
        name: "CloudShield Edge",
        description: "High-throughput secure proxy service managing auth and rate-limiting at the network edge.",
        technologies: ["Go", "Redis", "eBPF", "Envoy"]
      }
    ],
    certifications: [
      { name: "AWS Solutions Architect Professional", issuer: "Amazon Web Services" },
      { name: "Certified Scrum Product Owner (CSPO)", issuer: "Scrum Alliance" }
    ],
    social_links: ["https://github.com/nandhini-s", "https://linkedin.com/in/nandhini-s-tech"],
    external_mentions: ["Keynote Speaker at DevSummit 2025", "Top Technical PM of the Year (2024)"],
    recent_posts: [
      {
        content: "API performance is the unsung hero of AI integration. If your rate-limits or response parsing are brittle, your agent loop crashes. That's why we focused on high-speed JSON repair and robust retrieval schemas this quarter.",
        summary: "Nandhini explains the importance of API resilience and speed in autonomous AI loops.",
        date: "3 days ago (May 18, 2026 at 09:15 AM)",
        link: "https://linkedin.com/posts/nandhini_s_api_resilience"
      },
      {
        content: "Just finalized Phase 1 of DevForge sandbox environments. Giving developers instant self-service sandboxes with mock RAG layers has increased active signups by 50%. Developer experience is product experience!",
        summary: "Nandhini announces the release of DevForge sandbox environments, leading to a 50% increase in developer engagement.",
        date: "2 weeks ago (May 07, 2026 at 04:30 PM)"
      }
    ]
  },
  insights: {
    summary: "Nandhini S is a highly capable hybrid professional who effectively bridges the gap between deep systems engineering and high-level product strategy.",
    key_strengths: ["Strategic Alignment", "Scalable System Architecture", "Developer Ecosystem Strategy"],
    expertise_areas: ["API Platforms", "Developer Experience", "Enterprise AI integrations"],
    online_presence: "Strong professional presence across LinkedIn, developer communities, and product forums."
  },
  confidence: {
    score: 0.96,
    justification: "Multi-source alignment across professional profiles, enterprise registry, and developer forums."
  }
};

(mockTechNormalProfile as any).profile_type = "tech_normal";
(mockTechNormalProfile as any).osint_dossier_markdown = `📁 SECURE TECH-NORMAL DOSSIER // PROFESSIONAL BRIEFING: Nandhini S
======================================================================
SECURITY LEVEL: CONFIDENTIAL // AGENTIC EYE ONLY // TECH-NORMAL DIVISION

👤 PROFESSIONAL PROFILE
---------------------------
* Full Name: Nandhini S
* Title/Role: Lead Technical Product Manager
* Tech Focus: Enterprise AI Integrations & Developer Systems
* Location: Bengaluru, Karnataka, India
* Active Career Span: 2018 - Present
* Core Tech Matrix: TypeScript, React, Node.js, GraphQL, Python, Docker

💼 KEY INITIATIVES & IMPACT
----------------------------------
A versatile technical leader bridging software engineering, system architecture, and product lifecycle strategy. Proven track record of orchestrating enterprise-grade AI applications and developer sandbox environments.

📊 STRATEGIC PROJECTS & PRODUCTS
------------------------------
| Product / Project | Tech Stack | Role | Business & Technical Impact |
|-------------------|------------|------|----------------------------|
| DevForge Platform | React, GraphQL, K8s | Lead Product Owner | Unified enterprise APIs, reducing developer sandbox setup times by 70%. |
| CloudShield Edge | Go, Redis, Envoy Proxy | Solutions Architect | Managed high-throughput routing at the edge, scaling to 15K req/sec. |
| Persona.IQ Agent | Python, LangGraph, Qdrant | System Lead | Orchestrated RAG profiling pipelines, ensuring 99.8% semantic relevance. |

🏆 ACCOLADES & COMMUNITY FOOTPRINT
------------------------------------
* AWS Certified Solutions Architect - Professional
* Speaker at Developer Leadership Summit 2025 on "Enterprise AI Orchestration"
* Top Contributor to Developer Sandbox open-source specifications

🌐 VERIFIED PUBLIC FOOTPRINT
------------------------------------
* GitHub: https://github.com/nandhini-s
* LinkedIn: https://linkedin.com/in/nandhini-s-tech
* Developer Profile: https://nandhini.dev

🔒 OSINT THREAT ANALYSIS & ENGINE CLASSIFICATION
-----------------------------------------------
* OSINT Engine Confidence: 96%
* Audit Justification: High coherence across multiple professional directories and verified repository footprints.`;


