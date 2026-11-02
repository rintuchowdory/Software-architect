"""Move the live data into the new Supabase project.

Neither the sandbox nor a laptop can open a Postgres port here, so the transfer
runs over HTTPS in two halves: this script builds the DDL and INSERTs from the
JSON export, then posts them through the Supabase Management API.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

import models

TOKEN = os.environ["SUPABASE_TOKEN"]
REF = os.environ["SUPABASE_REF"]
API = f"https://api.supabase.com/v1/projects/{REF}/database/query"

ORDER = [models.User, models.Client, models.Project, models.Invoice, models.StudioSettings]


def sql_literal(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, dict) and value.get("__type__"):
        stamp = value["value"]
        if value["__type__"] == "datetime":
            return f"TIMESTAMP '{stamp}'"
        return f"DATE '{stamp}'"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return repr(value)
    return "'" + str(value).replace("'", "''") + "'"


def build_statements(payload: dict) -> list[str]:
    dialect = postgresql.dialect()
    statements: list[str] = []

    for model in ORDER:
        statements.append(str(CreateTable(model.__table__).compile(dialect=dialect)))
        for index in model.__table__.indexes:
            statements.append(str(CreateIndex(index).compile(dialect=dialect)))

    for model in ORDER:
        rows = payload["tables"].get(model.__tablename__, [])
        if not rows:
            continue
        columns = [col.name for col in model.__table__.columns]
        values = []
        for row in rows:
            values.append(
                "(" + ", ".join(sql_literal(row.get(col)) for col in columns) + ")"
            )
        statements.append(
            f"INSERT INTO {model.__tablename__} ({', '.join(columns)}) VALUES\n"
            + ",\n".join(values)
            + "\nON CONFLICT (id) DO NOTHING"
        )
    return statements


def run(sql: str) -> list:
    body = json.dumps({"query": sql}).encode()
    req = urllib.request.Request(API, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.loads(response.read() or b"[]")
    except urllib.error.HTTPError as error:
        detail = error.read().decode()[:500]
        raise RuntimeError(f"HTTP {error.code}: {detail}") from None


def main() -> None:
    payload = json.loads(Path(sys.argv[1]).read_text())
    statements = build_statements(payload)

    for statement in statements:
        head = statement.strip().splitlines()[0][:70]
        run(statement)
        print(f"ok  {head}")

    counts = run(
        "select 'users' as t, count(*) from users union all "
        "select 'clients', count(*) from clients union all "
        "select 'projects', count(*) from projects union all "
        "select 'invoices', count(*) from invoices union all "
        "select 'studio_settings', count(*) from studio_settings"
    )
    print("verified:", counts)


if __name__ == "__main__":
    main()
