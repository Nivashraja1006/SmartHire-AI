"use client";

import { motion } from "framer-motion";
import { Award, Briefcase, Sparkles } from "lucide-react";
import type { CandidateResult } from "@/app/results/page";

interface ResultCardProps {
  candidate: CandidateResult;
  index: number;
}

export default function ResultCard({ candidate, index }: ResultCardProps) {
  const isTop = index === 0;

  return (
    <motion.article
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08 }}
      className={`rounded-[28px] border p-5 backdrop-blur-xl ${
        isTop
          ? "border-cyan-400/35 bg-gradient-to-br from-cyan-500/10 to-violet-500/10 shadow-[0_25px_80px_rgba(59,130,246,0.25)]"
          : "border-white/10 bg-white/5"
      }`}
    >
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <p className="text-xl font-semibold text-white">{candidate.name}</p>
          <p className="text-sm text-slate-400">{candidate.role}</p>
        </div>

        <div className={`rounded-full px-3 py-1 text-sm font-semibold ${
          isTop ? "bg-cyan-500/15 text-cyan-200" : "bg-white/5 text-slate-200"
        }`}>
          #{candidate.ranking || index + 1}
        </div>
      </div>

      <div className="mb-4 flex items-center justify-between text-sm text-slate-300">
        <span>Matching score</span>
        <span className="font-semibold text-white">{candidate.score}%</span>
      </div>

      <div className="mb-5 h-2.5 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-blue-500 to-violet-500"
          style={{ width: `${candidate.score}%` }}
        />
      </div>

      <div className="space-y-3 text-sm text-slate-300">
        <div className="flex items-center gap-2">
          <Award className="h-4 w-4 text-cyan-300" />
          <span>Score: {candidate.score}%</span>
        </div>
        <div className="flex items-center gap-2">
          <Briefcase className="h-4 w-4 text-violet-300" />
          <span>Experience: {candidate.experience}</span>
        </div>
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-emerald-300" />
          <span>Skills: {candidate.skills.join(", ")}</span>
        </div>
      </div>
    </motion.article>
  );
}
