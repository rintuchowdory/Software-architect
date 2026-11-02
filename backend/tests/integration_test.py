"""
End-to-end integration tests for the Software Architect backend.

Self-contained: spawns a real uvicorn server on a free port with a
throwaway SQLite database, exercises the HTTP API through urllib
(no external deps), then shuts the server down.

Run from anywhere:

    python backend/tests/integration_test.py

Exit code 0 = all checks passed, 1 = at least one failure
(the failing checks are printed).

Used by .github/workflows/ci.yml on every push/PR to main.
"""

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent  # backend/
MAIN_PY = BACKEND_DIR / "main.py"

PASS: list[str] = []
FAIL: list[str] = []


def call(method, path, body=None, token=None):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=10) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except Exception:
            return e.code, {}


def check(name, cond, extra=""):
    (PASS if cond else FAIL).append(name)
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"  [{extra}]" if extra and not cond else ""))


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = free_port()


def wait_for_server(proc, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited early with code {proc.returncode}")
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/docs", timeout=2) as r:
                if r.status == 200:
                    return
        except Exception:
            time.sleep(0.3)
    raise RuntimeError("server did not become ready in time")


def main():
    tmp = tempfile.mkdtemp(prefix="sa_it_")
    db_path = os.path.join(tmp, "test.db")
    env = {
        **os.environ,
        "DATABASE_URL": f"sqlite:///{db_path}",
        "JWT_SECRET": "ci-test-secret",
    }
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", str(PORT)],
        cwd=BACKEND_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_server(proc)
        run_checks()
    finally:
        proc.terminate()
        proc.wait(timeout=10)

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    sys.exit(1 if FAIL else 0)


def run_checks():
    ts = int(time.time())
    email = f"integration_{ts}@test.dev"
    pw = "correcthorse123"

    # --- social sign-in is removed (email + password only) -------------------
    s, r = call("GET", "/api/auth/providers")
    check("providers endpoint removed: 404", s == 404, f"{s} {r}")

    s, r = call("POST", "/api/auth/google", {"credential": "fake.google.token"})
    check("google endpoint removed: 404", s == 404, f"{s} {r}")

    s, r = call("GET", "/api/auth/github/authorize?redirect_uri=http://localhost:5173/login")
    check("github authorize removed: 404", s == 404, f"{s} {r}")

    s, r = call("GET", "/api/auth/microsoft/authorize")
    check("microsoft authorize removed: 404", s == 404, f"{s} {r}")

    # --- register -----------------------------------------------------------
    s, r = call("POST", "/api/auth/register", {"name": "Integration Test", "email": email, "password": pw})
    check("register: 200 + token + user", s == 200 and "access_token" in r and r["user"]["email"] == email, f"{s} {r}")

    s, r = call("POST", "/api/auth/register", {"name": "Dup", "email": email, "password": pw})
    check("duplicate email: 409", s == 409, f"{s} {r}")

    s, r = call("POST", "/api/auth/register", {"name": "Short", "email": f"s{ts}@test.dev", "password": "short"})
    check("short password: 422", s == 422, f"{s} {r}")

    s, r = call("POST", "/api/auth/register", {"name": "Bad", "email": "not-an-email", "password": pw})
    check("invalid email: 422", s == 422, f"{s} {r}")

    # --- login ---------------------------------------------------------------
    s, r = call("POST", "/api/auth/login", {"email": email, "password": pw})
    check("login correct: 200 + token", s == 200 and "access_token" in r, f"{s} {r}")
    token = r.get("access_token")

    s, r = call("POST", "/api/auth/login", {"email": email, "password": "wrongpassword"})
    check("wrong password: 401 generic", s == 401 and r.get("detail") == "Invalid email or password", f"{s} {r}")

    s, r = call("POST", "/api/auth/login", {"email": f"nobody_{ts}@test.dev", "password": pw})
    check("unknown email: 401 same message (no account probing)", s == 401 and r.get("detail") == "Invalid email or password", f"{s} {r}")

    # --- protected routes ------------------------------------------------------
    for route in ["/api/dashboard/stats", "/api/clients", "/api/projects",
                  "/api/financials/invoices", "/api/financials/summary"]:
        s, r = call("GET", route, token=token)
        check(f"GET {route} with token: 200", s == 200 and isinstance(r, (list, dict)), f"{s} {str(r)[:80]}")

    s, r = call("GET", "/api/dashboard/stats")
    check("no token: 401", s == 401, f"{s} {r}")

    s, r = call("GET", "/api/dashboard/stats", token="garbage.token.here")
    check("garbage token: 401", s == 401, f"{s} {r}")

    # --- session check -------------------------------------------------------
    s, r = call("GET", "/api/auth/me", token=token)
    check("GET /api/auth/me with token: 200 + matching email", s == 200 and r.get("email") == email, f"{s} {r}")

    s, r = call("GET", "/api/auth/me")
    check("GET /api/auth/me without token: 401", s == 401, f"{s} {r}")

    # --- dashboard overview --------------------------------------------------
    s, r = call("GET", "/api/dashboard/overview", token=token)
    check("overview: 200", s == 200, f"{s} {r}")
    check(
        "overview: KPI fields present",
        all(k in r for k in ("paid_this_month", "outstanding", "pipeline_value", "overdue_amount")),
        str(list(r.keys())),
    )
    check("overview: six revenue months", len(r.get("revenue_series", [])) == 6, str(r.get("revenue_series")))
    check("overview: pipeline has four stages", len(r.get("pipeline", [])) == 4, str(r.get("pipeline")))
    check("overview: actions list present", isinstance(r.get("actions"), list), str(r.get("actions")))

    # --- invoices: numbering, VAT, status ------------------------------------
    s, invoices = call("GET", "/api/financials/invoices", token=token)
    check("invoices: 200 + list", s == 200 and isinstance(invoices, list) and len(invoices) > 0, f"{s}")
    numbers = [i["number"] for i in invoices]
    check("invoices: every invoice numbered RE-YYYY-NNNN",
          all(n.startswith("RE-") and len(n.split("-")) == 3 and n.split("-")[2].isdigit() for n in numbers),
          str(numbers[:3]))
    check("invoices: numbers unique", len(set(numbers)) == len(numbers), str(numbers))
    first = invoices[0]
    net = float(first["amount"].replace(".", "").replace(" €", ""))
    tax = float(first["tax_amount"].replace(".", "").replace(" €", ""))
    total = float(first["total"].replace(".", "").replace(" €", ""))
    check("invoices: total equals net plus tax", abs((net + tax) - total) <= 2, f"{net} + {tax} != {total}")

    project_id = first["project_id"]
    s, created = call("POST", "/api/financials/invoices",
                      {"project_id": project_id, "amount": 1000, "due_date": None}, token=token)
    check("invoice create: 200 + next number", s == 200 and created.get("number") not in numbers, f"{s} {created}")
    check("invoice create: 19% default VAT", created.get("tax_rate") == 19.0 and created.get("tax_amount") == "190 €", str(created))
    check("invoice create: draft status", created.get("status") == "draft", str(created.get("status")))

    s, paid = call("PATCH", f"/api/financials/invoices/{created['id']}", {"status": "paid"}, token=token)
    check("invoice mark paid: paid_at set", s == 200 and paid.get("paid_at") != "", f"{s} {paid}")

    s, r = call("PATCH", f"/api/financials/invoices/{created['id']}", {"status": "banana"}, token=token)
    check("invoice invalid status: 422", s == 422, f"{s} {r}")

    s, r = call("GET", f"/api/financials/invoices/{created['id']}", token=token)
    check("invoice by id: 200", s == 200 and r.get("id") == created["id"], f"{s} {r}")

    s, r = call("GET", "/api/financials/invoices/doesnotexist", token=token)
    check("invoice by id unknown: 404", s == 404, f"{s} {r}")

    # --- studio profile (invoice sender block) -------------------------------
    s, r = call("GET", "/api/studio/profile", token=token)
    check("studio profile: 200 + completeness flag", s == 200 and "complete" in r, f"{s} {r}")

    # --- public intake: no login, generates brief + project ------------------
    s, r = call("GET", "/api/public/intake/options")
    check("intake options: public 200 + types/features",
          s == 200 and len(r.get("project_types", [])) > 3 and len(r.get("features", [])) > 5, f"{s} {r}")

    intake_body = {
        "project_type": "shop",
        "goal": "Handgemachte Kerzen online verkaufen",
        "features": ["payments", "cms"],
        "timeline": "8w",
        "budget": "4000",
        "client_name": "Intake Tester",
        "company": "Kerzen GmbH",
        "email": f"intake_{ts}@test.dev",
    }
    s, intake = call("POST", "/api/public/intake", intake_body)
    check("intake submit: public 200", s == 200, f"{s} {intake}")
    check("intake submit: brief with estimate",
          intake.get("hours", 0) > 0 and "€" in intake.get("estimate_low", "") and "## Umfang" in intake.get("brief", ""),
          str(intake)[:200])
    check("intake submit: hours match feature sum", intake.get("hours") == 110, str(intake.get("hours")))

    s, r = call("POST", "/api/public/intake", {**intake_body, "project_type": "spaceship"})
    check("intake unknown project type: 422", s == 422, f"{s} {r}")

    s, projects = call("GET", "/api/projects", token=token)
    intake_project = next((p for p in projects if p["id"] == intake.get("project_id")), None)
    check("intake created a project visible to the studio",
          intake_project is not None and intake_project["stage"] == "intake" and intake_project["has_brief"],
          str(intake_project))

    s, clients = call("GET", "/api/clients", token=token)
    check("intake created a lead client",
          any(c["email"] == intake_body["email"] and c["status"] == "lead" for c in clients), str(clients)[:200])

    s, r = call("POST", f"/api/projects/{intake['project_id']}/brief", token=token)
    check("regenerate brief from intake answers: 200", s == 200 and r.get("has_brief"), f"{s} {r}")

    # manual project without intake answers cannot be regenerated
    s, manual_client = call("POST", "/api/clients",
                            {"name": "Manual", "email": f"manual_{ts}@test.dev"}, token=token)
    s, manual_project = call("POST", "/api/projects",
                             {"name": "Manual project", "client_id": manual_client["id"]}, token=token)
    s, r = call("POST", f"/api/projects/{manual_project['id']}/brief", token=token)
    check("regenerate brief without intake answers: 422", s == 422, f"{s} {r}")

    # --- rate limit on the public endpoint ----------------------------------
    statuses = []
    for _ in range(4):
        s, _r = call("POST", "/api/public/intake", intake_body)
        statuses.append(s)
    check("intake rate limit kicks in after 5 per hour", 429 in statuses, str(statuses))

    # --- legacy (password-less) account can set a password on sign-up --------
    s, r = call("POST", "/api/auth/register", {"name": "", "email": email, "password": "anotherpass123"})
    check("register on account that already has a password: 409", s == 409, f"{s} {r}")


if __name__ == "__main__":
    if not MAIN_PY.exists():
        print(f"backend/main.py not found at {MAIN_PY}")
        sys.exit(2)
    main()
