# Privacy Policy Analyzer

A webapp that grades website privacy policies using an LLM-powered rubric inspired by [PrivacySpy](https://privacyspy.org).

Paste a URL or upload a file (.txt, .html, .pdf) and get an instant privacy score from 0-10.

## Grading Rubric

12 questions across 3 categories, scored 0-10 per category:

**Handling (35% weight)** — Behavioral marketing, data deletion, law enforcement access, third-party sharing

**Transparency (25% weight)** — Breach notification, policy change notification, policy history, security practices

**Collection (40% weight)** — Collection reasoning, data listing, non-critical use control, third-party collection

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r code/requirements.txt
```

Add your OpenRouter API key to `SECRETS/openrouter.key` (plain text, just the key).

## Run locally

```bash
python code/api/index.py
# Open http://localhost:5001
```

## Deploy to Vercel

The `code/` directory is structured for Vercel deployment. Set `OPENROUTER_API_KEY` as an environment variable in your Vercel project settings.

## Cost controls

- Uses Claude 3.5 Haiku via OpenRouter (~$0.01-0.12 per analysis depending on policy length)
- Results cached for 7 days
- Budget enforcement: $20 total, $10/day (tracked in local SQLite)
