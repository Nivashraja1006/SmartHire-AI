import Link from "next/link";
import { Sparkles } from "lucide-react";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 via-blue-500 to-violet-600 shadow-[0_0_30px_rgba(59,130,246,0.45)]">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-semibold tracking-tight text-white">SmartHire AI</span>
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          <Link href="/" className="text-sm text-slate-300 transition hover:text-white">Home</Link>
          <Link href="/upload" className="text-sm text-slate-300 transition hover:text-white">Upload</Link>
          <Link href="/results" className="text-sm text-slate-300 transition hover:text-white">Results</Link>
        </div>

        <Link
          href="/upload"
          className="rounded-full border border-cyan-400/35 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-200 transition hover:border-cyan-300 hover:bg-cyan-500/20"
        >
          Launch AI
        </Link>
      </nav>
    </header>
  );
}
