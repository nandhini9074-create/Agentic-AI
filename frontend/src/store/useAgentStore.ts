import { create } from 'zustand';
import { AgentStep, FinalProfile, Phase } from '../types/agent';

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

interface AgentStore {
  status: 'idle' | 'running' | 'completed' | 'error';
  steps: AgentStep[];
  finalProfile: FinalProfile | null;
  error: string | null;
  currentJobId: string | null;
  
  startAgent: (name: string, urls: string[]) => Promise<void>;
  stopAgent: () => Promise<void>;
  pollJobStatus: (jobId: string) => Promise<void>;
  addStep: (step: AgentStep) => void;
  setFinalProfile: (profile: FinalProfile) => void;
  reset: () => Promise<void>;
  setStatus: (status: 'idle' | 'running' | 'completed' | 'error') => void;
}

export const useAgentStore = create<AgentStore>((set, get) => ({
  status: 'idle',
  steps: [],
  finalProfile: null,
  currentJobId: null,
  error: null,

  startAgent: async (name, urls) => {
    set({ status: 'running', steps: [], finalProfile: null, error: null, currentJobId: null });
    
    try {
      const response = await axios.post(`${API_BASE_URL}/build-profile`, { name, urls });
      const { job_id } = response.data;
      set({ currentJobId: job_id });
      get().pollJobStatus(job_id);
    } catch (err: any) {
      set({ status: 'error', error: err.message });
    }
  },

  stopAgent: async () => {
    const { currentJobId } = get();
    if (!currentJobId) return;

    try {
      await axios.post(`${API_BASE_URL}/job/${currentJobId}/cancel`);
      set({ status: 'idle', currentJobId: null });
    } catch (err: any) {
      console.error('Failed to stop agent:', err);
    }
  },

  pollJobStatus: async (jobId) => {
    const poll = async () => {
      // Don't poll if we're no longer running or job changed
      if (get().status !== 'running' || get().currentJobId !== jobId) return;

      try {
        const response = await axios.get(`${API_BASE_URL}/job/${jobId}`);
        const { status, steps, data } = response.data;

        if (status === 'cancelled') {
           set({ status: 'idle', currentJobId: null });
           return;
        }

        // Map backend steps to frontend format
        const formattedSteps: AgentStep[] = steps.map((s: any) => ({
          phase: s.phase,
          thought: s.thought,
          action: s.action,
          action_input: s.action_input,
          observation: s.observation,
          reflection: s.reflection,
          timestamp: new Date().toLocaleTimeString()
        }));

        set({ steps: formattedSteps });

        if (status === 'completed') {
          // Find the FINAL step which contains the profile data
          const finalStep = steps.find((s: any) => s.node === 'final');
          const finalData = finalStep?.data || data; // Fallback to top-level data
          
          if (finalData && (finalData.profile || finalData.insights)) {
            console.log('Final profile data received:', finalData);
            set({ finalProfile: finalData, status: 'completed' });
          } else {
            console.error('Job completed but no valid profile data found in steps or response', { finalStep, data });
            set({ status: 'error', error: 'Completed but no data found' });
          }
          return;
        }

        if (status === 'error') {
          set({ status: 'error', error: 'Agent job failed' });
          return;
        }

        // Poll again in 2 seconds
        setTimeout(poll, 2000);
      } catch (err: any) {
        set({ status: 'error', error: err.message });
      }
    };

    poll();
  },

  addStep: (step) => set((state) => ({ 
    steps: [...state.steps, step] 
  })),

  setFinalProfile: (profile) => set({ 
    finalProfile: profile, 
    status: 'completed' 
  }),

  reset: async () => {
    const { currentJobId, stopAgent } = get();
    if (currentJobId) {
      await stopAgent();
    }
    set({ 
      status: 'idle', 
      steps: [], 
      finalProfile: null, 
      error: null,
      currentJobId: null
    });
  },

  setStatus: (status) => set({ status }),
}));
