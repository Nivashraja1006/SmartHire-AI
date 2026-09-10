"use client";

import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

export default function Loader({ message = "Analyzing with AI..." }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm"
    >
      <div className="flex flex-col items-center gap-4 rounded-[28px] border border-white/10 bg-slate-900/80 px-8 py-7 shadow-[0_25px_100px_rgba(45,212,191,0.18)] backdrop-blur-xl">
        <Loader2 className="h-10 w-10 animate-spin text-cyan-300" />
        <p className="text-lg font-medium text-white">{message}</p>
      </div>
    </motion.div>
  );
}
