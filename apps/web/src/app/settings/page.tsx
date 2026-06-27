"use client";

import { useState } from "react";

import { AppShell } from "@/components/app-shell";
import { clearSession, getAccessToken } from "@/lib/auth";
import { apiRequest } from "@/lib/api";

type ActionResponse = {
  message: string;
  token?: string | null;
};

type ReportResponse = {
  id: string;
  content_json: {
    highlights?: string[];
    weekly_reflection?: string;
  };
};

export default function SettingsPage() {
  const [message, setMessage] = useState("");
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [exportData, setExportData] = useState<string>("");

  async function onResetMemory() {
    const token = getAccessToken();
    if (!token) {
      setMessage("Log in first to manage memory.");
      return;
    }

    try {
      const result = await apiRequest<ActionResponse>("/privacy/memory", {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage(result.message);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not reset memory");
    }
  }

  async function onExportData() {
    const token = getAccessToken();
    if (!token) {
      setMessage("Log in first to export data.");
      return;
    }
    try {
      const result = await apiRequest<unknown>("/privacy/export", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setExportData(JSON.stringify(result, null, 2));
      setMessage("Data export prepared.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not export data");
    }
  }

  async function onGenerateReport() {
    const token = getAccessToken();
    if (!token) {
      setMessage("Log in first to generate a report.");
      return;
    }
    try {
      const result = await apiRequest<ReportResponse>("/insights/reports/weekly", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      setReport(result);
      setMessage("Weekly report generated.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not generate report");
    }
  }

  async function onDeleteAccount() {
    const token = getAccessToken();
    if (!token) {
      setMessage("Log in first to delete the account.");
      return;
    }
    try {
      const result = await apiRequest<ActionResponse>("/privacy/account", {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      clearSession();
      setMessage(result.message);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not delete account");
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <section className="glass-card p-6">
          <p className="pill">Privacy center</p>
          <h1 className="mt-5 font-display text-5xl text-pine">Control what the companion keeps.</h1>
          <p className="mt-4 max-w-3xl leading-7 text-ink/70">
            Trust improves when students can inspect, export, and delete what the system remembers.
            These controls are part of the product, not hidden admin actions.
          </p>
        </section>

        <section className="grid gap-4 md:grid-cols-2">
          <div className="glass-card p-6">
            <h2 className="font-display text-3xl text-pine">Memory reset</h2>
            <p className="mt-4 leading-7 text-ink/70">
              Delete learned conversation and journal memory while keeping your account active.
            </p>
            <button
              type="button"
              onClick={onResetMemory}
              className="primary-button mt-6"
            >
              Reset AI memory
            </button>
          </div>

          <div className="glass-card p-6">
            <h2 className="font-display text-3xl text-pine">Data export</h2>
            <p className="mt-4 leading-7 text-ink/70">
              Export profile, journals, mood logs, memories, goals, habits, reports, and conversations.
            </p>
            <button
              type="button"
              onClick={onExportData}
              className="primary-button mt-6"
            >
              Prepare export
            </button>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2">
          <div className="glass-card p-6">
            <h2 className="font-display text-3xl text-pine">Weekly reflection report</h2>
            <p className="mt-4 leading-7 text-ink/70">
              Generate a judge-friendly weekly summary with highlights, risk posture, and reflection guidance.
            </p>
            <button
              type="button"
              onClick={onGenerateReport}
              className="primary-button mt-6"
            >
              Generate report
            </button>
            {report ? (
              <div className="mt-6 rounded-[24px] bg-white/75 p-4 text-sm leading-7 text-ink/70">
                {(report.content_json.highlights || []).map((item) => (
                  <p key={item}>- {item}</p>
                ))}
                <p className="mt-3">{report.content_json.weekly_reflection}</p>
              </div>
            ) : null}
          </div>

          <div className="glass-card p-6">
            <h2 className="font-display text-3xl text-pine">Emergency boundaries</h2>
            <p className="mt-4 leading-7 text-ink/70">
              MindGarden is supportive but not a therapist or emergency service. If a student feels
              unsafe or overwhelmed, the product encourages reaching out to trusted people,
              professionals, or local crisis support right away.
            </p>
            <button
              type="button"
              onClick={onDeleteAccount}
              className="mt-6 rounded-full bg-coral px-6 py-3 font-semibold text-pine"
            >
              Delete account
            </button>
          </div>
        </section>

        <section className="glass-card p-5 text-sm text-ink/65">
          {message || "No recent privacy action."}
          {exportData ? <pre className="mt-4 overflow-x-auto rounded-[24px] bg-night p-4 text-xs text-mist">{exportData}</pre> : null}
        </section>
      </div>
    </AppShell>
  );
}
