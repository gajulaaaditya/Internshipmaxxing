"""Generate a local, baseline-first résumé preview from a pasted posting."""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASELINE = {"experience": ("T06", "W01", "W03"), "projects": ("T05", "T04", "T01")}
SECTION = {"experience": "Experience", "projects": r"Projects \& Research"}
BULLET_COUNT = {"experience": 3, "projects": 2}
# Each baseline entry uses the original block in main.tex. The catalog supplies candidate swaps.
BASELINE_ENTRIES = {
    "T06": {"title": "Te Vārtā", "topics": ["applied AI", "finance"], "ended": "present"},
    "W01": {"title": "Parrami Finance Private Limited", "topics": ["finance", "Excel"], "ended": "2026-07"},
    "W03": {"title": "My Style", "topics": ["Python", "APIs", "Git", "testing", "web development"], "ended": "2025-07"},
    "T05": {"title": "Search Engine from Scratch", "topics": ["Python", "APIs", "search"]},
    "T04": {"title": "GatorQuantHacks", "topics": ["Python", "finance", "backtesting"]},
    "T01": {"title": "PharmaBeacon", "topics": ["Python", "applied AI", "dashboards", "forecasting"]},
}
FIXED_TOPICS = {"SQL", "Python", "APIs", "Git", "statistics", "finance", "applied AI", "search"}
TOPICS = {
    "SQL": r"sql",
    "Python": r"python",
    "Excel": r"excel",
    "Microsoft Office": r"microsoft office",
    "APIs": r"apis?|api calls|restful",
    "Git": r"git|version control",
    "statistics": r"statistics|statistical",
    "communication": r"presentation|presenting|public speaking|communication",
    "stakeholders": r"stakeholders?|gather requirements|business partners",
    "finance": r"financial modeling|quantitative finance|credit risk|lending|investment research",
    "search": r"information retrieval|search engine|bm25",
    "forecasting": r"forecasting|predictive modeli[ns]g",
    "backtesting": r"backtest\w*|event studies|trading strateg\w*",
    "applied AI": r"machine learning|agentic ai|applied.ai|generative ai|llms?",
    "guest feedback": r"guest (?:follow.up|chat|feedback)|post.cruise contact|conversational (?:ai|data)",
    "AI evaluation": r"evaluat\w* (?:ai )?outputs|validat\w* ai outputs|responsible ai",
    "human review": r"human (?:review|in the loop|oversight)",
    "dashboards": r"dashboards?|visualizations?|data visualisation",
    "reporting": r"reporting|visual reports|operational reports",
    "event operations": r"event operations|event logistics|event management",
    "sustainability": r"sustainability|waste diversion",
    "volunteer coordination": r"volunteer coordination|coordinat\w* volunteers|volunteer management",
    "automation": r"automati\w*|automat\w*",
    "data validation": r"data validation|validat\w* data",
    "SAS": r"sas",
    "testing": r"unit tests?|automated tests?|test automation",
    "geospatial": r"geospatial|gis|spatial analysis",
    "web development": r"web development|web applications?|website building|front.end",
    "Snowflake": r"snowflake(?! cortex)",
    "Power BI": r"power bi",
    "Tableau": r"tableau",
    "Microsoft Copilot": r"microsoft copilot",
    "Snowflake Cortex AI": r"snowflake cortex(?: ai)?",
    "knowledge bases": r"knowledge[ -]base|structuring content",
}
HEADINGS = {
    "job description": 2, "essential functions": 2, "responsibilities": 2,
    "qualifications": 3, "required qualifications": 3, "minimum qualifications": 3,
    "preferred qualifications": 1, "knowledge, skills, and abilities": 2,
    "knowledge, skills and abilities": 2,
}
STOP = re.compile(r"^(?:summer \d{4} internship program|program details|about (?:us|the company)|benefits|job info)\b", re.I)
ELIGIBILITY = re.compile(r"graduat|current undergraduate|sophomore|freshm[ae]n|first.year|work authori|sponsor|full dates|in.office|relocat|citizen|candidates must|cohort:", re.I)
BLOCK = re.compile(r"(?ms)^([ \t]*)\\resume(?:Subheading|ProjectHeading)\b.*?^[ \t]*\\resumeItemListEnd\b[^\S\n]*")
METRIC = re.compile(r"(?<!\w)[$~≈]?\d+(?:[.,]\d+)*(?:(?:--?|–)\d+(?:[.,]\d+)*)?(?:[%+]|[kKmMbBsS]\b|(?:st|nd|rd|th)\b)?(?!\w|-[A-Z])")


