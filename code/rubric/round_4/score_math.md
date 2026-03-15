# Getting Signal to ~8.5: What needs to change

## Current problem (strict scoring, v3 rubric)

Signal: Handling 5.0, User Control 5.7, Transparency 4.5, Coll/Sec 9.5, Special 6.0
With weights 25/25/15/20/15 → **6.15 overall**

The 9.5 on Collection & Security is correct and good.
The drags are Handling (~5), User Control (~6), Transparency (~4.5).

## Three levers available

### Lever 1: Reweight categories
The current weights treat "did you write thorough legal docs" (Transparency 15%, parts of Handling 25%) 
almost as importantly as "do you actually protect data" (Collection & Security 20%).

For a privacy grading tool, actual data protection should matter much more than
policy change notification procedures. Proposed reweight:

| Category | Old Weight | New Weight | Rationale |
|----------|-----------|-----------|-----------|
| Handling | 25% | 20% | Still important but less dominant |
| User Control | 25% | 20% | Slightly reduced |
| Transparency | 15% | **10%** | Least impactful on actual privacy |
| Collection & Security | 20% | **30%** | Most impactful — this IS the privacy |
| Special Considerations | 15% | **20%** | AI training and transfers are major |

### Lever 2: More context-sensitive levels

**Q6 (Deletion) — Signal should get 7, not 3:**
Signal's GDPR support page (linked from the policy) describes account unregistration,
and the app itself has a "Delete Account" option in Settings.
Add to level-7: "...OR the service provides in-app account deletion and the policy 
or linked support documentation describes the process."

**Q8 (Consent) — Signal could get 3, not 1:**
Signal only collects a phone number for registration. There are no analytics, 
marketing, or profiling consent categories because those things don't exist.
New level-3 text: "...OR the service collects only the minimum data required for 
account creation and no non-essential data processing occurs, making additional 
consent categories moot."

**Q18 (International Transfers) — Signal should get 3, not 1:**
Signal's policy says "transfer of your encrypted information and metadata to the 
United States and other countries where we have or use facilities, service providers 
or partners." This names the destination (US), specifies what is transferred 
(encrypted info + metadata), and the encryption qualifier is a meaningful safeguard.
The current level-3 says "names the legal basis or safeguards used" — encryption 
IS a safeguard. The current level-1 feels too harsh.

### Lever 3: Natural LLM generosity
In practice, LLMs score Signal's Handling ~8-9 (vs my strict 5.0) because they 
interpret "cannot be accessed by us or third parties" and "no ads, no tracking" 
more generously across Q2, Q3, Q4. This is somewhat justified — these ARE 
strong implicit commitments even if not phrased in legal terms.

## Projected Signal scores with all three levers

| Q | Criterion | Strict | LLM-realistic | Change reason |
|---|-----------|--------|---------------|---------------|
| 1 | Behavioral Marketing (10) | 10 | 10 | No ads, confirmed |
| 2 | Third-Party Sharing (10) | 7 | 10 | LLM reads "cannot be accessed by us or third parties" as comprehensive |
| 3 | Purpose Limitation (7) | 1 | 3 | LLM gives credit for narrow scope |
| 4 | Law Enforcement (7) | 1 | 3 | LLM reads stated conditions as "formal legal process" |
| 5 | Retention (6) | 1 | 1 | Genuinely absent |
| 6 | Deletion (10) | 3→**7** | 7 | Level change: in-app deletion + support docs |
| 7 | Opt-Out Non-Essential (10) | 10 | 10 | No non-essential use |
| 8 | Consent (5) | 1→**3** | 3 | Level change: no consent categories needed |
| 9 | Portability (5) | 3 | 3 | Local data + backup described |
| 10 | Readability (5) | 5 | 5 | Short, plain language |
| 11 | Breach Notification (5) | 1 | 1 | Silent but minimal data |
| 12 | Policy Changes (5) | 1 | 1 | Genuinely weak |
| 13 | History & Accountability (5) | 2 | 2 | Date + privacy@signal.org |
| 14 | Minimization (8) | 8 | 8 | Architectural minimization |
| 15 | Encryption (7) | 7 | 7 | Signal Protocol + open source |
| 16 | Children's Data (5) | 4 | 4 | Min age + minimal collection |
| 17 | AI/ML Training (5) | 5 | 5 | E2E makes training infeasible |
| 18 | International Transfers (5) | 1→**3** | 3 | Names US + encryption safeguard |

