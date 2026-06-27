import Link from "next/link";
import { ArrowRight, Brain, ShieldCheck, Sparkles } from "lucide-react";

export function Hero() {
  return (
    <section className="relative overflow-hidden rounded-[40px] border border-white/60 bg-white/70 px-6 py-8 shadow-float backdrop-blur md:px-10 md:py-12">
      <div className="absolute right-0 top-0 h-48 w-48 rounded-full bg-sea/25 blur-3xl" />
      <div className="absolute bottom-0 left-0 h-56 w-56 rounded-full bg-coral/20 blur-3xl" />

      <div className="relative max-w-3xl space-y-6">
        <div className="pill">
          <Sparkles className="h-4 w-4" />
          Gemini-powered emotional memory companion
        </div>
        <div className="space-y-4">
          <h1 className="max-w-2xl font-display text-5xl leading-tight text-pine md:text-6xl">
            The study companion that remembers how you feel, not just what you type.
          </h1>
          <p className="max-w-2xl text-lg text-ink/70">
            MindGarden helps exam students track stress, journal honestly, spot burnout early, and
            feel supported by an AI companion that grows more useful over time.
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            href="/login"
            className="inline-flex items-center gap-2 rounded-full bg-pine px-6 py-3 font-semibold text-white"
          >
            Start your calm system
            <ArrowRight className="h-4 w-4" />
          </Link>
          <div className="pill">
            <ShieldCheck className="h-4 w-4" />
            Privacy-first with export and memory reset controls
          </div>
          <div className="pill">
            <Brain className="h-4 w-4" />
            Journals, mood tracking, evolving AI memory
          </div>
        </div>
      </div>
    </section>
  );
}

