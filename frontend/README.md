# Software Architect — Frontend

React + Vite + TypeScript + Tailwind v4. Marketing landing page plus a logged-in
app shell (Dashboard, Clients, Projects, Financials) wired to the FastAPI backend
in the sibling `backend/` folder.

## Local development

```bash
npm install
npm run dev
```

The dev server proxies `/api/*` to `http://localhost:8000` (see `vite.config.ts`),
so run the backend locally on port 8000 alongside this.

Visit `http://localhost:5173` for the landing page, `/login` to sign in (any
email/password works against the demo backend — first sign-in for an email
creates the account), and `/app` for the dashboard.

## Environment variables

Copy `.env.development` as a starting point. In production, set:

```
VITE_API_BASE=https://your-backend.onrender.com/api
```

(There's no proxy in production, so this must be the full URL of your deployed
backend, including the `/api` prefix.)

## Deploy to Vercel

1. Import this repo in Vercel. Framework preset: **Vite**.
2. Set the project's **Root Directory** to `frontend` (this is a monorepo).
3. Set the `VITE_API_BASE` environment variable to your Render backend URL.
4. Deploy. `vercel.json` already rewrites all routes to `index.html` so client-side
   routing (`/app`, `/login`, etc.) works on refresh.

## What's real vs. stubbed

- **Real:** routing, auth flow (JWT issued by the backend, stored in
  `localStorage`), all four app pages fetch live data from the API, client/project
  creation forms write to the database.
- **Stubbed / next steps:** Stripe checkout, the guided intake questionnaire,
  the AI brief/prompt generator, and the branded client portal (no-login view)
  are not built yet — the feature list from the brief that goes beyond this
  shell. Happy to build any of those next.
