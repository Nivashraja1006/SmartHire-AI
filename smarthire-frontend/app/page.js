"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Bot, BrainCircuit, FileText, ShieldCheck, Sparkles, Zap } from "lucide-react";

const features = [
  {
    icon: FileText,
    title: "Resume Analysis",
    description: "Parse skills, experience, and certifications in seconds using AI-driven ranking.",
  },
  {
    icon: BrainCircuit,
    title: "Smart Matching",
    description: "Compare candidate profiles against job requirements with precision and fairness.",
  },
  {
    icon: ShieldCheck,
    title: "Explainable Insights",
    description: "Understand the score drivers behind every hiring recommendation and decision.",
  },
];

const metrics = [
  { value: "92%", label: "Match Accuracy" },
  { value: "3x", label: "Faster Screening" },
  { value: "24/7", label: "AI Recruiting" },
];

export default function HomePage() {
  return (
    <main className="relative overflow-hidden bg-slate-950 text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.15),transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(168,85,247,0.2),transparent_30%)]" />

      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="heartbeat-wave" />
        {[...Array(22)].map((_, index) => (
          <span
            key={index}
            className="floating-particle"
            style={{
              left: `${(index * 13) % 100}%`,
              top: `${(index * 17) % 100}%`,
              animationDelay: `${index * 0.4}s`,
              animationDuration: `${8 + index * 0.6}s`,
            }}
          />
        ))}
      </div>

      <section className="relative mx-auto max-w-7xl px-5 pb-24 pt-16 sm:px-6 lg:px-8 lg:pt-20">
        <div className="grid items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="relative z-10"
          >
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-500/10 px-3 py-1.5 text-sm text-cyan-200 backdrop-blur-md">
              <Sparkles className="h-4 w-4" />
              AI-powered hiring intelligence
            </div>

            <h1 className="max-w-xl text-5xl font-black tracking-[-0.05em] text-white sm:text-6xl">
              Hire Smarter with AI
            </h1>
            <p className="mt-6 max-w-lg text-lg leading-8 text-slate-300">
              Upload resumes. Get instant ranking using AI. Transform hiring from slow and manual into precise, fair, and data-driven decisions.
            </p>

            <div className="mt-8 flex flex-col gap-4 sm:flex-row">
              <Link
                href="/upload"
                className="inline-flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-cyan-500 to-violet-500 px-6 py-3.5 text-base font-semibold text-white shadow-[0_0_30px_rgba(45,212,191,0.35)] transition hover:scale-[1.02]"
              >
                Upload Resume
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/results"
                className="inline-flex items-center justify-center gap-2 rounded-full border border-white/15 bg-white/5 px-6 py-3.5 text-base font-semibold text-slate-100 backdrop-blur-md transition hover:border-cyan-400/50 hover:bg-white/10"
              >
                Start Screening
              </Link>
            </div>

            <div className="mt-12 grid max-w-lg gap-6 sm:grid-cols-3">
              {metrics.map((metric) => (
                <div key={metric.label} className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                  <div className="text-2xl font-bold text-white">{metric.value}</div>
                  <div className="mt-1 text-sm text-slate-400">{metric.label}</div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="relative z-10"
          >
            <div className="rounded-[32px] border border-white/10 bg-slate-900/60 p-5 shadow-[0_35px_120px_rgba(59,130,246,0.3)] backdrop-blur-2xl">
              <div className="rounded-[24px] border border-cyan-400/20 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-5">
                <div className="mb-4 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-slate-300">
                    <Bot className="h-4 w-4 text-cyan-300" />
                    AI Recruiter
                  </div>
                  <div className="rounded-full border border-emerald-400/20 bg-emerald-500/10 px-2 py-1 text-xs font-medium text-emerald-300">
                    Live
                  </div>
                </div>

                <div className="space-y-4">
                  {[
                    { label: "Candidate Match", value: "94%", tone: "cyan" },
                    { label: "Skill Alignment", value: "88%", tone: "violet" },
                    { label: "Experience Fit", value: "91%", tone: "emerald" },
                  ].map((item) => (
                    <div key={item.label} className="space-y-2">
                      <div className="flex items-center justify-between text-sm text-slate-300">
                        <span>{item.label}</span>
                        <span className="font-semibold text-white">{item.value}</span>
                      </div>
                      <div className="h-2 rounded-full bg-slate-800">
                        <div
                          className={`h-full rounded-full ${
                            item.tone === "cyan"
                              ? "bg-gradient-to-r from-cyan-400 to-blue-500"
                              : item.tone === "violet"
                                ? "bg-gradient-to-r from-violet-400 to-fuchsia-500"
                                : "bg-gradient-to-r from-emerald-400 to-teal-500"
                          }`}
                          style={{ width: item.value }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center gap-2 text-sm text-slate-300">
                    <Zap className="h-4 w-4 text-yellow-300" />
                    Highlighted strengths
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {['Python', 'AI', 'Leadership', 'Product Strategy', 'Analytics'].map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full border border-white/10 bg-slate-800/80 px-2.5 py-1 text-xs text-slate-200"
                      >
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

      <section className="relative mx-auto max-w-7xl px-5 py-10 sm:px-6 lg:px-8">
        <div className="grid gap-6 md:grid-cols-3">
          {features.map(({ icon: Icon, title, description }, index) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
              className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
            >
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-500/20 to-violet-500/20 text-cyan-300">
                <Icon className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold text-white">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-300">{description}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </main>
  );
}
