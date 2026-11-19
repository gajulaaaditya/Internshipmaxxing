# Résumé intelligence system
**Research and implementation specification for Aaditya Gajula · November 19, 2026**

Build around the existing 50-entry achievement bank and its 47 source references. Review individual claims, match approved evidence to each posting, and render an auditable one-page résumé. Use a language model for ambiguous posting language and optional wording suggestions. Use code for dates, numbers, attribution rules, selection, layout and release. The system targets interview invitations by making relevant work easier to find and assess.

Assumptions: one user on an existing laptop, primarily U.S. undergraduate applications, 10–200 versions monthly, one page by default, manual submission, private local originals. Performance figures below are proposed targets unless labeled observed.

## 1. Research findings

| Layer | Documented behavior | Confidence and implication |
|---|---|---|
| ATS and application rules | Greenhouse documents routing and automatic rejection based on configured application-question answers. Ashby documents manual application review alongside assisted workflows. | High for these features. Employer settings are unknown. Analyze form eligibility and résumé evidence separately. [Greenhouse rules](https://support.greenhouse.io/hc/en-us/articles/203105595-Application-rules-overview) · [Ashby review](https://docs.ashbyhq.com/application-review) |
| Parsing | Lever extracts readable profile data such as name, organization and contact information. Its parser accepts PDF and DOCX. Greenhouse’s Talent Matching documentation describes skills, titles, experience, dates and employers as inputs. | High for the named surfaces. Test contact, education, employer/title/date association, skills and reading order. Fields differ across integrations. [Lever parsing](https://help.lever.co/s/article/Understanding-Resume-Parsing) · [Greenhouse processing](https://support.greenhouse.io/hc/en-us/articles/41131616864283-Talent-Matching-Data-Processing-FAQ) |
| Exact and Boolean search | Greenhouse Talent Filtering documents exact terms and required AND or preferred OR controls. Lever supports Boolean search and a filter limited to parsed résumé text. | High for these surfaces. Use the posting’s conventional terminology when supported by a real contribution. Recruiter filter labels need not mirror the written qualifications. [Greenhouse filtering](https://support.greenhouse.io/hc/en-us/articles/27104809835291-Talent-Filtering) · [Lever search](https://help.lever.co/s/article/Searching-the-Database-for-Candidates) |
| Semantic matching | iCIMS documents job recommendations based on skills, education, experience and job objective in Digital Assistant, and describes profile-level role fit. Greenhouse documents separate Talent Matching controls and parsed résumé data. | High for documented functionality, low for any inference about public posting keywords, tenant settings, vector models or weights. [iCIMS matching](https://community.icims.com/articles/HowTo/Understanding-iCIMS-ARI) · [iCIMS profiles](https://www.icims.com/en-gb/products/talent-cloud-platform/dynamic-talent-profile/) · [Greenhouse Talent Matching](https://support.greenhouse.io/hc/en-us/articles/47209071041051-Report-on-Talent-Matching-and-AI-opt-out-data) |
| Automated ranking and AI assistance | Workday HiredScore describes grades and qualification-level explanations based on parsed résumés. Ashby’s opt-in AI review evaluates employer-defined criteria and exposes a sortable share met. Ashby’s human reviewer average is separate. | High for product behavior, unknown for any specific requisition. A score belongs to a configured workflow. [Workday release notes](https://doc.workday.com/hiredscore/en-us/workday-hiredscore/hiredscore-release-notes/2026/august/wednesday--5th-august.html) · [Workday integration](https://blog.workday.com/en-us/screen-candidates-50-faster-workday-recruiting.html) · [Ashby AI review](https://docs.ashbyhq.com/ai-assisted-application-review) |
| Human screening and writing | A randomized field study in one online labor market found 8% more hires among jobseekers offered algorithmic writing help. | High for that intervention and population. The study tested writing assistance. The effect of job-specific wording or automated screening for these internships remains unknown. [Original study and published version](https://www.nber.org/papers/w30886) |

Greenhouse identifies layouts with columns, tables, text boxes, headers/footers, images and spaced letters as parse risks. Lever recommends selectable text as a first check. Selectable text can still have merged words or bad reading order. Use standard headings, body text for contact details, ordinary spaces and consistent month/year dates. Follow the posting’s format instructions. Treat one page as an editorial decision. The reviewed sources establish no universal ATS score, magical keyword density, obligatory font, universal six-second rule or blanket PDF penalty. Avoid hidden keywords and repeated lists. Report actual text extraction, direct/partial/missing coverage and eligibility uncertainty separately. [Greenhouse parsing failures](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse) · [Lever parsing](https://help.lever.co/s/article/Understanding-Resume-Parsing)

**Observed baseline.** I extracted the one-page Desktop résumé with pypdf. Education, Experience, Projects & Research and Technical Skills survived in sequence. The university and location merged into “Florida International UniversityMiami, FL.” The file contains “Expected May 2029,” while the bank records December 2028 as your latest confirmed expectation. These are two regression cases. The check used a local extractor and establishes no employer-specific parse or rank. [Baseline PDF](</Users/aadityagajula/Desktop/ResumeAaditya.pdf>) · [Achievement bank](Aaditya_Gajula_Master_Achievement_Bank.md)

## 2. Architecture options

| Option | Quality and control | Cost and latency | Effort and maintenance |
|---|---|---|---|
| A. Rules, approved variants, fixed template | Highly reproducible. More manual work on unfamiliar postings and implicit duties. Valuable fallback and benchmark. | No model fees, local retrieval. | 2–4 focused days after seed review for a usable prototype. Maintain the vocabulary and wording yourself. |
| B. Local relational store, lexical matching, bounded model assistance | Better treatment of ambiguous qualifications and flexible phrasing, with factual review and deterministic export checks. | ~2.2¢ per application in the budget below. Target p95 under 45 seconds, excluding user review. | 5–9 focused days for the first supported path, plus evidence curation and evaluation. One app and one database. |
| C. Hosted Postgres, vector search, cross-encoder and workers | Potentially better candidate discovery at larger scale. Hosting increases concurrent access and data management requirements. Quality gain is unproven. | Additional inference, hosting and maintenance. | 3–5 focused weeks for a reliable hosted version, assuming one developer. |

## 3. Recommended architecture

Choose **B** with A as fallback and comparison. With this bank, score every eligible claim per requirement. Use JSON for interchange and reproducible imports, SQLite for relationships and versioning, and FTS5/BM25 as a secondary text signal. Represent skill relationships as typed relational edges. Move to Postgres when shared access or concurrent writes justify it. Add embeddings or a cross-encoder if held-out tests show the simpler approach consistently misses credible evidence. A model may propose interpretations and edits, and a user must confirm new claims at their exact scope. Record explicit owner confirmation separately from independent verification. [SQLite FTS5](https://www.sqlite.org/fts5.html) · [BEIR research](https://arxiv.org/abs/2104.08663)

## 4. System boundaries and user workflow

~~~mermaid
flowchart TD
    A[Achievement bank and new evidence] --> B[Local import and claim review]
    B --> C[(Local database and evidence references)]
    J[Posting text, public URL or PDF] --> D[Input adapters and sanitization]
    D --> E[Extract and review job requirements]
    E <-. bounded redacted excerpts .-> M[Optional model service]
    C --> F[Score all eligible claims and select sections]
    E --> F
    F --> G[Assemble approved wording]
    G <-. optional suggestions .-> M
    G --> H[Fact checks, rendering and parse verification]
    H --> I[Preview, fit report and user approval]
    I -->|Missing evidence| B
    I -->|Approved version| K[PDF, DOCX and version manifest]
    K --> L[Manual submission and outcome log]
    L --> C
    L --> N[Offline evaluation]
    N --> F
~~~

The evidence view presents proposed claims beside their original records. The job view highlights requirement spans, alternatives and eligibility unknowns. The draft view shows the actual PDF, a baseline diff, selected and omitted evidence, and gaps. The applications view stores the exact version and a timeline of later events. Confirm disputed facts and sensitive form answers in their dedicated views. Approve text and render together. Editing approved text creates a new version.

## 5. Database and achievement-bank seed

| Entity | Fields and relationships |
|---|---|
| Organization, engagement, achievement | Organization name/domain. Engagement records organization, role, kind, scope, date precision, actual/expected dates and state. Achievement links to engagement and keeps import ID and original wording. Related achievements have typed edges such as same project, team award or follow-up. |
| Claim, claim revision | Stable claim ID and immutable revisions. Achievement FK, predicate, action/object, context, performer, technical depth, domain and scope. Typed roles, duties, individual actions, team results, skills, qualifications and leadership. State, confidence rationale, reviewer and timestamp. |
| Metric context | Claim-revision FK, value/range/unit, population, denominator, timeframe, baseline, evaluation run/split, horizon/threshold, team scope and synthetic/historical/live status. |
| Source, evidence edge, decision event | Hash or external locator, visibility, capture date and independence group. Join exact claim revision to source page/span with a supports/conflicts relationship. Decisions append actor, time, new state and reason. |
| Skill, alias, skill relation, claim skill | Taxonomy version and aliases. Directed relations include equivalent, implies in context, related and distinct. Claim links carry used, coursework, exploratory and demonstrated scopes. |
| Wording variant, variant claim, inclusion rule | Approved alternative text, allowed slots and exact claim revision IDs. Job-family/section eligibility, approval revision and overlap group. |
| Posting snapshot, requirement group, requirement | Normalized immutable text and hash. Requirement has original offset span, category, priority, constraints and extraction confidence. AND/OR groups preserve alternatives and conjunctions. |
| Match run, requirement match, résumé version/item | Snapshot IDs, scoring and template versions, verdicts and explanations. Ordered items reference claim revisions, recorded validation, artifact hashes and approval. |
| Application, application event | Posting/resume IDs, employer/requisition, referral, submitted time, channel and status events. |

Stage all 50 entries with provenance and preserve original bytes/hash. The inventory is an import source. Its résumé-use field does not approve individual claims. Split dates, methods, ownership, results and awards into atomic records, then resolve conflicts. Import retries use the same snapshot hash and IDs. A correction appends a revision and can invalidate an old claim for future exports. Preserve past exports with a stale-evidence label. Git tracks code, fixtures and nonprivate taxonomy/version policies. Keep private originals and database exports encrypted and separate, with backups and explicit deletion. [Machine-readable seed](Aaditya_Gajula_Achievement_Inventory.json)

| Actual seed evidence | How the design would use it | What still needs review |
|---|---|---|
| **T05 Search Engine from Scratch** | For SWE/IR, foreground Python, FastAPI, inverted indexing and BM25. The stored 538.919 → 17.138 ms comparison can be used with the specific query and 10,000-document synthetic benchmark. | Verify personal ownership for additional capabilities and keep benchmark scope in the text. |
| **T01/A03 PharmaBeacon** | For applied ML, foreground a team forecasting prototype using historical FDA data. For analytics, surface the explainable dashboard and evaluation work. | Hold 90.03% accuracy and 61.3% recall until a frozen evaluation ties them to the right population, threshold and run. A03 second place remains owner-reported. Require proof of your contribution before promoting specific APIs or pipelines. |
| **A02/T03 BackFill, T04 separate 8-K research** | For quant, highlight archived FDA data and reproducible event-driven research with **MLH Best Use of Solana** as a team result. | Preserve individual component attribution. Keep 8-K experiments separate and evaluate backtest results as historical claims. |
| **W03 My Style, W01 Parrami, T14/T15** | User-confirmed SWE title. Credit analysis and Excel can support finance roles after scope review. SQL/SAS can draw on synthetic analysis T14 and the submission record T15. | My Style dates and employer impact metrics need review. The SQL/SAS exercise belongs to its own engagement. |
| **T11 BERT/SEC research, W04 FIU offer** | Present T11 as exploratory research and W04 as a dated offer if relevant. | Confirm later milestones before presenting formal appointment, completed models or publication. |
| **P01, E01, T10 and C/C++** | Break Through Tech acceptance and FIU enrollment can be reviewed for use. | Acceptance is distinct from certification. Expected graduation December 2028 is latest owner-confirmed. Reconcile exact degree wording, Claude Sentinel attribution, and where C/C++ were personally used. |

## 6. Job analysis, ranking and page selection

Save posting snapshot and preserve headings, list structure, verbatim spans and placement. Extract title, seniority, required and preferred qualifications, languages/frameworks, domain, duties, education, years, soft skills, location, authorization and explicit disqualifiers. Use heading and modal language jointly. “Required” in an application question differs from “preferred” in a skill list, while “we use X” under a team description may only be context. Strip navigation and benefits/EEO boilerplate from scoring, retaining policies that contain real gates. Preserve negation, dates, units, quantifiers and alternatives. Show disagreement between model and rules. Give applicant-confirmed eligibility one of four states: met, unmet, unknown or inapplicable. Merge overlapping dated intervals before counting relevant years. Leave application answers to the user.

Normalize common aliases with token boundaries and punctuation-aware rules for C++, C#, .NET, R and Go. Document the direction of implications. Documented pandas and Python use supports Python data analysis. Spark needs its own evidence. A semantic model can suggest related claims for review. It cannot confer proficiency.

Score all eligible claim clusters. The following are tunable priors, with each factor tied to a specific ranking tradeoff:

- **Requirement priority:** required 3, central duty 2, preferred 1. Boilerplate and eligibility gates contribute zero to this relevance score. Missing a gate is reported separately.
- **Match factor:** demonstrated exact or reviewed equivalent 1.0, partial/directional 0.5, adjacent 0.2, missing 0. Adjacent evidence may appear in the fit report without asserting the skill.
- **Evidence factor:** independently supported at the asserted scope 1.0, expressly user-confirmed 0.85, team artifact 0.75 for a team-scoped claim. These are ordering preferences, not confidence probabilities. Disputed/unreviewed claims are ineligible, regardless of relevance.
- **Block score:** sum priority × match × evidence. Use BM25 rank and outcome specificity as tie-breaks capped at 0.10 each. Magnitude of a metric earns no extra weight. For OR, use the best match once. For AND, preserve each component and separately report whether all were met.

Optimize weighted coverage as a set. For each requirement use the strongest selected match so repeated bullets have diminishing value. Start with a 0.20 bonus per additional relevant competency and a 0.25 penalty per overlapping story pair. Reserve space for contact and education, use actual wrapped line costs, enforce one variant per overlap group and a default maximum of two bullets per project. Choose the best marginal value per line, then try swaps. If export overflows, use a shorter approved variant or remove a low-value block. Maintain accessible font size and margins. Test exact selection or integer programming only if replay shows a material gain over greedy selection.

Calibrate on development postings using required-evidence recall, false positives, nDCG and blind reader comparisons. Run sensitivity tests on all weights and test held-out jobs once per locked policy. If implicit terms consistently hide strong candidates, compare BM25 to exact cosine over local embeddings, fuse candidate ranks, then benchmark a cross-encoder on top candidates. A model can classify difficult claim/requirement pairs using two quoted spans and enumerated labels. The code validates IDs and allowable scope. On this bank all results should be explainable by the source and weighted contribution, including rejected claims and the marginal reason for omission. No displayed score should suggest an employer ranking. [BEIR research](https://arxiv.org/abs/2104.08663) · [Cross-encoder study](https://arxiv.org/abs/2212.06121)

For a SWE posting requesting Python, REST APIs and testing, surface T05 and consider reviewed GridLock contributions. For forecasting and stakeholder communication, lead with PharmaBeacon and its discovery evidence, with metrics held. For financial analysis and SQL/SAS, pair Parrami with independent practice or the SAS assessment and identify exactly which requirement each satisfies. For event-driven quant research, lead with BackFill and its precise team prize.

## 7. Generation, formats and quality gates

Start with approved clause variants and fixed slots for titles, dates, tools and numbers. Give an optional wording model only selected claim IDs and their approved facts, verbs and scope. Request text plus span-to-claim bindings in structured output. Reject unknown claims, added quantities, titles or technology names, and unsupported changes such as “contributed” → “led.” A citation ID cannot prove entailment. MVP exports only preapproved language or text that the user has reviewed clause by clause. Every approved draft goes through the same hard gates.

Prioritize **action + particular contribution + evidence + result**. Use a result when defensible. Add a summary only if it supplies a distinct, relevant bridge. Order demonstrated skills by relevance. Keep education visible for internship eligibility and reverse chronology within employment. Projects can lead when they best establish the technical role. Keep source IDs in the private manifest.

| Format | Use |
|---|---|
| Markdown | Good for drafts and diffs. Layout depends on conversion. |
| DOCX | Editable export and source. Use single-column paragraph styles and real hyperlinks. Layout can vary across editors. |
| HTML | Good local report. Print output can be stable with a pinned browser, but a second renderer can drift from DOCX. |
| LaTeX | Useful for Overleaf and exact typography. Verify ligatures, Unicode mapping and extraction. The baseline PDF shows why visual order alone is insufficient. |
| PDF | Fixed-layout delivery. Generate selectable text from the approved DOCX via pinned LibreOffice and verify the pair. Follow portal-specific instructions. |

| Validation layer | Release behavior |
|---|---|
| Factual integrity | Block unresolved required dates, wrong titles, invalid evidence IDs, held metrics, asserted team work as individual, and skills inferred from the posting. Every external clause has approved claim revisions. |
| Coverage | Show direct, partial, adjacent, missing and unknown alongside text spans and links. A gap can remain valid and visible. |
| ATS compatibility | Read DOCX structure and compare PDF extraction with pypdf and Poppler when configured against the canonical ordered fields. Test associations, Unicode/punctuation, headings, links and one-page fit. Review the rendered preview. Local tests measure recoverability. |
| Readability and overoptimization | Flag excessive repetition, copied phrases, generic claims, date/section duplication, wrapping and unreadable sizes. Show top-half preview and source/claim diff. |
| Approval | Record exact content and render hashes. Any edit resets approval. Save bytes, version and validation manifest atomically. |

## 8. Stack, privacy and operational limits

Use Python with Pydantic, SQLite with FTS5, SQLAlchemy and Alembic, a loopback FastAPI/Jinja UI, python-docx, pinned LibreOffice, pypdf and Poppler, and pytest fixtures. Expose the same service functions through a local CLI for import and replay. Run model calls through one provider adapter with a pinned structured-output model, capped retries and an offline variant mode. Optional local embeddings/cross-encoder are rebuildable indexes if later justified. A hosted model simplifies deployment and costs usage fees. A local model keeps content on-device and adds hardware, distribution and evaluation work. [SQLite FTS5](https://www.sqlite.org/fts5.html) · [Model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-mini)

Private evidence, contacts, source URLs and sensitive eligibility data stay local. Send narrow claim excerpts and the relevant posting text, with identifiers redacted where possible. Keep prompts out of ordinary logs. Use OS credentials, encrypted backups, deletion controls and loopback access with cross-site request protection. For the OpenAI Responses API, disable application-state storage where supported and verify retention separately. Default abuse-monitoring retention can still apply. [Provider data controls](https://developers.openai.com/api/docs/guides/your-data)

Treat outside content as data. Give extraction and wording models no authority to use tools or mutate the bank. Later public URL adapters validate destinations and redirects, restrict responses, avoid login cookies and fall back to paste when access is restricted. Later PDF adapter validates type, limits size/pages/time and isolates processing. OCR errors require review. Model or fetch failures leave a usable draft or a clear recovery path.

## 9. MVP roadmap

| Phase | Build | Exit test |
|---|---|---|
| 1. Private evidence and first usable export | Import and review claims, paste JD, extract requirements, rank, use approved variants, preview/export PDF and DOCX, record application. | Four representative job families produce approved one-page drafts. Stale, disputed and held claims are blocked. |
| 2. Prove quality and expand inputs | Add benchmark and human trials, supported URL and text PDF intake, faster corrections and evidence review. | Pass held-out accuracy, parser and time targets before reporting gains. |
| 3. Add complexity where it pays | Pilot embeddings/rerankers and controlled wording on measured misses. Improve outcome tracking, add optional layout variants. | Better held-out performance and reader preference with factual precision and layout maintained. |

## 10. Evaluation and outcome tracking

Freeze 60 postings, 12 each across SWE, ML, DS/analytics, quant and research. Hold out four per family, grouped by employer, duplicate requisition/template and time. Include ambiguous alternatives, mixed seniority and eligibility. Preserve dated, sanitized posting snapshots. Two people independently label a subset with required/preferred classification, supporting spans and evidence relevance from 0–3, then adjudicate differences. Maintain 20 independent parser/claim fixtures including image-only PDF, joined employer/location, Unicode, ambiguous dates, overlapping employment and ownership drift.

Compare (1) the frozen Desktop résumé, (2) a generic résumé rewriter with the same approved facts and template, and (3) the pipeline. Add deterministic and semantic ablations. Randomize left/right display for blinded readers. Measure requirement span F1, required/preferred macro F1, disqualifier recall and false alarms, eligible evidence recall, evidence precision, nDCG@10, and supported weighted coverage. Measure unsupported clause rate, degree/date/title and field-association accuracy, overflow, reading order, links and formatting. Target zero unsupported clauses and 100% critical-field recovery on the accepted fixture set, with denominators. Compare blind preference and rubric scores for specificity, credibility and ease of scanning. Initial targets are over 60% preference across at least 20 pairs versus the rewriter and 30% less median review time than manual tailoring. Report counts and uncertainty.

Log company/requisition, posting version, job family, timing, referral, known eligibility, exact résumé version and matched requirements. Append assessment, recruiter response, interview, rejection and offer timestamps. Define interview invitation within 30 days as the primary metric, using fully observed windows. Track open applications separately and record stage transitions explicitly. Report counts and Wilson intervals. Five invitations among 50 applications give an approximate 95% interval of 4–21%.

For a live test, choose genuine applications before assigning a résumé policy. Randomize one credible version policy per requisition, stratified by family and referral status, with comparable calendar windows. Track employer clustering, referral, eligibility and posting age. Record deviations and analyze assigned policy as well as actual submission. Avoid duplicate applications and repeated significance checks. Observational outcomes support associations. Tune weights on offline labels first and require held-out improvement before updating them. At low volume, review time, evidence quality and blinded preference will provide clearer feedback than short-term conversion changes.

## 11. Cost estimates

Assume two model calls use **12,000 input and 2,000 billed output tokens** together, including reasoning within the cap. At **$0.75/M input and $4.50/M output**, each costs **$0.018**, or **$0.0216** with a 20% reserve. Rates checked November 19, 2026. No recurring hosting assumed on the existing laptop. [GPT-5.4 mini published rates](https://developers.openai.com/api/docs/models/gpt-5.4-mini)

| Applications per month | Base inference | With reserve |
|---:|---:|---:|
| 10 | $0.18 | $0.22 |
| 50 | $0.90 | $1.08 |
| 200 | $3.60 | $4.32 |

Local rule-only runs have zero inference charges. Hardware, backups, hosted services, external ATS testing and review labor are excluded. At three minutes per review, 200 applications take about ten review hours. Set monthly token limits, cache extraction by posting/model/schema version and measure actual per-run spend before scaling.

## 12. Failure modes

| Failure | Prevention or recovery |
|---|---|
| Related tool gets treated as demonstrated skill | Directional taxonomy and reviewed evidence requirements. |
| Metric or award outranks relevance, team credit becomes personal | Bounded specificity weight, exact attribution, run-bound metrics and factual release gate. |
| Posting boilerplate becomes a blocker | Span-grounded classification and explicit eligibility review. |
| Beautiful layout drops fields | Extraction round trip and visual check, with a validated alternate document format available. |
| Model fails or posting tries to direct it | Schema checks, scoped context, no tools, retry cap and local fallback. |
| Approved version changes after review | Hash-bound approval and immutable exports. |
| One project dominates the first page | Reward new coverage, constrain overlap and surface better omitted alternatives. |
| Résumé looks optimized but outcomes decline | Compare credible baselines, track confounders and keep actual conversion distinct from offline proxy tests. |

## 13. Implementation specification

Modules: **inventory** stages claims and manages decisions. **postings** ingests and extracts grounded rules. **matching** evaluates typed pairs. **planner** selects with constraints. **render** generates the Word/PDF pair. **validation** checks references, assertion strength and extraction. **applications** records the outcome timeline. **evaluation** replays frozen inputs. The model adapter has no database write authority.

| Local API | Request → response |
|---|---|
| POST /inventory/import | Schema version, snapshot hash and payload → staged IDs, conflicts and error report. Identical retry returns original import result. |
| POST /claims/{id}/decisions | Expected revision, decision, reviewer reason and source-span IDs → immutable revision. Stale edits return 409. |
| POST /postings | Text or supported source reference → snapshot ID, hash, requirement groups and review status. Unsupported source offers paste recovery. |
| POST /drafts | Snapshot, reviewed requirement revision, bank revision, role family, policy and page cap → ordered plan, fit report, validation state and preview ID. |
| POST /drafts/{id}/approve | Version ID, content hash and render hash → approval ID after hard checks. |
| GET /exports/{version_id} | Format → exact immutable approved bytes and digest. |
| POST /applications and POST /applications/{id}/events | Version IDs, timestamp, referral and stage event → persisted ID. Same idempotency key creates one record. |

~~~json
{
  "requirement": {
    "id": "req_7",
    "text": "Experience building Python APIs",
    "span": {"start": 120, "end": 151},
    "kind": "technical_skill",
    "importance": "required",
    "skill_ids": ["python", "api_development"]
  },
  "match": {
    "requirement_id": "req_7",
    "verdict": "direct",
    "inventory_id": "T05",
    "claim_revision_ids": ["example_t05_python_r1", "example_t05_fastapi_r1"],
    "reason": "The repository documents a Python search API built with FastAPI."
  }
}
~~~

IDs and offsets are illustrative. Production spans are zero-based and end-exclusive against frozen normalized text. Validation verifies that the selected span reproduces the requirement text or records an explicit split from the original sentence.

~~~text
snapshot = preserve_and_sanitize(input)
requirements = review(extract_with_spans(snapshot))
claims = active_approved_claims(bank_revision)
matches = score_all(requirements, claims, taxonomy, policy)
plan = select_approved_variants(matches, role_family, page_budget)

for each of at most three render attempts:
    preview = render_docx_and_pdf(plan)
    report = validate_claims_and_parse(plan, preview)
    if no overflow: stop rendering
    plan = shorten_or_remove_lowest_value_block(plan)

show preview, claim bindings, gaps, and report
if hard checks pass and user approves matching content and render hashes:
    save immutable exports and manifest
~~~

Acceptance for phase 1: double import stages 50 rows and 47 references once. Held PharmaBeacon metrics, unresolved Claude Sentinel attribution and disputed My Style dates stay ineligible. BackFill retains the exact team award. P01 cannot become a completed credential without new evidence. FIU and Miami extract separately, with the latest approved expected graduation. “Python or Java” counts once, and Spark remains a gap when evidence contains pandas alone. An untrusted posting cannot edit the bank or cause private source content to be included. Changing a draft invalidates approval. Reopening a tracked application retrieves its exact export. Benchmark thresholds above are proposed and must be tested before reporting improvement.

**The exact MVP I would build first:** A one-user local app that imports your bank and reviews the highest-value claims for FIU, Search Engine from Scratch, PharmaBeacon, BackFill, Parrami and the remaining relevant experiences. Paste one posting, review its extracted requirements, select from approved evidence, and approve a one-page PDF plus editable DOCX. Save the application and version. This single path addresses the stale graduation date and merged fields observed in the baseline, puts role-specific projects ahead of weaker evidence, and prevents held metrics from turning into résumé claims. It also gives you a credible comparison against your current résumé and a generic rewrite before investing time in more automation.