def load_entries():
    inventory = json.loads((ROOT / "Aaditya_Gajula_Achievement_Inventory.json").read_text())
    records = {item["id"]: item for item in inventory["achievements"]}
    entries = json.loads((ROOT / "resume_entries.json").read_text())
    for section, keys in BASELINE.items():
        for key in keys:
            entries[section][key] = BASELINE_ENTRIES[key].copy()
    for section, expected_count in BULLET_COUNT.items():
        for key, entry in entries[section].items():
            entry["evidence"] = {}
            for evidence_id in [key, *entry.get("related", [])]:
                record = records[evidence_id]
                if record["resume_use"] not in {"Yes", "Optional"}:
                    raise ValueError(f"{evidence_id} is held in the achievement inventory")
                entry["evidence"][evidence_id] = record["sources"].split()
            if ((key not in BASELINE[section] and len(entry["bullets"]) != expected_count)
                    or not set(entry["topics"]) <= TOPICS.keys()):
                raise ValueError(f"Invalid bullets or topic labels for {key}")
    return entries


def analyze(posting):
    requirements = {}
    priority = 2
    for number, line in enumerate(posting.splitlines(), 1):
        line = line.strip().lstrip("-• ").strip()
        heading = line.rstrip(":").lower()
        if STOP.match(heading):
            break
        if heading in HEADINGS:
            priority = HEADINGS[heading]
            continue
        for sentence in re.split(r"(?<=[.!?;])\s+", line):
            matches = {topic: match for topic, pattern in TOPICS.items()
                       if (match := re.search(r"(?<!\w)(?:" + pattern + r")(?!\w)", sentence, re.I))}
            alternatives = set()
            for first, second in (("Power BI", "Tableau"), ("Python", "SQL")):
                if first in matches and second in matches:
                    left, right = sorted((matches[first], matches[second]), key=lambda m: m.start())
                    if re.fullmatch(r"\s+or\s+", sentence[left.end():right.start()], re.I):
                        alternatives.update({first, second})
                        add_requirement(requirements, (first, second), priority, number, sentence)
            for topic in matches.keys() - alternatives:
                add_requirement(requirements, (topic,), priority, number, sentence)
    eligibility = [line.strip() for line in posting.splitlines() if ELIGIBILITY.search(line)]
    return requirements, eligibility


def add_requirement(requirements, topics, priority, number, span):
    current = requirements.get(topics)
    if current is None or priority > current["priority"]:
        requirements[topics] = {"priority": priority, "line": number, "span": span}


def entry_topics(selection, entries):
    return {
        topic for section, ids in selection.items()
        for entry_id in ids for topic in entries[section][entry_id]["topics"]
    }


def coverage(selection, entries, requirements):
    shown = FIXED_TOPICS | entry_topics(selection, entries)
    return {topics for topics in requirements if shown.intersection(topics)}


def select(entries, requirements):
    baseline = coverage(BASELINE, entries, requirements)
    best = None
    for section, current in BASELINE.items():
        for position, outgoing in enumerate(current):
            for incoming in entries[section].keys() - set(current):
                revised = dict(BASELINE)
                revised[section] = (*current[:position], incoming, *current[position + 1:])
                if section == "experience":
                    end_dates = [entries[section][key]["ended"] for key in revised[section]]
                    if end_dates != sorted(end_dates, reverse=True):
                        continue
                shown = coverage(revised, entries, requirements)
                gained, lost = shown - baseline, baseline - shown
                gain = sum(requirements[key]["priority"] for key in gained)
                cost = sum(requirements[key]["priority"] for key in lost)
                # Require a new duty or qualification. Keep any unique required coverage.
                if gain - cost < 2 or not any(requirements[key]["priority"] >= 2 for key in gained):
                    continue
                if any(requirements[key]["priority"] == 3 for key in lost):
                    continue
                outgoing_topics = set(entries[section][outgoing]["topics"])
                outgoing_relevance = sum(item["priority"] for key, item in requirements.items()
                                         if outgoing_topics.intersection(key))
                rank = (gain - cost, -cost, -outgoing_relevance, incoming, outgoing)
                if best is None or rank > best[0]:
                    best = (rank, revised, section, outgoing, incoming, gained, lost)
    return best


def latex(value):
    escapes = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
               "{": r"\{", "}": r"\}", "\\": r"\textbackslash{}", "~": r"\textasciitilde{}",
               "^": r"\textasciicircum{}", "ā": r"\=a"}
    return "".join(escapes.get(character, character) for character in value)


