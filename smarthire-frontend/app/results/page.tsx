"use client";

import { useEffect, useState } from "react";
import ResultCard from "@/components/ResultCard";

export type CandidateResult = {
  name: string;
  role: string;
  score: number;
  skills: string[];
  experience: string;
  ranking: number;
};

const defaultResults: CandidateResult[] = [
  {
    name: "Ariana Patel",
    role: "Senior Product Manager",
    score: 96,
    skills: ["AI Strategy", "Roadmapping", "Leadership"],
    experience: "8 years",
    ranking: 1,
  },
  {
    name: "David Kim",
    role: "Data Scientist",
    score: 91,
    skills: ["Python", "ML", "Analytics"],
    experience: "6 years",
    ranking: 2,
  },
  {
    name: "Leah Gomez",
    role: "Full Stack Engineer",
    score: 88,
    skills: ["React", "Node.js", "Cloud"],
    experience: "5 years",
    ranking: 3,
  },
];

export default function ResultsPage() {
  const [candidates, setCandidates] = useState<CandidateResult[]>(defaultResults);

  useEffect(() => {
    const saved = localStorage.getItem("smarthire-results");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setCandidates(parsed);
        }
      } catch {
        setCandidates(defaultResults);
      }
    }
  }, []);

  return (
    <main className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
      <div className="mb-10 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-violet-300">AI ranking</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight text-white md:text-5xl">
            Top candidate matches
          </h1>
        </div>

        <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300 backdrop-blur-xl">
          Sorted by best fit
        </div>
      </div>

      {candidates.length === 0 ? (
        <div className="rounded-[28px] border border-dashed border-white/15 bg-white/5 p-12 text-center text-slate-300">
          No candidate results yet. Upload a resume to generate the ranking.
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {candidates
            .slice()
            .sort((a, b) => b.score - a.score)
            .map((candidate, index) => (
              <ResultCard key={`${candidate.name}-${index}`} candidate={candidate} index={index} />
            ))}
        </div>
      )}
    </main>
  );
}
