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

## Auth

Email + password only, two endpoints:

| Endpoint | Body | Returns |
| --- | --- | --- |
| `POST /api/auth/register` | `{name, email, password}` | `{access_token, user}` |
| `POST /api/auth/login` | `{email, password}` | `{access_token, user}` |
| `GET /api/auth/me` | none (Bearer token) | `{id, name, email}` |

- Passwords are hashed with PBKDF2-SHA256 (390k iterations, random salt) and
  checked in constant time (see `utils.py`).
- Registration requires 8+ characters and rejects an email that already has a
  password (409). Unknown email and wrong password both return the same
  `401 Invalid email or password`, so the endpoint can't be used to probe for
  accounts.
- The JWT is HS256 signed with `JWT_SECRET` and valid for 7 days.
- Social sign-in (Google, GitHub, Microsoft) has been removed. Accounts that
  were created through Google have no password: signing up again with that
  email sets one.

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

- Password reset by email (needs a transactional mail provider) and refresh
  tokens, so the 7-day JWT can be short-lived.
- Stripe integration for deposits/milestone invoices (webhook → update
  `Invoice.status`).
- The guided intake questionnaire → auto-creates a `Client` + `Project` with a
  generated brief.
- An AI endpoint that turns a project's brief into a build prompt (this is
  where the "copy-paste ready Base44 prompt" feature from the brief would live).
- A no-login client portal view (public read-only project + invoice status by
  share token).

## Moving to another database

The free Render Postgres expires; Supabase and Neon both work because the app
only needs a `DATABASE_URL` (SQLAlchemy creates the schema on startup). To carry
the data over without losing invoices:

```bash
cd backend
DATABASE_URL="postgresql://...render..." python scripts/db_snapshot.py export backup.json
DATABASE_URL="postgresql://...supabase..." python scripts/db_snapshot.py import backup.json
```

Then swap `DATABASE_URL` in the Render service and deploy. The snapshot is plain
JSON, so it also restores into the SQLite fallback for local work. Existing rows
are skipped by id, so importing twice does not duplicate anything.

## Studio details on invoices

`Settings` in the app writes the `studio_settings` row: name, owner, address,
VAT ID / tax number, IBAN, hourly rate and the §19 UStG flag. Environment
variables (`STUDIO_*`, `HOURLY_RATE`) are only the initial value for a fresh
instance, so a clone of the repository contains no personal data. The invoice
print view marks a profile as incomplete until owner, address, email and a tax
reference are filled in.
