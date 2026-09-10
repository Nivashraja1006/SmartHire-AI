import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "SmartHire AI",
  description: "AI-powered resume screening and ranking for modern recruiting teams.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-slate-950 text-slate-50">
          <Navbar />
          {children}
        </div>
      </body>
    </html>
  );
}
