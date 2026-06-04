"use client";

import React, { useState } from 'react';
import { Plus, Trash2, Send, User, Mail, Phone, Calendar, Award, MapPin, Globe, Compass } from 'lucide-react';
import { useAgentStore } from '@/store/useAgentStore';

export const InputForm = () => {
  /*
  // Old State & Handlers commented out as requested
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
  */

  // New State Fields
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [dob, setDob] = useState('');
  const [skills, setSkills] = useState('');
  const [location, setLocation] = useState('');
  const [query, setQuery] = useState('');

  const startAgent = useAgentStore((state) => state.startAgent);
  const status = useAgentStore((state) => state.status);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name) {
      startAgent({
        name,
        email: email || undefined,
        phone: phone || undefined,
        skills: skills || undefined,
        age: age || undefined,
        gender: gender || undefined,
        dob: dob || undefined,
        location: location || undefined,
        query: query || undefined,
        urls: []
      });
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-6">
      <form onSubmit={handleSubmit} className="w-full bg-zinc-900/50 p-8 rounded-3xl border border-zinc-800/80 backdrop-blur-xl shadow-2xl space-y-6">
        <div className="border-b border-zinc-800/80 pb-4 mb-2">
          <h2 className="text-xl font-bold text-white tracking-tight">Create Professional Profile</h2>
          <p className="text-xs text-zinc-500 mt-1">Fill out the credentials below. The autonomous agent will cross-reference open-source portals to compile your verified resume portfolio.</p>
        </div>

        {/* Primary Details Section */}
        <div className="space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-widest text-blue-400">Primary Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* Full Name */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5 ml-1">
                Full Name <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500">
                  <User size={16} />
                </div>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Full name"
                  className="w-full bg-zinc-950/80 border border-zinc-800/80 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all"
                  required
                />
              </div>
            </div>

            {/* Email Address */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5 ml-1">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500">
                  <Mail size={16} />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email address"
                  className="w-full bg-zinc-950/80 border border-zinc-800/80 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all"
                />
              </div>
            </div>

            {/* Phone Number */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5 ml-1">
                Phone Number
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500">
                  <Phone size={16} />
                </div>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="Phone number"
                  className="w-full bg-zinc-950/80 border border-zinc-800/80 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all"
                />
              </div>
            </div>

            {/* Core Skills */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5 ml-1">
                Core Skills
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500">
                  <Award size={16} />
                </div>
                <input
                  type="text"
                  value={skills}
                  onChange={(e) => setSkills(e.target.value)}
                  placeholder="Skills & specialties"
                  className="w-full bg-zinc-950/80 border border-zinc-800/80 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all"
                />
              </div>
            </div>

          </div>
        </div>

        {/* Optional Fields Section */}
        <div className="space-y-4 pt-2 border-t border-zinc-800/40">
          <h3 className="text-xs font-bold uppercase tracking-widest text-purple-400">Additional Profile Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* Age */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5 ml-1">Age</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500">
                  <Calendar size={16} />
                </div>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  placeholder="Age"
                  className="w-full bg-zinc-950/80 border border-zinc-800/80 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all"
                />
              </div>
            </div>

            {/* Gender */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5 ml-1">Gender</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500">
                  <User size={16} />
                </div>
                <input
                  type="text"
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  placeholder="Gender"
                  className="w-full bg-zinc-950/80 border border-zinc-800/80 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all"
                />
              </div>
            </div>

            {/* Date of Birth */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5 ml-1">Date of Birth</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500">
                  <Calendar size={16} />
                </div>
                <input
                  type="date"
                  value={dob}
                  onChange={(e) => setDob(e.target.value)}
                  className="w-full bg-zinc-950/80 border border-zinc-800/80 rounded-xl pl-10 pr-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all [color-scheme:dark]"
                />
              </div>
            </div>


            {/* Location */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5 ml-1">Location</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500">
                  <MapPin size={16} />
                </div>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Location"
                  className="w-full bg-zinc-950/80 border border-zinc-800/80 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all"
                />
              </div>
            </div>

            {/* Custom Search Query */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5 ml-1">Custom Search Query (Optional)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500">
                  <Compass size={16} />
                </div>
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter custom search directives..."
                  className="w-full bg-zinc-950/80 border border-zinc-800/80 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-purple-500/40 focus:border-purple-500/40 transition-all"
                />
              </div>
            </div>

          </div>
        </div>

        {/* Submit Action */}
        <button
          type="submit"
          disabled={status === 'running'}
          className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2.5 transition-all shadow-lg shadow-blue-600/20 mt-4 active:scale-[0.99]"
        >
          <Send size={18} />
          {status === 'running' ? 'Agent Profiling...' : 'Generate AI Portfolio'}
        </button>
      </form>

      {/* Old Codes commented out below to comply with instructions */}
      {/*
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
      </form>
      */}
    </div>
  );
};
