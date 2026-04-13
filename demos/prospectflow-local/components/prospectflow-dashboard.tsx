"use client";

import { useMemo, useState } from "react";
import { filters, leads } from "@/lib/data";

export function ProspectFlowDashboard() {
  const [city, setCity] = useState(filters.cities[0]);
  const [niche, setNiche] = useState("All niches");
  const [opportunityType, setOpportunityType] = useState("All opportunities");
  const [selectedLeadId, setSelectedLeadId] = useState(leads[0]?.id ?? 1);

  const filteredLeads = useMemo(() => {
    return leads.filter((lead) => {
      const cityMatch = lead.city === city;
      const nicheMatch = niche === "All niches" || lead.niche === niche;
      const opportunityMatch =
        opportunityType === "All opportunities" ||
        lead.opportunityType === opportunityType;
      return cityMatch && nicheMatch && opportunityMatch;
    });
  }, [city, niche, opportunityType]);

  const selectedLead =
    filteredLeads.find((lead) => lead.id === selectedLeadId) ?? filteredLeads[0] ?? leads[0];

  const pipelineCounts = useMemo(() => {
    return {
      New: filteredLeads.filter((lead) => lead.stage === "New").length,
      Qualified: filteredLeads.filter((lead) => lead.stage === "Qualified").length,
      Proposal: filteredLeads.filter((lead) => lead.stage === "Proposal").length,
    };
  }, [filteredLeads]);

  const averageScore = Math.round(
    filteredLeads.reduce((sum, lead) => sum + lead.score, 0) /
      Math.max(filteredLeads.length, 1),
  );

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8">
      <section className="overflow-hidden rounded-[30px] border border-emerald-900/10 bg-white/85 shadow-[0_30px_90px_-50px_rgba(16,185,129,0.45)] backdrop-blur">
        <div className="grid gap-8 px-5 py-7 sm:px-6 lg:grid-cols-[1.1fr_0.9fr] lg:px-10 lg:py-8">
          <div className="space-y-6">
            <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600">
              <div className="flex items-center gap-3 rounded-full bg-emerald-100 px-3 py-2 font-medium text-emerald-700">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-600 text-xs font-semibold tracking-[0.28em] text-white">
                  PF
                </span>
                <span>ProspectFlow Local</span>
              </div>
              <span className="rounded-full border border-slate-200 px-3 py-2">
                Agency pipeline engine
              </span>
            </div>
            <div className="space-y-4">
              <p className="text-sm uppercase tracking-[0.35em] text-emerald-700/70">
                Opportunity intelligence for local-growth operators
              </p>
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
                Build a cleaner pipeline of local businesses with visible revenue
                upside before the first call.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-slate-600">
                ProspectFlow helps agencies and consultants move from vague
                prospecting to ranked opportunities, practical quick wins, and
                outreach angles that already sound informed.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <a
                className="rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                href="#pipeline"
              >
                Review live pipeline
              </a>
              <a
                className="rounded-full border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-900 transition hover:border-emerald-300 hover:bg-emerald-50"
                href="#custom-build"
              >
                Book custom build
              </a>
            </div>
          </div>

          <div className="rounded-[26px] border border-emerald-100 bg-emerald-50/70 p-5 sm:p-6">
            <p className="text-sm text-emerald-700">Commercial snapshot</p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">
              Prospecting that already speaks in business outcomes.
            </h2>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              {[
                ["Average lead score", `${averageScore}`],
                ["Estimated monthly upside", "$28k+"],
                [
                  "Pitch-ready accounts",
                  `${filteredLeads.filter((lead) => lead.stage !== "New").length}`,
                ],
                ["Fastest win category", "Conversion fixes"],
              ].map(([label, value]) => (
                <div key={label} className="rounded-2xl bg-white p-4 shadow-sm shadow-emerald-100/60">
                  <p className="text-sm text-slate-500">{label}</p>
                  <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="pipeline" className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <div className="rounded-[26px] border border-slate-200 bg-white/90 p-5 sm:p-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-sm text-slate-500">Search controls</p>
                <h2 className="text-2xl font-semibold text-slate-950">Lead scanner</h2>
              </div>
              <div className="grid gap-3 md:grid-cols-3">
                <label className="text-sm text-slate-600">
                  <span className="mb-2 block">City</span>
                  <select
                    className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none"
                    onChange={(event) => {
                      setCity(event.target.value);
                      setSelectedLeadId(
                        leads.find((lead) => lead.city === event.target.value)?.id ??
                          leads[0]?.id ??
                          1,
                      );
                    }}
                    value={city}
                  >
                    {filters.cities.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="text-sm text-slate-600">
                  <span className="mb-2 block">Niche</span>
                  <select
                    className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none"
                    onChange={(event) => setNiche(event.target.value)}
                    value={niche}
                  >
                    <option>All niches</option>
                    {filters.niches.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="text-sm text-slate-600">
                  <span className="mb-2 block">Opportunity</span>
                  <select
                    className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none"
                    onChange={(event) => setOpportunityType(event.target.value)}
                    value={opportunityType}
                  >
                    <option>All opportunities</option>
                    {filters.opportunityTypes.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </div>

            <div className="mt-6 overflow-hidden rounded-3xl border border-slate-200">
              <div className="hidden grid-cols-[1.2fr_0.75fr_0.75fr_0.7fr] gap-3 bg-slate-950 px-5 py-3 text-xs uppercase tracking-[0.3em] text-slate-300 md:grid">
                <span>Business</span>
                <span>Status</span>
                <span>Opportunity</span>
                <span>Score</span>
              </div>
              <div className="divide-y divide-slate-200 bg-white">
                {filteredLeads.map((lead) => {
                  const isActive = lead.id === selectedLead.id;
                  return (
                    <button
                      key={lead.id}
                      className={`grid w-full gap-3 px-4 py-4 text-left transition md:grid-cols-[1.2fr_0.75fr_0.75fr_0.7fr] md:px-5 ${
                        isActive ? "bg-emerald-50" : "hover:bg-slate-50"
                      }`}
                      onClick={() => setSelectedLeadId(lead.id)}
                      type="button"
                    >
                      <div>
                        <p className="font-semibold text-slate-950">{lead.name}</p>
                        <p className="mt-1 text-sm text-slate-500">
                          {lead.city} · {lead.niche}
                        </p>
                      </div>
                      <div className="md:hidden">
                        <div className="flex flex-wrap items-center gap-2 text-sm text-slate-600">
                          <span className="rounded-full bg-slate-100 px-3 py-1">
                            {lead.websiteStatus}
                          </span>
                          <span className="rounded-full bg-emerald-100 px-3 py-1 text-emerald-700">
                            {lead.opportunityType}
                          </span>
                          <span className="rounded-full bg-slate-950 px-3 py-1 font-semibold text-white">
                            {lead.score}
                          </span>
                        </div>
                      </div>
                      <p className="hidden text-sm text-slate-600 md:block">{lead.websiteStatus}</p>
                      <p className="hidden text-sm text-slate-600 md:block">{lead.opportunityType}</p>
                      <div className="hidden items-start justify-start md:flex">
                        <span className="rounded-full bg-slate-950 px-3 py-1 text-sm font-semibold text-white">
                          {lead.score}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {([
              ["New", pipelineCounts.New],
              ["Qualified", pipelineCounts.Qualified],
              ["Proposal", pipelineCounts.Proposal],
            ] as const).map(([stage, count]) => (
              <div key={stage} className="rounded-[24px] border border-slate-200 bg-white/90 p-5">
                <p className="text-sm text-slate-500">{stage}</p>
                <p className="mt-3 text-3xl font-semibold text-slate-950">{count}</p>
                <p className="mt-2 text-sm text-slate-500">Pipeline visibility for clean follow-through</p>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-[26px] border border-slate-200 bg-white/90 p-5 sm:p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-slate-500">Lead detail</p>
                <h2 className="text-2xl font-semibold text-slate-950">Why this account matters</h2>
              </div>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
                {selectedLead.monthlyValue}
              </span>
            </div>

            <div className="mt-6 rounded-3xl border border-emerald-100 bg-emerald-50/70 p-5">
              <p className="text-xs uppercase tracking-[0.3em] text-emerald-700/70">
                {selectedLead.name}
              </p>
              <p className="mt-3 text-sm leading-6 text-slate-700">
                {selectedLead.notes}
              </p>
              <p className="mt-4 text-sm font-medium text-slate-900">
                Primary pain point: {selectedLead.painPoint}
              </p>
            </div>

            <div className="mt-6">
              <p className="text-sm font-medium text-slate-700">Recommended quick wins</p>
              <div className="mt-3 grid gap-3">
                {selectedLead.quickWins.map((win) => (
                  <div key={win} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                    {win}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="rounded-[26px] border border-slate-200 bg-slate-950 p-5 text-white sm:p-6">
            <p className="text-sm text-white/60">Outreach angle</p>
            <h2 className="mt-2 text-2xl font-semibold">Contact-ready opener</h2>
            <p className="mt-5 text-sm leading-7 text-white/85">{selectedLead.outreach}</p>
            <div className="mt-5 flex flex-wrap gap-3">
              <button
                className="rounded-full bg-emerald-300 px-4 py-2 text-sm font-semibold text-slate-950"
                type="button"
              >
                Queue for outreach
              </button>
              <a
                className="rounded-full border border-white/20 px-4 py-2 text-sm font-semibold text-white"
                href="#custom-build"
              >
                Book custom build
              </a>
            </div>
          </div>
        </div>
      </section>

      <section
        id="custom-build"
        className="rounded-[28px] border border-slate-200 bg-white/90 p-5 sm:p-6 lg:p-8"
      >
        <div className="grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
          <div className="space-y-4">
            <p className="text-sm uppercase tracking-[0.32em] text-emerald-700/70">
              Custom build path
            </p>
            <h2 className="text-3xl font-semibold text-slate-950">
              Turn this into a vertical-specific pipeline engine for your own market.
            </h2>
            <p className="max-w-3xl text-base leading-7 text-slate-600">
              Rework the scoring model, data intake, proposal output, and CRM handoff so
              your team sees qualified opportunities and pitch angles in one clean sales layer.
            </p>
            <div className="grid gap-3 md:grid-cols-3">
              {[
                "Vertical-specific scoring and opportunity rules",
                "CRM exports, shortlists, and owner assignment",
                "Proposal-ready outreach copy and audit exports",
              ].map((item) => (
                <div key={item} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                  {item}
                </div>
              ))}
            </div>
          </div>
          <a
            className="inline-flex items-center justify-center rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
            href="mailto:demo@example.com?subject=ProspectFlow%20custom%20build"
          >
            Book custom build
          </a>
        </div>
      </section>
    </main>
  );
}
