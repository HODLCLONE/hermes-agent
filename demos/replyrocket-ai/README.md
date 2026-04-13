# ReplyRocket AI

ReplyRocket AI is a customer-facing portfolio demo for an internal communication product that helps lean teams draft outbound, support, and follow-up messages with a consistent premium voice. The product story is simple: define the brand once, choose the moment, and generate polished replies that already feel approved.

## Target buyer

- Founders running lean GTM or customer-success teams
- Agencies or productized-service firms that want a branded AI messaging layer
- Startups that need useful internal AI software without a heavyweight implementation

## What it shows

- Brand setup panel for company context, offer, ideal buyer, and voice direction
- Four task modes: outbound, support rescue, objection handling, and follow-up
- Three generated response variants in a premium dark workspace
- Reusable voice rules and snippet bank for team consistency
- Commercial proof metrics and a clear path to a commissioned custom build

## Local run

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## Verification

```bash
npm run build
npm run lint
```

## Customization ideas

- Connect real LLM providers and usage tracking
- Save brand voice libraries by team, product line, or customer segment
- Add inbox, CRM, or helpdesk integrations with approval states
- Turn the proof metrics into admin analytics and billing hooks
