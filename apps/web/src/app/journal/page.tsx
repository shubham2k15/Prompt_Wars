"use client";

import { FormEvent, useEffect, useState } from "react";
import { Heart, MoonStar, Sparkles } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { getAccessToken } from "@/lib/auth";
import { apiRequest } from "@/lib/api";

type JournalEntry = {
  id: string;
  title: string;
  content: string;
  mood_self_score: number;
  energy_score: number;
  sleep_hours: number;
  ai_summary: string;
  detected_triggers: string[];
  created_at: string;
};

const prompts = [
  "What happened today that felt heavier than it looked from the outside?",
  "Where did I lose energy, and what helped me recover even a little?",
  "What is one pressure point I want the AI to help me untangle?",
];

export default function JournalPage() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [saved, setSaved] = useState<JournalEntry | null>(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [mood, setMood] = useState(3);
  const [energy, setEnergy] = useState(3);
  const [sleep, setSleep] = useState(7);

  async function loadEntries() {
    const token = getAccessToken();
    if (!token) {
      return;
    }
    const result = await apiRequest<JournalEntry[]>("/journals", {
      headers: { Authorization: `Bearer ${token}` },
    });
    setEntries(result);
    if (!saved && result.length) {
      setSaved(result[0]);
    }
  }

  useEffect(() => {
    loadEntries().catch(() => setStatus("Could not load your journal history yet."));
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getAccessToken();
    if (!token) {
      setStatus("Log in first to save this journal entry.");
      return;
    }

    setLoading(true);
    try {
      const result = await apiRequest<JournalEntry>("/journals", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          title,
          content,
          mood_self_score: mood,
          energy_score: energy,
          sleep_hours: sleep,
        }),
      });
      setSaved(result);
      setStatus("Journal saved. Your reflection is ready.");
      setTitle("");
      setContent("");
      await loadEntries();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not save journal");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <section className="space-y-6">
          <div className="glass-card p-6 md:p-8">
            <p className="pill">Journal intelligence</p>
            <h1 className="mt-5 font-display text-5xl text-pine">Write honestly. Get a reflection that feels useful, not generic.</h1>
            <p className="mt-4 text-lg leading-8 text-ink/70">
              Capture what happened, what your body was carrying, and what you need next. MindGarden turns that into clearer patterns and kinder next steps.
            </p>
          </div>

          <section className="glass-card p-6">
            <div className="flex items-center gap-3">
              <Sparkles className="h-6 w-6 text-pine" />
              <h2 className="section-title">Write today&apos;s check-in</h2>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              {prompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => setContent((current) => (current ? `${current}\n\n${prompt}\n` : `${prompt}\n`))}
                  className="secondary-button text-left"
                >
                  {prompt}
                </button>
              ))}
            </div>

            <form onSubmit={onSubmit} className="mt-6 space-y-4">
              <input
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="Today felt heavier after the mock test"
                className="w-full rounded-2xl border border-ink/10 bg-white/85 px-4 py-3"
                required
              />
              <textarea
                value={content}
                onChange={(event) => setContent(event.target.value)}
                placeholder="Write freely about the day, your stress, energy, thoughts, and what you need."
                className="min-h-72 w-full rounded-[28px] border border-ink/10 bg-white/85 px-4 py-4 leading-7"
                required
              />

              <div className="grid gap-4 md:grid-cols-3">
                <label className="rounded-[24px] bg-white/70 p-4">
                  <span className="block text-sm font-medium text-ink/65">Mood: {mood}/5</span>
                  <input type="range" min="1" max="5" value={mood} onChange={(event) => setMood(Number(event.target.value))} className="mt-3 w-full" />
                </label>
                <label className="rounded-[24px] bg-white/70 p-4">
                  <span className="block text-sm font-medium text-ink/65">Energy: {energy}/5</span>
                  <input type="range" min="1" max="5" value={energy} onChange={(event) => setEnergy(Number(event.target.value))} className="mt-3 w-full" />
                </label>
                <label className="rounded-[24px] bg-white/70 p-4">
                  <span className="block text-sm font-medium text-ink/65">Sleep: {sleep}h</span>
                  <input type="range" min="0" max="12" value={sleep} onChange={(event) => setSleep(Number(event.target.value))} className="mt-3 w-full" />
                </label>
              </div>

              <div className="flex items-center justify-between gap-4">
                <p className="text-sm text-ink/60">{status || "Your entry stays private and encrypted."}</p>
                <button type="submit" disabled={loading} className="primary-button">
                  {loading ? "Saving..." : "Save journal"}
                </button>
              </div>
            </form>
          </section>
        </section>

        <section className="space-y-6">
          <div className="glass-card p-6">
            <p className="text-sm uppercase tracking-[0.22em] text-ink/50">AI reflection</p>
            <div className="mt-4 rounded-[28px] bg-gradient-to-br from-pine via-pine to-sea p-6 text-white shadow-xl shadow-pine/20">
              <p className="text-sm uppercase tracking-[0.18em] text-white/70">Supportive readback</p>
              <div className="mt-4 space-y-3 whitespace-pre-wrap leading-7">
                {saved?.ai_summary || "After you save a journal, this panel will return a more thoughtful emotional read, likely triggers, and a supportive next step."}
              </div>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-3">
              <div className="rounded-[24px] bg-white/75 p-4">
                <div className="flex items-center gap-2 text-pine">
                  <Heart className="h-4 w-4" />
                  <p className="text-sm font-semibold">Mood</p>
                </div>
                <p className="mt-3 font-display text-3xl text-pine">{saved?.mood_self_score ?? mood}/5</p>
              </div>
              <div className="rounded-[24px] bg-white/75 p-4">
                <div className="flex items-center gap-2 text-pine">
                  <Sparkles className="h-4 w-4" />
                  <p className="text-sm font-semibold">Energy</p>
                </div>
                <p className="mt-3 font-display text-3xl text-pine">{saved?.energy_score ?? energy}/5</p>
              </div>
              <div className="rounded-[24px] bg-white/75 p-4">
                <div className="flex items-center gap-2 text-pine">
                  <MoonStar className="h-4 w-4" />
                  <p className="text-sm font-semibold">Sleep</p>
                </div>
                <p className="mt-3 font-display text-3xl text-pine">{saved?.sleep_hours ?? sleep}h</p>
              </div>
            </div>

            <div className="mt-5">
              <p className="text-sm uppercase tracking-[0.22em] text-ink/50">Detected themes</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {(saved?.detected_triggers || ["exam stress", "recovery", "self-talk"]).map((item) => (
                  <span key={item} className="pill">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="glass-card p-6">
            <div className="flex items-center justify-between">
              <h2 className="section-title">Recent entries</h2>
              <div className="pill">{entries.length} reflections</div>
            </div>
            <div className="mt-5 space-y-3">
              {entries.map((entry) => (
                <button
                  key={entry.id}
                  type="button"
                  onClick={() => setSaved(entry)}
                  className="w-full rounded-[24px] bg-white/78 p-4 text-left transition hover:bg-white"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-semibold text-pine">{entry.title}</p>
                      <p className="mt-1 line-clamp-2 text-sm leading-6 text-ink/62">{entry.content}</p>
                    </div>
                    <p className="text-xs uppercase tracking-[0.16em] text-ink/45">
                      {new Date(entry.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </button>
              ))}
              {!entries.length ? <p className="text-sm text-ink/55">Your saved journal entries will appear here.</p> : null}
            </div>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
