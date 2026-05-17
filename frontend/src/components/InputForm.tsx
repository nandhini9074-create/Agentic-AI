"use client";

import React, { useState } from 'react';
import { Plus, Trash2, Send } from 'lucide-react';
import { useAgentStore } from '@/store/useAgentStore';

export const InputForm = () => {
  const [name, setName] = useState('');
  const [urls, setUrls] = useState(['']);
  const startAgent = useAgentStore((state) => state.startAgent);
  const status = useAgentStore((state) => state.status);

  const addUrlField = () => setUrls([...urls, '']);
  
  const removeUrlField = (index: number) => {
    if (urls.length > 1) {
      const newUrls = urls.filter((_, i) => i !== index);
      setUrls(newUrls);
    }
  };

  const updateUrl = (index: number, value: string) => {
    const newUrls = [...urls];
    newUrls[index] = value;
    setUrls(newUrls);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name && urls.some(url => url.trim() !== '')) {
      startAgent(name, urls.filter(url => url.trim() !== ''));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto space-y-6 bg-zinc-900/50 p-8 rounded-2xl border border-zinc-800 backdrop-blur-xl">
      <div className="space-y-2">
        <label className="text-sm font-medium text-zinc-400 ml-1">Full Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. John Doe"
          className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
          required
        />
      </div>

      <div className="space-y-3">
        <label className="text-sm font-medium text-zinc-400 ml-1">Profile URLs</label>
        {urls.map((url, index) => (
          <div key={index} className="flex gap-2">
            <input
              type="text"
              value={url}
              onChange={(e) => updateUrl(index, e.target.value)}
              placeholder="e.g. linkedin.com/in/username"
              className="flex-1 bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
              required={index === 0}
            />
            {urls.length > 1 && (
              <button
                type="button"
                onClick={() => removeUrlField(index)}
                className="p-3 text-zinc-500 hover:text-red-400 hover:bg-red-400/10 rounded-xl transition-all"
              >
                <Trash2 size={20} />
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={addUrlField}
          className="flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 transition-colors ml-1"
        >
          <Plus size={16} />
          Add another URL
        </button>
      </div>

      <button
        type="submit"
        disabled={status === 'running'}
        className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-600/20"
      >
        <Send size={20} />
        {status === 'running' ? 'Agent Working...' : 'Generate Profile'}
      </button>
    </form>
  );
};
