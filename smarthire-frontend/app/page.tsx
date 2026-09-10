"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, BrainCircuit, FileText, ShieldCheck, Sparkles, Zap } from "lucide-react";

const featureCards = [
  {
    icon: FileText,
    title: "Resume Intelligence",
    description: "Extract skills, experience, and role-fit signals in seconds.",
  },
  {
    icon: BrainCircuit,
    title: "AI Matching",
    description: "Score candidates against job requirements with explainable precision.",
  },
  {
    icon: ShieldCheck,
    title: "Fair & Fast",
    description: "Reduce hiring bias while accelerating review cycles for recruiters.",
  },
];

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

      <section id="features" className="relative mx-auto max-w-7xl px-6 pb-24 lg:px-8">
        <div className="grid gap-6 md:grid-cols-3">
          {featureCards.map(({ icon: Icon, title, description }, index) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 * (index + 1) }}
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
