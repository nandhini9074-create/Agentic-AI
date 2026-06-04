"use client";
 
import React from 'react';
import { useAgentStore } from '@/store/useAgentStore';
import { motion } from 'framer-motion';
import { 
  User, Briefcase, Code, Award, Link as LinkIcon, 
  MapPin, Sparkles, TrendingUp, ShieldCheck, MessageSquare, Brain,
  Clock, Calendar, Globe, ExternalLink, Mail, Phone, Terminal, Zap,
  Cpu, Star, BookOpen, GraduationCap, ShieldAlert, Award as Trophy
} from 'lucide-react';
import { cn } from '@/utils';
 
export const ProfileDashboard = () => {
  const finalProfile = useAgentStore((state) => state.finalProfile);
  const status = useAgentStore((state) => state.status);
 
  if (status !== 'completed' || !finalProfile) return null;
 
  const { 
    profile,
    insights,
    confidence
  } = finalProfile || {};
 
  // Unified dossier markdown support (backward compatible)
  const dossierMarkdown = 
    (finalProfile as any)?.osint_dossier_markdown || 
    (profile as any)?.osint_dossier_markdown ||
    (finalProfile as any)?.sports_profile_markdown || 
    (profile as any)?.sports_profile_markdown;
 
  const headline = (profile?.basic_info?.headline || profile?.headline || '').toLowerCase();
  const bio = (profile?.bio || '').toLowerCase();
  
  // Local fallback classification if not provided by backend
  const profileType = (() => {
    const backendType = (finalProfile as any)?.profile_type || (profile as any)?.profile_type;
    if (backendType) return backendType.toLowerCase();

    // Check sports keywords
    const sportsKeywords = [
      'athlete', 'footballer', 'soccer', 'cricketer', 'basketball', 'tennis', 'runner', 'swimmer',
      'coach', 'club', 'sport', 'olympic', 'striker', 'midfielder', 'defender', 'goalkeeper', 
      'champion', 'athletics', 'player', 'team player', 'winger', 'forward', 'ball', 'f1', 'racer'
    ];
    if (sportsKeywords.some(keyword => headline.includes(keyword) || bio.includes(keyword))) {
      return 'sports';
    }

    // Check hybrid administrative/tech_normal keywords
    const hybridKeywords = [
      'product manager', 'project manager', 'solutions architect', 'dev advocate', 'developer advocate',
      'tech manager', 'technical manager', 'product lead', 'scrum master', 'digital architect', 'startup founder',
      'tech founder', 'technology officer', 'technology leader', 'business-tech', 'technical director',
      'pm', 'delivery manager', 'agile coach'
    ];
    if (hybridKeywords.some(keyword => headline.includes(keyword) || bio.includes(keyword))) {
      return 'tech_normal';
    }

    // Check tech keywords
    const techKeywords = [
      'developer', 'engineer', 'programmer', 'coder', 'tech', 'software', 'architect', 'cto', 
      'full-stack', 'frontend', 'backend', 'devops', 'open-source', 'github', 'stars', 'repository', 
      'programming', 'computer science', 'sysadmin', 'hacker'
    ];
    if (techKeywords.some(keyword => headline.includes(keyword) || bio.includes(keyword))) {
      return 'tech';
    }

    return 'general';
  })();

  // -------------------------------------------------------------
  // Theme Configurations (Aesthetics and Accent Colors)
  // -------------------------------------------------------------
  const theme = (() => {
    switch (profileType) {
      case 'sports':
        return {
          type: 'sports',
          colorName: 'emerald',
          bgGradient: 'from-emerald-950/20 via-teal-950/10 to-zinc-950/50',
          border: 'border-emerald-500/20',
          borderHover: 'hover:border-emerald-500/40',
          borderLight: 'border-emerald-500/10',
          textAccent: 'text-emerald-400',
          textMuted: 'text-emerald-500/70',
          badge: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
          glow: 'shadow-[0_0_50px_rgba(16,185,129,0.08)]',
          avatarBg: 'bg-gradient-to-br from-emerald-600 to-teal-500 shadow-emerald-500/20',
          avatarIcon: Zap,
          headerLabel: 'ATHLETIC PROFILE',
          dossierTitle: '🛡️ CLASSIFIED OSINT SYSTEM // DEEP SPORTS DOSSIER',
          dossierBg: 'bg-zinc-950/80 text-emerald-400 border-emerald-500/20',
          scanlineColor: 'from-emerald-500 via-teal-500 to-emerald-500',
          cardBg: 'bg-zinc-900/40 backdrop-blur-md border border-zinc-800/80',
          titleIconColor: 'text-emerald-400',
          bulletColor: 'text-emerald-400',
          progressColor: 'bg-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.5)]',
          confidenceBadge: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
        };
      case 'tech':
        return {
          type: 'tech',
          colorName: 'cyan',
          bgGradient: 'from-cyan-950/20 via-purple-950/10 to-zinc-950/50',
          border: 'border-cyan-500/25',
          borderHover: 'hover:border-cyan-500/40',
          borderLight: 'border-cyan-500/10',
          textAccent: 'text-cyan-400',
          textMuted: 'text-cyan-500/70',
          badge: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
          glow: 'shadow-[0_0_50px_rgba(6,182,212,0.12)]',
          avatarBg: 'bg-gradient-to-br from-cyan-500 to-purple-600 shadow-cyan-500/20',
          avatarIcon: Terminal,
          headerLabel: 'DEVELOPER LOG',
          dossierTitle: '💻 SECURE DEVNET LOG // CYBERPUNK DEEP DOSSIER',
          dossierBg: 'bg-black/90 text-cyan-400 border-cyan-500/25',
          scanlineColor: 'from-cyan-500 via-purple-500 to-cyan-500',
          cardBg: 'bg-zinc-900/40 backdrop-blur-md border border-zinc-800/80',
          titleIconColor: 'text-cyan-400',
          bulletColor: 'text-cyan-400',
          progressColor: 'bg-cyan-500 shadow-[0_0_20px_rgba(6,182,212,0.5)]',
          confidenceBadge: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20'
        };
      case 'tech_normal':
        return {
          type: 'tech_normal',
          colorName: 'indigo',
          bgGradient: 'from-indigo-950/20 via-blue-950/10 to-zinc-950/50',
          border: 'border-indigo-500/25',
          borderHover: 'hover:border-indigo-500/40',
          borderLight: 'border-indigo-500/10',
          textAccent: 'text-indigo-400',
          textMuted: 'text-indigo-500/70',
          badge: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
          glow: 'shadow-[0_0_50px_rgba(99,102,241,0.12)]',
          avatarBg: 'bg-gradient-to-br from-indigo-500 to-blue-600 shadow-indigo-500/20',
          avatarIcon: Cpu,
          headerLabel: 'TECH-NORMAL BRIEFING',
          dossierTitle: '📁 SECURE TECH-NORMAL DOSSIER // PROFESSIONAL BRIEFING',
          dossierBg: 'bg-zinc-950/90 text-indigo-200 border-indigo-500/20 font-sans text-sm',
          scanlineColor: 'from-indigo-500 via-blue-500 to-indigo-500',
          cardBg: 'bg-zinc-900/40 backdrop-blur-md border border-zinc-800/80',
          titleIconColor: 'text-indigo-400',
          bulletColor: 'text-indigo-400',
          progressColor: 'bg-indigo-500 shadow-[0_0_20px_rgba(99,102,241,0.5)]',
          confidenceBadge: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20'
        };
      case 'general':
      default:
        return {
          type: 'general',
          colorName: 'amber',
          bgGradient: 'from-amber-950/20 via-rose-950/10 to-zinc-950/50',
          border: 'border-amber-500/20',
          borderHover: 'hover:border-amber-500/40',
          borderLight: 'border-amber-500/10',
          textAccent: 'text-amber-400',
          textMuted: 'text-amber-500/70',
          badge: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
          glow: 'shadow-[0_0_50px_rgba(245,158,11,0.08)]',
          avatarBg: 'bg-gradient-to-br from-amber-500 to-rose-600 shadow-amber-500/20',
          avatarIcon: User,
          headerLabel: 'EXECUTIVE BRIEFING',
          dossierTitle: '💼 EXECUTIVE OSINT REPORT // CONFIDENTIAL BRIEFING',
          dossierBg: 'bg-zinc-950/80 text-amber-200 border-amber-500/20',
          scanlineColor: 'from-amber-500 via-rose-500 to-amber-500',
          cardBg: 'bg-zinc-900/40 backdrop-blur-md border border-zinc-800/80',
          titleIconColor: 'text-amber-400',
          bulletColor: 'text-amber-400',
          progressColor: 'bg-amber-500 shadow-[0_0_20px_rgba(245,158,11,0.5)]',
          confidenceBadge: 'text-amber-400 bg-amber-500/10 border-amber-500/20'
        };
    }
  })();

  const getSourceDisplay = (urlStr?: string) => {
    if (!urlStr) return "Source Link";
    try {
      return new URL(urlStr).hostname;
    } catch (_) {
      return "Source Link";
    }
  };
 
  // Deduplicate discovered links
  const profileUrls = Array.from(new Set([
    ...(profile?.social_links || []),
    ...(profile?.social_profiles || []),
    ...Object.values(profile?.verified_profiles || {}),
    ...(profile?.sources_used || [])
  ])).filter((url): url is string => typeof url === 'string' && url.startsWith('http'));
 
  const getUrlDetails = (url: string) => {
    try {
      const parsed = new URL(url);
      const host = parsed.hostname.toLowerCase();
      if (host.includes('github.com')) {
        return { name: 'GitHub', color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' };
      }
      if (host.includes('linkedin.com')) {
        return { name: 'LinkedIn', color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' };
      }
      if (host.includes('twitter.com') || host.includes('x.com')) {
        return { name: 'Twitter / X', color: 'text-sky-400 bg-sky-500/10 border-sky-500/20' };
      }
      if (host.includes('medium.com') || host.includes('dev.to')) {
        return { name: 'Blog', color: 'text-pink-400 bg-pink-500/10 border-pink-500/20' };
      }
      if (host.includes('youtube.com') || host.includes('youtu.be')) {
        return { name: 'YouTube', color: 'text-red-400 bg-red-500/10 border-red-500/20' };
      }
      if (host.includes('facebook.com')) {
        return { name: 'Facebook', color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20' };
      }
      return { name: parsed.hostname.replace('www.', ''), color: 'text-zinc-400 bg-zinc-800/50 border-zinc-700/50' };
    } catch (_) {
      return { name: 'Link', color: 'text-zinc-400 bg-zinc-800/50 border-zinc-700/50' };
    }
  };
 
  const validExperience = (profile?.experience || []).filter(
    (exp: any) => exp.title && exp.title.toLowerCase() !== 'unknown' && exp.title.trim() !== ''
  );
  
  const validProjects = (profile?.projects || []).filter(
    (proj: any) => proj.name && proj.name.toLowerCase() !== 'unknown' && proj.name.trim() !== ''
  );
  
  const validPosts = (profile?.recent_posts || []).filter(
    (post: any) => post.content && post.content.trim() !== ''
  );
 
  const hasGithubData = !!(
    profile?.github_data && 
    ((profile.github_data.repositories_count ?? 0) > 0 || 
     (profile.github_data.top_repositories && profile.github_data.top_repositories.length > 0))
  );
 
  const validEducation = (profile?.education || []).filter(
    (edu: any) => 
      (edu.school && edu.school.toLowerCase() !== 'unknown' && edu.school.trim() !== '') || 
      (edu.degree && edu.degree.toLowerCase() !== 'unknown' && edu.degree.trim() !== '')
  );
 
  const validArticles = (profile?.articles || []).filter(
    (art: any) => art.title && art.title.toLowerCase() !== 'unknown' && art.title.trim() !== ''
  );
 
  const validAchievements = (profile?.achievements || []).filter(
    (ach: string) => ach && ach.trim() !== '' && ach.toLowerCase() !== 'unknown'
  );
 
  const validSkills = (profile?.skills || []).filter(
    (s: string) => s && s.trim() !== '' && s.toLowerCase() !== 'unknown'
  );
 
  const validTechStack = (profile?.tech_stack || []).filter(
    (s: string) => s && s.trim() !== '' && s.toLowerCase() !== 'unknown'
  );
 
  const validCommunities = (profile?.communities || []).filter(
    (s: string) => s && s.trim() !== '' && s.toLowerCase() !== 'unknown'
  );
 
  const hasContactInfo = !!(
    profile?.contact_info && 
    ((profile.contact_info.email && profile.contact_info.email.trim() !== '' && profile.contact_info.email.toLowerCase() !== 'unknown') ||
     (profile.contact_info.phone && profile.contact_info.phone.trim() !== '' && profile.contact_info.phone.toLowerCase() !== 'unknown'))
  );
 
  const hasMainContent = !!(
    validExperience.length > 0 ||
    validProjects.length > 0 ||
    validPosts.length > 0 ||
    hasGithubData ||
    validEducation.length > 0 ||
    validArticles.length > 0
  );

  const AvatarIcon = theme.avatarIcon;
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-5xl mx-auto space-y-10 pb-32"
    >
      {/* -------------------------------------------------------------
          Header / Bio Section (Curated Harmonic Gradients)
         ------------------------------------------------------------- */}
      <section className={cn(
        "bg-gradient-to-br border p-10 rounded-3xl backdrop-blur-3xl relative overflow-hidden transition-all duration-500",
        theme.bgGradient,
        theme.border,
        theme.glow
      )}>
        <div className="absolute top-0 right-0 p-8 opacity-10">
          <Sparkles size={120} className={theme.textAccent} />
        </div>
        <div className="relative z-10 flex flex-col md:flex-row gap-8 items-start">
          <div className={cn(
            "w-24 h-24 rounded-3xl flex items-center justify-center shadow-2xl transition-all duration-300 shrink-0",
            theme.avatarBg
          )}>
            <AvatarIcon size={44} className="text-white" />
          </div>
          <div className="space-y-4 max-w-2xl w-full">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className={cn("text-[10px] font-bold font-mono tracking-widest uppercase px-2 py-0.5 rounded border", theme.badge)}>
                  {theme.headerLabel}
                </span>
                {profileType === 'tech' && (
                  <span className="text-[10px] font-bold font-mono tracking-widest text-purple-400 bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded">
                    CYBER MATRIX ACTIVE
                  </span>
                )}
                {profileType === 'tech_normal' && (
                  <span className="text-[10px] font-bold font-mono tracking-widest text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded animate-pulse">
                    HYBRID INTEL AGGREGATED
                  </span>
                )}
                {profileType === 'sports' && (
                  <span className="text-[10px] font-bold font-mono tracking-widest text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                    TRACK RECORD VERIFIED
                  </span>
                )}
              </div>
              <h1 className="text-4xl font-extrabold text-white tracking-tight">{profile?.name || 'Unknown Profile'}</h1>
              {profile?.basic_info?.headline && (
                <p className={cn("text-lg font-semibold", theme.textAccent)}>{profile.basic_info.headline}</p>
              )}
              {profile?.location && (
                <div className="flex items-center gap-2 text-zinc-400 pt-1">
                  <MapPin size={16} className={theme.textAccent} />
                  <span className="text-sm">{profile.location}</span>
                </div>
              )}
            </div>
            {profile?.bio && (
              <p className="text-xl text-zinc-300 leading-relaxed font-sans">{profile.bio}</p>
            )}
            
            {/* Contact Details Display */}
            {hasContactInfo && (
              <div className="flex flex-wrap gap-4 text-sm pt-1">
                {profile?.contact_info?.email && profile.contact_info.email.trim() !== '' && profile.contact_info.email.toLowerCase() !== 'unknown' && (
                  <div className="flex items-center gap-2 text-zinc-300 bg-zinc-950 border border-zinc-800/80 px-3 py-1.5 rounded-xl hover:border-zinc-700 transition-colors">
                    <Mail size={14} className={theme.textAccent} />
                    <span className="font-mono text-xs">{profile.contact_info.email}</span>
                  </div>
                )}
                {profile?.contact_info?.phone && profile.contact_info.phone.trim() !== '' && profile.contact_info.phone.toLowerCase() !== 'unknown' && (
                  <div className="flex items-center gap-2 text-zinc-300 bg-zinc-950 border border-zinc-800/80 px-3 py-1.5 rounded-xl hover:border-zinc-700 transition-colors">
                    <Phone size={14} className="text-pink-400" />
                    <span className="font-mono text-xs">{profile.contact_info.phone}</span>
                  </div>
                )}
              </div>
            )}
 
            {profile?.basic_info?.source_url && (
              <div className="pt-1">
                <a 
                  href={profile.basic_info.source_url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className={cn(
                    "inline-flex items-center gap-1.5 text-xs transition-colors group/link",
                    theme.textAccent,
                    "opacity-80 hover:opacity-100"
                  )}
                >
                  <LinkIcon size={12} className="shrink-0 group-hover/link:translate-x-0.5 transition-transform" />
                  <span className="hover:underline truncate max-w-xs font-mono">
                    Source: {getSourceDisplay(profile.basic_info.source_url)}
                  </span>
                </a>
              </div>
            )}
            {profileUrls.length > 0 && (
              <div className="flex flex-wrap gap-2 pt-2">
                {profileUrls.slice(0, 8).map((link, i) => {
                  const details = getUrlDetails(link);
                  return (
                    <a key={i} href={link} target="_blank" rel="noopener noreferrer" className="px-3 py-1.5 bg-zinc-900/60 border border-zinc-800 hover:border-zinc-700 rounded-lg text-xs text-zinc-400 hover:text-white transition-all flex items-center gap-1.5">
                      <LinkIcon size={12} className="text-zinc-500" />
                      <span>{details.name}</span>
                    </a>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </section>
 
      {/* -------------------------------------------------------------
          Scope Restrictions Alerts (Out of Scope / Insufficient Data)
         ------------------------------------------------------------- */}
      {dossierMarkdown === "OUT_OF_SCOPE" && (
        <motion.div 
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-red-950/20 border border-red-500/30 p-8 rounded-3xl backdrop-blur-xl relative overflow-hidden shadow-[0_0_50px_rgba(239,68,68,0.1)]"
        >
          <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-red-500 via-orange-500 to-red-500" />
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center shrink-0">
              <ShieldAlert className="text-red-400" size={24} />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-bold text-red-200 tracking-wider font-mono">⚠️ SECURITY BRIEFING: TARGET OUT OF SCOPE</h3>
              <p className="text-sm text-red-300/80 leading-relaxed font-mono">
                The designated target entity does not match the active dossier scope rules. Deep categorical profile compilation has been aborted to preserve resource allocation bounds.
              </p>
            </div>
          </div>
        </motion.div>
      )}
 
      {dossierMarkdown === "INSUFFICIENT SPORTS DATA AVAILABLE" && (
        <motion.div 
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-amber-950/20 border border-amber-500/30 p-8 rounded-3xl backdrop-blur-xl relative overflow-hidden shadow-[0_0_50px_rgba(245,158,11,0.1)]"
        >
          <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-amber-500 via-yellow-500 to-amber-500" />
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center shrink-0">
              <ShieldAlert className="text-amber-400" size={24} />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-bold text-amber-200 tracking-wider font-mono">⚠️ SECURITY BRIEFING: INSUFFICIENT DATA</h3>
              <p className="text-sm text-amber-300/80 leading-relaxed font-mono">
                Classified RAG database scanning completed. Insufficient verified intelligence or metrics exist online to compile a full-fidelity category dossier. Default visual dashboard panels active.
              </p>
            </div>
          </div>
        </motion.div>
      )}
 
      {/* -------------------------------------------------------------
          Custom OSINT Dossiers (Bespoke Neon HUD / Executive Briefings)
         ------------------------------------------------------------- */}
      {dossierMarkdown && dossierMarkdown !== "OUT_OF_SCOPE" && dossierMarkdown !== "INSUFFICIENT SPORTS DATA AVAILABLE" && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            "border p-8 rounded-3xl relative overflow-hidden backdrop-blur-xl transition-all duration-500",
            theme.dossierBg,
            theme.glow
          )}
        >
          {/* Scanline and glowing top bar */}
          <div className={cn("absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r animate-pulse", theme.scanlineColor)} />
          <div className="absolute top-0 right-0 p-4 flex gap-1.5 opacity-40 shrink-0">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500" />
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-500" />
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
          </div>
          
          <div className={cn("flex items-center justify-between border-b pb-4 mb-6", theme.borderLight)}>
            <div className="flex items-center gap-3">
              <div className={cn("w-2.5 h-2.5 rounded-full animate-ping shrink-0", theme.progressColor.split(' ')[0])} />
              <span className="text-xs uppercase font-mono tracking-widest font-bold">
                {theme.dossierTitle}
              </span>
            </div>
            <span className="text-[10px] font-mono text-zinc-500 tracking-wider">
              EST. TRUST MATRIX: {Math.round((confidence?.score || 0) * 100)}% // SECURE_CHANNEL
            </span>
          </div>
 
          <div className="relative">
            {/* Custom Terminal/Serif Container */}
            <pre className={cn(
              "whitespace-pre-wrap font-mono text-[13px] leading-relaxed p-6 rounded-2xl border max-h-[550px] overflow-y-auto custom-scrollbar shadow-inner select-text transition-all duration-300",
              profileType === 'tech' ? 'bg-black text-cyan-400 border-cyan-500/10' :
              profileType === 'sports' ? 'bg-zinc-950/70 text-emerald-400 border-emerald-500/10' :
              profileType === 'tech_normal' ? 'bg-zinc-950/80 text-indigo-200 border-indigo-500/10 font-sans text-sm' :
              'bg-zinc-950/60 text-amber-200 border-amber-500/10 font-sans text-sm'
            )}>
              {dossierMarkdown}
            </pre>
            
            {/* Blinking cursor */}
            <div className={cn("flex items-center gap-2 mt-4 text-xs font-mono", theme.textMuted)}>
              <span>$ osint_engine --status=SYNTHESIS_COMPLETE --type={profileType.toUpperCase()}</span>
              <span className={cn("w-1.5 h-4 inline-block animate-pulse", theme.progressColor)} />
            </div>
          </div>
        </motion.div>
      )}
 
      {/* -------------------------------------------------------------
          Two-Column Dashboard Grid Layout (Theme-Sensitive Ordering)
         ------------------------------------------------------------- */}
      <div className={cn(
        "grid grid-cols-1 gap-8",
        hasMainContent ? "lg:grid-cols-3" : "max-w-2xl mx-auto"
      )}>
        {/* Main Content Column */}
        {hasMainContent && (
          <div className="lg:col-span-2 space-y-8">
            
            {/* 1. GitHub Open Source Card (Prioritized for Tech & Tech-Normal Professionals) */}
            {(profileType === 'tech' || profileType === 'tech_normal') && hasGithubData && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className={cn("p-8 rounded-3xl space-y-6 transition-all duration-300", theme.cardBg)}
              >
                <h3 className="text-xl font-bold text-white flex items-center gap-3">
                  <Code size={22} className={theme.titleIconColor} />
                  GitHub Open Source
                </h3>
                <div className="grid grid-cols-2 gap-4 pb-2">
                  <div className={cn("bg-zinc-950 border border-zinc-800/80 p-4 rounded-2xl text-center shadow-inner transition-all",
                    profileType === 'tech' ? 'hover:border-cyan-500/30' : 'hover:border-indigo-500/30'
                  )}>
                    <span className={cn("text-2xl font-black", theme.textAccent)}>{profile?.github_data?.repositories_count || 0}</span>
                    <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold pt-1 font-mono">Repositories</p>
                  </div>
                  <div className={cn("bg-zinc-950 border border-zinc-800/80 p-4 rounded-2xl text-center shadow-inner transition-all",
                    profileType === 'tech' ? 'hover:border-purple-500/30' : 'hover:border-blue-500/30'
                  )}>
                    <span className={cn("text-2xl font-black",
                      profileType === 'tech' ? 'text-purple-400' : 'text-blue-400'
                    )}>{profile?.github_data?.stars_received || 0}</span>
                    <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold pt-1 font-mono">Stars Received</p>
                  </div>
                </div>
                {profile?.github_data?.top_repositories && profile.github_data.top_repositories.length > 0 && (
                  <div className="space-y-3">
                    <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest font-mono">Top Repositories</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {profile.github_data.top_repositories.map((repo: any, i: number) => (
                        <a key={i} href={repo.link || "#"} target="_blank" rel="noopener noreferrer" className={cn(
                          "bg-zinc-950/60 border border-zinc-850 p-4 rounded-2xl flex items-center justify-between transition-all group",
                          profileType === 'tech' ? 'hover:border-cyan-500/30' : 'hover:border-indigo-500/30'
                        )}>
                          <div className="space-y-0.5 truncate pr-2">
                            <p className={cn("font-bold text-sm text-zinc-100 transition-colors truncate font-mono",
                              profileType === 'tech' ? 'group-hover:text-cyan-400' : 'group-hover:text-indigo-400'
                            )}>{repo.name}</p>
                            <p className="text-xs text-zinc-500 font-mono">⭐ {repo.stars || 0} stars</p>
                          </div>
                          <LinkIcon size={14} className={cn("text-zinc-500 shrink-0 transition-colors",
                            profileType === 'tech' ? 'group-hover:text-cyan-400' : 'group-hover:text-indigo-400'
                          )} />
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {/* 2. Experience Section */}
            {validExperience.length > 0 && (
              <div className={cn("p-8 rounded-3xl space-y-6 transition-all duration-300", theme.cardBg)}>
                <h3 className="text-xl font-bold text-white flex items-center gap-3">
                  {profileType === 'sports' ? (
                    <Trophy size={22} className="text-amber-400" />
                  ) : profileType === 'tech' ? (
                    <Terminal size={22} className="text-cyan-400" />
                  ) : (
                    <Briefcase size={22} className="text-blue-400" />
                  )}
                  {profileType === 'sports' ? "Club & Career History" : "Professional Experience"}
                </h3>
                <div className="space-y-8 relative before:absolute before:left-4 before:top-2 before:bottom-2 before:w-px before:bg-zinc-800">
                  {validExperience.map((exp, i) => (
                    <div key={i} className="relative pl-10">
                      <div className="absolute left-0 w-8 h-8 bg-zinc-950 border border-zinc-800 rounded-full flex items-center justify-center z-10">
                        <div className={cn("w-2.5 h-2.5 rounded-full", 
                          profileType === 'tech' ? 'bg-cyan-500' :
                          profileType === 'tech_normal' ? 'bg-indigo-500' :
                          profileType === 'sports' ? 'bg-emerald-500' : 'bg-amber-500'
                        )}></div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex flex-col md:flex-row md:items-center justify-between">
                          <h4 className="font-bold text-zinc-100">{exp.title}</h4>
                          {exp.period && exp.period.toLowerCase() !== 'unknown' && (
                            <span className="text-xs font-medium text-zinc-500 bg-zinc-800/50 px-2 py-1 rounded font-mono">{exp.period}</span>
                          )}
                        </div>
                        {exp.company && exp.company.toLowerCase() !== 'unknown' && (
                          <p className={cn("text-sm font-semibold", theme.textAccent)}>{exp.company}</p>
                        )}
                        {exp.description && exp.description.toLowerCase() !== 'unknown' && (
                          <p className="text-sm text-zinc-400 leading-relaxed font-sans">{exp.description}</p>
                        )}
                        {exp.source_url && (
                          <a 
                            href={exp.source_url} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="pt-2 inline-flex items-center gap-1.5 text-[11px] text-blue-400/70 hover:text-blue-300 transition-colors group/link font-mono"
                          >
                            <LinkIcon size={11} className="shrink-0 group-hover/link:translate-x-0.5 transition-transform" />
                            <span className="hover:underline truncate max-w-xs">
                              Source: {getSourceDisplay(exp.source_url)}
                            </span>
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
  
            {/* 3. Projects Section */}
            {validProjects.length > 0 && (
              <div className={cn("p-8 rounded-3xl space-y-6 transition-all duration-300", theme.cardBg)}>
                <h3 className="text-xl font-bold text-white flex items-center gap-3">
                  {profileType === 'sports' ? (
                    <TrendingUp size={22} className="text-emerald-400" />
                  ) : profileType === 'tech' ? (
                    <Code size={22} className="text-purple-400" />
                  ) : (
                    <Briefcase size={22} className="text-amber-400" />
                  )}
                  {profileType === 'sports' ? "Tournaments & Championships" : "Key Projects"}
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {validProjects.map((project, i) => (
                    <div key={i} className="bg-zinc-950 border border-zinc-800/80 p-6 rounded-2xl space-y-3 hover:border-zinc-700 transition-all group flex flex-col justify-between">
                      <div className="space-y-3">
                        <h4 className="font-bold text-zinc-100 group-hover:text-blue-400 transition-colors">{project.name}</h4>
                        {project.description && project.description.toLowerCase() !== 'unknown' && (
                          <p className="text-sm text-zinc-400 line-clamp-3 leading-relaxed font-sans">{project.description}</p>
                        )}
                      </div>
                      <div className="space-y-2 pt-2">
                        {project.source_url && (
                          <a 
                            href={project.source_url} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="inline-flex items-center gap-1.5 text-[11px] text-blue-400/70 hover:text-blue-300 transition-colors group/link font-mono"
                          >
                            <LinkIcon size={11} className="shrink-0 group-hover/link:translate-x-0.5 transition-transform" />
                            <span className="hover:underline truncate max-w-full">
                              Source: {getSourceDisplay(project.source_url)}
                            </span>
                          </a>
                        )}
                        {project.technologies && project.technologies.length > 0 && (
                          <div className="space-y-1 pt-1">
                            {profileType === 'sports' && (
                              <span className="text-[9px] uppercase tracking-widest font-black text-amber-500/80 block font-mono">Performance Stats</span>
                            )}
                            <div className="flex flex-wrap gap-1.5">
                              {project.technologies.map((tech: string, j: number) => (
                                <span key={j} className="text-[9px] uppercase tracking-wider font-bold text-zinc-400 bg-zinc-900 px-2 py-0.5 rounded font-mono">
                                  {tech}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
  
            {/* 4. Recent Activity Section */}
            {validPosts.length > 0 && (
              <div className={cn("p-8 rounded-3xl space-y-6 transition-all duration-300", theme.cardBg)}>
                <h3 className="text-xl font-bold text-white flex items-center gap-3">
                  <MessageSquare size={22} className="text-amber-400" />
                  Recent Activity
                </h3>
                <div className="space-y-4">
                  {validPosts.map((post, i) => (
                    <div key={i} className="bg-zinc-950 border border-zinc-800/80 p-6 rounded-2xl space-y-3">
                      <div className="flex items-center justify-between">
                         <div className="flex items-center gap-2 text-zinc-500">
                           <Clock size={12} className="text-amber-400/80" />
                           <span className="text-[10px] uppercase tracking-widest font-bold font-mono">{post.date || 'Recent Post'}</span>
                         </div>
                         {post.link && (
                           <a href={post.link} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 transition-colors">
                             <LinkIcon size={14} />
                           </a>
                         )}
                      </div>
                      <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap font-sans">{post.content}</p>
                      {post.source_url && (
                        <a 
                          href={post.source_url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="pt-1 inline-flex items-center gap-1.5 text-[11px] text-blue-400/70 hover:text-blue-300 transition-colors group/link font-mono"
                        >
                          <LinkIcon size={11} className="shrink-0 group-hover/link:translate-x-0.5 transition-transform" />
                          <span className="hover:underline truncate max-w-full">
                            Source: {getSourceDisplay(post.source_url)}
                          </span>
                        </a>
                      )}
                      
                      {post.summary && (
                        <div className="bg-blue-500/5 border border-blue-500/10 p-3 rounded-xl flex gap-3">
                          <Brain size={16} className="text-blue-400 shrink-0 mt-0.5" />
                          <div className="space-y-1">
                            <p className="text-[10px] font-bold text-blue-400 uppercase tracking-widest font-mono">AI Summary</p>
                            <p className="text-xs text-blue-200/80 italic leading-relaxed font-sans">{post.summary}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
  
            {/* 5. Legacy GitHub display (Only for non-tech & non-tech_normal profiles if data exists) */}
            {profileType !== 'tech' && profileType !== 'tech_normal' && hasGithubData && (
              <div className={cn("p-8 rounded-3xl space-y-6 transition-all duration-300", theme.cardBg)}>
                <h3 className="text-xl font-bold text-white flex items-center gap-3">
                  <Code size={22} className="text-emerald-400" />
                  GitHub Open Source
                </h3>
                <div className="grid grid-cols-2 gap-4 pb-2">
                  <div className="bg-zinc-950 border border-zinc-800/80 p-4 rounded-2xl text-center">
                    <span className="text-2xl font-black text-emerald-400">{profile?.github_data?.repositories_count || 0}</span>
                    <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold pt-1 font-mono">Repositories</p>
                  </div>
                  <div className="bg-zinc-950 border border-zinc-800/80 p-4 rounded-2xl text-center">
                    <span className="text-2xl font-black text-amber-400">{profile?.github_data?.stars_received || 0}</span>
                    <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold pt-1 font-mono">Stars Received</p>
                  </div>
                </div>
                {profile?.github_data?.top_repositories && profile.github_data.top_repositories.length > 0 && (
                  <div className="space-y-3">
                    <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest font-mono">Top Repositories</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {profile.github_data.top_repositories.map((repo: any, i: number) => (
                        <a key={i} href={repo.link || "#"} target="_blank" rel="noopener noreferrer" className="bg-zinc-950/60 border border-zinc-850 hover:border-zinc-700 p-4 rounded-2xl flex items-center justify-between transition-all group">
                          <div className="space-y-0.5 truncate pr-2">
                            <p className="font-bold text-sm text-zinc-100 group-hover:text-emerald-400 transition-colors truncate font-mono">{repo.name}</p>
                            <p className="text-xs text-zinc-500 font-mono">⭐ {repo.stars || 0} stars</p>
                          </div>
                          <LinkIcon size={14} className="text-zinc-500 group-hover:text-white shrink-0" />
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
  
            {/* 6. Education Section */}
            {validEducation.length > 0 && (
              <div className={cn("p-8 rounded-3xl space-y-6 transition-all duration-300", theme.cardBg)}>
                <h3 className="text-xl font-bold text-white flex items-center gap-3">
                  <GraduationCap size={22} className="text-indigo-400" />
                  Education & Credentials
                </h3>
                <div className="space-y-4">
                  {validEducation.map((edu: any, i: number) => (
                    <div key={i} className="bg-zinc-950 border border-zinc-800/80 p-4 rounded-2xl flex justify-between items-start gap-4 hover:border-zinc-750 transition-colors">
                      <div className="space-y-1">
                        {edu.degree && edu.degree.toLowerCase() !== 'unknown' && (
                          <h4 className="font-bold text-sm text-zinc-100">{edu.degree}</h4>
                        )}
                        {edu.school && edu.school.toLowerCase() !== 'unknown' && (
                          <p className="text-xs text-indigo-400 font-semibold">{edu.school}</p>
                        )}
                        {edu.source_url && (
                          <a 
                            href={edu.source_url} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="pt-2 inline-flex items-center gap-1.5 text-[11px] text-blue-400/70 hover:text-blue-300 transition-colors group/link font-mono"
                          >
                            <LinkIcon size={11} className="shrink-0 group-hover/link:translate-x-0.5 transition-transform" />
                            <span className="hover:underline truncate max-w-full">
                              Source: {getSourceDisplay(edu.source_url)}
                            </span>
                          </a>
                        )}
                      </div>
                      {edu.period && edu.period.toLowerCase() !== 'unknown' && (
                        <span className="text-[10px] text-zinc-500 bg-zinc-900 px-2 py-0.5 rounded font-mono shrink-0">{edu.period}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
  
            {/* 7. Articles & Publications Section */}
            {validArticles.length > 0 && (
              <div className={cn("p-8 rounded-3xl space-y-6 transition-all duration-300", theme.cardBg)}>
                <h3 className="text-xl font-bold text-white flex items-center gap-3">
                  <BookOpen size={22} className="text-pink-400" />
                  Featured Articles & Publications
                </h3>
                <div className="space-y-4">
                  {validArticles.map((art: any, i: number) => (
                    <div key={i} className="bg-zinc-950 border border-zinc-800/80 p-6 rounded-2xl space-y-3 hover:border-zinc-750 transition-colors">
                      <div className="flex justify-between items-start gap-4">
                        <h4 className="font-bold text-sm text-zinc-100 leading-snug">{art.title}</h4>
                        {art.date && art.date.toLowerCase() !== 'unknown' && (
                          <span className="text-[9px] text-zinc-500 bg-zinc-900 px-2 py-0.5 rounded font-mono shrink-0">{art.date}</span>
                        )}
                      </div>
                      {art.publisher && art.publisher.toLowerCase() !== 'unknown' && (
                        <p className="text-xs text-pink-400 font-semibold">{art.publisher}</p>
                      )}
                      {art.summary && art.summary.toLowerCase() !== 'unknown' && (
                        <p className="text-xs text-zinc-400 leading-relaxed font-sans">{art.summary}</p>
                      )}
                      {art.source_url && (
                        <a 
                          href={art.source_url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="pt-2 inline-flex items-center gap-1.5 text-[11px] text-blue-400/70 hover:text-blue-300 transition-colors group/link font-mono"
                        >
                          <LinkIcon size={11} className="shrink-0 group-hover/link:translate-x-0.5 transition-transform" />
                          <span className="hover:underline truncate max-w-full">
                            Source: {getSourceDisplay(art.source_url)}
                          </span>
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
 
        {/* -------------------------------------------------------------
            Sidebar Column (Curated harmoniously with dynamic info)
           ------------------------------------------------------------- */}
        <div className={cn("space-y-8", !hasMainContent && "w-full")}>
          
          {/* 1. AI Insights */}
          <div className={cn("p-8 rounded-3xl space-y-6 transition-all duration-300", theme.cardBg)}>
            <h3 className="text-xl font-bold text-white flex items-center gap-3">
              <TrendingUp size={22} className={cn(
                profileType === 'sports' ? 'text-emerald-400' :
                profileType === 'tech' ? 'text-purple-400' :
                profileType === 'tech_normal' ? 'text-indigo-400' : 'text-amber-400'
              )} />
              AI Insights
            </h3>
            <div className="space-y-6">
              {insights?.summary && (
                <div className="space-y-2">
                  <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest font-mono">Summary</p>
                  <p className="text-sm text-zinc-350 leading-relaxed font-sans">{insights.summary}</p>
                </div>
              )}
              {insights?.key_strengths && insights.key_strengths.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest font-mono">Key Strengths</p>
                  <div className="flex flex-wrap gap-2">
                    {insights.key_strengths.map((s, i) => (
                      <span key={i} className={cn(
                        "text-xs px-3 py-1.5 rounded-full font-sans border",
                        profileType === 'sports' ? 'text-emerald-300 bg-emerald-500/10 border-emerald-500/20' :
                        profileType === 'tech' ? 'text-purple-300 bg-purple-500/10 border-purple-500/20' :
                        profileType === 'tech_normal' ? 'text-indigo-300 bg-indigo-500/10 border-indigo-500/20' :
                        'text-amber-300 bg-amber-500/10 border-amber-500/20'
                      )}>{s}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
 
          {/* 2. Connected Social and OSINT Profiles */}
          {profileUrls.length > 0 && (
            <div className={cn("p-8 rounded-3xl space-y-6 transition-all duration-300", theme.cardBg)}>
              <h3 className="text-xl font-bold text-white flex items-center gap-3">
                <Globe size={22} className="text-cyan-400" />
                Connected Profiles
              </h3>
              <p className="text-xs text-zinc-400 leading-relaxed font-sans">
                Aggregated public profiles and social footprints discovered across the web.
              </p>
              <div className="space-y-3">
                {profileUrls.map((url, idx) => {
                  const details = getUrlDetails(url);
                  return (
                    <a
                      key={idx}
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-3.5 bg-zinc-950 border border-zinc-900 hover:border-zinc-700 rounded-2xl transition-all group hover:bg-zinc-900/20"
                    >
                      <div className="flex items-center gap-3 truncate pr-2">
                        <span className={cn("px-2 py-1 text-[10px] font-bold uppercase rounded-lg border font-mono shrink-0", details.color)}>
                          {details.name}
                        </span>
                        <span className="text-xs text-zinc-400 group-hover:text-zinc-200 transition-colors truncate font-mono">
                          {url.replace(/^https?:\/\/(www\.)?/, '')}
                        </span>
                      </div>
                      <ExternalLink size={14} className="text-zinc-500 group-hover:text-white shrink-0 transition-colors" />
                    </a>
                  );
                })}
              </div>
            </div>
          )}
 
          {/* 3. Key Achievements / Awards (Styled beautifully) */}
          {validAchievements.length > 0 && (
            <div className={cn("p-8 rounded-3xl space-y-4 transition-all duration-300", theme.cardBg)}>
              <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest font-mono">Key Achievements</p>
              <ul className="space-y-3">
                {validAchievements.map((ach, i) => (
                  <li key={i} className="text-xs text-zinc-300 flex items-start gap-2.5 leading-relaxed font-sans">
                    <span className="text-amber-400 shrink-0 mt-0.5">🏆</span>
                    <span>{ach}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
 
          {/* 4. Core Skills & Attributes */}
          {validSkills.length > 0 && (
            <div className={cn("p-8 rounded-3xl space-y-4 transition-all duration-300", theme.cardBg)}>
              <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest font-mono">
                {profileType === 'sports' ? "Athletic Attributes" : "Core Competencies"}
              </p>
              <div className="flex flex-wrap gap-2">
                {validSkills.map((skill, i) => (
                  <span key={i} className="text-xs font-medium text-zinc-300 bg-zinc-950 px-3 py-1.5 rounded-lg border border-zinc-800">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
 
          {/* 5. Tech Stack (Matrix look for Tech Targets, Play Style for Athletes) */}
          {validTechStack.length > 0 && (
            <div className={cn("p-8 rounded-3xl space-y-4 transition-all duration-300", theme.cardBg)}>
              <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest flex items-center gap-2 font-mono">
                <Sparkles size={14} className={theme.textAccent} />
                {profileType === 'sports' ? "Specialties & Play Style" : "Tech Matrix & Languages"}
              </p>
              <div className="flex flex-wrap gap-2">
                {validTechStack.map((tech, i) => (
                  <span key={i} className={cn(
                    "text-xs font-semibold px-3 py-1.5 rounded-lg border font-mono",
                    profileType === 'sports' ? 'text-emerald-400 bg-emerald-500/5 border-emerald-500/20' :
                    profileType === 'tech' ? 'text-cyan-400 bg-cyan-500/5 border-cyan-500/20' :
                    profileType === 'tech_normal' ? 'text-indigo-400 bg-indigo-500/5 border-indigo-500/20' :
                    'text-amber-300 bg-amber-500/5 border-amber-500/20'
                  )}>
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}
 
          {/* 6. Communities & Affiliations */}
          {validCommunities.length > 0 && (
            <div className={cn("p-8 rounded-3xl space-y-4 transition-all duration-300", theme.cardBg)}>
              <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest flex items-center gap-2 font-mono">
                <Globe size={14} className="text-indigo-400" />
                {profileType === 'sports' ? "Sports Affiliations" : "Professional Communities"}
              </p>
              <div className="flex flex-wrap gap-2">
                {validCommunities.map((comm, i) => (
                  <span key={i} className="text-xs font-medium text-indigo-350 bg-indigo-500/5 border border-indigo-500/10 px-3 py-1.5 rounded-lg">
                    {comm}
                  </span>
                ))}
              </div>
            </div>
          )}
 
          {/* 7. Confidence Score Tracker */}
          <div className="bg-blue-600/5 border border-blue-600/10 p-6 rounded-3xl space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-blue-400 flex items-center gap-2 font-mono">
                <ShieldCheck size={18} />
                Confidence
              </span>
              <span className="text-xl font-black text-blue-300 font-mono">{Math.round((confidence?.score || 0) * 100)}%</span>
            </div>
            <div className="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${(confidence?.score || 0) * 100}%` }}
                className="h-full bg-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.5)]"
              />
            </div>
            {confidence?.justification && (
              <p className="text-[10px] text-zinc-500 italic leading-tight font-sans">
                {confidence.justification}
              </p>
            )}
          </div>
        </div>
      </div>
 
      {/* -------------------------------------------------------------
          Sources Footer
         ------------------------------------------------------------- */}
      {profile?.sources_used && profile.sources_used.length > 0 && (
        <div className="bg-zinc-950/40 border border-zinc-900 p-6 rounded-2xl flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-zinc-500 max-w-5xl mx-auto">
          <span className="font-medium tracking-wide text-zinc-400 font-mono">Autonomous Sources Aggregated:</span>
          <div className="flex flex-wrap gap-2 justify-center">
            {profile.sources_used.map((source, i) => {
              let hostname = "Source Link";
              try {
                hostname = new URL(source).hostname;
              } catch (_) {}
              return (
                <a key={i} href={source} target="_blank" rel="noopener noreferrer" className="px-3 py-1.5 bg-zinc-900/60 hover:bg-zinc-850 hover:text-white border border-zinc-800/80 hover:border-zinc-700 rounded-lg transition-colors font-mono truncate max-w-[200px]">
                  {hostname}
                </a>
              );
            })}
          </div>
        </div>
      )}
    </motion.div>
  );
};
