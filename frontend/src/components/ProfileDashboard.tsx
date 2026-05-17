"use client";

import React from 'react';
import { useAgentStore } from '@/store/useAgentStore';
import { motion } from 'framer-motion';
import { 
  User, Briefcase, Code, Award, Link as LinkIcon, 
  MapPin, Sparkles, TrendingUp, ShieldCheck, MessageSquare, Brain
} from 'lucide-react';
import { cn } from '@/utils';

export const ProfileDashboard = () => {
  const finalProfile = useAgentStore((state) => state.finalProfile);
  const status = useAgentStore((state) => state.status);

  if (status !== 'completed' || !finalProfile) return null;

  const { 
    profile = { name: 'Unknown User', bio: '', location: '', social_links: [], experience: [], projects: [], skills: [] }, 
    insights = { summary: '', key_strengths: [] }, 
    confidence = { score: 0, justification: '' } 
  } = finalProfile || {};

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-5xl mx-auto space-y-10 pb-32"
    >
      {/* Header / Bio Section */}
      <section className="bg-gradient-to-br from-blue-600/10 to-purple-600/10 border border-blue-500/20 p-10 rounded-3xl backdrop-blur-3xl relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-10">
          <Sparkles size={120} className="text-blue-400" />
        </div>
        <div className="relative z-10 flex flex-col md:flex-row gap-8 items-start">
          <div className="w-24 h-24 bg-blue-600 rounded-3xl flex items-center justify-center shadow-2xl shadow-blue-600/40">
            <User size={48} className="text-white" />
          </div>
          <div className="space-y-4 max-w-2xl">
            <div className="space-y-1">
              <h1 className="text-4xl font-extrabold text-white tracking-tight">{profile?.name || 'Unknown Profile'}</h1>
              {profile?.location && (
                <div className="flex items-center gap-2 text-zinc-400">
                  <MapPin size={16} />
                  <span className="text-sm">{profile.location}</span>
                </div>
              )}
            </div>
            <p className="text-xl text-zinc-300 leading-relaxed">{profile?.bio}</p>
            <div className="flex flex-wrap gap-2 pt-2">
              {profile?.social_links?.map((link, i) => (
                <a key={i} href={link} target="_blank" rel="noopener noreferrer" className="p-2 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-400 hover:text-white hover:border-zinc-600 transition-all">
                  <LinkIcon size={18} />
                </a>
              ))}
            </div>
          </div>
        </div>
      </section>

      <div className={cn(
        "grid grid-cols-1 gap-8",
        (profile?.experience?.length > 0 || profile?.projects?.length > 0 || profile?.recent_posts?.length > 0) 
          ? "lg:grid-cols-3" 
          : "lg:grid-cols-1 max-w-2xl mx-auto"
      )}>
        {/* Main Content (Experience & Projects) */}
        {(profile?.experience?.length > 0 || profile?.projects?.length > 0 || profile?.recent_posts?.length > 0) && (
          <div className="lg:col-span-2 space-y-8">
          {/* Experience */}
          {profile?.experience?.length > 0 && (
            <div className="bg-zinc-900/50 border border-zinc-800 p-8 rounded-3xl space-y-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-3">
                <Briefcase size={22} className="text-blue-400" />
                Professional Experience
              </h3>
              <div className="space-y-8 relative before:absolute before:left-4 before:top-2 before:bottom-2 before:w-px before:bg-zinc-800">
                {profile.experience.map((exp, i) => (
                  <div key={i} className="relative pl-10">
                    <div className="absolute left-0 w-8 h-8 bg-zinc-950 border border-zinc-800 rounded-full flex items-center justify-center z-10">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex flex-col md:flex-row md:items-center justify-between">
                        <h4 className="font-bold text-zinc-100">{exp.title}</h4>
                        <span className="text-xs font-medium text-zinc-500 bg-zinc-800/50 px-2 py-1 rounded">{exp.period}</span>
                      </div>
                      <p className="text-sm text-blue-400 font-medium">{exp.company}</p>
                      <p className="text-sm text-zinc-400 leading-relaxed">{exp.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Projects */}
          {profile?.projects?.length > 0 && (
            <div className="bg-zinc-900/50 border border-zinc-800 p-8 rounded-3xl space-y-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-3">
                <Code size={22} className="text-emerald-400" />
                Key Projects
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {profile.projects.map((project, i) => (
                  <div key={i} className="bg-zinc-950 border border-zinc-800 p-6 rounded-2xl space-y-3 hover:border-zinc-700 transition-all group">
                    <h4 className="font-bold text-zinc-100 group-hover:text-blue-400 transition-colors">{project.name}</h4>
                    <p className="text-sm text-zinc-400 line-clamp-3">{project.description}</p>
                    <div className="flex flex-wrap gap-2 pt-2">
                      {project.technologies?.map((tech, j) => (
                        <span key={j} className="text-[10px] uppercase tracking-wider font-bold text-zinc-500 bg-zinc-900 px-2 py-1 rounded">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Activity */}
          {profile?.recent_posts?.length > 0 && (
            <div className="bg-zinc-900/50 border border-zinc-800 p-8 rounded-3xl space-y-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-3">
                <MessageSquare size={22} className="text-amber-400" />
                Recent Activity
              </h3>
              <div className="space-y-4">
                {profile.recent_posts.map((post, i) => (
                  <div key={i} className="bg-zinc-950 border border-zinc-800 p-6 rounded-2xl space-y-3">
                    <div className="flex items-center justify-between">
                       <span className="text-[10px] uppercase tracking-widest font-bold text-zinc-500">{post.date || 'Recent Post'}</span>
                       {post.link && (
                         <a href={post.link} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 transition-colors">
                           <LinkIcon size={14} />
                         </a>
                       )}
                    </div>
                    <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">{post.content}</p>
                    
                    {post.summary && (
                      <div className="bg-blue-500/5 border border-blue-500/10 p-3 rounded-xl flex gap-3">
                        <Brain size={16} className="text-blue-400 shrink-0 mt-0.5" />
                        <div className="space-y-1">
                          <p className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">AI Summary</p>
                          <p className="text-xs text-blue-200/80 italic leading-relaxed">{post.summary}</p>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

        {/* Sidebar (Skills, Insights, Confidence) */}
        <div className="space-y-8">
          {/* Insights */}
          <div className="bg-zinc-900/50 border border-zinc-800 p-8 rounded-3xl space-y-6">
            <h3 className="text-xl font-bold text-white flex items-center gap-3">
              <TrendingUp size={22} className="text-purple-400" />
              AI Insights
            </h3>
            <div className="space-y-6">
              <div className="space-y-2">
                <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Summary</p>
                <p className="text-sm text-zinc-300 leading-relaxed">{insights?.summary || 'Generating insights...'}</p>
              </div>
              <div className="space-y-2">
                <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Key Strengths</p>
                <div className="flex flex-wrap gap-2">
                  {insights?.key_strengths?.map((s, i) => (
                    <span key={i} className="text-xs text-purple-200 bg-purple-500/10 border border-purple-500/20 px-3 py-1.5 rounded-full">{s}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Skills */}
          {profile?.skills?.length > 0 && (
            <div className="bg-zinc-900/50 border border-zinc-800 p-8 rounded-3xl space-y-4">
              <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Core Skills</p>
              <div className="flex flex-wrap gap-2">
                {profile.skills.map((skill, i) => (
                  <span key={i} className="text-xs font-medium text-zinc-300 bg-zinc-800 px-3 py-1.5 rounded-lg border border-zinc-700/50">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Confidence */}
          <div className="bg-blue-600/5 border border-blue-600/10 p-6 rounded-3xl space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-blue-400 flex items-center gap-2">
                <ShieldCheck size={18} />
                Confidence
              </span>
              <span className="text-xl font-black text-blue-300">{Math.round((confidence?.score || 0) * 100)}%</span>
            </div>
            <div className="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${(confidence?.score || 0) * 100}%` }}
                className="h-full bg-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.5)]"
              />
            </div>
            <p className="text-[10px] text-zinc-500 italic leading-tight">
              {confidence?.justification || 'Baseline extraction confidence.'}
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