def bold_metrics(text):
    parts = []
    cursor = 0
    for match in METRIC.finditer(text):
        parts.extend([latex(text[cursor:match.start()]), r"\textbf{" + latex(match[0]) + "}"])
        cursor = match.end()
    return "".join([*parts, latex(text[cursor:])])


def render_entry(entry, section, indent):
    title = latex(entry["title"])
    date = latex(entry["date"])
    if section == "experience":
        args = [title, latex(entry["location"]), latex(entry["role"]), date]
        heading = r"\resumeSubheading"
    else:
        name = rf"\textbf{{{title}}} $|$ \emph{{{latex(entry['stack'])}}}"
        if url := entry.get("url"):
            if not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+", url):
                raise ValueError(f"Unexpected project link for {entry['title']}")
            name += rf" $|$ \href{{{url}}}{{\underline{{Link}}}}"
        args, heading = [name, date], r"\resumeProjectHeading"
    lines = [indent + heading, indent + "  " + "".join("{" + arg + "}" for arg in args),
             indent + r"  \resumeItemListStart"]
    for bullet in entry["bullets"]:
        parts = bullet.split("**")
        if len(parts) % 2 == 0:
            raise ValueError(f"Unclosed metric emphasis for {entry['title']}")
        body = "".join(r"\textbf{" + latex(part) + "}" if i % 2 else bold_metrics(part)
                       for i, part in enumerate(parts))
        lines.append(indent + r"    \resumeItem{" + body + "}")
    return "\n".join([*lines, indent + r"  \resumeItemListEnd"])


def render(source, entries, selection, graduation):
    source, count = re.subn(r"\{Expected [A-Za-z]+ 20\d{2}\}", "{Expected " + graduation + "}", source)
    if count != 1:
        raise ValueError("Expected one graduation field in main.tex")
    if r"\usepackage[hidelinks]{hyperref}" in source:
        source = source.replace("\\usepackage{hyperref}\n", "", 1)
    for section, heading in SECTION.items():
        marker = r"\section{" + heading + "}"
        if source.count(marker) != 1:
            raise ValueError(f"Expected one {heading} section in main.tex")
        before, after = source.split(marker, 1)
        body, separator, rest = after.partition(r"\section{")
        blocks = list(BLOCK.finditer(body))
        if len(blocks) != len(BASELINE[section]):
            raise ValueError(f"Update BASELINE to match the number of {section} entries in main.tex")
        for block, original, selected in reversed(list(zip(blocks, BASELINE[section], selection[section]))):
            title = entries[section][original]["title"]
            if "{" + title + "}" not in block[0]:
                raise ValueError(f"Expected {title} in its baseline slot in main.tex")
            if original != selected:
                replacement = render_entry(entries[section][selected], section, block[1])
                body = body[:block.start()] + replacement + body[block.end():]
        source = before + marker + body + separator + rest
    return source


