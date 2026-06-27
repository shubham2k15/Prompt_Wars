"use client";

import { FormEvent, useEffect, useState } from "react";
import { PauseCircle, PlayCircle, Target, Trophy } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { getAccessToken } from "@/lib/auth";
import { apiRequest } from "@/lib/api";

type Goal = {
  id: string;
  title: string;
  category: string;
  target_date: string;
  progress: number;
  status: string;
};

type Habit = {
  id: string;
  name: string;
  frequency: string;
  target_count: number;
  completion_count: number;
  latest_status: string;
};

const goalStatusLabel: Record<string, string> = {
  not_started: "Not started",
  in_progress: "In progress",
  paused: "Paused",
  completed: "Completed",
};

export default function PlansPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [goalTitle, setGoalTitle] = useState("");
  const [goalCategory, setGoalCategory] = useState("study");
  const [goalTargetDate, setGoalTargetDate] = useState("");
  const [habitName, setHabitName] = useState("");
  const [message, setMessage] = useState("");
  const [savingGoalId, setSavingGoalId] = useState("");

  async function loadData() {
    const token = getAccessToken();
    if (!token) {
      return;
    }
    const [goalData, habitData] = await Promise.all([
      apiRequest<Goal[]>("/goals", { headers: { Authorization: `Bearer ${token}` } }),
      apiRequest<Habit[]>("/habits", { headers: { Authorization: `Bearer ${token}` } }),
    ]);
    setGoals(goalData);
    setHabits(habitData);
  }

  useEffect(() => {
    loadData().catch(() => setMessage("Could not load your plans yet."));
  }, []);

  async function createGoal(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getAccessToken();
    if (!token || !goalTitle.trim()) {
      return;
    }
    await apiRequest<Goal>("/goals", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        title: goalTitle,
        category: goalCategory,
        target_date: goalTargetDate,
        progress: 0,
        status: "not_started",
      }),
    });
    setGoalTitle("");
    setGoalCategory("study");
    setGoalTargetDate("");
    setMessage("Plan added. You can start it whenever you are ready.");
    await loadData();
  }

  async function updateGoal(goal: Goal, updates: Partial<Pick<Goal, "progress" | "status">>) {
    const token = getAccessToken();
    if (!token) {
      return;
    }
    setSavingGoalId(goal.id);
    try {
      await apiRequest<Goal>(`/goals/${goal.id}`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          progress: updates.progress ?? goal.progress,
          status: updates.status ?? goal.status,
        }),
      });
      setMessage("Goal updated.");
      await loadData();
    } finally {
      setSavingGoalId("");
    }
  }

  async function createHabit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getAccessToken();
    if (!token || !habitName.trim()) {
      return;
    }
    await apiRequest<Habit>("/habits", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ name: habitName, frequency: "daily", target_count: 1 }),
    });
    setHabitName("");
    setMessage("Support habit added.");
    await loadData();
  }

  async function markHabit(habitId: string) {
    const token = getAccessToken();
    if (!token) {
      return;
    }
    await apiRequest<Habit>(`/habits/${habitId}/logs`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ status: "done" }),
    });
    setMessage("Habit check-in saved.");
    await loadData();
  }

  const activeGoals = goals.filter((goal) => goal.status !== "completed").length;
  const completedGoals = goals.filter((goal) => goal.status === "completed").length;

  return (
    <AppShell>
      <div className="space-y-6">
        <section className="glass-card overflow-hidden p-6 md:p-8">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-3xl">
              <p className="pill">Goals and habits</p>
              <h1 className="mt-5 font-display text-5xl text-pine">Turn emotional insight into a plan you can actually sustain.</h1>
              <p className="mt-4 text-lg leading-8 text-ink/70">
                Start small, track honestly, and close the loop on what is working. The goal is steadier progress, not louder pressure.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-3 xl:w-[25rem]">
              <div className="rounded-[24px] bg-white/80 p-4">
                <p className="text-sm uppercase tracking-[0.18em] text-ink/45">Open goals</p>
                <p className="mt-3 font-display text-4xl text-pine">{activeGoals}</p>
              </div>
              <div className="rounded-[24px] bg-white/80 p-4">
                <p className="text-sm uppercase tracking-[0.18em] text-ink/45">Completed</p>
                <p className="mt-3 font-display text-4xl text-pine">{completedGoals}</p>
              </div>
              <div className="rounded-[24px] bg-white/80 p-4">
                <p className="text-sm uppercase tracking-[0.18em] text-ink/45">Habit streaks</p>
                <p className="mt-3 font-display text-4xl text-pine">{habits.reduce((sum, habit) => sum + habit.completion_count, 0)}</p>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.45fr_0.55fr]">
          <div className="glass-card p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="section-title">Goal tracker</h2>
                <p className="mt-2 text-sm leading-6 text-ink/60">Create a goal, start it when you are ready, and update progress without rebuilding the whole plan.</p>
              </div>
              <div className="pill">{goals.length} total goals</div>
            </div>

            <form onSubmit={createGoal} className="mt-6 grid gap-3 md:grid-cols-[1.3fr_0.8fr_0.8fr_auto]">
              <input
                value={goalTitle}
                onChange={(event) => setGoalTitle(event.target.value)}
                placeholder="Finish revision of organic chemistry reactions"
                className="rounded-2xl border border-ink/10 bg-white/85 px-4 py-3"
              />
              <select
                value={goalCategory}
                onChange={(event) => setGoalCategory(event.target.value)}
                className="rounded-2xl border border-ink/10 bg-white/85 px-4 py-3"
              >
                <option value="study">Study</option>
                <option value="wellbeing">Wellbeing</option>
                <option value="revision">Revision</option>
                <option value="routine">Routine</option>
              </select>
              <input
                value={goalTargetDate}
                onChange={(event) => setGoalTargetDate(event.target.value)}
                placeholder="This week"
                className="rounded-2xl border border-ink/10 bg-white/85 px-4 py-3"
              />
              <button className="primary-button">Add plan</button>
            </form>

            <div className="mt-6 space-y-4">
              {goals.map((goal) => (
                <div key={goal.id} className="rounded-[28px] border border-white/60 bg-white/78 p-5 shadow-sm">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-lg font-semibold text-pine">{goal.title}</p>
                        <span className="pill !px-3 !py-1 text-xs">{goalStatusLabel[goal.status] || goal.status}</span>
                      </div>
                      <p className="mt-2 text-sm text-ink/55">
                        {goal.category} | {goal.target_date || "No date set yet"}
                      </p>
                    </div>
                    <div className="text-left lg:text-right">
                      <p className="text-sm font-semibold text-ink/65">Progress</p>
                      <p className="font-display text-3xl text-pine">{goal.progress}%</p>
                    </div>
                  </div>

                  <div className="mt-4 h-3 rounded-full bg-mist">
                    <div className="h-3 rounded-full bg-gradient-to-r from-sea to-pine" style={{ width: `${goal.progress}%` }} />
                  </div>

                  <div className="mt-4 flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
                    <div className="flex flex-wrap gap-2">
                      <button type="button" onClick={() => updateGoal(goal, { status: "in_progress", progress: goal.progress === 0 ? 10 : goal.progress })} className="secondary-button" disabled={savingGoalId === goal.id}>
                        <PlayCircle className="h-4 w-4" />
                        Start
                      </button>
                      <button type="button" onClick={() => updateGoal(goal, { status: "paused" })} className="secondary-button" disabled={savingGoalId === goal.id}>
                        <PauseCircle className="h-4 w-4" />
                        Pause
                      </button>
                      <button type="button" onClick={() => updateGoal(goal, { status: "completed", progress: 100 })} className="secondary-button" disabled={savingGoalId === goal.id}>
                        <Trophy className="h-4 w-4" />
                        Complete
                      </button>
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      {[10, 25, 50, 75].map((value) => (
                        <button
                          key={value}
                          type="button"
                          onClick={() => updateGoal(goal, { progress: value, status: value === 100 ? "completed" : "in_progress" })}
                          className="secondary-button"
                          disabled={savingGoalId === goal.id}
                        >
                          Track {value}%
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
              {!goals.length ? <p className="text-sm text-ink/55">No goals yet. Add one that feels realistic this week.</p> : null}
            </div>
          </div>

          <div className="grid gap-4">
            <div className="glass-card p-6">
              <div className="flex items-center justify-between">
                <h2 className="section-title">Habit support</h2>
                <div className="pill">{habits.length} rituals</div>
              </div>
              <form onSubmit={createHabit} className="mt-5 flex gap-3">
                <input
                  value={habitName}
                  onChange={(event) => setHabitName(event.target.value)}
                  placeholder="10-minute breathing reset after mock tests"
                  className="flex-1 rounded-2xl border border-ink/10 bg-white/85 px-4 py-3"
                />
                <button className="primary-button">Add</button>
              </form>
              <div className="mt-6 space-y-3">
                {habits.map((habit) => (
                  <div key={habit.id} className="rounded-[24px] bg-white/75 p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-semibold text-pine">{habit.name}</p>
                        <p className="mt-1 text-sm text-ink/55">
                          {habit.frequency} | {habit.completion_count} check-ins | {habit.latest_status}
                        </p>
                      </div>
                      <button type="button" onClick={() => markHabit(habit.id)} className="secondary-button">
                        Mark done
                      </button>
                    </div>
                  </div>
                ))}
                {!habits.length ? <p className="text-sm text-ink/55">No habits yet. Add one calming or recovery habit first.</p> : null}
              </div>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center gap-3">
                <Target className="h-6 w-6 text-pine" />
                <h3 className="font-display text-2xl text-pine">Planning guidance</h3>
              </div>
              <div className="mt-4 space-y-3 text-sm leading-7 text-ink/68">
                <p>Start only the goals you can protect this week.</p>
                <p>Pause a plan when recovery needs to come first. Pausing is information, not failure.</p>
                <p>Track progress honestly so the dashboard reflects your real load.</p>
              </div>
            </div>
          </div>
        </section>

        <div className="glass-card p-5 text-sm text-ink/65">
          {message || "MindGarden works best when plans stay small, specific, and repeatable."}
        </div>
      </div>
    </AppShell>
  );
}
