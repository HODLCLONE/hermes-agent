export type TaskMode = {
  id: string;
  label: string;
  summary: string;
  badge: string;
  win: string;
};

export type Variant = {
  title: string;
  channel: string;
  angle: string;
  copy: string;
  metric: string;
};

export const startupProfile = {
  company: "Helio Grove",
  product: "AI-powered client communication workspace for modern service teams",
  icp: "5-40 person teams selling high-trust services, onboarding retainers, or managing premium support",
  tone: "clear, composed, premium, practical, never robotic",
  promise: "Ship production-ready replies in under 90 seconds without diluting voice.",
};

export const taskModes: TaskMode[] = [
  {
    id: "outbound",
    label: "Outbound intro",
    summary: "Open new conversations with a sharp first message built around buyer context.",
    badge: "Pipeline",
    win: "+22% reply rate on founder-led sequences",
  },
  {
    id: "support",
    label: "Support rescue",
    summary: "Calm tense moments fast while protecting trust and premium positioning.",
    badge: "Retention",
    win: "Cuts time-to-first-reply from 3h to 18m",
  },
  {
    id: "objection",
    label: "Objection handling",
    summary: "Turn pricing or timing hesitation into a credible next step.",
    badge: "Sales",
    win: "Improves demo-to-close confidence",
  },
  {
    id: "follow-up",
    label: "Follow-up",
    summary: "Keep warm deals moving with clear proof and low-pressure urgency.",
    badge: "Revenue",
    win: "Keeps high-fit deals from going dark",
  },
];

export const brandVoiceChips = [
  "Confident, never pushy",
  "Use plain-English proof",
  "Respect busy operators",
  "End with one crisp CTA",
];

export const savedSnippets = [
  {
    label: "Proof point",
    text: "Teams usually recover 5-8 hours per week once repeat replies stop bouncing between founders, account managers, and support leads.",
  },
  {
    label: "Founder voice",
    text: "Short version: we help small teams sound as dialed-in as the best-run company in their category.",
  },
  {
    label: "Close",
    text: "If useful, I can mock this inside your workflow and send a tailored version your team can react to immediately.",
  },
];

export const outputVariants: Variant[] = [
  {
    title: "Variant A · consultative intro",
    channel: "Outbound email",
    angle: "Lead with observed friction and a fast operational win",
    metric: "Predicted fit: 91%",
    copy:
      "Hey Maya — I spent a few minutes looking at how agency teams manage onboarding after the sale, and the same issue keeps showing up: strong sales energy followed by a handoff that feels too manual for the client experience you're trying to deliver. Helio Grove gives your team one branded place to collect assets, automate nudges, and keep every touchpoint sounding intentional. If helpful, I can send a version mapped to your current kickoff flow so you can see where the senior time gets reclaimed.",
  },
  {
    title: "Variant B · support recovery",
    channel: "Support reply",
    angle: "Own the miss quickly and preserve the premium feel",
    metric: "Time saved: 14 min",
    copy:
      "Thanks for flagging this — you're right to expect a cleaner handoff here. We've already isolated where the onboarding sequence drifted, and we're resetting the workspace so your team sees the correct assets and next steps immediately. I'll stay with it until the flow is clean, then send a short recap with the exact fix so no one has to chase context twice.",
  },
  {
    title: "Variant C · founder follow-up",
    channel: "Founder follow-up",
    angle: "Use one sharp proof point instead of pressure",
    metric: "Reply probability: 68%",
    copy:
      "Quick follow-up in case this got buried: the reason teams keep buying Helio Grove is simple — it helps a lean operation deliver a bigger-team communication experience. The best fit is usually when replies already sound good, but senior people are still doing too much of the drafting. If that's close to your world, I can send a tailored workflow mock so you can judge it in five minutes, not fifty.",
  },
];

export const usageInsights = [
  { label: "Messages generated", value: "148" },
  { label: "Reusable snippets adopted", value: "73%" },
  { label: "Average approval score", value: "4.8/5" },
  { label: "Weekly operator time saved", value: "11.4 hrs" },
];
