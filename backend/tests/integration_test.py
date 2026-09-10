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
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{db_path}", "JWT_SECRET": "ci-test-secret"}
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

    # --- google endpoint (must fail cleanly when GOOGLE_CLIENT_ID unset) --------
    s, r = call("POST", "/api/auth/google", {"credential": "fake.google.token"})
    check("google endpoint with fake credential: 401 (no 500)", s == 401, f"{s} {r}")


if __name__ == "__main__":
    if not MAIN_PY.exists():
        print(f"backend/main.py not found at {MAIN_PY}")
        sys.exit(2)
    main()
