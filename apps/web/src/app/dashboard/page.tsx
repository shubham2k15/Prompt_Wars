"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { DashboardCards } from "@/components/dashboard-cards";
import { apiRequest } from "@/lib/api";

type TimelinePoint = {
  label: string;
  mood: number;
  stress: number;
};

type HeatmapCell = {
  day: string;
  intensity: number;
};

type DashboardSnapshot = {
  wellness_score: number;
  burnout_risk: string;
  study_life_balance_score: number;
  mood_forecast: string;
  recent_triggers: string[];
  top_memories: string[];
  check_in_streak: number;
  today_focus: string;
  emotional_timeline: TimelinePoint[];
  emotional_heatmap: HeatmapCell[];
  weekly_reflection: string;
  achievements: string[];
  active_goals: string[];
  habit_signals: string[];
};

const fallback: DashboardSnapshot = {
  wellness_score: 76,
  burnout_risk: "medium",
  study_life_balance_score: 68,
  mood_forecast: "Forecast is mixed. Smaller workloads and cleaner breaks should help the next two days.",
  recent_triggers: ["mock tests", "comparison", "sleep drift"],
  top_memories: ["User mentioned revision fatigue", "User mentioned consistency", "User mentioned physics"],
  check_in_streak: 5,
  today_focus: "Protect your next study block by choosing one topic and one recovery break ahead of time.",
  emotional_timeline: [
    { label: "Mon", mood: 3.3, stress: 3.7 },
    { label: "Tue", mood: 2.8, stress: 4.1 },
    { label: "Wed", mood: 3.4, stress: 3.8 },
    { label: "Thu", mood: 3.7, stress: 3.1 },
    { label: "Fri", mood: 2.9, stress: 4.2 },
    { label: "Sat", mood: 3.8, stress: 2.9 },
    { label: "Sun", mood: 3.5, stress: 3.2 }
  ],
  emotional_heatmap: [
    { day: "Mon", intensity: 0.52 },
    { day: "Tue", intensity: 0.44 },
    { day: "Wed", intensity: 0.61 },
    { day: "Thu", intensity: 0.66 },
    { day: "Fri", intensity: 0.39 },
    { day: "Sat", intensity: 0.74 },
    { day: "Sun", intensity: 0.58 }
  ],
  weekly_reflection:
    "This week shows that your emotional state is closely tied to study pressure and recovery quality. You are holding a moderate amount of strain, so structure matters more than motivation.",
  achievements: ["Check-in streak unlocked", "Reflection rhythm unlocked"],
  active_goals: ["Finish electrostatics revision", "Protect 7 hours of sleep this week"],
  habit_signals: ["Breathing reset: on track", "Mock-review ritual: needs one more check-in"]
};