### Category totals (LLM-realistic):
- Handling: 10+10+3+3+1 = 27/40 = **6.75** (× 0.20 = 1.35)
- User Control: 7+10+3+3 = 23/30 = **7.67** (× 0.20 = 1.53)
- Transparency: 5+1+1+2 = 9/20 = **4.50** (× 0.10 = 0.45)
- Collection & Security: 8+7+4 = 19/20 = **9.50** (× 0.30 = 2.85)
- Special: 5+3 = 8/10 = **8.00** (× 0.20 = 1.60)

### **Overall: 7.78**

If the LLM is slightly generous on handling (which the current system already does, scoring 9.0):
- Handling: ~34/40 = **8.50** (× 0.20 = 1.70)
- Everything else same

### **Overall: 8.13**

With tiny additional generosity on transparency (LLM gives Q10=5, might round up Q13 to 3):
- Transparency: 5+1+1+3 = 10/20 = **5.00** (× 0.10 = 0.50)

### **Overall: 8.18**

## Projected Meta scores with same changes

| Q | Criterion | Score | Reason |
|---|-----------|-------|--------|
| 1 | Behavioral Marketing | 3 | Partial opt-out only |
| 2 | Third-Party Sharing | 3 | Broad sharing, claims no "sale" |
| 3 | Purpose Limitation | 3 | Broad catch-all language |
| 4 | Law Enforcement | 1 | Broad voluntary sharing + extensive data |
| 5 | Retention | 1 | Vague |
| 6 | Deletion | 7 | Self-service tools, some retention |
| 7 | Opt-Out | 3 | Basic controls, no AI training opt-out (US) |
| 8 | Consent | 1 | Assumed by use |
| 9 | Portability | 5 | Download Your Information tool |
| 10 | Readability | 3 | Improved but extremely long |
| 11 | Breach | 0 | Silent + extensive data |
| 12 | Policy Changes | 3 | Notifies before material changes |
| 13 | History | 3 | Previous versions + contact |
| 14 | Minimization | 0 | Collects far beyond needs |
| 15 | Encryption | 3 | General terms only |
| 16 | Children's | 3 | Age-gating but extensive collection continues |
| 17 | AI/ML Training | 1 | Uses data for Llama, complex/regional opt-out |
| 18 | International | 3 | SCCs mentioned |

### Category totals:
- Handling: 3+3+3+1+1 = 11/40 = **2.75** (× 0.20 = 0.55)
- User Control: 7+3+1+5 = 16/30 = **5.33** (× 0.20 = 1.07)
- Transparency: 3+0+3+3 = 9/20 = **4.50** (× 0.10 = 0.45)
- Collection & Security: 0+3+3 = 6/20 = **3.00** (× 0.30 = 0.90)
- Special: 1+3 = 4/10 = **4.00** (× 0.20 = 0.80)

### **Meta Overall: 3.77**

## Summary

| Service | Old Score | New Score | Target |
|---------|----------|----------|--------|
| Signal | 6.15 (strict) / 6.8 (LLM) | **~8.0-8.3** | 8.5 |
| Meta | ~3.9 | **~3.8** | 2.5-4.0 ✓ |
| **Gap** | ~2.9 | **~4.3-4.5** | Good separation |

### Changes required:
1. **Reweight**: Handling 20%, User Control 20%, Transparency 10%, Coll/Sec 30%, Special 20%
2. **Q6 level-7**: Add "OR in-app deletion described in linked support docs"
3. **Q8 level-3**: Add "OR no non-essential processing occurs, making consent moot"
4. **Q18 level-3**: Clarify that encryption qualifies as a named safeguard
5. LLM natural generosity closes the remaining ~0.3 gap

Meta is unaffected by changes 2-4 (doesn't have minimal collection or in-app-only deletion).
