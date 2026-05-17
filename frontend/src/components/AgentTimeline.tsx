"use client";

import React from 'react';
import { useAgentStore } from '@/store/useAgentStore';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Cpu, Eye, BarChart3, CheckCircle2 } from 'lucide-react';
import { cn } from '@/utils';

const phaseIcons = {
  REASON: <Brain className="text-purple-400" size={20} />,
  ACT: <Cpu className="text-blue-400" size={20} />,
  OBSERVE: <Eye className="text-amber-400" size={20} />,
  REFLECT: <BarChart3 className="text-rose-400" size={20} />,
  FINAL: <CheckCircle2 className="text-emerald-400" size={20} />,
};

export const AgentTimeline = () => {
  const steps = useAgentStore((state) => state.steps);
  const status = useAgentStore((state) => state.status);

  if (status === 'idle') return null;

  return (
    <div className="w-full max-w-4xl mx-auto mt-12 space-y-8 pb-20">
      <div className="flex items-center justify-between px-2">
        <h2 className="text-2xl font-bold text-white flex items-center gap-3">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
          </span>
          Agentic Loop
        </h2>
        <span className="text-zinc-500 text-sm">{steps.length} steps completed</span>
      </div>

      <div className="relative space-y-6 before:absolute before:left-6 before:top-4 before:bottom-4 before:w-px before:bg-zinc-800">
        <AnimatePresence mode="popLayout">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="relative pl-14"
            >
              <div className="absolute left-0 p-3 bg-zinc-900 border border-zinc-800 rounded-2xl z-10">
                {phaseIcons[step.phase as keyof typeof phaseIcons]}
              </div>
              
              <div className="bg-zinc-900/40 border border-zinc-800/50 p-6 rounded-2xl space-y-4 hover:border-zinc-700 transition-colors">
                <div className="flex items-center justify-between">
                  <span className={cn(
                    "text-xs font-bold tracking-widest px-2 py-1 rounded bg-zinc-800",
                    step.phase === 'REASON' && "text-purple-400 bg-purple-400/10",
                    step.phase === 'ACT' && "text-blue-400 bg-blue-400/10",
                    step.phase === 'OBSERVE' && "text-amber-400 bg-amber-400/10",
                    step.phase === 'REFLECT' && "text-rose-400 bg-rose-400/10",
                  )}>
                    {step.phase}
                  </span>
                  <span className="text-xs text-zinc-600">{step.timestamp}</span>
                </div>

                {step.thought && (
                  <p className="text-zinc-300 leading-relaxed italic">
                    "{step.thought}"
                  </p>
                )}

                {step.action && (
                  <div className="flex items-center gap-2 bg-zinc-950 p-3 rounded-xl border border-zinc-800/50">
                    <span className="text-zinc-500 text-xs">Action:</span>
                    <span className="text-blue-400 font-mono text-sm">{step.action}</span>
                    <span className="text-zinc-700 mx-2">|</span>
                    <span className="text-zinc-400 text-xs truncate max-w-xs">
                      {JSON.stringify(step.action_input)}
                    </span>
                  </div>
                )}

                {step.observation && (
                  <div className="bg-zinc-950/50 p-4 rounded-xl border border-zinc-800/30 overflow-hidden">
                    <p className="text-xs text-zinc-500 mb-2 font-medium">Observation:</p>
                    <div className="text-zinc-400 text-sm font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
                      {typeof step.observation === 'string' 
                        ? step.observation 
                        : JSON.stringify(step.observation, null, 2)}
                    </div>
                  </div>
                )}

                {step.reflection && (
                  <div className="flex gap-3 bg-rose-400/5 p-4 rounded-xl border border-rose-400/10">
                    <BarChart3 className="text-rose-400 shrink-0" size={18} />
                    <p className="text-sm text-rose-200/80">{step.reflection}</p>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {status === 'running' && (
          <div className="relative pl-14 animate-pulse">
            <div className="absolute left-0 p-3 bg-zinc-900 border border-zinc-800 rounded-2xl z-10">
              <div className="w-5 h-5 bg-zinc-800 rounded-full"></div>
            </div>
            <div className="bg-zinc-900/20 border border-zinc-800/30 p-12 rounded-2xl"></div>
          </div>
        )}
      </div>
    </div>
  );
};
