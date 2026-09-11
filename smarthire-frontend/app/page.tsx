"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Bot,
  Flag,
  Sparkles,
  User,
  Zap,
  Quote,
} from "lucide-react";

const testimonials = [
  { initials: "MC", name: "Maya Chen", role: "VP People, Northstar", rating: 5, accent: "#22d3ee", quote: "SmartHire turned a week of resume triage into one clear afternoon. The signal is remarkably easy to trust." },
  { initials: "JR", name: "Jon Rivera", role: "Talent Lead, Meridian", rating: 5, accent: "#34d399", quote: "Our recruiters spend less time sorting and more time having the conversations that actually move candidates forward." },
  { initials: "AS", name: "Amara Singh", role: "Founder, Loom Labs", rating: 4, accent: "#f472b6", quote: "The explainable scores gave our hiring panel a shared language, without hiding the human judgment in the process." },
  { initials: "DK", name: "David Kim", role: "COO, Atlas Works", rating: 5, accent: "#818cf8", quote: "We finally have a clean view of candidate quality across every role, not just a pile of disconnected spreadsheets." },
];

const weeklyBars = [
  { day: "M", value: 64, color: "from-indigo-500 to-indigo-400" },
  { day: "T", value: 71, color: "from-indigo-500 to-cyan-400" },
  { day: "W", value: 68, color: "from-indigo-500 to-cyan-400" },
  { day: "T", value: 79, color: "from-cyan-500 to-cyan-300" },
  { day: "F", value: 84, color: "from-cyan-500 to-emerald-300" },
  { day: "S", value: 91, color: "from-cyan-400 to-emerald-300" },
  { day: "S", value: 96, color: "from-emerald-400 to-emerald-300" },
];

const raceMilestones = ["Upload", "Review", "Fix issues", "Validate", "Ready"];

