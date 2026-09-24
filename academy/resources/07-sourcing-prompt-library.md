# Sourcing prompt library — 20 prompts
*Module 3, Lesson 6. Four parts every prompt needs: role, input, constraints, output format.*

Placeholders are in `<ANGLE BRACKETS>`. Every prompt states its output format so you
are not reformatting by hand.

---
## Profiling

**1. Intake notes → structured profile**
See `02-job-profile-extraction-prompt.md`.

**2. Job brief → scorecard lines**
> From the job brief below, list 5–7 competencies. For each, write an observable
> definition (what you would see someone do) and state whether it can be evidenced from
> a resume, an interview, a work sample, or a reference. Quote the phrase in the brief
> that supports each. Write `not stated` for anything you are inferring.
> Output: a markdown table. Brief: <<<BRIEF>>>

**3. Requirement triage**
> Sort each requirement below into: MUST ARRIVE INTACT, LEARNABLE HERE, or UNMEASURABLE.
> For anything you place in MUST ARRIVE INTACT, state why it could not be learned in six
> months. Output: three lists, no commentary. <<<REQUIREMENTS>>>

---
## Expansion

**4. Title variants**
> List 15 job titles used for the role described below, across startups, enterprises and
> at least three countries. Include titles people hold immediately before moving into it.
> Mark any you are unsure exist with (?). Output: a single Boolean OR group, multi-word
> titles quoted, no commentary. <<<ROLE>>>

**5. Skill and tool expansion**
> For the skill <<<SKILL>>>, list the tool itself, its three main competitors, common
> abbreviations, and the category term. Output: one Boolean OR group, no commentary.

**6. Employer expansion**
> List 20 companies likely to employ people who can do the role below: direct
> competitors, adjacent industries with the same problem, and consultancies serving the
> sector. Group under those three headings. Region: <<<REGION>>>. Role: <<<ROLE>>>

**7. Feeder roles**
> What roles do people typically hold immediately before <<<ROLE>>>? List 8, each with
> one line on what transfers and what does not.

**8. Adjacent-industry framing**
> Which industries face the same underlying problem as <<<PROBLEM>>>? List 6 with one
> line each on why the experience transfers.

---
## Search

**9. Requirements → Boolean**
> Build a Boolean search from the requirements below using three blocks: core titles
> (OR), skills (OR), location (OR), plus exclusions for job ads and recruiters.
> Output: the query only. <<<REQUIREMENTS>>>

**10. Boolean → X-Ray**
> Convert the query below into an X-Ray search for <<<PLATFORM>>>, adding the correct
> site: prefix. Output: the query only. <<<QUERY>>>

**11. Query debugging**
> This query returns <<<PROBLEM: too few / wrong people>>>. Identify the likely cause and
> return one revised query. Explain the change in one sentence. <<<QUERY>>>

**12. Term validation triage**
> For each term below, say whether it is a real, current job title in <<<REGION>>>, an
> obsolete one, or ambiguous (returns unrelated people). Output: a table with a
> keep/drop recommendation. <<<TERMS>>>

---
## Screening support

**13. Evidence extraction**
> From the resume below, for each criterion listed, quote the exact sentence that
> evidences it. If there is no evidence, write `no evidence`. Do not summarise, infer or
> characterise. Output: criterion, quote, location in document.
> Criteria: <<<CRITERIA>>> Resume: <<<RESUME>>>

**14. Gap questions for one candidate**
> Based on the resume and criteria below, list the three things you cannot determine
> from the document that would most change the decision. Phrase each as a question to
> ask the candidate. <<<RESUME>>> <<<CRITERIA>>>

**15. Second-pass full-text search**
> Given the capability <<<CAPABILITY>>>, list 10 phrases someone might use to describe
> having done it without using that term. Output: a Boolean OR group for searching
> rejected resumes.

---
## Outreach

**16. First touch from evidence**
> Write a first outreach message under 90 words using only these facts: <<<WHAT THEY
> WORK ON>>>, <<<TRAJECTORY>>>, <<<CITABLE DETAIL>>>, <<<WHY THIS IS A STEP UP>>>.
> Rules: no superlatives; no "impressive", "excited", "passionate", "reached out",
> "came across"; open with them not us; end with a question, not a meeting request;
> invent nothing beyond the facts given.

**17. Follow-up with new information**
> Write touch 2 of a sequence. It must add this fact, which was deliberately held back:
> <<<NEW FACT>>>. Under 70 words. Do not say "following up" or "checking in".
> Previous message: <<<TOUCH 1>>>

**18. Rejection by stage**
> Write a rejection for a candidate at the <<<STAGE>>> stage. Reference the criterion
> <<<CRITERION>>>. Do not compare them to other candidates. Do not mention anything
> about communication style, presence or fit. Under 120 words.

---
## Summarising

**19. Longlist themes**
> From the profiles below, identify the 4–6 recurring background patterns. For each,
> state how many profiles fit and what it implies about where this talent sits.
> <<<PROFILES>>>

**20. Transcript → scorecard evidence**
> From the interview transcript below, for each competency listed, extract the passages
> where it was discussed. Quote with timestamps. Do not rate. Do not summarise. If a
> competency was not covered, write `no evidence`.
> Competencies: <<<COMPETENCIES>>> Transcript: <<<TRANSCRIPT>>>

---
## Version log
| Date | Prompt | Change | Why |
|---|---|---|---|
| | | | |

Test any new prompt on five cases whose correct answer you already know before adding it.
