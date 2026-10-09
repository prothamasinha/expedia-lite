
"""IST 402 Assignment 2.2 - SQLite-grounded hotel chatbot."""

import json
import os
import re
import sqlite3
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "expedia_lite.db"
load_dotenv(BASE_DIR / ".env")

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "nvidia/nemotron-3-ultra-550b-a55b:free"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

MAX_RESULTS = 40

router = APIRouter(
    prefix="/chat",
    tags=["AI Hotel Chatbot"]
)

ALLOWED_TABLES = {
    "saved_hotels",
    "demo_hotel_nights"
}

ALLOWED_FUNCTIONS = {
    "abs", "avg", "coalesce", "count", "date",
    "datetime", "glob", "ifnull", "instr",
    "julianday", "length", "like", "lower",
    "ltrim", "max", "min", "nullif", "round",
    "rtrim", "strftime", "substr", "sum",
    "time", "total", "trim", "upper"
}


class ChatQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=500)


# --------------------------------------------------
# STEP 1 - OPENROUTER LLM REQUEST
# --------------------------------------------------

def call_llm(messages, max_tokens=4096):

    api_key = os.getenv(
        "OPENROUTER_API_KEY", ""
    ).strip()

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Missing OPENROUTER_API_KEY in backend/.env"
        )

    last_finish_reason = "unknown"

    # Retry once if the model returns no visible answer.
    for attempt in range(2):

        payload = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0,
            "max_tokens": (
                max_tokens if attempt == 0 else 8192
            ),
            "reasoning": {
                "effort": (
                    "low" if attempt == 0 else "minimal"
                )
            }
        }

        try:
            response = requests.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "X-OpenRouter-Title": "Expedia Lite IST 402"
                },
                json=payload,
                timeout=100
            )

        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=504,
                detail="OpenRouter timed out."
            )

        except requests.exceptions.RequestException:
            raise HTTPException(
                status_code=502,
                detail="Cannot connect to OpenRouter."
            )

        if response.status_code == 429:
            raise HTTPException(
                status_code=503,
                detail="OpenRouter rate limit reached."
            )

        if response.status_code in (401, 403):
            raise HTTPException(
                status_code=502,
                detail="OpenRouter API key or model access rejected."
            )

        if not response.ok:
            raise HTTPException(
                status_code=502,
                detail=(
                    f"OpenRouter error {response.status_code}. "
                    "Check the selected model."
                )
            )

        try:
            data = response.json()
            choice = data["choices"][0]
            message = choice.get("message") or {}
            content = message.get("content")

            last_finish_reason = (
                choice.get("finish_reason") or "unknown"
            )

            if isinstance(content, list):
                content = "\n".join(
                    item.get("text", "")
                    for item in content
                    if isinstance(item, dict)
                )

            if isinstance(content, str) and content.strip():
                return content.strip()

        except (
            ValueError,
            TypeError,
            KeyError,
            IndexError,
            AttributeError
        ):
            last_finish_reason = "invalid response"

    raise HTTPException(
        status_code=502,
        detail=(
            "OpenRouter returned no visible answer after "
            f"a retry (finish_reason={last_finish_reason}). "
            "The free reasoning model may be busy or "
            "out of output tokens."
        )
    )


# --------------------------------------------------
# STEP 2 - CLEAN GENERATED SQL
# --------------------------------------------------

def normalize_sql(raw_sql):

    sql = raw_sql.strip()

    sql = re.sub(
        r"^```(?:sql)?\s*",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"\s*```$",
        "",
        sql
    ).strip()

    sql = re.sub(
        r"^SQL\s*:\s*",
        "",
        sql,
        flags=re.IGNORECASE
    )

    # Allow one final semicolon, but no interior ones.
    if sql.endswith(";"):
        sql = sql[:-1].rstrip()

    return sql


# --------------------------------------------------
# STEP 3 - FIRST LLM CALL: GENERATE SQL
# --------------------------------------------------

def generate_sql(question):

    prompt = """
You produce SQLite SQL for a hotel comparison application.

The only accessible tables are:

saved_hotels(
    place_id TEXT PRIMARY KEY,
    hotel_name TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    postcode TEXT,
    latitude REAL,
    longitude REAL,
    search_zip TEXT,
    saved_at TEXT
)

demo_hotel_nights(
    place_id TEXT,
    stay_date TEXT,
    nightly_rate_usd REAL,
    rooms_available INTEGER
)

Join these tables using place_id.

RULES:
- Return exactly ONE SELECT statement.
- Return SQL only, without markdown or explanations.
- Do not use CTEs, comments, or multiple statements.
- Never use INSERT, UPDATE, DELETE, DROP or writes.
- Only use saved_hotels and demo_hotel_nights.
- Never query the original Assignment 1 tables.
- Include LIMIT 40 or less.
- Prices and availability are SIMULATED.
- They are not real hotel booking information.
- For multi-night stays, check every requested night.
- Include check-in but exclude checkout.
- Use SUM(nightly_rate_usd) for total stay costs.
- Count the nights retrieved.
- Every requested night must exist and have
  rooms_available > 0 for the entire stay
  to be considered available.
- Missing nights must not count as available.
- Do not invent prices, dates, or records.
"""

    result = call_llm([
        {
            "role": "system",
            "content": prompt
        },
        {
            "role": "user",
            "content": (
                f"Current date: {date.today().isoformat()}\n"
                f"Question: {question}"
            )
        }
    ])

    return normalize_sql(result)