function SpeedRaceTrack({
  accent,
  complete,
  icon: Icon,
  label,
  progress,
  status,
  time,
}: {
  accent: "red" | "green";
  complete?: boolean;
  icon: typeof User;
  label: string;
  progress: number;
  status: string;
  time: string;
}) {
  const isGreen = accent === "green";
  const accentText = isGreen ? "text-emerald-300" : "text-red-300";
  const accentBorder = isGreen ? "border-emerald-400/25" : "border-red-400/25";
  const badgeBackground = isGreen ? "bg-emerald-400/10" : "bg-red-400/10";
  const fill = isGreen ? "from-emerald-400 to-teal-300" : "from-red-400 to-rose-300";
  const glow = isGreen ? "rgba(52,211,153,0.55)" : "rgba(248,113,113,0.45)";

  return (
    <div className={`rounded-2xl border ${accentBorder} bg-[#111319] p-5 sm:p-6`}>
      <div className="flex items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${badgeBackground} ${accentText}`}>
            <Icon className="h-5 w-5" />
          </div>
          <span className="text-base font-semibold text-[#eef0f5]">{label}</span>
        </div>
        {complete && <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-2.5 py-1 font-mono text-[10px] tracking-[0.14em] text-emerald-300">COMPLETE</span>}
      </div>

      <div className="relative mt-7 h-3 rounded-full bg-white/[0.08]">
        <div className={`h-full rounded-full bg-gradient-to-r ${fill} transition-[width] duration-75`} style={{ width: `${progress * 100}%`, boxShadow: `0 0 14px ${glow}` }} />
        <span className="absolute top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white/80 bg-white" style={{ left: `${Math.max(progress * 100, 1)}%`, boxShadow: `0 0 12px 3px ${glow}` }} />
      </div>

      <div className="mt-3 grid grid-cols-5 gap-2">
        {raceMilestones.map((milestone, index) => {
          const milestoneProgress = index / (raceMilestones.length - 1);
          const passed = progress >= milestoneProgress;
          return <span key={milestone} className={`text-center font-mono text-[9px] leading-4 transition-colors duration-300 sm:text-[10px] ${passed ? accentText : "text-[#8b90a3]"}`}>{milestone}</span>;
        })}
      </div>

      <div className="mt-5 flex items-center justify-between gap-4 border-t border-white/[0.08] pt-4">
        <span className={`text-xs ${complete ? "text-emerald-300" : "text-[#8b90a3]"}`}>{status}</span>
        <span className={`shrink-0 font-mono text-sm font-semibold ${accentText}`}>{time}</span>
      </div>
    </div>
  );
}

function SpeedRaceComparison() {
  const [elapsed, setElapsed] = useState(0);
  const cycleDuration = 8000;
  const aiDuration = 5500;

  useEffect(() => {
    let frameId: number;
    const startedAt = performance.now();
    const animate = (now: number) => {
      setElapsed((now - startedAt) % cycleDuration);
      frameId = requestAnimationFrame(animate);
    };
    frameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameId);
  }, []);

  const aiProgress = Math.min(elapsed / aiDuration, 1);
  const manualProgress = Math.min(elapsed / (cycleDuration * 28), 0.08);
  const aiComplete = aiProgress >= 1;
  const manualHours = (elapsed / 3000).toFixed(1);
  const aiMinutes = (aiProgress * 6).toFixed(1);

  return (
    <section className="relative mx-auto max-w-7xl px-6 pb-24 pt-10 lg:px-8">
      <div className="mb-9 max-w-3xl">
        <p className="font-mono text-[11px] tracking-[0.24em] text-indigo-300">HOW IT WORKS</p>
        <h2 className="mt-3 text-3xl font-bold tracking-tight text-[#eef0f5] sm:text-4xl">The same dataset. Two very different afternoons.</h2>
        <p className="mt-4 text-base leading-7 text-[#8b90a3]">Watch a 200K-row file move through manual review versus DataMedic, side by side.</p>
      </div>

      <div className="space-y-4">
        <SpeedRaceTrack accent="red" icon={User} label="Manual review" progress={manualProgress} status="analyst hours spent, still in progress" time={`${manualHours} hrs`} />
        <SpeedRaceTrack accent="green" complete={aiComplete} icon={Bot} label="DataMedic AI" progress={aiProgress} status={aiComplete ? "done — ready for modeling" : "cleaning in progress"} time={`${aiMinutes} min`} />
      </div>

      <div className="mt-7 flex items-center justify-center gap-2 font-mono text-[10px] tracking-[0.12em] text-emerald-300 sm:text-xs">
        <Flag className="h-4 w-4" />
        <span>DataMedic finishes ~30x faster on the same workload</span>
      </div>
    </section>
  );
}

