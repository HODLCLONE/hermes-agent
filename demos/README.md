# Demo Portfolio Workspace

This workspace contains three independent, buyer-facing demo apps built to help win product, growth, and internal-tools work. Each demo runs on its own and is designed to feel polished enough for a sales call, portfolio walkthrough, or rapid customization sprint.

## Included demos

### ReplyRocket AI
AI sales and support copilot for founders and lean teams. It turns company context into branded outbound emails, support replies, objection handling, and follow-ups with saved voice snippets and lightweight usage analytics.

- Folder: `demos/replyrocket-ai`
- Run: `cd demos/replyrocket-ai && npm install && npm run dev`
- Build: `cd demos/replyrocket-ai && npm run build`
- Lint: `cd demos/replyrocket-ai && npm run lint`

### ProspectFlow Local
Local lead-gen opportunity scanner for agencies, freelancers, and growth operators. It surfaces plausible businesses with weak digital presence, explains why each lead matters, and turns findings into outreach-ready recommendations.

- Folder: `demos/prospectflow-local`
- Run: `cd demos/prospectflow-local && npm install && npm run dev`
- Build: `cd demos/prospectflow-local && npm run build`
- Lint: `cd demos/prospectflow-local && npm run lint`

### CommandHQ Metrics
Premium internal command center for founders and operators. It packages revenue, funnel health, support load, churn risk, and team activity into a presentation-ready dashboard with coherent seeded data.

- Folder: `demos/commandhq-metrics`
- Run: `cd demos/commandhq-metrics && npm install && npm run dev`
- Build: `cd demos/commandhq-metrics && npm run build`
- Lint: `cd demos/commandhq-metrics && npm run lint`

## Notes

- All demos are intentionally independent so they can be shown, deployed, or sold separately.
- Seed data lives inside each app so the portfolio works without external APIs.
- Each app includes a visible customization CTA for buyer conversations.
