# CommandHQ Metrics

CommandHQ Metrics is a customer-facing portfolio demo for founders and operators who want one premium operating view across revenue, funnel health, support pressure, and customer risk. It tells a coherent business story in a format that feels closer to an executive operating layer than a generic BI dashboard.

## Target buyer

- SaaS founders who want a more premium internal dashboard
- Operators combining revenue, support, and customer-health reporting
- Product studios or agencies pitching bespoke internal tools for leadership teams

## What it shows

- Executive KPI header row with immediate commercial context
- Chart-style sections for revenue, funnel health, and segment mix
- Support, incident, and customer-health widgets
- Activity timeline plus a drill-down pod panel
- Filters for time range, team, and segment
- A clear path to a commissioned custom build

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

- Replace seeded numbers with warehouse, CRM, and support-system feeds
- Add role-based dashboards, saved views, and account drill-downs
- Layer in alerts, exports, and operating playbooks around the metrics
- Build leadership review and weekly business review workflows on top
