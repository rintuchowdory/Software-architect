# Software Architect — Backend

FastAPI + SQLAlchemy (SQLite by default, swap `DATABASE_URL` for Postgres in
production). Provides auth, clients, projects, financials, and dashboard stats
for the frontend in the sibling `software-architect` project.

## Local development

```bash
python3 -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

On first run it seeds three demo clients, four projects, and four invoices so
the dashboard isn't empty. Delete `software_architect.db` to reset.

Interactive API docs: `http://localhost:8000/docs`

## Environment variables

| Variable        | Default                          | Notes                                             |
|-----------------|-----------------------------------|----------------------------------------------------|
| `DATABASE_URL`  | `sqlite:///./software_architect.db` | Use a Postgres URL in production (e.g. Render/Supabase). |
| `JWT_SECRET`    | `dev-secret-change-me`           | **Set a real secret in production.**               |
| `CORS_ORIGINS`  | `http://localhost:5173`          | Comma-separated list of allowed frontend origins.  |

## Auth (demo mode)

`POST /api/auth/login` accepts any email/password. The first sign-in for an
email creates the account with that password; later sign-ins don't hard-fail
on a mismatched password (this is a demo shortcut — swap in a real password
check, or an OAuth/passkey flow, before shipping this for real users).

## Social sign-in providers

Sign-in options are discovered by the frontend via `GET /api/auth/providers`.
A provider appears on the login page only when its credentials are configured:

| Provider | Environment variables | Where to register |
| --- | --- | --- |
| Google | `GOOGLE_CLIENT_ID` | Google Cloud Console → Credentials → OAuth client (used by Google Identity Services) |
| GitHub | `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` | GitHub → Settings → Developer settings → OAuth Apps |
| Microsoft | `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`, `MICROSOFT_TENANT_ID` (default `common`) | Azure Portal → Microsoft Entra ID → App registrations (add a web redirect URI) |

Both OAuth providers use the authorization-code flow with a signed state
parameter (CSRF protection, 10-minute TTL). The provider callback URL to
register is:

```
{FRONTEND_URL}/api/auth/github/callback     # plus /microsoft/callback
```

`FRONTEND_URL` (default `http://localhost:5173`) must be set to the deployed
frontend origin — it is used both for the provider callback URL and for the
post-login redirect back to `/login?token=…`. Accounts are linked by email,
so a user can combine providers on one account.

## Deploy to Render

1. Push this folder to a GitHub repo.
2. In Render, "New +" → "Blueprint" and point it at the repo (`render.yaml` is
   already set up), or create a Web Service manually with:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Set `CORS_ORIGINS` to your deployed Vercel URL.
4. For anything beyond a demo, attach a managed Postgres instance and set
   `DATABASE_URL` to its connection string (SQLite on Render's free tier is
   not persistent across deploys).

## Next steps beyond this scaffold

- Swap the demo auth for real password verification + refresh tokens.
- Stripe integration for deposits/milestone invoices (webhook → update
  `Invoice.status`).
- The guided intake questionnaire → auto-creates a `Client` + `Project` with a
  generated brief.
- An AI endpoint that turns a project's brief into a build prompt (this is
  where the "copy-paste ready Base44 prompt" feature from the brief would live).
- A no-login client portal view (public read-only project + invoice status by
  share token).
