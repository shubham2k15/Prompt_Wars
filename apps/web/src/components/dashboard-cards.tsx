type DashboardSnapshot = {
  wellness_score: number;
  burnout_risk: string;
  recent_triggers: string[];
  top_memories: string[];
  check_in_streak: number;
  today_focus: string;
};

export function DashboardCards({ snapshot }: { snapshot: DashboardSnapshot }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <div className="glass-card p-5">
        <p className="text-sm uppercase tracking-[0.22em] text-ink/50">Wellness score</p>
        <p className="mt-4 text-5xl font-display text-pine">{snapshot.wellness_score}</p>
        <p className="mt-3 text-sm text-ink/60">A blended signal of mood, stress, confidence, and consistency.</p>
      </div>
      <div className="glass-card p-5">
        <p className="text-sm uppercase tracking-[0.22em] text-ink/50">Burnout risk</p>
        <p className="mt-4 text-3xl font-semibold capitalize text-pine">{snapshot.burnout_risk}</p>
        <div className="mt-4 h-2 rounded-full bg-mist">
          <div
            className={`h-2 rounded-full ${
              snapshot.burnout_risk === "high"
                ? "w-11/12 bg-coral"
                : snapshot.burnout_risk === "medium"
                  ? "w-7/12 bg-sea"
                  : "w-4/12 bg-pine"
            }`}
          />
        </div>
      </div>
      <div className="glass-card p-5">
        <p className="text-sm uppercase tracking-[0.22em] text-ink/50">Check-in streak</p>
        <p className="mt-4 text-5xl font-display text-pine">{snapshot.check_in_streak}</p>
        <p className="mt-3 text-sm text-ink/60">Momentum matters. A small honest check-in still counts.</p>
      </div>
      <div className="glass-card p-5">
        <p className="text-sm uppercase tracking-[0.22em] text-ink/50">Today&apos;s focus</p>
        <p className="mt-4 text-base leading-7 text-ink/75">{snapshot.today_focus}</p>
      </div>
    </div>
  );
}

