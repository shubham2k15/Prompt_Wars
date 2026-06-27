"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  ArrowRight,
  Brain,
  ChartSpline,
  HeartHandshake,
  LogOut,
  NotebookPen,
  Settings,
  Target,
} from "lucide-react";
import type { ReactNode } from "react";

import { clearSession, getRefreshToken } from "@/lib/auth";
import { apiRequest } from "@/lib/api";

const nav = [
  { href: "/dashboard", label: "Overview", icon: ChartSpline },
  { href: "/chat", label: "Companion", icon: HeartHandshake },
  { href: "/journal", label: "Journal", icon: NotebookPen },
  { href: "/plans", label: "Plans", icon: Target },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  async function onLogout() {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      try {
        await apiRequest<{ message: string }>("/auth/logout", {
          method: "POST",
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      } catch {
        // Clearing the local session is still the most important logout behavior.
      }
    }
    clearSession();
    router.push("/login");
  }

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 px-4 py-6 md:px-6">
      <div className="glass-card flex items-center justify-between gap-4 p-4 lg:hidden">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-pine text-white shadow-lg shadow-pine/20">
            <Brain className="h-6 w-6" />
          </div>
          <div>
            <p className="font-display text-2xl text-pine">MindGarden</p>
            <p className="text-sm text-ink/60">Your calmer exam companion</p>
          </div>
        </Link>
        <button type="button" onClick={onLogout} className="secondary-button">
          <LogOut className="h-4 w-4" />
          Logout
        </button>
      </div>

      <div className="flex gap-6">
      <aside className="glass-card hidden w-80 flex-col justify-between overflow-hidden p-6 lg:flex xl:w-84">
        <div className="space-y-8">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-pine text-white shadow-lg shadow-pine/20">
              <Brain className="h-6 w-6" />
            </div>
            <div>
              <p className="font-display text-2xl">MindGarden</p>
              <p className="text-sm text-ink/60">Companion for exam calm</p>
            </div>
          </Link>

          <nav className="space-y-2">
            {nav.map(({ href, label, icon: Icon }) => {
              const active = pathname.startsWith(href);
              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center gap-3 rounded-2xl px-4 py-3 transition ${
                    active
                      ? "bg-pine text-white shadow-lg shadow-pine/15"
                      : "bg-white/55 text-ink/80 hover:bg-white"
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="rounded-[28px] bg-gradient-to-br from-pine via-pine to-sea p-5 text-white shadow-xl shadow-pine/20">
          <p className="text-sm uppercase tracking-[0.22em] text-white/70">Today&apos;s reminder</p>
          <p className="mt-3 text-lg font-medium leading-7">
            Consistency matters more than intensity. Protect the next small win.
          </p>
          <button type="button" onClick={onLogout} className="mt-5 flex items-center gap-2 text-sm font-semibold text-white/90">
            Log out
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </aside>

      <main className="flex-1 space-y-4">
        <nav className="glass-card flex gap-2 overflow-x-auto p-2 lg:hidden">
          {nav.map(({ href, label, icon: Icon }) => {
            const active = pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={`flex min-w-max items-center gap-2 rounded-2xl px-4 py-3 text-sm font-medium transition ${
                  active ? "bg-pine text-white" : "bg-white/70 text-ink/75"
                }`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>
        {children}
      </main>
      </div>
    </div>
  );
}
