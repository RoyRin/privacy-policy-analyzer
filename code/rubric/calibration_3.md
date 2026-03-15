# Rubric v3 Calibration: Signal vs Meta

This document shows expected scores under the revised rubric for two extreme cases: Signal (should score high) and Meta/Facebook (should score low). Use this to verify the rubric produces adequate separation.

---

## HANDLING (max 40)

| # | Criterion (max) | Signal Expected | Meta Expected |
|---|----------------|-----------------|---------------|
| 1 | Behavioral Marketing (10) | **10** — No advertising whatsoever; homepage confirms "no ads, no affiliate marketers, no creepy tracking" | **3** — Pervasive behavioral ads across FB/IG/Messenger; partial opt-out via Ad Preferences but cannot fully disable tracking or interest-based targeting |
| 2 | Third-Party Sharing (10) | **7** — Shares only with SMS verification providers and support processors for specified service purposes; states these providers are bound by their own privacy policies | **3** — Claims no "sale" under CCPA narrow definition, but shares extensively with "partners, vendors, and third parties" including advertisers and data providers; receives data FROM third parties about user activity off-platform |
| 3 | Purpose Limitation (7) | **1** — Purposes are inherently narrow (messaging service) and data collection is minimal, but no explicit purpose limitation commitment in policy text | **3** — Lists purposes but includes broad catch-alls: "research and innovate for social good," "promote safety, integrity and security," "communicate with you" for marketing |
| 4 | Law Enforcement (7) | **1** — Broad language: "any applicable law, regulation, legal process or enforceable governmental request" + "protect against harm to rights, property, or safety" — BUT collects minimal data, so structural exposure is low | **1** — Same broad "to protect safety" language + voluntary sharing for "safety and security" — AND collects extensive data. Note: doesn't reach 0 because conditions ARE stated, even if broad |
| 5 | Retention (6) | **1** — No explicit retention policy for the limited data held; E2E architecture means message content never stored server-side, but policy doesn't state this | **1** — "As long as necessary," "extended amount of time" — vague with no concrete periods |
| | **HANDLING** | **20/40 = 5.0** | **11/40 = 2.8** |

**Note on Signal Handling = 5.0:** This is lower than the 9.0 your current system produced, which suggests the LLM was being generous on Q3/Q4/Q5 by reading Signal's *reputation* into the policy text. The v3 rubric's new level-1 options for Q3, Q4, Q5 (recognizing minimal-collection context) help Signal relative to level-0, but appropriately don't give full credit for things the policy simply doesn't address. If your LLM consistently scores Signal Handling ~8-9, the levels themselves aren't the problem — the LLM is interpreting generously, which may be acceptable calibration behavior.

---

## USER CONTROL (max 30)

| # | Criterion (max) | Signal Expected | Meta Expected |
|---|----------------|-----------------|---------------|
| 6 | Data Deletion (10) | **3** — Policy doesn't describe a deletion mechanism directly; GDPR support page mentions unregistering via Settings, but the policy itself is vague on process and completeness | **7** — Self-service tools for data deletion in Settings; some data retained for legal/safety reasons with explanation |
| 7 | Opt-Out Non-Essential (10) | **10** — Service does not engage in any non-essential data use (no analytics, no profiling, no AI training, no marketing); this is confirmed by the policy's architecture disclosures | **3** — Cookie controls and ad preference adjustments exist, but no opt-out for analytics, cross-app profiling, or AI training (US users); EU opt-out is complex multi-step process |
| 8 | Consent Model (5) | **1** — "You agree to our data practices as described in our Privacy Policy" + "your continued use confirms acceptance" — consent assumed by use | **1** — Consent assumed by use; no granular controls at consent stage |
| 9 | Data Portability (5) | **3** — Data stored locally on user devices (user already possesses it); community tools exist for parsing; backup/transfer described in support docs but not in the privacy policy itself | **5** — Self-service Download Your Information tool in standard formats |
| | **USER CONTROL** | **17/30 = 5.7** | **16/30 = 5.3** |

