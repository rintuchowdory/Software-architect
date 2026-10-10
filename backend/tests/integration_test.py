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


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_no_redirect_opener = urllib.request.build_opener(NoRedirect)


def call_no_redirect(method, path, body=None):
    """Like call(), but returns (status, {location}) for 3xx responses."""
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", method=method)
    try:
        with _no_redirect_opener.open(req, timeout=10) as r:
            return r.status, {"location": r.headers.get("Location", "")}
    except urllib.error.HTTPError as e:
        # 3xx arrives here when redirects are disabled — keep the Location.
        if 300 <= e.code < 400:
            return e.code, {"location": e.headers.get("Location", "")}
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
        # Deterministic social-provider config (regardless of host env):
        # GitHub "configured" with fake creds, Microsoft unconfigured, Google unset.
        "GITHUB_CLIENT_ID": "ci-fake-github-id",
        "GITHUB_CLIENT_SECRET": "ci-fake-github-secret",
        "MICROSOFT_CLIENT_ID": "",
        "MICROSOFT_CLIENT_SECRET": "",
        "GOOGLE_CLIENT_ID": "",
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

    # --- social providers -----------------------------------------------------
    s, r = call("GET", "/api/auth/providers")
    check(
        "providers: github on, microsoft/google off",
        s == 200 and r.get("github") is True and r.get("microsoft") is False and r.get("google") is False,
        f"{s} {r}",
    )

    s, r = call_no_redirect("GET", "/api/auth/github/authorize?redirect_uri=http://localhost:5173/login")
    check(
        "github authorize: 302 to github.com",
        s == 302 and r.get("location", "").startswith("https://github.com/login/oauth/authorize"),
        f"{s} {r}",
    )

    s, r = call_no_redirect("GET", "/api/auth/github/authorize?redirect_uri=http://evil.example.com/login")
    check("github authorize: rejects foreign redirect_uri (400)", s == 400, f"{s} {r}")

    s, r = call("GET", "/api/auth/microsoft/authorize?redirect_uri=http://localhost:5173/login")
    check("microsoft authorize: 404 when not configured", s == 404, f"{s} {r}")

    s, r = call("GET", "/api/auth/facebook/authorize")
    check("unknown provider authorize: 404", s == 404, f"{s} {r}")

    s, r = call("GET", "/api/auth/github/callback?code=x&state=garbage")
    check("github callback: 400 on invalid state", s == 400, f"{s} {r}")

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
