# Step-by-step achievement ranking implementation plan

Build a local Python ranker that evaluates every achievement for a specific internship, asks you why when it cannot explain a ranking change you make, and uses your answer in future contexts where it applies. The first release should produce a ranked review alongside the current workflow. After calibration, it can recommend one résumé swap for your approval. [Achievement Ranking Build Plan](Achievement_Ranking_Build_Plan.md)

## 1. Capture the current behavior and create the evaluation cases

- [ ] Run `tailor.py` on an excerpt or full snapshot of the Princess Cruises posting, a general Python/SWE posting, and a SQL/reporting-heavy posting. Save the expected selections as regression fixtures. Use sanitized posting text in the repository.
- [ ] Add a case with a niche employer context, such as geospatial infrastructure, and another where two employers hiring for the same role emphasize different duties. Reserve at least one posting per tested role family for evaluation after calibration.
- [ ] Assert that a no-swap draft preserves `main.tex` except for the existing graduation and LaTeX handling. A swap draft should change exactly one entry and preserve the required bullet counts.

**Done when** the current baseline, swap behavior, and source-preservation rules are reproducible before ranking code is added.

## 2. Build the achievement ranking index

- [ ] Load every achievement in `Aaditya_Gajula_Achievement_Inventory.json` by its stable ID. Keep source IDs, status, and related achievements. Read `resume_entries.json` for available replacement wording and use the baseline mappings in `tailor.py` for entries already in `main.tex`.
- [ ] Create a small reviewed metadata file, `ranking_profiles.json`, with competency tags, contribution scope, result type, and leadership or domain signals for the first set of relevant entries. Record the evidence behind each tag. Show other achievements as awaiting profile review instead of assigning an invented low score.
- [ ] Give each achievement a display status such as **ready for résumé**, **rankable, wording needed**, or **held for review**. Link related records such as PharmaBeacon and its stakeholder interviews so multiple records from the same project count as one résumé slot.

**Done when** every inventory ID appears in the index, and a high ranking alone cannot make a held or unwritten entry eligible for export.

## 3. Capture role and employer context from the posting

- [ ] Reuse `tailor.py`’s posting analysis for recognized requirements and original text spans. Add a reviewable context record with job family, employer, team or domain, and weighted requirements. Use required qualifications, core duties, and preferred qualifications as separate priorities.
- [ ] Allow manual corrections to the classification. Attach a posting excerpt or a note supplied by you to any claim about what a specific employer values. Keep unknown team preferences blank. Show eligibility constraints separately from achievement rank.
- [ ] Save the reviewed context alongside the posting hash so the same analysis can be replayed.

**Done when** the same data internship title can produce different priorities for a guest AI team and a SQL-heavy reporting team, with a clear source for each priority.

## 4. Implement the first explainable ranker

- [ ] Add `rank_achievements.py` with a deterministic scoring function. Give it the reviewed posting context and achievement index. Return each achievement’s rank, **achievement strength**, **posting fit**, source IDs, and a short explanation.
- [ ] Score strength using ownership, scope, outcome, and evidence quality. Score fit using the strongest evidence for each required skill, central duty, or preference. Mark unknown ownership or metrics as unknown. Treat a project’s scale, a team result, and an individual outcome according to their stated scope.
- [ ] Store weights and rubric definitions in one versioned configuration. Start with posting fit weighted more heavily than general achievement strength. Cap the effect of duplicate terms and resolve ties consistently. Rank unsupported tools as gaps.

**Done when** each rank can be explained from recorded factors and test postings can move the same achievement up or down for an understandable reason.

## 5. Implement your feedback session

- [ ] Add a local `review` command that starts with the top eligible candidates and close calls around a possible swap. Let you move an item up or down, choose between two items, declare a tie, or skip. An override should take effect in the current review immediately.
- [ ] Compare each override with the reasons already recorded for the affected achievements and context. If those reasons do not explain the change, ask one focused **why** question whenever it happens. Show the model’s current reason so you can correct it directly. An unexplained override remains local to that review until you supply a reason.
- [ ] If the answer is new information about your contribution, record it as an evidence update for review. If it is your hiring judgment, ask where it applies when ambiguous. Offer this posting, this employer or team, this job family, or a broader preference. Show the saved interpretation and let you edit or undo it.

**Example prompt**

> You moved Borrower Credit Risk Analysis above FeedBack. I ranked FeedBack higher because this posting mentions guest follow-up and AI review. What makes the SQL project stronger for this team?

**Done when** you can finish a five-comparison session, receive a question for every unexplained override, and reopen the session with your choices and reasons intact.

## 6. Persist and apply feedback with an audit trail

- [ ] Store feedback in a private local SQLite database outside the repository. Record the posting context, both achievement IDs, previous order, your choice, explanation, scope, timestamp, and scoring version. Preserve prior records when you edit or retract a decision.
- [ ] Apply explicit feedback only where its scope matches. Prefer a specific employer or posting decision over a broader preference. Use bounded adjustments and show which saved reasons changed the score. Leave a conflict visible for review if equally specific feedback points in different directions.
- [ ] Keep the ranking reproducible from the posting, achievement metadata, scoring version, and active feedback. Distinguish the before-feedback and after-feedback ranks in the report.

**Done when** you can demonstrate an employer-specific change, a broader preference that applies across appropriate postings, and a retracted preference that stops affecting later rankings.

## 7. Connect ranking to résumé recommendations

- [ ] Start in recommendation mode. For each possible one-entry replacement, compare what the overall résumé would gain or lose. Preserve required coverage, entry type, and experience chronology. Check that the replacement has the required bullets and is close enough in length to fill the same space.
- [ ] Add the recommendation, evidence gained or lost, and influencing feedback to the review. Continue using the current `tailor.py` output during calibration. Once you approve a recommendation, reuse `tailor.py`’s renderer to apply that one change and record the ranker version and decision in the manifest.
- [ ] Verify a real PDF for one-page fit, links, and reading order after installing pdfLaTeX and the PDF inspection tools. Keep visual approval separate from acceptance of the ranking.

**Done when** one accepted recommendation can produce a traceable draft while all unselected entries keep the approved wording in `main.tex`.

## 8. Calibrate, verify, and roll out

- [ ] Run the ranker on the initial postings. Compare nearby entries with you, capture your reasons, and replay the postings. Then test on the reserved postings without adjusting weights mid-test. Track agreement with your pair choices, usefulness of the top recommendation, and how often a why-question exposed a missing fact or misplaced assumption.
- [ ] Test exceptions including skipped explanations, ties, contradictory feedback, unsupported tool names, overlapping achievement records, missing replacement wording, and a swap that would remove the only evidence for a requirement.
- [ ] Keep the current selector available while evaluating recommendations. Enable ranker-driven recommendations by default after they improve agreement on the reserved cases and pass the résumé regression checks. Track later recruiter and interview outcomes by submitted version as supporting evidence, accounting for differences in role, posting age, and referral status.

**First milestone** is a working review session for the Princess Cruises posting that explains the order of FeedBack, Borrower Credit Risk Analysis, and Search Engine from Scratch, accepts your ranking, asks why about any unexplained change, and saves the answer locally for the next applicable posting.
