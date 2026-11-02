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

Visit `http://localhost:5173` for the landing page, `/login` to register or
sign in with email + password (8 characters minimum), and `/app` for the
dashboard.

## API base URL

The app always calls `/api` on its own origin. In dev, Vite proxies that to
`http://localhost:8000`; in production, `vercel.json` rewrites `/api/*` to the
deployed Render backend. There is no `VITE_API_BASE` variable to forget: a
stale value used to point builds at a deleted backend, so it is gone.

If you host this somewhere other than Vercel, add an equivalent `/api/*`
proxy to `https://software-architect-api.onrender.com/api/*` (Cloudflare Pages
`_redirects`, Netlify redirects, nginx `proxy_pass`).

## Deploy to Vercel

1. Import this repo in Vercel. Framework preset: **Vite**.
2. Set the project's **Root Directory** to `frontend` (this is a monorepo).
3. Deploy. `vercel.json` rewrites `/api/*` to the Render backend and every other
   route to `index.html`, so client-side routing (`/app`, `/login`) works on
   refresh and no environment variables are needed.

## What's real vs. stubbed

- **Real:** routing, auth flow (JWT issued by the backend, stored in
  `localStorage`), all four app pages fetch live data from the API, client/project
  creation forms write to the database.
- **Stubbed / next steps:** Stripe checkout, the guided intake questionnaire,
  the AI brief/prompt generator, and the branded client portal (no-login view)
  are not built yet — the feature list from the brief that goes beyond this
  shell. Happy to build any of those next.
