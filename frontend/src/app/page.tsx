"use client";

import React from 'react';
import { InputForm } from '@/components/InputForm';
import { AgentTimeline } from '@/components/AgentTimeline';
import { ProfileDashboard } from '@/components/ProfileDashboard';
import { useAgentStore } from '@/store/useAgentStore';
import { mockProfile, mockSportsProfile, mockTechNormalProfile } from '@/mockData';
import { Sparkles, History, Bot, Zap, Trophy, Cpu } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Home() {
  const { status, setFinalProfile, addStep, reset, stopAgent, error } = useAgentStore();

  const simulateAgent = async (type: 'tech' | 'sports' | 'tech_normal' = 'tech') => {
    reset();
    
    let simulationSteps = [];
    if (type === 'sports') {
      simulationSteps = [
        { phase: 'REASON', thought: 'Analyzing sports history databases, club records, and social handles to extract athlete profile metrics.', timestamp: '12:00:01' },
        { phase: 'ACT', action: 'scraper', action_input: { url: 'https://instagram.com/leomessi' }, timestamp: '12:00:05' },
        { phase: 'OBSERVE', observation: 'Successfully verified Inter Miami current contract and Instagram post history.', timestamp: '12:00:12' },
        { phase: 'REASON', thought: 'Need to cross-reference historical club achievements (Barcelona, PSG) and official tournament statistics.', timestamp: '12:00:15' },
        { phase: 'ACT', action: 'scraper', action_input: { url: 'https://fcbarcelona.com/history' }, timestamp: '12:00:20' },
        { phase: 'OBSERVE', observation: 'Confirmed 672 Barcelona goals and 10 La Liga titles. Verified 2022 FIFA World Cup Golden Ball award.', timestamp: '12:00:30' },
        { phase: 'REFLECT', reflection: 'Trophy cabinet and stats fully corroborated. High confidence in athletic specialties and club history.', timestamp: '12:00:35' },
        { phase: 'REASON', thought: 'Aggregating final sports credentials and playstyle insights.', timestamp: '12:00:40' },
      ];
    } else if (type === 'tech_normal') {
      simulationSteps = [
        { phase: 'REASON', thought: 'Initializing search targets for corporate bio, enterprise product portfolios, and developer communities.', timestamp: '12:00:01' },
        { phase: 'ACT', action: 'scraper', action_input: { url: 'https://linkedin.com/in/nandhini-s-tech' }, timestamp: '12:00:05' },
        { phase: 'OBSERVE', observation: 'Retrieved profile for Nandhini S. Confirmed title: Lead Technical Product Manager at SynthAI Systems.', timestamp: '12:00:12' },
        { phase: 'REASON', thought: 'Checking developer ecosystems, API specifications, and public architectures. Inspecting GitHub for enterprise contributions.', timestamp: '12:00:15' },
        { phase: 'ACT', action: 'scraper', action_input: { url: 'https://github.com/nandhini-s' }, timestamp: '12:00:20' },
        { phase: 'OBSERVE', observation: 'Found product-management and architectural specifications for "DevForge Platform" and "CloudShield Edge".', timestamp: '12:00:30' },
        { phase: 'REFLECT', reflection: 'Multi-source alignment confirmed. Data suggests a strong hybrid profile with system architecture and product-technical leadership.', timestamp: '12:00:35' },
        { phase: 'REASON', thought: 'Compiling premium Indigo-themed tech-normal dossier briefing.', timestamp: '12:00:40' },
      ];
    } else {
      simulationSteps = [
        { phase: 'REASON', thought: 'Analyzing provided URLs to prioritize data extraction sources. LinkedIn seems most relevant for bio and experience.', timestamp: '12:00:01' },
        { phase: 'ACT', action: 'scraper', action_input: { url: 'https://linkedin.com/in/elenavance' }, timestamp: '12:00:05' },
        { phase: 'OBSERVE', observation: 'Successfully extracted LinkedIn profile. Found current role: Lead AI Scientist at Aether Dynamics.', timestamp: '12:00:12' },
        { phase: 'REASON', thought: 'Need to verify project details and technical skills. Checking GitHub for repositories and contributions.', timestamp: '12:00:15' },
        { phase: 'ACT', action: 'scraper', action_input: { url: 'https://github.com/evance' }, timestamp: '12:00:20' },
        { phase: 'OBSERVE', observation: 'Found multiple high-star repositories in Rust and Python. Key project "LumenCore" identified.', timestamp: '12:00:30' },
        { phase: 'REFLECT', reflection: 'Data is consistent between professional bio and technical contributions. High confidence in skills and experience sections.', timestamp: '12:00:35' },
        { phase: 'REASON', thought: 'Performing final synthesis and generating professional insights based on extracted data.', timestamp: '12:00:40' },
      ];
    }

    for (const step of simulationSteps) {
      addStep(step as any);
      await new Promise(r => setTimeout(r, 1000));
    }

    setFinalProfile(
      type === 'sports' 
        ? mockSportsProfile 
        : type === 'tech_normal' 
          ? mockTechNormalProfile 
          : mockProfile
    );
  };

  return (
    <main className="min-h-screen bg-black text-zinc-100 selection:bg-blue-500/30">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] bg-blue-600/10 blur-[120px] rounded-full"></div>
        <div className="absolute top-[20%] -right-[10%] w-[40%] h-[40%] bg-purple-600/10 blur-[120px] rounded-full"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between mb-20 gap-8">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-blue-400 font-bold tracking-tighter text-2xl">
              <Bot size={32} strokeWidth={2.5} />
              PERSONA.IQ
            </div>
            <p className="text-zinc-500 font-medium">Autonomous Professional Intelligence Agent</p>
          </div>
          
          <div className="flex items-center gap-4">
            {status !== 'idle' && (
              <div className="flex items-center gap-3">
                <button 
                  onClick={reset}
                  className="px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-xl text-xs font-semibold hover:bg-zinc-800 transition-all text-zinc-400"
                >
                  Go Back
                </button>
                {status === 'running' && (
                  <button 
                    onClick={stopAgent}
                    className="px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-xl text-xs font-semibold hover:bg-red-500/20 transition-all text-red-500"
                  >
                    Stop Agent
                  </button>
                )}
              </div>
            )}
            <button 
              onClick={() => simulateAgent('tech')}
              disabled={status === 'running'}
              className="px-4 py-2.5 bg-zinc-900/80 border border-zinc-800 hover:border-zinc-700 rounded-xl text-xs font-bold hover:bg-zinc-800 transition-all flex items-center gap-2"
            >
              <Zap size={14} className="text-amber-400" />
              Simulate Tech
            </button>
            <button 
              onClick={() => simulateAgent('tech_normal')}
              disabled={status === 'running'}
              className="px-4 py-2.5 bg-zinc-900/80 border border-zinc-800 hover:border-zinc-700 rounded-xl text-xs font-bold hover:bg-zinc-800 transition-all flex items-center gap-2"
            >
              <Cpu size={14} className="text-indigo-400" />
              Simulate Tech/Normal
            </button>
            <button 
              onClick={() => simulateAgent('sports')}
              disabled={status === 'running'}
              className="px-4 py-2.5 bg-zinc-900/80 border border-zinc-800 hover:border-zinc-700 rounded-xl text-xs font-bold hover:bg-zinc-800 transition-all flex items-center gap-2"
            >
              <Trophy size={14} className="text-amber-400" />
              Simulate Sports
            </button>
            <div className="h-10 w-px bg-zinc-800"></div>
            <div className="flex -space-x-2">
              {[1, 2, 3].map(i => (
                <div key={i} className="w-10 h-10 rounded-full border-2 border-black bg-zinc-800 flex items-center justify-center">
                  <UserIcon i={i} />
                </div>
              ))}
            </div>
          </div>
        </header>

        <AnimatePresence mode="wait">
          {status === 'idle' && (
            <motion.div 
              key="idle"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-12"
            >
              <div className="text-center space-y-4 max-w-3xl mx-auto mb-16">
                <h1 className="text-5xl md:text-7xl font-black text-white tracking-tight leading-[1.1]">
                  Build a complete <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">Digital Profile</span> with AI.
                </h1>
                <p className="text-xl text-zinc-500">
                  Enter a name and social links. Our agent will browse the web, verify facts, and synthesize a professional identity in real-time.
                </p>
              </div>
              <InputForm />
            </motion.div>
          )}

          {status !== 'idle' && (
            <motion.div 
              key="active"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-20"
            >
              {error && (
                <div className="bg-red-500/10 border border-red-500/20 p-6 rounded-2xl text-red-500 flex flex-col items-center gap-2 max-w-2xl mx-auto">
                   <p className="font-bold text-lg">Agent Error</p>
                   <p className="text-sm opacity-80">{error}</p>
                   <button onClick={reset} className="mt-2 px-4 py-2 bg-red-500 text-white rounded-lg text-xs font-bold">Try Again</button>
                </div>
              )}
              <AgentTimeline />
              <ProfileDashboard />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <footer className="mt-20 border-t border-zinc-900 py-12 text-center text-zinc-600 text-sm">
        <p>© 2026 Persona.IQ • Powered by Groq Llama 3 & LangGraph</p>
      </footer>
    </main>
  );
}

const UserIcon = ({ i }: { i: number }) => {
  const colors = ["bg-blue-500", "bg-purple-500", "bg-emerald-500"];
  return <div className={`w-6 h-6 rounded-full ${colors[i-1]} opacity-50`}></div>;
};