function DatasetHealthPanel() {
  const [score, setScore] = useState(0);

  useEffect(() => {
    const timer = window.setTimeout(() => setScore(96), 180);
    return () => window.clearTimeout(timer);
  }, []);

  const circumference = 2 * Math.PI * 44;
  return (
    <div className="rounded-[24px] border border-white/[0.08] bg-[#111319] p-6 sm:p-7">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-mono text-[10px] tracking-[0.22em] text-cyan-300">WEEKLY TREND</p>
          <h3 className="mt-2 text-xl font-semibold text-[#eef0f5]">Dataset health score</h3>
        </div>
        <span className="flex items-center gap-1.5 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2.5 py-1 font-mono text-[10px] tracking-[0.12em] text-emerald-300"><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-300" /> LIVE</span>
      </div>
      <div className="mt-7 flex items-center gap-5">
        <div className="relative h-32 w-32 shrink-0">
          <svg className="h-full w-full -rotate-90" viewBox="0 0 100 100" aria-label="Dataset health score 96 out of 100">
            <defs><linearGradient id="health-ring" x1="0" x2="1"><stop stopColor="#6366f1" /><stop offset="0.55" stopColor="#22d3ee" /><stop offset="1" stopColor="#34d399" /></linearGradient></defs>
            <circle cx="50" cy="50" r="44" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
            <circle cx="50" cy="50" r="44" fill="none" stroke="url(#health-ring)" strokeLinecap="round" strokeWidth="8" strokeDasharray={circumference} strokeDashoffset={circumference * (1 - score / 100)} style={{ transition: "stroke-dashoffset 1.2s ease-out" }} />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center"><span className="font-mono text-3xl text-[#eef0f5]">{score}</span><span className="font-mono text-[9px] text-[#8b90a3]">/ 100</span></div>
        </div>
        <p className="max-w-[220px] text-sm leading-6 text-[#8b90a3]">Up <span className="font-mono text-emerald-300">+34%</span> vs last week, driven by fewer duplicate and null-value flags.</p>
      </div>
      <div className="mt-8 flex h-24 items-end justify-between gap-2 border-b border-white/[0.08] px-1">
        {weeklyBars.map((bar, index) => <div key={`${bar.day}-${index}`} className="flex h-full flex-1 flex-col items-center justify-end gap-2"><div className={`w-full max-w-7 rounded-t-sm bg-gradient-to-t ${bar.color} transition-all duration-700`} style={{ height: `${score ? bar.value : 0}%`, transitionDelay: `${index * 90}ms` }} /><span className="font-mono text-[9px] text-[#8b90a3]">{bar.day}</span></div>)}
      </div>
    </div>
  );
}

function TestimonialsPanel() {
  const [active, setActive] = useState(0);
  const testimonial = testimonials[active];

  useEffect(() => {
    const timer = window.setInterval(() => setActive((current) => (current + 1) % testimonials.length), 4200);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="flex min-h-[350px] flex-col rounded-[24px] border border-white/[0.08] bg-[#111319] p-6 sm:p-7">
      <div className="flex items-center justify-between"><div><p className="font-mono text-[10px] tracking-[0.22em] text-cyan-300">WHAT TEAMS SAY</p><h3 className="mt-2 text-xl font-semibold text-[#eef0f5]">Built for better decisions</h3></div><Quote className="h-8 w-8 text-indigo-400/70" /></div>
      <div key={testimonial.name} className="animate-testimonial-in flex flex-1 flex-col justify-center">
        <div className="mb-4 flex gap-1" aria-label={`${testimonial.rating} out of 5 stars`}>{[0, 1, 2, 3, 4].map((star) => <span key={star} className="text-lg" style={{ color: star < testimonial.rating ? testimonial.accent : "#3b3e49" }}>★</span>)}</div>
        <blockquote className="max-w-xl text-xl leading-8 text-[#eef0f5] sm:text-2xl">“{testimonial.quote}”</blockquote>
        <div className="mt-6 flex items-center gap-3"><div className="flex h-10 w-10 items-center justify-center rounded-full font-mono text-xs font-semibold text-[#0a0b12]" style={{ backgroundColor: testimonial.accent }}>{testimonial.initials}</div><div><p className="text-sm font-semibold text-[#eef0f5]">{testimonial.name}</p><p className="mt-0.5 text-xs text-[#8b90a3]">{testimonial.role}</p></div></div>
      </div>
      <div className="flex gap-2">{testimonials.map((item, index) => <span key={item.name} className={`h-1.5 rounded-full transition-all duration-500 ${index === active ? "w-8" : "w-1.5 bg-white/20"}`} style={index === active ? { backgroundColor: item.accent } : undefined} />)}</div>
    </div>
  );
}

export default function HomePage() {
  return (
    <main className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.35),transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(168,85,247,0.3),transparent_25%)]" />
      <div className="pointer-events-none absolute inset-0 opacity-80">
        <div className="hero-orb hero-orb-one" />
        <div className="hero-orb hero-orb-two" />
        {[...Array(18)].map((_, index) => (
          <span
            key={index}
            className="floating-dot"
            style={{
              left: `${(index * 12 + 8) % 100}%`,
              top: `${(index * 17 + 10) % 100}%`,
              animationDelay: `${index * 0.4}s`,
              animationDuration: `${7 + index * 0.6}s`,
            }}
          />
        ))}
      </div>

      <section className="relative mx-auto max-w-7xl px-6 pb-24 pt-20 lg:px-8">
        <div className="grid items-center gap-14 lg:grid-cols-[1.08fr_0.92fr]">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="relative z-10"
          >
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-200 backdrop-blur-md">
              <Sparkles className="h-4 w-4" />
              AI-powered hiring intelligence
            </div>

            <h1 className="max-w-xl text-5xl font-black tracking-[-0.06em] text-white sm:text-6xl lg:text-7xl">
              AI-Powered Resume Screening & Ranking
            </h1>

            <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">
              Discover top candidates faster with automated resume parsing, skill extraction, and hiring score insights designed for modern recruiting teams.
            </p>

            <div className="mt-8 flex flex-col gap-4 sm:flex-row">
              <Link
                href="/upload"
                className="inline-flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-cyan-500 via-blue-500 to-violet-500 px-6 py-3.5 text-base font-semibold text-white shadow-[0_0_30px_rgba(34,211,238,0.35)] transition duration-200 hover:scale-[1.02]"
              >
                Try Now
                <ArrowRight className="h-4 w-4" />
              </Link>
              <a
                href="#features"
                className="inline-flex items-center justify-center rounded-full border border-white/15 bg-white/5 px-6 py-3.5 text-base font-semibold text-slate-100 backdrop-blur-md transition hover:border-cyan-400/50 hover:bg-white/10"
              >
                Explore Platform
              </a>
            </div>

            <div className="mt-12 grid gap-5 sm:grid-cols-3">
              {[
                { value: "92%", label: "Match Accuracy" },
                { value: "3x", label: "Faster Review" },
                { value: "24/7", label: "AI Screening" },
              ].map((item) => (
                <div key={item.label} className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                  <div className="text-2xl font-bold text-white">{item.value}</div>
                  <div className="mt-1 text-sm text-slate-400">{item.label}</div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="relative z-10"
          >
            <div className="rounded-[30px] border border-white/10 bg-slate-900/60 p-5 shadow-[0_35px_120px_rgba(59,130,246,0.28)] backdrop-blur-2xl">
              <div className="rounded-[24px] border border-cyan-400/20 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-5">
                <div className="mb-4 flex items-center justify-between text-sm text-slate-300">
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-cyan-300" />
                    Candidate IQ
                  </div>
                  <span className="rounded-full border border-emerald-400/30 bg-emerald-500/10 px-2 py-1 text-xs font-medium text-emerald-300">
                    Live
                  </span>
                </div>

                <div className="space-y-5">
                  {[
                    { label: "Skill Match", value: 94, color: "cyan" },
                    { label: "Experience Fit", value: 88, color: "violet" },
                    { label: "Leadership Fit", value: 91, color: "green" },
                  ].map((item) => (
                    <div key={item.label}>
                      <div className="mb-2 flex items-center justify-between text-sm text-slate-300">
                        <span>{item.label}</span>
                        <span className="font-semibold text-white">{item.value}%</span>
                      </div>
                      <div className="h-2.5 rounded-full bg-slate-800">
                        <div
                          className={`h-full rounded-full ${
                            item.color === "cyan"
                              ? "bg-gradient-to-r from-cyan-400 to-blue-500"
                              : item.color === "violet"
                                ? "bg-gradient-to-r from-violet-400 to-purple-500"
                                : "bg-gradient-to-r from-emerald-400 to-teal-500"
                          }`}
                          style={{ width: `${item.value}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center gap-2 text-sm text-slate-300">
                    <Sparkles className="h-4 w-4 text-violet-300" />
                    Top strengths
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {['Python', 'AI', 'Product', 'Leadership', 'Analytics'].map((tag) => (
                      <span key={tag} className="rounded-full border border-white/10 bg-slate-800/80 px-2.5 py-1 text-xs text-slate-100">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <SpeedRaceComparison />

      <section id="features" className="relative mx-auto grid max-w-7xl gap-6 px-6 pb-24 lg:grid-cols-2 lg:px-8">
        <DatasetHealthPanel />
        <TestimonialsPanel />
      </section>
    </main>
  );
}
