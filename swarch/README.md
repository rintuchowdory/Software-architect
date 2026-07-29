# Software Architect

A project-management and client-collaboration platform for running a small
software studio solo — client intake, project pipeline, quotes/invoices, and
a dashboard, split into two deployable pieces.

- **`frontend/`** — React + Vite + TypeScript + Tailwind v4. Marketing landing
  page plus the logged-in app (Dashboard, Clients, Projects, Financials).
  Deploys to Vercel.
- **`backend/`** — FastAPI + SQLAlchemy. Auth, clients, projects, invoices,
  dashboard stats. Deploys to Render.

See the README in each folder for local setup and deployment steps.

## Status

Working scaffold: auth, routing, and all four app pages are wired to a real
API with seeded demo data. Not yet built: Stripe checkout, the guided intake
questionnaire, the AI brief/prompt generator, and the public (no-login)
client portal.
