"use client";

import { useMemo, useState } from "react";
import {
  brandVoiceChips,
  outputVariants,
  savedSnippets,
  startupProfile,
  taskModes,
  usageInsights,
} from "@/lib/data";

export function ReplyRocketDashboard() {
  const [selectedMode, setSelectedMode] = useState(taskModes[0].id);

  const activeMode = useMemo(
    () => taskModes.find((mode) => mode.id === selectedMode) ?? taskModes[0],
    [selectedMode],
  );

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8">
      <section className="overflow-hidden rounded-[28px] border border-white/10 bg-white/6 shadow-2xl shadow-sky-950/30 backdrop-blur">
        <div className="grid gap-10 px-5 py-7 sm:px-6 lg:grid-cols-[1.15fr_0.85fr] lg:px-10 lg:py-8">
          <div className="space-y-8">
            <div className="flex flex-wrap items-center gap-3 text-sm text-slate-300">
              <div className="flex items-center gap-3 rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-2 text-cyan-100">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-300 text-xs font-semibold tracking-[0.28em] text-slate-950">
                  RR
                </span>
                <span className="font-medium">ReplyRocket AI</span>
              </div>
              <span className="rounded-full border border-white/10 px-3 py-2">
                Revenue messaging suite
              </span>
            </div>

            <div className="space-y-4">
              <p className="max-w-xl text-sm uppercase tracking-[0.35em] text-sky-200/80">
                Founder-grade communication for sales, success, and support
              </p>
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                Turn scattered message drafting into a polished revenue system your
                team can trust.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-slate-300">
                ReplyRocket gives lean teams one place to lock in brand voice,
                switch between high-stakes reply moments, and ship client-facing
                drafts that already sound approved.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <a
                className="rounded-full bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
                href="#workspace"
              >
                Review live workflow
              </a>
              <a
                className="rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-white transition hover:border-cyan-300/50 hover:bg-white/5"
                href="#custom-build"
              >
                Book custom build
              </a>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {taskModes.slice(0, 3).map((mode) => (
                <div
                  key={mode.id}
                  className="rounded-2xl border border-white/10 bg-slate-950/35 p-4"
                >
                  <p className="text-xs uppercase tracking-[0.25em] text-sky-200/70">
                    {mode.badge}
                  </p>
                  <h2 className="mt-3 text-lg font-semibold text-white">
                    {mode.label}
                  </h2>
                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    {mode.summary}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[24px] border border-cyan-400/20 bg-slate-950/75 p-5 shadow-lg shadow-cyan-950/30 sm:p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm text-slate-400">Workspace status</p>
                <p className="text-2xl font-semibold text-white">Ready for production voice</p>
              </div>
              <div className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-sm text-emerald-200">
                Approval loops reduced
              </div>
            </div>

            <div className="mt-6 space-y-4 rounded-2xl border border-white/8 bg-white/4 p-5">
              <div>
                <p className="text-sm text-slate-400">Brand</p>
                <p className="mt-1 text-lg font-medium text-white">
                  {startupProfile.company}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Offer</p>
                <p className="mt-1 text-sm leading-6 text-slate-200">
                  {startupProfile.product}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Ideal buyer</p>
                <p className="mt-1 text-sm leading-6 text-slate-200">
                  {startupProfile.icp}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Voice direction</p>
                <p className="mt-1 text-sm leading-6 text-slate-200">
                  {startupProfile.tone}
                </p>
              </div>
              <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-4 text-sm leading-6 text-cyan-50">
                {startupProfile.promise}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="workspace" className="grid gap-6 xl:grid-cols-[0.82fr_1.18fr_0.8fr]">
        <div className="rounded-[26px] border border-white/10 bg-slate-950/55 p-5 sm:p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-slate-400">Context setup</p>
              <h2 className="text-2xl font-semibold text-white">Brand inputs</h2>
            </div>
            <span className="rounded-full border border-white/10 px-3 py-1 text-xs uppercase tracking-[0.25em] text-slate-300">
              Ready to reuse
            </span>
          </div>

          <div className="mt-6 space-y-4">
            {[
              ["Company", startupProfile.company],
              ["Product", startupProfile.product],
              ["Ideal customer", startupProfile.icp],
              ["Tone", startupProfile.tone],
            ].map(([label, value]) => (
              <div key={label} className="rounded-2xl border border-white/8 bg-white/4 p-4">
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">
                  {label}
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-200">{value}</p>
              </div>
            ))}
          </div>

          <div className="mt-6">
            <p className="text-sm text-slate-400">Voice rules</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {brandVoiceChips.map((chip) => (
                <button
                  key={chip}
                  className="rounded-full border border-cyan-400/25 bg-cyan-400/10 px-3 py-2 text-sm text-cyan-100"
                  type="button"
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-[26px] border border-white/10 bg-white/6 p-5 shadow-lg shadow-slate-950/20 sm:p-6">
          <div className="flex flex-col gap-4 border-b border-white/10 pb-5">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-sm text-slate-400">Prompt task selector</p>
                <h2 className="text-2xl font-semibold text-white">Draft workspace</h2>
              </div>
              <p className="text-sm text-slate-400">Switch the workflow, keep the voice.</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {taskModes.map((mode) => {
                const isActive = mode.id === activeMode.id;
                return (
                  <button
                    key={mode.id}
                    className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                      isActive
                        ? "bg-cyan-300 text-slate-950"
                        : "border border-white/10 bg-slate-950/40 text-slate-200 hover:bg-white/10"
                    }`}
                    onClick={() => setSelectedMode(mode.id)}
                    type="button"
                  >
                    {mode.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-5 rounded-2xl border border-cyan-400/15 bg-slate-950/55 p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/70">
                  Selected flow
                </p>
                <p className="mt-2 text-lg font-semibold text-white">
                  {activeMode.label}
                </p>
              </div>
              <div className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-sm text-cyan-100">
                {activeMode.win}
              </div>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              {activeMode.summary}
            </p>
          </div>

          <div className="mt-6 grid gap-4">
            {outputVariants.map((variant) => (
              <article
                key={variant.title}
                className="rounded-3xl border border-white/10 bg-slate-950/45 p-5"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-slate-500">
                      {variant.channel}
                    </p>
                    <h3 className="mt-2 text-lg font-semibold text-white">
                      {variant.title}
                    </h3>
                  </div>
                  <span className="rounded-full border border-white/10 px-3 py-1 text-xs uppercase tracking-[0.25em] text-slate-300">
                    {variant.metric}
                  </span>
                </div>
                <p className="mt-4 text-sm leading-7 text-slate-200">
                  {variant.copy}
                </p>
                <p className="mt-4 text-sm font-medium text-cyan-200">
                  Angle: {variant.angle}
                </p>
              </article>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-[26px] border border-white/10 bg-slate-950/55 p-5 sm:p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Messaging assets</p>
                <h2 className="text-2xl font-semibold text-white">Snippet bank</h2>
              </div>
              <span className="rounded-full border border-white/10 px-3 py-1 text-xs uppercase tracking-[0.25em] text-slate-300">
                Reusable
              </span>
            </div>

            <div className="mt-5 space-y-4">
              {savedSnippets.map((snippet) => (
                <article
                  key={snippet.label}
                  className="rounded-2xl border border-white/8 bg-white/4 p-4"
                >
                  <p className="text-xs uppercase tracking-[0.28em] text-slate-500">
                    {snippet.label}
                  </p>
                  <p className="mt-3 text-sm leading-6 text-slate-200">
                    {snippet.text}
                  </p>
                </article>
              ))}
            </div>
          </div>

          <div className="rounded-[26px] border border-cyan-400/20 bg-cyan-400/8 p-5 sm:p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-cyan-100/70">Commercial signal</p>
                <h2 className="text-2xl font-semibold text-white">Adoption pulse</h2>
              </div>
              <span className="text-2xl">↗</span>
            </div>
            <div className="mt-5 grid gap-3">
              {usageInsights.map((item) => (
                <div
                  key={item.label}
                  className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3"
                >
                  <span className="text-sm text-slate-300">{item.label}</span>
                  <span className="text-sm font-semibold text-white">{item.value}</span>
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
            <p className="text-sm uppercase tracking-[0.32em] text-cyan-200/75">
              Custom build path
            </p>
            <h2 className="text-3xl font-semibold text-white">
              Launch a private version tuned to your own outbound, support, or account workflows.
            </h2>
            <p className="max-w-3xl text-base leading-7 text-slate-300">
              This concept can be re-skinned around your voice library, review flow, CRM logic,
              and approval steps so the product feels native to your team from day one.
            </p>
            <div className="grid gap-3 md:grid-cols-3">
              {[
                "Brand voice libraries by team or segment",
                "Private prompt templates and approval states",
                "CRM, helpdesk, or inbox integrations",
              ].map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
                  {item}
                </div>
              ))}
            </div>
          </div>
          <a
            className="inline-flex items-center justify-center rounded-full bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
            href="mailto:demo@example.com?subject=ReplyRocket%20custom%20build"
          >
            Book custom build
          </a>
        </div>
      </section>
    </main>
  );
}
