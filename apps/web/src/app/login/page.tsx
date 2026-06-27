"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { apiRequest } from "@/lib/api";

type AuthResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [identifier, setIdentifier] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const payload =
        mode === "register"
          ? { user_id: identifier, email, password }
          : { identifier, password, device_label: "web-demo" };

      const path = mode === "register" ? "/auth/register" : "/auth/login";
      const tokens = await apiRequest<AuthResponse>(path, {
        method: "POST",
        body: JSON.stringify(payload)
      });
      window.localStorage.setItem("mindgarden_access_token", tokens.access_token);
      window.localStorage.setItem("mindgarden_refresh_token", tokens.refresh_token);
      router.push("/dashboard");
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-7xl items-center justify-center px-4 py-8 md:px-6">
      <div className="grid w-full gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <section className="glass-card p-8">
          <p className="pill">Secure companion access</p>
          <h1 className="mt-6 font-display text-5xl leading-tight text-pine">
            A calmer system for hard exam seasons.
          </h1>
          <p className="mt-5 max-w-lg leading-7 text-ink/70">
            Log in to your private wellness space, keep your journals encrypted, and let the AI
            companion build context over time.
          </p>
        </section>

        <section className="glass-card p-8">
          <div className="flex gap-2 rounded-full bg-mist p-1">
            {(["login", "register"] as const).map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setMode(item)}
                className={`flex-1 rounded-full px-4 py-3 text-sm font-semibold capitalize transition ${
                  mode === item ? "bg-white text-pine shadow-sm" : "text-ink/65"
                }`}
              >
                {item}
              </button>
            ))}
          </div>

          <form onSubmit={onSubmit} className="mt-6 space-y-4">
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-ink/70">
                {mode === "register" ? "User ID" : "User ID or email"}
              </span>
              <input
                value={identifier}
                onChange={(event) => setIdentifier(event.target.value)}
                className="w-full rounded-2xl border border-ink/10 bg-white/85 px-4 py-3 outline-none ring-0"
                placeholder="neet-warrior-24"
                required
              />
            </label>

            {mode === "register" && (
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-ink/70">Email</span>
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="w-full rounded-2xl border border-ink/10 bg-white/85 px-4 py-3 outline-none ring-0"
                  placeholder="student@example.com"
                  required
                />
              </label>
            )}

            <label className="block">
              <span className="mb-2 block text-sm font-medium text-ink/70">Password</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded-2xl border border-ink/10 bg-white/85 px-4 py-3 outline-none ring-0"
                placeholder="Use a strong password"
                required
              />
            </label>

            {error ? <p className="rounded-2xl bg-coral/15 px-4 py-3 text-sm text-pine">{error}</p> : null}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-2xl bg-pine px-4 py-3 font-semibold text-white transition hover:opacity-95 disabled:opacity-60"
            >
              {loading ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}

