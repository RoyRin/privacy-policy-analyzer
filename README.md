# Privacy Policy Analyzer

**Live at: https://privacy-policy-evaluator.vercel.app/**

A webapp that grades website privacy policies using an LLM-powered rubric inspired by [PrivacySpy](https://privacyspy.org).

## How it works

1. You paste a URL to a privacy policy page (or upload a .txt/.html/.pdf file)
2. The backend fetches the page, extracts the text, and sends it to Claude 3.5 Haiku via OpenRouter
3. The LLM grades the policy against a 15-question rubric across 4 categories
4. You get an overall score (0-10) with per-category breakdowns and per-question explanations

Results are cached for 7 days — repeated lookups of the same URL are free and instant. All past analyses are shown in a leaderboard table at the bottom of the page, and you can click any row to view the full report.

## Grading Rubric

15 questions across 4 weighted categories (see `code/rubric.md` for full details):

| Category | Weight | Questions |
|---|---|---|
| **Handling** | 30% | Behavioral marketing, data selling, third-party sharing, law enforcement access, data retention |
| **User Control** | 25% | Data deletion, opt-out of non-critical use, consent model, data portability |
| **Transparency** | 20% | Readability, breach notification, policy change notification, policy history |
| **Collection & Security** | 25% | Data minimization, encryption & security practices |

The rubric is stored as a standalone file (`code/rubric.md`) so it can be iterated on independently of the code.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r code/requirements.txt
```

Add your OpenRouter API key to `SECRETS/openrouter.key` (plain text, just the key).

## Run locally

```bash
python code/dev.py
# Open http://localhost:5001
```

## Deploy to Vercel

The `code/` directory is the Vercel project root. Set `OPENROUTER_API_KEY` as an environment variable in the Vercel dashboard.

```bash
cd code && npx vercel --prod
```

## Cost controls

- Uses Claude 3.5 Haiku via OpenRouter (~$0.01-0.12 per analysis depending on policy length)
- Results cached for 7 days
- Budget enforcement: $20 total lifetime, $10/day (tracked in SQLite)
- On Vercel, the DB is ephemeral (/tmp) — set a hard budget on OpenRouter as a safety net
# privacy-policy-analyzer
