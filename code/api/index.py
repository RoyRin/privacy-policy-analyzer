import hashlib
import json
import os
import re
import sqlite3
import time
from datetime import datetime
from html.parser import HTMLParser
from io import BytesIO
from urllib.parse import urlparse

import requests as http_requests
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader

# --- Config ---

SECRETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "SECRETS")

# Try to load OpenRouter key from file, fall back to env var (for Vercel)
_key_path = os.path.join(SECRETS_DIR, "openrouter.key")
if os.path.exists(_key_path):
    with open(_key_path) as f:
        OPENROUTER_API_KEY = f.read().strip()
else:
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

MODEL = "anthropic/claude-haiku-4.5"
BUDGET_TOTAL = 20.0   # $20 lifetime
BUDGET_DAILY = 10.0   # $10 per day
CACHE_TTL = 86400 * 7  # 7 days in seconds

# OpenRouter pricing for Claude 3.5 Haiku (per million tokens)
INPUT_COST_PER_M = 1.0
OUTPUT_COST_PER_M = 5.0

# Check same dir first (Vercel bundles api/ together), then parent (local dev)
for _p in [
    os.path.join(os.path.dirname(__file__), "rubric.md"),
    os.path.join(os.path.dirname(__file__), "..", "rubric.md"),
    os.path.join(os.getcwd(), "rubric.md"),
    os.path.join(os.getcwd(), "api", "rubric.md"),
]:
    if os.path.exists(_p):
        _rubric_path = _p
        break
else:
    raise FileNotFoundError("rubric.md not found")
with open(_rubric_path) as f:
    RUBRIC_PROMPT = f.read()


# --- Database (Postgres on Vercel, SQLite locally) ---

POSTGRES_URL = os.environ.get("POSTGRES_URL", "")
USE_POSTGRES = bool(POSTGRES_URL)

if USE_POSTGRES:
    import pg8000

_INIT_SQL_PG = [
    """CREATE TABLE IF NOT EXISTS cache (
        key TEXT PRIMARY KEY,
        result TEXT,
        created_at DOUBLE PRECISION
    )""",
    """CREATE TABLE IF NOT EXISTS spend (
        id SERIAL PRIMARY KEY,
        cost DOUBLE PRECISION,
        created_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS history (
        id SERIAL PRIMARY KEY,
        url TEXT,
        name TEXT,
        overall_score DOUBLE PRECISION,
        handling DOUBLE PRECISION,
        user_control DOUBLE PRECISION,
        transparency DOUBLE PRECISION,
        collection_security DOUBLE PRECISION,
        result TEXT,
        created_at TEXT
    )""",
]

_INIT_SQL_SQLITE = [
    """CREATE TABLE IF NOT EXISTS cache (
        key TEXT PRIMARY KEY,
        result TEXT,
        created_at REAL
    )""",
    """CREATE TABLE IF NOT EXISTS spend (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cost REAL,
        created_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        name TEXT,
        overall_score REAL,
        handling REAL,
        user_control REAL,
        transparency REAL,
        collection_security REAL,
        result TEXT,
        created_at TEXT
    )""",
]

_db_initialized = False


