# Privacy Policy Grading — Interpretation Guide

## Rubric & Calibration Files
- `revised_rubric_v3.md` — the grading prompt. Send this as the system prompt along with the policy text.
- `calibration.md` — reference expected scores. Do NOT send this to the grading model; use it to sanity-check outputs.

## Key Principles for the Grading Call

### 1. Grade the document, not the company's reputation
The most common failure mode is the LLM "knowing" that Signal is private or Meta is bad and letting that bleed into scores. The rubric grades POLICY TEXT ONLY. If the policy doesn't say something, it doesn't get credit — even if you know the company does it in practice.

Corollary: don't penalize a company extra because you know they've been in scandals. Grade the text.

### 2. Architecture claims IN the policy count; external knowledge doesn't
If Signal's policy says "end-to-end encrypted" — that's a policy claim and can be scored. If you know Signal uses the Signal Protocol because you read their blog, but the privacy policy doesn't mention it — don't give credit for it in the policy grading. The rubric has levels that recognize architectural claims (e.g., Q14 level-8 mentions "architectural design that prevents collection") but the architecture must be described or clearly implied in the policy itself.

### 3. Silence ≠ absence, but silence ≠ presence either
The rubric's calibration note says to evaluate silence in context. A minimal-collection service being silent on breach notification is a minor gap (level 1); an extensive-collection service being silent is a major failure (level 0). Several criteria have split level-0 and level-1 to capture this distinction. Make sure the model is actually using these context-sensitive levels rather than defaulting to 0 for all silence.

### 4. Watch for these specific LLM tendencies
- **Halo effect:** Giving Signal 10/10 on everything because the first few criteria score high. Each criterion is independent.
- **Punishment stacking:** Docking a company on Q1 (behavioral marketing), Q7 (opt-out), AND Q8 (consent model) for what is essentially the same issue (ad tracking with no opt-in). Some overlap is expected, but watch for the same fact being penalized 3x.
- **Generosity on vague language:** "We take your privacy seriously" and "we use industry-standard security" are essentially meaningless. These should score at the lower levels (1-3), not mid-range.
- **False equivalence on law enforcement:** Almost every policy says "we may share data to comply with legal process or protect safety." The rubric distinguishes between companies that say this while holding minimal data (level 1) vs. extensive data (level 0). Make sure the model is reading Q4 in context of what the service actually collects.

### 5. Expected score anchors
Use these to sanity-check outputs. If a score falls outside the range, investigate before accepting it.

| Service | Expected Overall | If outside this range... |
|---------|-----------------|------------------------|
| Signal | 7.5 - 8.5 | If < 7.5: probably penalizing silence too harshly — check Q6 (should get 7 for in-app deletion), Q8 (should get 3 for minimal collection), Q14/Q15 (should get 8/7 for architecture). If > 9: probably reading reputation into handling/transparency scores. |
| ProtonMail | 7.0 - 8.5 | Similar profile to Signal but with more detailed policy. |
| Apple | 5.0 - 7.0 | Good security, some tracking, detailed but long policy. |
| Google | 3.5 - 5.5 | Good tools and transparency, extensive collection, ad-funded. |
| Meta/Facebook | 2.5 - 4.5 | Extensive everything, complex opt-outs, broad sharing. |
| TikTok | 2.0 - 4.0 | Extensive collection, opaque, international transfer concerns. |

### 6. Post-processing checks
After receiving the JSON response from the grading model:
- Verify all scores are valid levels from the rubric (no interpolation — e.g., there's no level 4 on a criterion that only has 0/3/5/7/10)
- Verify arithmetic: category scores should equal (sum of question scores in category) / category max * 10
- Verify overall score equals the weighted average with correct weights (Handling 20%, User Control 20%, Transparency 10%, Collection & Security 30%, Special Considerations 20%)
- Flag if any explanation references information not present in the policy text (reputation leakage)

### 7. What to include with the score on the website
Always display the disclaimer (see `website_disclaimer.md`). The short version goes near the score. Link to the full methodology. The disclaimer explains that this tool grades the policy document — a company with excellent practices but a sparse policy may score somewhat lower than its actual privacy posture warrants.
