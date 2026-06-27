import { CompanionPreview } from "@/components/companion-preview";
import { Hero } from "@/components/hero";

const pillars = [
  {
    title: "Emotional memory",
    text: "The companion remembers pressure patterns, calming strategies, and what usually makes a hard week worse."
  },
  {
    title: "Journal intelligence",
    text: "Daily writing becomes weekly insight with emotional summaries, hidden trigger detection, and reflection prompts."
  },
  {
    title: "Burnout prevention",
    text: "Mood signals, confidence drift, and consistency trends come together into a score that surfaces risks early."
  }
];

export default function HomePage() {
  return (
    <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 px-4 py-6 md:px-6">
      <Hero />

      <section className="grid gap-4 md:grid-cols-3">
        {pillars.map((pillar) => (
          <article key={pillar.title} className="glass-card p-6">
            <h2 className="font-display text-3xl text-pine">{pillar.title}</h2>
            <p className="mt-4 leading-7 text-ink/70">{pillar.text}</p>
          </article>
        ))}
      </section>

      <CompanionPreview />
    </div>
  );
}