# --------------------------------------------------
# STEP 4 - VALIDATE AND EXECUTE SAFE SQLITE
# --------------------------------------------------

def safe_query(proposed_sql):

    sql = normalize_sql(proposed_sql)

    if not sql or len(sql) > 6000:
        raise ValueError(
            "Empty or excessively long SQL."
        )

    if not re.match(
        r"^SELECT\b",
        sql,
        flags=re.IGNORECASE
    ):
        raise ValueError(
            "Only SELECT statements are allowed."
        )

    if (
        ";" in sql
        or "--" in sql
        or "/*" in sql
        or "*/" in sql
    ):
        raise ValueError(
            "Multiple statements and comments are forbidden."
        )

    forbidden = (
        r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|"
        r"ALTER|ATTACH|DETACH|PRAGMA|REPLACE|"
        r"VACUUM|TRIGGER|REINDEX)\b"
    )

    if re.search(
        forbidden,
        sql,
        re.IGNORECASE
    ):
        raise ValueError(
            "A forbidden SQL operation was proposed."
        )

    if not re.search(
        r"\b(FROM|JOIN)\s+"
        r"(saved_hotels|demo_hotel_nights)\b",
        sql,
        flags=re.IGNORECASE
    ):
        raise ValueError(
            "Query must retrieve the approved local hotel tables."
        )

    if not DB_PATH.exists():
        raise ValueError(
            "SQLite database is missing."
        )

    connection = sqlite3.connect(
        DB_PATH.as_uri() + "?mode=ro",
        uri=True,
        timeout=5
    )

    connection.row_factory = sqlite3.Row

    # Only allow reading approved tables and functions.
    def authorizer(action, arg1, arg2, database, source):

        if action == sqlite3.SQLITE_SELECT:
            return sqlite3.SQLITE_OK

        if (
            action == sqlite3.SQLITE_READ
            and arg1 in ALLOWED_TABLES
        ):
            return sqlite3.SQLITE_OK

        if (
            action == sqlite3.SQLITE_FUNCTION
            and (arg2 or "").lower() in ALLOWED_FUNCTIONS
        ):
            return sqlite3.SQLITE_OK

        return sqlite3.SQLITE_DENY

    connection.set_authorizer(authorizer)

    # Prevent excessively expensive queries.
    progress = [0]

    def limit_work():
        progress[0] += 1
        return 1 if progress[0] > 300 else 0

    connection.set_progress_handler(
        limit_work,
        1000
    )

    try:
        bounded_sql = (
            f"SELECT * FROM ({sql}) AS results "
            f"LIMIT {MAX_RESULTS}"
        )

        rows = connection.execute(
            bounded_sql
        ).fetchall()

        return [dict(row) for row in rows]

    except sqlite3.DatabaseError as error:
        raise ValueError(
            "Read-only SQL validation/execution rejected: "
            + str(error)
        )

    finally:
        connection.close()


# --------------------------------------------------
# STEP 5 - SECOND LLM CALL: GROUNDED ANSWER
# --------------------------------------------------

def generate_answer(question, records):

    instructions = """
You are an AI hotel comparison assistant.

Answer ONLY from the supplied SQLite records.

Important rules:
- Records come from locally saved hotels.
- Prices and availability are SIMULATED course data.
- They are not live prices or bookable rooms.
- Never claim a real booking has been made.
- Never invent hotels, prices, dates, or availability.
- Give hotel names, dates, costs, and room availability
  only when the retrieved records support them.
- For multi-night stays, check every requested night.
- Missing dates cannot count as available.
- Use total stay costs for multi-night comparisons.
- If the records are empty, clearly say no
  matching local data was retrieved.
- Be concise, specific, and helpful.
"""

    return call_llm(
        [
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    "Retrieved SQLite records (JSON):\n"
                    + json.dumps(records, indent=2)
                )
            }
        ],
        max_tokens=4096
    )


# --------------------------------------------------
# STEP 6 - COMPLETE RAG CHATBOT ENDPOINT
# --------------------------------------------------

@router.post("/ask")
def ask_hotel_chatbot(request: ChatQuestion):

    question = request.question.strip()

    if len(question) < 3:
        raise HTTPException(
            status_code=422,
            detail="Enter a hotel question."
        )

    # First LLM call: propose SQL.
    proposed_sql = generate_sql(question)

    # Backend validates and retrieves SQLite records.
    try:
        records = safe_query(proposed_sql)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsafe or invalid SQL rejected.",
                "reason": str(error),
                "proposed_sql": proposed_sql
            }
        )

    # Second LLM call: grounded answer.
    answer = generate_answer(
        question,
        records
    )

    return {
        "question": question,
        "proposed_sql": proposed_sql,
        "retrieved_records": records,
        "row_count": len(records),
        "answer": answer,
        "model": MODEL,
        "simulated_data": True,
        "notice": (
            "Hotel rates and availability are simulated "
            "course data, not live bookings."
        )
    }