def get_db():
    global _db_initialized
    if USE_POSTGRES:
        parsed = urlparse(POSTGRES_URL)
        conn = pg8000.connect(
            host=parsed.hostname, port=parsed.port or 5432,
            user=parsed.username, password=parsed.password,
            database=parsed.path.lstrip("/"), ssl_context=True,
        )
        conn.autocommit = False
        if not _db_initialized:
            cur = conn.cursor()
            for sql in _INIT_SQL_PG:
                cur.execute(sql)
            conn.commit()
            _db_initialized = True
        return conn
    else:
        db_path = os.path.join(os.path.dirname(__file__), "..", "data", "analyzer.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        if not _db_initialized:
            for sql in _INIT_SQL_SQLITE:
                conn.execute(sql)
            conn.commit()
            _db_initialized = True
        return conn


def db_execute(conn, sql, params=None):
    """Execute SQL, handling placeholder differences between Postgres (%s) and SQLite (?)."""
    if USE_POSTGRES:
        sql = sql.replace("?", "%s")
    cur = conn.cursor()
    cur.execute(sql, params or ())
    return cur


class BudgetExceeded(Exception):
    pass


def check_budget():
    conn = get_db()
    try:
        total = db_execute(conn, "SELECT COALESCE(SUM(cost), 0) FROM spend").fetchone()[0]
        if total >= BUDGET_TOTAL:
            raise BudgetExceeded(f"Total budget of ${BUDGET_TOTAL:.0f} exceeded (${total:.2f} spent)")

        today = datetime.utcnow().strftime("%Y-%m-%d")
        daily = db_execute(conn,
            "SELECT COALESCE(SUM(cost), 0) FROM spend WHERE created_at LIKE ?",
            (today + "%",)
        ).fetchone()[0]
        if daily >= BUDGET_DAILY:
            raise BudgetExceeded(f"Daily budget of ${BUDGET_DAILY:.0f} exceeded (${daily:.2f} spent today)")
    finally:
        conn.close()


def record_spend(cost):
    conn = get_db()
    try:
        db_execute(conn, "INSERT INTO spend (cost, created_at) VALUES (?, ?)",
                    (cost, datetime.utcnow().isoformat()))
        conn.commit()
    finally:
        conn.close()


def get_cached(key):
    conn = get_db()
    try:
        row = db_execute(conn, "SELECT result, created_at FROM cache WHERE key = ?", (key,)).fetchone()
        if row and (time.time() - row[1]) < CACHE_TTL:
            return json.loads(row[0])
        return None
    finally:
        conn.close()


def set_cached(key, result):
    conn = get_db()
    try:
        if USE_POSTGRES:
            db_execute(conn,
                """INSERT INTO cache (key, result, created_at) VALUES (?, ?, ?)
                   ON CONFLICT (key) DO UPDATE SET result = EXCLUDED.result, created_at = EXCLUDED.created_at""",
                (key, json.dumps(result), time.time()))
        else:
            db_execute(conn, "INSERT OR REPLACE INTO cache (key, result, created_at) VALUES (?, ?, ?)",
                        (key, json.dumps(result), time.time()))
        conn.commit()
    finally:
        conn.close()


def save_history(url_or_name, result):
    """Save an analysis to the history table."""
    cats = result.get("categories", {})
    conn = get_db()
    try:
        name = url_or_name
        if name.startswith("http"):
            name = urlparse(name).netloc.replace("www.", "")

        db_execute(conn,
            """INSERT INTO history (url, name, overall_score, handling, user_control,
               transparency, collection_security, result, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                url_or_name,
                name,
                result.get("overall_score", 0),
                cats.get("handling", {}).get("score", 0),
                cats.get("user_control", {}).get("score", 0),
                cats.get("transparency", {}).get("score", 0),
                cats.get("collection_security", {}).get("score", 0),
                json.dumps(result),
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


# --- HTML text extraction ---

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._skip = False
        self._skip_tags = {"script", "style", "noscript"}
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._skip = True

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self.parts.append(text)

    def get_text(self):
        return "\n".join(self.parts)


def extract_text_from_html(html):
    extractor = TextExtractor()
    extractor.feed(html)
    return extractor.get_text()


def extract_text_from_pdf(pdf_bytes):
    reader = PdfReader(BytesIO(pdf_bytes))
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n".join(parts)


# --- LLM call ---

def call_llm(policy_text):
    check_budget()

    resp = http_requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": RUBRIC_PROMPT},
                {"role": "user", "content": f"Please analyze this privacy policy:\n\n{policy_text}"},
            ],
            "max_tokens": 4096,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    # Calculate and record cost
    usage = data.get("usage", {})
    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)
    cost = (input_tokens * INPUT_COST_PER_M + output_tokens * OUTPUT_COST_PER_M) / 1_000_000
    record_spend(cost)

    return data["choices"][0]["message"]["content"]


def analyze_policy(text):
    if len(text.strip()) < 50:
        raise ValueError("The extracted text is too short to be a privacy policy.")

    raw = call_llm(text)

    # Extract JSON from response — handle code fences or preamble text
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

    # Find the first { and last } to extract JSON object
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        raw = raw[start:end + 1]

    return json.loads(raw)


# --- Flask app ---

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB


@app.route("/")
def home():
    for p in [
        os.path.join(os.path.dirname(__file__), "index.html"),
        os.path.join(os.path.dirname(__file__), "..", "public", "index.html"),
    ]:
        if os.path.exists(p):
            with open(p) as f:
                return f.read()
    return "Not found", 404


@app.route("/api/analyze/url", methods=["POST"])
def analyze_url():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "No URL provided."}), 400
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Check cache by URL
    cache_key = "url:" + hashlib.sha256(url.encode()).hexdigest()
    cached = get_cached(cache_key)
    if cached:
        cached["_cached"] = True
        return jsonify(cached)

    try:
        resp = http_requests.get(
            url, timeout=20,
            headers={"User-Agent": "Mozilla/5.0 (compatible; PrivacyPolicyAnalyzer/1.0)"},
        )
        resp.raise_for_status()
    except http_requests.RequestException as e:
        return jsonify({"error": f"Could not fetch URL: {e}"}), 400

    content_type = resp.headers.get("Content-Type", "")
    if "pdf" in content_type:
        text = extract_text_from_pdf(resp.content)
    else:
        text = extract_text_from_html(resp.text)

    try:
        result = analyze_policy(text)
        set_cached(cache_key, result)
        save_history(url, result)
    except BudgetExceeded as e:
        return jsonify({"error": str(e)}), 429
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except (json.JSONDecodeError, http_requests.RequestException) as e:
        return jsonify({"error": f"Analysis failed: {e}"}), 502

    return jsonify(result)


@app.route("/api/analyze/upload", methods=["POST"])
def analyze_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected."}), 400

    filename = file.filename.lower()
    raw = file.read()

    # Cache by content hash
    cache_key = "file:" + hashlib.sha256(raw).hexdigest()
    cached = get_cached(cache_key)
    if cached:
        cached["_cached"] = True
        return jsonify(cached)

    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(raw)
    elif filename.endswith((".txt", ".html", ".htm")):
        html = raw.decode("utf-8", errors="replace")
        if filename.endswith((".html", ".htm")):
            text = extract_text_from_html(html)
        else:
            text = html
    else:
        return jsonify({"error": "Unsupported file type. Upload .txt, .html, or .pdf"}), 400

    try:
        result = analyze_policy(text)
        set_cached(cache_key, result)
        save_history(file.filename, result)
    except BudgetExceeded as e:
        return jsonify({"error": str(e)}), 429
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except (json.JSONDecodeError, http_requests.RequestException) as e:
        return jsonify({"error": f"Analysis failed: {e}"}), 502

    return jsonify(result)


@app.route("/api/history", methods=["GET"])
def get_history():
    conn = get_db()
    try:
        rows = db_execute(conn,
            """SELECT id, name, url, overall_score, handling, user_control,
                      transparency, collection_security, created_at
               FROM history ORDER BY created_at DESC"""
        ).fetchall()
        return jsonify([
            {
                "id": r[0], "name": r[1], "url": r[2], "overall_score": r[3],
                "handling": r[4], "user_control": r[5],
                "transparency": r[6], "collection_security": r[7],
                "date": r[8][:10],
            }
            for r in rows
        ])
    finally:
        conn.close()


@app.route("/api/history/<int:report_id>", methods=["GET"])
def get_report(report_id):
    conn = get_db()
    try:
        row = db_execute(conn, "SELECT result FROM history WHERE id = ?", (report_id,)).fetchone()
        if not row:
            return jsonify({"error": "Report not found"}), 404
        return jsonify(json.loads(row[0]))
    finally:
        conn.close()


@app.route("/api/spend", methods=["GET"])
def get_spend():
    conn = get_db()
    try:
        total = db_execute(conn, "SELECT COALESCE(SUM(cost), 0) FROM spend").fetchone()[0]
        today = datetime.utcnow().strftime("%Y-%m-%d")
        daily = db_execute(conn,
            "SELECT COALESCE(SUM(cost), 0) FROM spend WHERE created_at LIKE ?",
            (today + "%",)
        ).fetchone()[0]
        return jsonify({
            "total_spent": round(total, 4),
            "daily_spent": round(daily, 4),
            "total_budget": BUDGET_TOTAL,
            "daily_budget": BUDGET_DAILY,
        })
    finally:
        conn.close()


@app.route("/api/rubric", methods=["GET"])
def get_rubric():
    """Parse rubric.md into structured JSON for the frontend."""
    categories = []
    current_cat = None
    q_id = 0

    for line in RUBRIC_PROMPT.splitlines():
        line = line.strip()
        # Category headers: ## HANDLING (how the company handles your data)
        if line.startswith("## ") and not line.startswith("## SCORING"):
            name = line[3:].strip()
            current_cat = {"name": name, "weight": 0, "questions": []}
            categories.append(current_cat)
        # Question lines: N. **Name** — description (0-X points, ...)
        elif current_cat and line and line[0].isdigit() and "**" in line:
            q_id += 1
            name_start = line.index("**") + 2
            name_end = line.index("**", name_start)
            q_name = line[name_start:name_end]
            max_pts = 0
            if "(0-" in line:
                pts_str = line.split("(0-")[1].split(" ")[0]
                max_pts = int(pts_str)
            desc = ""
            if "\u2014" in line:
                desc = line.split("\u2014", 1)[1].strip()
                if "(" in desc:
                    desc = desc[:desc.index("(")].strip()
            current_cat["questions"].append({
                "id": q_id, "name": q_name, "max": max_pts, "description": desc,
            })

    # Set weights from rubric
    weights = {"HANDLING": 30, "USER CONTROL": 25, "TRANSPARENCY": 20, "COLLECTION & SECURITY": 25}
    for cat in categories:
        for key, w in weights.items():
            if key in cat["name"].upper():
                cat["weight"] = w
                break

    return jsonify({"categories": categories})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