**Note:** Signal and Meta land close on User Control, which feels counterintuitive but is correct: Meta has genuinely better *tooling* for deletion and portability (because it holds your data server-side and built tools to manage it). Signal holds almost nothing, so there's less to control — but the policy also doesn't describe what controls exist. The rubric correctly captures this as a documentation gap, not a privacy failure.

---

## TRANSPARENCY (max 20)

| # | Criterion (max) | Signal Expected | Meta Expected |
|---|----------------|-----------------|---------------|
| 10 | Readability (5) | **5** — Very short, plain language, well-organized with clear sections | **3** — Rewritten to be more accessible with examples and links, but extremely long (5000+ words across main policy + supplements); layered format helps |
| 11 | Breach Notification (5) | **1** — Silent on breach notification, but E2E architecture substantially limits breach impact (minimal server-side data to breach) | **0** — No breach notification commitment despite collecting extensive personal data |
| 12 | Policy Changes (5) | **1** — "We will update this privacy policy as needed" + "your continued use confirms acceptance" — no advance notice, no direct notification | **3** — "We'll notify you before we make material changes" + "opportunity to review before you choose to continue" |
| 13 | History & Accountability (5) | **2** — Shows "Effective/Updated" date; has DPO at privacy@signal.org (confirmed in GDPR support page) — but no version archive or changelog | **3** — Previous versions accessible ("see previous versions" links); privacy contact provided |
| | **TRANSPARENCY** | **9/20 = 4.5** | **9/20 = 4.5** |

