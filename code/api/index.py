import hashlib
import json
import os
import re
import sqlite3
import time
from datetime import datetime
from html.parser import HTMLParser
from io import BytesIO

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

MODEL = "anthropic/claude-3.5-haiku"
BUDGET_TOTAL = 20.0   # $20 lifetime
BUDGET_DAILY = 10.0   # $10 per day
CACHE_TTL = 86400 * 7  # 7 days in seconds

# OpenRouter pricing for Claude 3.5 Haiku (per million tokens)
INPUT_COST_PER_M = 1.0
OUTPUT_COST_PER_M = 5.0

# DB path: use /tmp on Vercel (ephemeral), local data/ dir otherwise
_local_db = os.path.join(os.path.dirname(__file__), "..", "data", "analyzer.db")
DB_PATH = os.environ.get("DB_PATH", _local_db)

RUBRIC_PROMPT = """You are a privacy policy analyst. Grade the following privacy policy using these 12 criteria. Be strict and evidence-based — only give high scores when the policy explicitly commits to good practices.

HANDLING (how the company handles your data):
1. Behavioral Marketing — Does the policy allow personally-targeted or behavioral marketing? (0-10 points, 10 = no behavioral marketing at all)
2. Data Deletion — Can users permanently delete their personal data? (0-5 points, 5 = easy automated deletion mechanism)
3. Law Enforcement Access — Under what conditions does the company share data with law enforcement? (0-5 points, 5 = only with court order or never)
4. Third-Party Sharing — Does the service share personal data with third parties? (0-10 points, 10 = never shares personal data)

TRANSPARENCY (how transparent the company is):
5. Data Breach Notification — Does the policy commit to notifying users of data breaches? (0-7 points, 7 = within 72 hours)
6. Policy Change Notification — Will users be notified when the policy changes? (0-5 points, 5 = always notifies before changes take effect)
7. Policy History — Is the policy's revision history available? (0-5 points, 5 = full changelog available)
8. Security Practices — Does the policy describe its security practices? (0-3 points, 3 = detailed practices with independent audits)

COLLECTION (what data is collected and why):
9. Collection Reasoning — Is it clear why the service collects each type of personal data? (0-10 points, 10 = every data type has a clear justification)
10. Data Listing — Does the policy exhaustively list the personal data it collects? (0-10 points, 10 = exhaustive list)
11. Non-Critical Use Control — Can users opt out of non-critical data collection/use? (0-10 points, 10 = full opt-in for all non-critical purposes)
12. Third-Party Collection — Does the service collect personal data from third-party sources? (0-10 points, 10 = never collects from third parties)

Score each question individually, then compute category and overall scores.

Category scores: normalize each category's earned points to a 0-10 scale (earned / max * 10).
- Handling max = 30
- Transparency max = 20
- Collection max = 40

Overall score: weighted average of categories — Handling 35%, Transparency 25%, Collection 40%.

Respond in EXACTLY this JSON format and nothing else:
{
  "questions": [
    {"id": 1, "category": "handling", "question": "short question text", "score": <number>, "max": <number>, "explanation": "1-2 sentence justification citing the policy"},
    ...all 12 questions...
  ],
  "categories": {
    "handling": {"score": <0-10 float, 1 decimal>, "summary": "2-3 sentence summary"},
    "transparency": {"score": <0-10 float, 1 decimal>, "summary": "2-3 sentence summary"},
    "collection": {"score": <0-10 float, 1 decimal>, "summary": "2-3 sentence summary"}
  },
  "overall_score": <0-10 float, 1 decimal>,
  "overall_summary": "3-4 sentence overall assessment"
}"""


# --- Database ---

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute("""CREATE TABLE IF NOT EXISTS cache (
        key TEXT PRIMARY KEY,
        result TEXT,
        created_at REAL
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS spend (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cost REAL,
        created_at TEXT
    )""")
    db.commit()
    return db


class BudgetExceeded(Exception):
    pass


def check_budget():
    db = get_db()
    try:
        total = db.execute("SELECT COALESCE(SUM(cost), 0) FROM spend").fetchone()[0]
        if total >= BUDGET_TOTAL:
            raise BudgetExceeded(f"Total budget of ${BUDGET_TOTAL:.0f} exceeded (${total:.2f} spent)")

        today = datetime.utcnow().strftime("%Y-%m-%d")
        daily = db.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM spend WHERE created_at LIKE ?",
            (today + "%",)
        ).fetchone()[0]
        if daily >= BUDGET_DAILY:
            raise BudgetExceeded(f"Daily budget of ${BUDGET_DAILY:.0f} exceeded (${daily:.2f} spent today)")
    finally:
        db.close()


def record_spend(cost):
    db = get_db()
    try:
        db.execute("INSERT INTO spend (cost, created_at) VALUES (?, ?)",
                    (cost, datetime.utcnow().isoformat()))
        db.commit()
    finally:
        db.close()


def get_cached(key):
    db = get_db()
    try:
        row = db.execute("SELECT result, created_at FROM cache WHERE key = ?", (key,)).fetchone()
        if row and (time.time() - row[1]) < CACHE_TTL:
            return json.loads(row[0])
        return None
    finally:
        db.close()


def set_cached(key, result):
    db = get_db()
    try:
        db.execute("INSERT OR REPLACE INTO cache (key, result, created_at) VALUES (?, ?, ?)",
                    (key, json.dumps(result), time.time()))
        db.commit()
    finally:
        db.close()


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
    html_path = os.path.join(os.path.dirname(__file__), "..", "public", "index.html")
    with open(html_path) as f:
        return f.read()


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
    except BudgetExceeded as e:
        return jsonify({"error": str(e)}), 429
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except (json.JSONDecodeError, http_requests.RequestException) as e:
        return jsonify({"error": f"Analysis failed: {e}"}), 502

    return jsonify(result)


@app.route("/api/spend", methods=["GET"])
def get_spend():
    db = get_db()
    try:
        total = db.execute("SELECT COALESCE(SUM(cost), 0) FROM spend").fetchone()[0]
        today = datetime.utcnow().strftime("%Y-%m-%d")
        daily = db.execute(
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
        db.close()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
