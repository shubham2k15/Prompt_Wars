"use client";

import { FormEvent, useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { getAccessToken } from "@/lib/auth";
import { apiRequest } from "@/lib/api";

type Message = {
  id: string;
  role: string;
  content: string;
  created_at: string;
};

type Session = {
  id: string;
  title: string;
  summary: string;
  risk_level: string;
  messages: Message[];
};

export default function ChatPage() {
  const [session, setSession] = useState<Session | null>(null);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const starters = [
    "I feel behind and I need help choosing one realistic study step for today.",
    "My mock test went badly and I cannot stop replaying it.",
    "I want a gentle plan for tonight because I feel mentally tired.",
  ];

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      return;
    }
    apiRequest<Session>("/chat/sessions", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ title: "Daily companion check-in" })
    })
      .then(setSession)
      .catch(() => setError("Could not start a companion session yet."));
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !draft.trim()) {
      return;
    }
    const token = getAccessToken();
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const nextSession = await apiRequest<Session>(`/chat/sessions/${session.id}/messages`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify({ content: draft })
      });
      setSession(nextSession);
      setDraft("");
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Message could not be sent.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <section className="glass-card p-6">
          <p className="pill">Companion intelligence</p>
          <h1 className="mt-5 font-display text-5xl text-pine">Talk to the part of the app that actually remembers.</h1>
          <p className="mt-4 leading-7 text-ink/70">
            MindGarden blends your recent context, profile preferences, and meaningful memories so
            the companion can respond like a calm guide instead of a generic bot.
          </p>
          <div className="mt-5 flex flex-wrap gap-2">
            {starters.map((starter) => (
              <button key={starter} type="button" onClick={() => setDraft(starter)} className="secondary-button text-left">
                {starter}
              </button>
            ))}
          </div>
          <div className="mt-6 rounded-[28px] bg-pine p-5 text-white">
            <p className="text-sm uppercase tracking-[0.22em] text-white/70">Safety stance</p>
            <p className="mt-3 leading-7">
              The companion is supportive and practical, but it does not diagnose or replace
              professional care.
            </p>
          </div>
        </section>

        <section className="glass-card flex min-h-[75vh] flex-col p-4">
          <div className="border-b border-ink/10 px-3 pb-4 pt-2">
            <p className="text-sm uppercase tracking-[0.22em] text-ink/50">Session</p>
            <h2 className="mt-1 font-display text-3xl text-pine">{session?.title || "Preparing conversation..."}</h2>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto px-3 py-5">
            {(session?.messages || []).map((message) => (
              <div
                key={message.id}
                className={`max-w-[85%] rounded-[28px] px-5 py-4 ${
                  message.role === "assistant"
                    ? "bg-pine text-white"
                    : "ml-auto bg-mist text-ink"
                }`}
              >
                <p className="text-xs uppercase tracking-[0.18em] opacity-70">{message.role}</p>
                <p className="mt-2 whitespace-pre-wrap leading-7">{message.content}</p>
              </div>
            ))}
            {error ? <p className="rounded-[24px] bg-coral/15 px-4 py-3 text-sm text-pine">{error}</p> : null}
          </div>

          <form onSubmit={onSubmit} className="border-t border-ink/10 px-3 pb-2 pt-4">
            <div className="rounded-[28px] border border-ink/10 bg-white/85 p-3">
              <textarea
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                className="min-h-28 w-full resize-none bg-transparent outline-none"
                placeholder="Tell your companion what happened today, what feels heavy, or what you need help with."
              />
              <div className="mt-3 flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="primary-button"
                >
                  {loading ? "Sending..." : "Send reflection"}
                </button>
              </div>
            </div>
          </form>
        </section>
      </div>
    </AppShell>
  );
}
