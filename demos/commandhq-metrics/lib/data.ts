export const kpis = [
  { label: "Net revenue", value: "$482k", delta: "+14.2% vs last month" },
  { label: "Pipeline coverage", value: "3.4x", delta: "Healthy for next 45 days" },
  { label: "Support backlog", value: "31", delta: "-18% after workflow reset" },
  { label: "Churn watchlist", value: "8", delta: "2 executive follow-ups today" },
];

export const revenueSeries = [52, 61, 58, 72, 76, 84, 96];
export const funnelSeries = [100, 81, 59, 39, 24];
export const segmentMix = [38, 27, 21, 14];

export const widgets = [
  {
    title: "Support load",
    value: "11 awaiting owner",
    note: "Top cause: billing clarification requests from expansion accounts that still need tighter routing.",
  },
  {
    title: "Customer health",
    value: "74% green",
    note: "Mid-market health improved after onboarding handoff fixes and stronger success playbooks.",
  },
  {
    title: "Incident watch",
    value: "1 active",
    note: "No customer-facing outage, but one data sync issue still merits operator attention.",
  },
];

export const timeline = [
  "08:12 · Customer success escalated Northline Health due to onboarding delay risk.",
  "09:05 · Founder review: expansion pipeline now above plan in SMB and mid-market.",
  "10:44 · Support backlog dropped after billing-response routing update shipped.",
  "12:16 · RevOps flagged two enterprise renewals that need executive intervention.",
  "14:31 · Product opened follow-up on export latency for board-report workflows.",
];

export const teamPanel = {
  team: "Lifecycle pod",
  owner: "Dana Mercer",
  summary:
    "This pod owns expansion and retention for accounts between $2k and $12k MRR. Health is improving, but two renewals still need executive attention this week.",
  actions: [
    "Prioritize QBR rescue for Northline Health",
    "Assign billing-response macros to cut support pressure",
    "Push onboarding checklist adoption above 90%",
  ],
};
