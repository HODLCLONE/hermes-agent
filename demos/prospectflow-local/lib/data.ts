export type Lead = {
  id: number;
  name: string;
  city: string;
  niche: string;
  score: number;
  websiteStatus: string;
  opportunityType: string;
  monthlyValue: string;
  painPoint: string;
  notes: string;
  quickWins: string[];
  outreach: string;
  stage: "New" | "Qualified" | "Proposal";
};

export const filters = {
  cities: ["Austin", "Nashville", "Denver", "Charlotte"],
  niches: ["Dental", "HVAC", "Legal", "Home services"],
  opportunityTypes: ["Slow site", "Weak SEO", "No conversion funnel", "Old branding"],
};

export const leads: Lead[] = [
  {
    id: 1,
    name: "Riverside Dental Studio",
    city: "Austin",
    niche: "Dental",
    score: 94,
    websiteStatus: "Weak booking path on mobile",
    opportunityType: "No conversion funnel",
    monthlyValue: "$2.8k - $4.5k",
    painPoint: "Strong reviews, weak lead capture where most patients actually browse.",
    notes:
      "Excellent reputation and premium photography, but the first-screen booking path is too soft for high-intent mobile traffic.",
    quickWins: ["Add sticky booking CTA", "Create implants landing page", "Install trust-led review rail"],
    outreach:
      "You already have trust in-market — the leak is conversion. I mapped three homepage fixes that could turn more of your existing traffic into booked consults without pushing spend higher.",
    stage: "Qualified",
  },
  {
    id: 2,
    name: "Cedar Peak HVAC",
    city: "Austin",
    niche: "HVAC",
    score: 88,
    websiteStatus: "Slow emergency-service pages",
    opportunityType: "Slow site",
    monthlyValue: "$3.2k - $6.1k",
    painPoint: "Urgent buyers wait too long before seeing the offer and next step.",
    notes:
      "The brand feels credible, but mobile speed and CTA hierarchy likely suppress the highest-intent weekend jobs.",
    quickWins: ["Compress hero media", "Add service-area trust badges", "Launch emergency booking page"],
    outreach:
      "Your site is probably losing urgent jobs before visitors even reach the offer. We can tighten speed, make the emergency CTA obvious, and improve conversion fast.",
    stage: "Proposal",
  },
  {
    id: 3,
    name: "Harbor Family Law",
    city: "Nashville",
    niche: "Legal",
    score: 91,
    websiteStatus: "Thin authority pages",
    opportunityType: "Weak SEO",
    monthlyValue: "$4.0k - $7.5k",
    painPoint: "Search visibility does not match the premium trust the firm already projects.",
    notes:
      "The brand reads trustworthy and established, but practice pages are too generic to win local authority or stronger consult intent.",
    quickWins: ["Rewrite service pages", "Add local authority schema", "Build consult booking funnel"],
    outreach:
      "You already look like a premium firm — the website just isn't carrying that authority into search or conversion. I can show the exact pages I would rebuild first.",
    stage: "Qualified",
  },
  {
    id: 4,
    name: "Oakline Remodel Co.",
    city: "Denver",
    niche: "Home services",
    score: 86,
    websiteStatus: "Strong gallery, weak estimate flow",
    opportunityType: "No conversion funnel",
    monthlyValue: "$3.5k - $5.2k",
    painPoint: "Buyers admire the work but are not guided into a confident next step.",
    notes:
      "Visual proof is strong, but the estimate path is buried and the site leaves financing questions unanswered too late.",
    quickWins: ["Add estimate CTA", "Create financing explainer", "Build neighborhood project pages"],
    outreach:
      "Your work looks expensive in the best way. The missed opportunity is that visitors admire the portfolio without being guided into a quote request.",
    stage: "New",
  },
  {
    id: 5,
    name: "Queen City Smile Care",
    city: "Charlotte",
    niche: "Dental",
    score: 83,
    websiteStatus: "Dated visual trust layer",
    opportunityType: "Old branding",
    monthlyValue: "$2.4k - $3.9k",
    painPoint: "The reputation is strong, but the digital front door feels older than the experience patients expect.",
    notes:
      "Brand inconsistencies and soft CTA design reduce premium trust, especially against newer clinics in the market.",
    quickWins: ["Refresh homepage visuals", "Unify trust modules", "Add treatment pricing lead magnet"],
    outreach:
      "Your reputation is doing the heavy lifting. A cleaner digital front-end would help the site match the quality patients likely experience in person.",
    stage: "New",
  },
  {
    id: 6,
    name: "Blue Mesa Cooling",
    city: "Denver",
    niche: "HVAC",
    score: 89,
    websiteStatus: "Thin location-page system",
    opportunityType: "Weak SEO",
    monthlyValue: "$3.0k - $5.8k",
    painPoint: "Strong service footprint, but not enough local search coverage where demand is already there.",
    notes:
      "Clear opportunity to win more near-me and branded traffic with better neighborhood depth and review markup.",
    quickWins: ["Launch neighborhood pages", "Improve review markup", "Add seasonal maintenance offer"],
    outreach:
      "You already have the footprint to dominate more local search. The quickest win is a tighter location-page system built around high-intent service terms.",
    stage: "Qualified",
  },
  {
    id: 7,
    name: "Summit Injury Counsel",
    city: "Charlotte",
    niche: "Legal",
    score: 90,
    websiteStatus: "Weak consultation flow",
    opportunityType: "No conversion funnel",
    monthlyValue: "$4.8k - $8.2k",
    painPoint: "Traffic lands, but anxious visitors are not given a confident intake path quickly enough.",
    notes:
      "High-value case opportunity if intake gets simplified and trust signals are sequenced earlier in the visit.",
    quickWins: ["Redesign consultation CTA", "Clarify contingency offer", "Add urgency proof blocks"],
    outreach:
      "You likely have enough attention already — the issue is that the site isn't guiding anxious visitors into a strong first step. That's fixable without a full rebuild.",
    stage: "Proposal",
  },
  {
    id: 8,
    name: "Greenway Family Dental",
    city: "Nashville",
    niche: "Dental",
    score: 85,
    websiteStatus: "Late mobile booking CTA",
    opportunityType: "No conversion funnel",
    monthlyValue: "$2.6k - $4.2k",
    painPoint: "Mobile users do not see the booking action early enough to act fast.",
    notes:
      "The gap is mostly UX, which makes this feel like a practical near-term win rather than a heavyweight redesign.",
    quickWins: ["Sticky booking bar", "Insurance explainer strip", "Text-us widget"],
    outreach:
      "This is the kind of site where small UX changes can produce outsized gains. I can show you a mobile-first version that makes booking much easier.",
    stage: "New",
  },
  {
    id: 9,
    name: "Mile High Roofing Partners",
    city: "Denver",
    niche: "Home services",
    score: 87,
    websiteStatus: "Outdated quote request flow",
    opportunityType: "Old branding",
    monthlyValue: "$3.9k - $6.0k",
    painPoint: "The trust signals are strong, but the conversion path feels older than the brand deserves.",
    notes:
      "Storm-season positioning is credible, yet the quote form and financing presentation create preventable drop-off.",
    quickWins: ["Modernize quote funnel", "Add financing banner", "Create hail-damage landing page"],
    outreach:
      "You already have the trust signals most roofers wish they had. The gap is that your conversion flow feels older than the brand deserves.",
    stage: "Qualified",
  },
  {
    id: 10,
    name: "Volunteer Cooling & Heat",
    city: "Nashville",
    niche: "HVAC",
    score: 82,
    websiteStatus: "Weak speed and service depth",
    opportunityType: "Slow site",
    monthlyValue: "$2.7k - $4.8k",
    painPoint: "Service urgency does not translate into enough clarity or momentum on-site.",
    notes:
      "Good local brand, but page speed and service-page depth likely suppress conversion when demand is hottest.",
    quickWins: ["Speed cleanup", "Service-plan offer page", "After-hours CTA hierarchy"],
    outreach:
      "The jobs are there — the website just isn't helping enough when someone needs service fast. We can fix the quick wins first and make the revenue case obvious.",
    stage: "New",
  },
];