def compile_pdf(folder):
    compiler = shutil.which("pdflatex")
    if not compiler:
        return "pdfLaTeX unavailable. Generated source requires a compiled preview."
    with tempfile.TemporaryDirectory() as temporary:
        result = subprocess.run(
            [compiler, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory=" + temporary, "resume.tex"],
            cwd=folder, capture_output=True, text=True, timeout=60, check=False,
        )
        if result.returncode:
            (folder / "compile.log").write_text(result.stdout + result.stderr)
            return "Compilation failed. See compile.log."
        pdf = Path(temporary) / "resume.pdf"
        pdfinfo = shutil.which("pdfinfo")
        if pdfinfo:
            info = subprocess.run([pdfinfo, str(pdf)], capture_output=True, text=True, check=False)
            if not re.search(r"^Pages:\s+1\s*$", info.stdout, re.M):
                return "One-page check failed. PDF was withheld."
        text_status = "Reading order requires manual review."
        if extractor := shutil.which("pdftotext"):
            extracted = subprocess.run([extractor, str(pdf), "-"], capture_output=True,
                                       text=True, check=False)
            lines = [" ".join(line.casefold().split()) for line in extracted.stdout.splitlines()]
            headings = ("education", "experience", "projects & research", "technical skills")
            if extracted.returncode or tuple(line for line in lines if line in headings) != headings:
                return "Section reading order check failed. PDF was withheld."
            text_status = "Section order passed text extraction."
        shutil.copyfile(pdf, folder / "resume.pdf")
    return ("Compiled and verified one page." if pdfinfo else "Compiled. Page count unverified.") + (
        f" {text_status} Review page fill, field associations, and links before use."
    )


def report(folder, entries, selection, swap, requirements, eligibility, graduation, render_status):
    lines = ["# Résumé tailoring review", "", f"- Expected graduation is **{graduation}**.",
             f"- {render_status}", "", "## Changes for this posting", ""]
    if swap:
        _, _, section, outgoing, incoming, gained, lost = swap
        lookup = entries[section]
        lines.append(f"Replaced **{lookup[outgoing]['title']}** with **{lookup[incoming]['title']}**.")
        for label, keys in [("Coverage gained", gained), ("Coverage lost", lost)]:
            lines.append(f"- {label} — " + (", ".join(" or ".join(key) for key in sorted(keys)) or "none"))
    else:
        lines.append("Kept the evidence-reviewed baseline. No candidate clearly improved the match.")
    lines += ["", "## Baseline and page fit", "",
              "- The original descriptions, metrics, and skills in main.tex are applicant-confirmed for this workflow.",
              "- Each unchanged entry keeps its original wording and length. Review any replacement in the compiled PDF for page fill and wrapping.", "",
              "## Requirements matched by the displayed evidence", ""]
    shown = coverage(selection, entries, requirements)
    demonstrated = entry_topics(selection, entries)
    for topics, item in sorted(requirements.items(), key=lambda row: (-row[1]["priority"], row[0])):
        if demonstrated.intersection(topics):
            status = "Shown in a selected entry"
        else:
            status = "Skills or coursework only" if topics in shown else "Review gap"
        lines.append(f"- **{' or '.join(topics)}** — {status}. Posting line {item['line']}.")
    if not requirements:
        lines.append("No tracked requirements were detected. Review the posting manually.")
    lines += ["", "## Eligibility to confirm from the posting", ""]
    lines.extend(f"- {line}" for line in eligibility)
    if not eligibility:
        lines.append("Review eligibility against the full posting and application form.")
    lines += ["", "## Selected achievement records", ""]
    for section, keys in selection.items():
        for key in keys:
            entry = entries[section][key]
            unquantified = sum("**" not in bullet for bullet in entry.get("bullets", []))
            evidence = ", ".join(f"{eid} ({' '.join(sources)})" for eid, sources in entry["evidence"].items())
            gap = f" Qualitative bullets awaiting supported metrics: {unquantified}." if unquantified else ""
            lines.append(f"- **{entry['title']}** — {evidence}.{gap}")
    (folder / "review.md").write_text("\n".join(lines) + "\n")
    return shown


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("posting", type=Path, help="plain-text posting snapshot")
    parser.add_argument("--graduation", required=True, metavar='"May 2028"', help="confirmed graduation for this application")
    parser.add_argument("--out", required=True, type=Path, help="new output directory; each run is a separate draft")
    args = parser.parse_args()
    if not re.fullmatch(r"(?:January|February|March|April|May|June|July|August|September|October|November|December) 20\d{2}", args.graduation):
        parser.error("use a full month and year for --graduation")
    try:
        posting = args.posting.read_text(encoding="utf-8-sig")
        if not posting.strip():
            raise ValueError("The posting is empty")
        source = (ROOT / "main.tex").read_bytes().decode("utf-8")
        entries = load_entries()
        requirements, eligibility = analyze(posting)
        swap = select(entries, requirements)
        selection = swap[1] if swap else BASELINE
        draft = render(source, entries, selection, args.graduation)
        args.out.mkdir(parents=True, exist_ok=False)
        (args.out / "posting.txt").write_text(posting)
        (args.out / "resume.tex").write_text(draft)
        try:
            render_status = compile_pdf(args.out)
        except subprocess.TimeoutExpired:
            render_status = "PDF compilation exceeded 60 seconds. Generated source requires a compiled preview."
        shown = report(args.out, entries, selection, swap, requirements, eligibility, args.graduation, render_status)
        manifest = {
            "graduation": args.graduation, "baseline_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "posting_sha256": hashlib.sha256(posting.encode()).hexdigest(),
            "artifacts_sha256": {name: hashlib.sha256((args.out / name).read_bytes()).hexdigest()
                                 for name in ("resume.tex", "resume.pdf", "review.md")
                                 if (args.out / name).exists()},
            "selected": selection, "swap": {"section": swap[2], "out": swap[3], "in": swap[4]} if swap else None,
            "requirements": [{**item, "topics": topics, "shown": topics in shown}
                             for topics, item in sorted(requirements.items())],
            "render_status": render_status,
        }
        (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    except (OSError, ValueError) as error:
        parser.exit(2, f"{parser.prog}: {error}\n")
    print(f"{args.out / 'resume.tex'}\n{args.out / 'review.md'}\n{render_status}")


if __name__ == "__main__":
    main()
