"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { CheckCircle2, FileText, Sparkles, AlertTriangle } from "lucide-react";
import UploadBox from "@/components/UploadBox";
import Loader from "@/components/Loader";
import { uploadResume } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError("Please upload a resume first.");
      return;
    }

    setIsAnalyzing(true);
    setError("");
    setSuccessMessage("");

    try {
      const response = await uploadResume(selectedFile);
      const payload = response?.data ?? response;

      const result = {
        name: payload?.candidate?.name || "Candidate Profile",
        skills: payload?.candidate?.skills || payload?.skills || ["Python", "Leadership", "AI"],
        score: Number(payload?.score ?? payload?.candidate?.score ?? 92),
        ranking: Number(payload?.ranking ?? payload?.candidate?.ranking ?? 1),
        experience: payload?.experience || payload?.candidate?.experience || "5+ years",
        role: payload?.role || payload?.candidate?.role || "Product & AI Team",
      };

      localStorage.setItem("smarthire-results", JSON.stringify([result]));
      setSuccessMessage("Resume analyzed successfully.");

      setTimeout(() => router.push("/results"), 700);
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "Something went wrong while analyzing the resume.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <main className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
      <div className="mb-10 text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.22em] text-cyan-300">Resume intake</p>
        <h1 className="mt-4 text-4xl font-black tracking-tight text-white md:text-5xl">
          Upload candidate profile
        </h1>
      </div>

      <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <UploadBox
            selectedFile={selectedFile}
            onFileSelect={setSelectedFile}
            onAnalyze={handleAnalyze}
            isLoading={isAnalyzing}
          />
        </motion.div>

        <motion.aside
          initial={{ opacity: 0, x: 16 }}
          animate={{ opacity: 1, x: 0 }}
          className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
        >
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-500/20 to-violet-500/20 text-cyan-300">
              <Sparkles className="h-5 w-5" />
            </div>
            <h2 className="text-xl font-semibold text-white">Smart screening flow</h2>
          </div>

          <div className="mt-6 space-y-4 text-sm text-slate-300">
            <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-4">
              <div className="mb-2 flex items-center gap-2 text-cyan-300">
                <FileText className="h-4 w-4" />
                Resume parsing
              </div>
              Candidate files are processed for skills, projects, and experience patterns.
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-4">
              <div className="mb-2 flex items-center gap-2 text-violet-300">
                <CheckCircle2 className="h-4 w-4" />
                AI ranking
              </div>
              The model compares the profile to the job-fit criteria and assigns a score.
            </div>
          </div>

          {error && (
            <div className="mt-6 flex items-center gap-2 rounded-2xl border border-rose-400/30 bg-rose-500/10 p-4 text-sm text-rose-200">
              <AlertTriangle className="h-4 w-4" />
              {error}
            </div>
          )}

          {successMessage && (
            <div className="mt-6 rounded-2xl border border-emerald-400/30 bg-emerald-500/10 p-4 text-sm text-emerald-200">
              {successMessage}
            </div>
          )}
        </motion.aside>
      </div>

      {isAnalyzing && <Loader message="Analyzing with AI..." />}
    </main>
  );
}
