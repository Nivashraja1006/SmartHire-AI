"use client";

import { useRef, useState } from "react";
import { motion } from "framer-motion";
import { FileText, UploadCloud, Loader2 } from "lucide-react";

interface UploadBoxProps {
  selectedFile: File | null;
  onFileSelect: (file: File | null) => void;
  onAnalyze: () => void;
  isLoading: boolean;
}

export default function UploadBox({
  selectedFile,
  onFileSelect,
  onAnalyze,
  isLoading,
}: UploadBoxProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = (file: File | null) => {
    if (!file) return;
    onFileSelect(file);
  };

  return (
    <div className="rounded-[30px] border border-white/10 bg-white/5 p-4 backdrop-blur-xl md:p-6">
      <div
        className={`relative flex min-h-[280px] cursor-pointer flex-col items-center justify-center rounded-[26px] border border-dashed px-6 py-10 text-center transition-all ${
          isDragging
            ? "border-cyan-400 bg-cyan-500/10 shadow-[0_0_28px_rgba(34,211,238,0.25)]"
            : "border-white/15 bg-slate-900/40 hover:border-cyan-400/60"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFile(e.dataTransfer.files?.[0] || null);
        }}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.doc,.docx"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0] || null)}
        />

        <motion.div
          animate={{ scale: isDragging ? 1.04 : 1 }}
          className="mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500/20 to-violet-500/20 ring-1 ring-white/10"
        >
          {isLoading ? (
            <Loader2 className="h-7 w-7 animate-spin text-cyan-300" />
          ) : selectedFile ? (
            <FileText className="h-7 w-7 text-emerald-300" />
          ) : (
            <UploadCloud className="h-7 w-7 text-cyan-300" />
          )}
        </motion.div>

        <p className="text-2xl font-semibold text-white">
          {selectedFile ? selectedFile.name : "Drag & drop your resume"}
        </p>
        <p className="mt-3 text-sm text-slate-300">PDF, DOCX, or DOC supported</p>

        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          <span className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200">
            {selectedFile ? "Resume ready" : "Browse files"}
          </span>

          {selectedFile && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onAnalyze();
              }}
              className="rounded-full bg-gradient-to-r from-cyan-500 to-violet-500 px-5 py-2.5 text-sm font-semibold text-white shadow-[0_0_25px_rgba(34,211,238,0.3)] transition hover:scale-[1.02]"
            >
              {isLoading ? "Analyzing..." : "Analyze Resume"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
