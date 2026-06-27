const transcript = [
  {
    role: "student",
    text: "I keep comparing myself after every mock test and it ruins the whole day."
  },
  {
    role: "assistant",
    text: "That comparison spiral sounds exhausting. Let us protect the next hour by separating your score from your worth and choosing one correction target."
  }
];

export function CompanionPreview() {
  return (
    <section className="grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
      <div className="glass-card p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-ink/50">Companion memory</p>
            <h2 className="mt-2 font-display text-3xl text-pine">A conversation that grows with the student</h2>
          </div>
          <div className="pill">Adaptive tone</div>
        </div>
        <div className="mt-6 space-y-4">
          {transcript.map((message) => (
            <div
              key={message.text}
              className={`max-w-2xl rounded-[28px] px-5 py-4 ${
                message.role === "assistant" ? "bg-pine text-white" : "bg-mist text-ink"
              }`}
            >
              <p className="text-xs uppercase tracking-[0.18em] opacity-70">{message.role}</p>
              <p className="mt-2 leading-7">{message.text}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-card p-6">
        <p className="text-sm uppercase tracking-[0.22em] text-ink/50">What MindGarden tracks</p>
        <div className="mt-5 flex flex-wrap gap-3">
          {[
            "Exam pressure triggers",
            "Sleep drift",
            "Confidence swings",
            "Journaling consistency",
            "Helpful break patterns",
            "Motivation style",
            "Burnout signals",
            "Recovery wins"
          ].map((item) => (
            <span key={item} className="pill">
              {item}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

