# Intake notes → structured job profile
*Module 2, Lesson 2. Paste your notes where marked.*

---

You are extracting a structured job profile from recruitment intake notes.

INPUT:
<<<
[PASTE INTAKE NOTES OR TRANSCRIPT HERE]
>>>

Return exactly these fields:
- role_title
- outcomes_first_six_months
- must_arrive_intact
- can_be_learned_here
- failed_hire_signals
- compensation_range
- decision_makers_and_what_each_assesses
- stated_trade_off
- location_and_working_pattern

CONSTRAINTS — these matter more than completeness:
1. For every field, quote the phrase from the notes that supports it.
2. If the notes do not address a field, write exactly: not stated
3. Do not infer. Do not fill gaps with what is typical for this kind of role.
4. Do not add competencies, skills or qualities that do not appear in the notes.

---

## How to read the output
If it comes back with no gaps at all, either your intake was exceptional or the model
filled them silently. Check three fields against your notes before trusting it.

The gaps are the valuable output — they are your follow-up questions.

## Sending it back for sign-off
Ask for corrections, not approval:

> "Two things I couldn't find in my notes, and one I may have inferred — can you confirm?"
