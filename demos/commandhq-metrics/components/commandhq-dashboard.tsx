"use client";

import { useState } from "react";
import {
  funnelSeries,
  kpis,
  revenueSeries,
  segmentMix,
  teamPanel,
  timeline,
  widgets,
} from "@/lib/data";

const rangeOptions = ["7 days", "30 days", "Quarter"];
const teamOptions = ["All teams", "Lifecycle", "Support", "Revenue"];
const segmentOptions = ["All segments", "SMB", "Mid-market", "Enterprise"];

export function CommandHQDashboard() {
  const [range, setRange] = useState(rangeOptions[1]);
  const [team, setTeam] = useState(teamOptions[1]);
  const [segment, setSegment] = useState(segmentOptions[1]);

  const revenueMax = Math.max(...revenueSeries);
  const funnelMax = Math.max(...funnelSeries);
  const segmentMax = Math.max(...segmentMix);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8">
      <section className="overflow-hidden rounded-[30px] border border-white/10 bg-white/5 shadow-[0_30px_90px_-50px_rgba(168,85,247,0.55)] backdrop-blur">
        <div className="grid gap-8 px-5 py-7 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-10 lg:py-8">
          <div className="space-y-6">
            <div className="flex flex-wrap items-center gap-3 text-sm text-zinc-300">
              <div className="flex items-center gap-3 rounded-full bg-fuchsia-500/15 px-3 py-2 font-medium text-fuchsia-100">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-fuchsia-300 text-xs font-semibold tracking-[0.28em] text-slate-950">
                  CH
                </span>
                <span>CommandHQ Metrics</span>
              </div>
              <span className="rounded-full border border-white/10 px-3 py-2">
                Executive operating layer
              </span>
            </div>
            <div className="space-y-4">
              <p className="text-sm uppercase tracking-[0.35em] text-fuchsia-200/70">
                Premium decision dashboard for founders and operators
              </p>
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                Give leadership one operating view for revenue momentum, risk,
                service pressure, and team execution.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-zinc-300">
                CommandHQ is built to replace scattered check-ins with one clean,
                board-ready surface that highlights what changed, where risk sits,
                and which team needs attention next.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <a
                className="rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-fuchsia-100"
                href="#dashboard"
              >
                Open control surface
              </a>
              <a
                className="rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-white transition hover:border-fuchsia-300/50 hover:bg-white/5"
                href="#custom-build"
              >
                Book custom build
              </a>
            </div>
          </div>

          <div className="rounded-[26px] border border-white/10 bg-slate-950/45 p-5 sm:p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm text-zinc-400">Executive pulse</p>
                <h2 className="mt-2 text-2xl font-semibold text-white">Board-ready snapshot</h2>
              </div>
              <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-sm text-emerald-200">
                Systems steady
              </span>
            </div>
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              {kpis.map((kpi) => (
                <div key={kpi.label} className="rounded-2xl border border-white/8 bg-white/5 p-4">
                  <p className="text-sm text-zinc-400">{kpi.label}</p>
                  <p className="mt-2 text-3xl font-semibold text-white">{kpi.value}</p>
                  <p className="mt-2 text-sm text-emerald-200">{kpi.delta}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="dashboard" className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-6">
          <div className="rounded-[26px] border border-white/10 bg-white/5 p-5 sm:p-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-sm text-zinc-400">Filters</p>
                <h2 className="text-2xl font-semibold text-white">Control surface</h2>
              </div>
              <div className="grid gap-3 md:grid-cols-3">
                <label className="text-sm text-zinc-300">
                  <span className="mb-2 block">Time range</span>
                  <select
                    className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 outline-none"
                    onChange={(event) => setRange(event.target.value)}
                    value={range}
                  >
                    {rangeOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="text-sm text-zinc-300">
                  <span className="mb-2 block">Team</span>
                  <select
                    className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 outline-none"
                    onChange={(event) => setTeam(event.target.value)}
                    value={team}
                  >
                    {teamOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="text-sm text-zinc-300">
                  <span className="mb-2 block">Segment</span>
                  <select
                    className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 outline-none"
                    onChange={(event) => setSegment(event.target.value)}
                    value={segment}
                  >
                    {segmentOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </div>
            <p className="mt-4 text-sm leading-6 text-zinc-400">
              Viewing <span className="text-white">{range}</span> · <span className="text-white">{team}</span> · <span className="text-white">{segment}</span>
            </p>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <article className="rounded-[26px] border border-white/10 bg-slate-950/45 p-5 sm:p-6">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-zinc-400">Revenue trend</p>
                  <h3 className="text-xl font-semibold text-white">Growth over {range.toLowerCase()}</h3>
                </div>
                <span className="text-sm text-emerald-200">Momentum intact</span>
              </div>
              <div className="mt-6 flex h-56 items-end gap-3">
                {revenueSeries.map((value, index) => (
                  <div key={`${value}-${index}`} className="flex flex-1 flex-col items-center gap-3">
                    <div
                      className="w-full rounded-t-2xl bg-gradient-to-t from-fuchsia-500 via-violet-400 to-cyan-300"
                      style={{ height: `${(value / revenueMax) * 180}px` }}
                    />
                    <span className="text-xs text-zinc-500">W{index + 1}</span>
                  </div>
                ))}
              </div>
            </article>

            <article className="rounded-[26px] border border-white/10 bg-slate-950/45 p-5 sm:p-6">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-zinc-400">Funnel health</p>
                  <h3 className="text-xl font-semibold text-white">Pipeline conversion</h3>
                </div>
                <span className="text-sm text-zinc-400">Lead → won</span>
              </div>
              <div className="mt-6 space-y-4">
                {funnelSeries.map((value, index) => (
                  <div key={`${value}-${index}`}>
                    <div className="mb-2 flex items-center justify-between text-sm text-zinc-300">
                      <span>{["Leads", "Qualified", "Demo", "Proposal", "Won"][index]}</span>
                      <span>{value}%</span>
                    </div>
                    <div className="h-3 rounded-full bg-white/8">
                      <div
                        className="h-3 rounded-full bg-gradient-to-r from-cyan-400 to-fuchsia-500"
                        style={{ width: `${(value / funnelMax) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </div>

          <article className="rounded-[26px] border border-white/10 bg-white/5 p-5 sm:p-6">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-zinc-400">Segment mix</p>
                <h3 className="text-xl font-semibold text-white">Revenue concentration</h3>
              </div>
              <span className="text-sm text-zinc-400">Balanced risk profile</span>
            </div>
            <div className="mt-6 grid gap-4 md:grid-cols-4">
              {segmentMix.map((value, index) => (
                <div key={`${value}-${index}`} className="rounded-2xl border border-white/8 bg-slate-950/45 p-4">
                  <p className="text-sm text-zinc-400">{["SMB", "Mid-market", "Enterprise", "Expansion"][index]}</p>
                  <div className="mt-4 h-32 rounded-2xl bg-white/5 p-3">
                    <div
                      className="h-full rounded-2xl bg-gradient-to-t from-cyan-400/60 to-fuchsia-500/90"
                      style={{ marginTop: `${100 - (value / segmentMax) * 100}%` }}
                    />
                  </div>
                  <p className="mt-4 text-2xl font-semibold text-white">{value}%</p>
                </div>
              ))}
            </div>
          </article>
        </div>

        <div className="space-y-6">
          <div className="grid gap-4">
            {widgets.map((widget) => (
              <div key={widget.title} className="rounded-[24px] border border-white/10 bg-slate-950/45 p-5">
                <p className="text-sm text-zinc-400">{widget.title}</p>
                <p className="mt-2 text-2xl font-semibold text-white">{widget.value}</p>
                <p className="mt-3 text-sm leading-6 text-zinc-300">{widget.note}</p>
              </div>
            ))}
          </div>

          <div className="rounded-[26px] border border-white/10 bg-slate-950/45 p-5 sm:p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-zinc-400">Recent activity</p>
                <h2 className="text-2xl font-semibold text-white">Ops timeline</h2>
              </div>
              <span className="rounded-full border border-white/10 px-3 py-1 text-xs uppercase tracking-[0.25em] text-zinc-300">
                Live-ish
              </span>
            </div>
            <div className="mt-5 space-y-3">
              {timeline.map((event) => (
                <div key={event} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm leading-6 text-zinc-200">
                  {event}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[26px] border border-fuchsia-400/20 bg-fuchsia-500/10 p-5 sm:p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-fuchsia-100/70">Drill-down panel</p>
                <h2 className="text-2xl font-semibold text-white">{teamPanel.team}</h2>
              </div>
              <span className="rounded-full border border-white/10 px-3 py-1 text-sm text-white">
                Owner: {teamPanel.owner}
              </span>
            </div>
            <p className="mt-5 text-sm leading-7 text-zinc-200">{teamPanel.summary}</p>
            <div className="mt-5 grid gap-3">
              {teamPanel.actions.map((action) => (
                <div key={action} className="rounded-2xl border border-white/10 bg-slate-950/45 px-4 py-3 text-sm text-zinc-100">
                  {action}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section
        id="custom-build"
        className="rounded-[28px] border border-white/10 bg-slate-950/50 p-5 sm:p-6 lg:p-8"
      >
        <div className="grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
          <div className="space-y-4">
            <p className="text-sm uppercase tracking-[0.32em] text-fuchsia-200/75">
              Custom build path
            </p>
            <h2 className="text-3xl font-semibold text-white">
              Rebuild this into the operating layer your leadership team actually wants to open daily.
            </h2>
            <p className="max-w-3xl text-base leading-7 text-zinc-300">
              Wire in warehouse data, role-based views, alerting, exports, and account-level
              drill-downs so the dashboard becomes a real internal command center instead of a passive report.
            </p>
            <div className="grid gap-3 md:grid-cols-3">
              {[
                "Role-based views for founders, RevOps, and support leads",
                "Real warehouse, CRM, and support-system data feeds",
                "Alerts, exports, and decision playbooks around the numbers",
              ].map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-zinc-200">
                  {item}
                </div>
              ))}
            </div>
          </div>
          <a
            className="inline-flex items-center justify-center rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-fuchsia-100"
            href="mailto:demo@example.com?subject=CommandHQ%20custom%20build"
          >
            Book custom build
          </a>
        </div>
      </section>
    </main>
  );
}