export default function DashboardPage() {
  const [snapshot, setSnapshot] = useState<DashboardSnapshot>(fallback);

  useEffect(() => {
    const token = window.localStorage.getItem("mindgarden_access_token");
    if (!token) {
      return;
    }

    apiRequest<DashboardSnapshot>("/insights/dashboard", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(setSnapshot)
      .catch(() => setSnapshot(fallback));
  }, []);

  return (
    <AppShell>
      <div className="space-y-6">
        <section className="glass-card p-6 md:p-8">
          <p className="pill">Daily overview</p>
          <h1 className="mt-5 font-display text-5xl text-pine">Your emotional study map</h1>
          <p className="mt-4 max-w-3xl text-lg leading-8 text-ink/70">
            See how stress, confidence, sleep, and journaling patterns move together so you can
            react early instead of waiting for burnout.
          </p>
        </section>

        <DashboardCards snapshot={snapshot} />

        <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="glass-card p-6">
            <div className="flex items-center justify-between">
              <h2 className="font-display text-3xl text-pine">Emotional timeline</h2>
              <div className="pill">Last 7 days</div>
            </div>
            <div className="mt-8 flex h-56 items-end gap-3">
              {snapshot.emotional_timeline.map((point) => (
                <div key={point.label} className="flex flex-1 flex-col items-center gap-3">
                  <div className="flex h-44 w-full items-end gap-2">
                    <div
                      className="w-1/2 rounded-t-2xl bg-sea"
                      style={{ height: `${Math.max(point.mood * 20, 10)}%` }}
                    />
                    <div
                      className="w-1/2 rounded-t-2xl bg-coral"
                      style={{ height: `${Math.max(point.stress * 20, 10)}%` }}
                    />
                  </div>
                  <span className="text-sm text-ink/55">{point.label}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 flex gap-5 text-sm text-ink/60">
              <span className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-sea" />
                Mood
              </span>
              <span className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-coral" />
                Stress
              </span>
            </div>
          </div>

          <div className="glass-card p-6">
            <h2 className="font-display text-3xl text-pine">Mood forecast</h2>
            <p className="mt-4 leading-7 text-ink/70">{snapshot.mood_forecast}</p>
            <div className="mt-6">
              <p className="text-sm uppercase tracking-[0.22em] text-ink/50">Study-life balance</p>
              <div className="mt-3 h-3 rounded-full bg-mist">
                <div
                  className="h-3 rounded-full bg-pine"
                  style={{ width: `${snapshot.study_life_balance_score}%` }}
                />
              </div>
              <p className="mt-3 text-3xl font-semibold text-pine">{snapshot.study_life_balance_score}</p>
            </div>
          </div>
        </section>

        <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
          <div className="glass-card p-6">
            <div className="flex items-center justify-between">
              <h2 className="font-display text-3xl text-pine">Trigger watch</h2>
              <div className="pill">High-pressure themes</div>
            </div>
            <div className="mt-6 flex flex-wrap gap-3">
              {snapshot.recent_triggers.map((trigger) => (
                <span key={trigger} className="rounded-full bg-coral/15 px-4 py-2 text-sm font-medium text-pine">
                  {trigger}
                </span>
              ))}
            </div>
            <div className="mt-8 grid grid-cols-7 gap-3">
              {snapshot.emotional_heatmap.map((cell) => (
                <div key={cell.day} className="text-center">
                  <div
                    className="h-16 rounded-2xl bg-pine"
                    style={{ opacity: Math.max(cell.intensity, 0.2) }}
                  />
                  <p className="mt-2 text-xs text-ink/55">{cell.day}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-4">
            <div className="glass-card p-6">
              <h2 className="font-display text-3xl text-pine">Weekly reflection</h2>
              <p className="mt-4 leading-7 text-ink/70">{snapshot.weekly_reflection}</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="glass-card p-6">
                <h3 className="font-display text-2xl text-pine">Achievements</h3>
                <div className="mt-4 flex flex-wrap gap-3">
                  {snapshot.achievements.map((item) => (
                    <span key={item} className="pill">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
              <div className="glass-card p-6">
                <h3 className="font-display text-2xl text-pine">Active goals</h3>
                <div className="mt-4 space-y-3">
                  {snapshot.active_goals.map((goal) => (
                    <div key={goal} className="rounded-[24px] bg-white/75 p-4 text-sm leading-7 text-ink/70">
                      {goal}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-4 xl:grid-cols-2">
          <div className="glass-card p-6">
            <h2 className="font-display text-3xl text-pine">Remembered support</h2>
            <div className="mt-5 space-y-3">
              {snapshot.top_memories.map((memory) => (
                <div key={memory} className="rounded-[24px] bg-white/75 p-4 text-sm leading-7 text-ink/70">
                  {memory}
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card p-6">
            <h2 className="font-display text-3xl text-pine">Habit intelligence</h2>
            <div className="mt-5 space-y-3">
              {snapshot.habit_signals.map((signal) => (
                <div key={signal} className="rounded-[24px] bg-white/75 p-4 text-sm leading-7 text-ink/70">
                  {signal}
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