**Note:** Same score! This is the rubric working correctly in one sense (Signal's policy IS sparse on transparency) but the LLM might push Meta to 3-4 on readability depending on how it interprets the length. The key insight: transparency measures how well the company COMMUNICATES, not how well it BEHAVES. Signal behaves well but communicates sparsely. Meta communicates elaborately but behaves poorly. These are different axes, and the rubric should measure them separately.

---

## COLLECTION & SECURITY (max 20)

| # | Criterion (max) | Signal Expected | Meta Expected |
|---|----------------|-----------------|---------------|
| 14 | Data Minimization (8) | **8** — E2E encryption means provider cannot access message content; collects only phone number, random cryptographic keys, profile info (optional), and basic usage tokens. Architecture enforces minimization beyond any policy promise. | **0** — Collects device IDs, Bluetooth signals, WiFi access points, GPS, IP, connection speed, cookie data, purchase history, data from third-party partners about off-platform activity. Far exceeds service needs. |
| 15 | Encryption & Security (7) | **7** — Names "Signal Protocol" (specific, well-known E2E encryption protocol); entire client and server code is open source on GitHub enabling public verification; has received independent security audits (widely documented). | **3** — Mentions using SCCs for transfers and "encryption" generally; no named encryption standards for user data protection; no reference to independent security audits in privacy policy. |
| 16 | Children's Data (5) | **4** — States minimum age of 13; does not knowingly collect children's data; service collects minimal personal data overall, substantially reducing risk to minors. No detailed remediation process but low-risk profile. | **3** — Has detailed age-gating for some products (parental consent for 10-12 on Meta Quest); states COPPA compliance. But children's data is then processed "much like any other Meta account" — extensive collection continues after parental consent. |
| | **COLLECTION & SECURITY** | **19/20 = 9.5** | **6/20 = 3.0** |

**THIS is the key separation.** Signal goes from 6.5 → 9.5 on this category. Meta stays low. The changes that enable this:
- Q14: "architectural design that prevents collection" recognized as equivalent to explicit minimization commitment
- Q15: "open-source code enabling public verification" recognized as equivalent to formal audits
- Q16: new level-4 for minimal-collection services

None of these changes help Meta because they all require demonstrated minimal collection or open-source verification.

---

## SPECIAL CONSIDERATIONS (max 10)

| # | Criterion (max) | Signal Expected | Meta Expected |
|---|----------------|-----------------|---------------|
| 17 | AI/ML Training (5) | **5** — E2E encryption makes training on message content technically infeasible; server has no access to decrypted user data. Policy's architecture disclosures confirm this. | **1** — Uses public posts, interactions, and AI chat data for training; opt-out only in some jurisdictions (EU) and through complex multi-step process that Meta must approve; no US opt-out |
| 18 | International Transfers (5) | **1** — Mentions "transfer of your encrypted information and metadata to the United States and other countries where we have facilities, service providers or partners" — discloses transfers but no legal basis or safeguards named | **3** — Mentions SCCs ("standard contract clauses") and EU adequacy decisions; does not offer data residency options |
| | **SPECIAL CONSIDERATIONS** | **6/10 = 6.0** | **4/10 = 4.0** |

---

## OVERALL SCORES

### Signal
| Category | Raw | Normalized (0-10) | Weight | Weighted |
|----------|-----|--------------------|--------|----------|
| Handling | 20/40 | 5.0 | 25% | 1.25 |
| User Control | 17/30 | 5.7 | 25% | 1.42 |
| Transparency | 9/20 | 4.5 | 15% | 0.68 |
| Collection & Security | 19/20 | 9.5 | 20% | 1.90 |
| Special Considerations | 6/10 | 6.0 | 15% | 0.90 |
| **OVERALL** | | | | **6.15** |

### Meta
| Category | Raw | Normalized (0-10) | Weight | Weighted |
|----------|-----|--------------------|--------|----------|
| Handling | 11/40 | 2.8 | 25% | 0.69 |
| User Control | 16/30 | 5.3 | 25% | 1.33 |
| Transparency | 9/20 | 4.5 | 15% | 0.68 |
| Collection & Security | 6/20 | 3.0 | 20% | 0.60 |
| Special Considerations | 4/10 | 4.0 | 15% | 0.60 |
| **OVERALL** | | | | **3.9** |

---

## Separation Analysis

| Metric | Signal | Meta | Gap |
|--------|--------|------|-----|
| Overall | **6.2** | **3.9** | 2.3 |
| Handling | 5.0 | 2.8 | 2.2 |
| User Control | 5.7 | 5.3 | 0.4 |
| Transparency | 4.5 | 4.5 | 0.0 |
| Collection & Security | **9.5** | **3.0** | **6.5** |
| Special Considerations | 6.0 | 4.0 | 2.0 |

**Key observations:**

1. **Collection & Security is the big differentiator** (6.5 point gap). This is correct — it's where Signal's architecture genuinely excels and Meta's data practices are worst.

2. **Signal overall = 6.2 feels low.** The reason is that Signal's POLICY DOCUMENT (which is what the rubric grades) genuinely has gaps: no retention policy, vague law enforcement language, consent-by-use, no breach notification, no policy change advance notice. These are real documentation failures even if Signal's actual practices are excellent.

3. **To push Signal above 7.0, you'd need either:**
   - (a) Increase weights on Collection & Security and Special Considerations (where Signal dominates)
   - (b) Accept that the LLM will score Handling more generously than my strict reading (likely — the LLM probably gives Q2=10 and Q3=3-5 rather than my 7 and 1)
   - (c) Add more context-sensitivity to the remaining criteria

4. **Meta at 3.9 feels about right** for a company whose business model is behavioral advertising.

5. **Recommendation:** Option (b) is the most likely outcome in practice. LLMs tend to give Signal 8-9 on Handling (not my strict 5.0), which would push Signal's overall to ~7.5-8.0. The rubric changes I've made to Collection/Security and Special Considerations ensure the gap is large and in the right direction. If you want to force stricter Handling scores, add more explicit examples in the rubric levels.

---

## Target Score Ranges for Common Services

For reference, here's where well-known services should roughly land:

| Service | Target Range | Key Characteristics |
|---------|-------------|---------------------|
| Signal | 7.5 - 9.0 | Minimal collection, E2E, open source, no ads, nonprofit |
| ProtonMail | 7.0 - 8.5 | E2E email, Swiss jurisdiction, open source, minimal collection |
| Apple (iCloud) | 5.5 - 7.0 | Strong security, some ad tracking, good tools, long policy |
| Google | 3.5 - 5.0 | Extensive collection, good tools/transparency, ad-funded |
| Meta/Facebook | 2.5 - 4.0 | Extensive collection, behavioral ads, broad sharing, complex opt-outs |
| TikTok | 2.0 - 3.5 | Extensive collection, opaque practices, biometric data, international transfer concerns |

If your rubric produces scores outside these ranges, something needs recalibrating.
