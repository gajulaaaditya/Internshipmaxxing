# Internship résumé workflow

Use [main.tex](main.tex) as the approved source for résumé content and layout. The local workflow preserves its wording, metrics, skills, section order, and density. A draft changes the expected graduation date for the application and replaces at most one complete entry when it adds evidence for a central duty or qualification.

## Run it

Save the full posting as plain text, including its qualifications, and run from this folder with Python 3.8 or newer. Use the expected graduation date you intend to give on the application.

```sh
python3 tailor.py /path/to/posting.txt --graduation 'May 2028' --out '../Tailored Resumes/company-requisition-v1'
```

Open `review.md` first. It shows the proposed change, the evidence gained or lost, preferred tools that still need evidence, eligibility lines, and achievement IDs. Check those against the saved `posting.txt`. Review the generated `resume.tex` and use `manifest.json` to identify the exact draft later. The CLI writes `resume.pdf` if pdfLaTeX is available and runs page-count and section-order checks when the corresponding Poppler tools are installed. Inspect the actual PDF for one-page fill, heading/date associations, wrapping, and links. Use a new output folder for each revision.

## How it decides

- It preserves the baseline by default. A swap must add a recognized duty or qualification, gain at least two weighted coverage points after losses, and retain any uniquely covered required topic. Required qualifications, duties, and preferred qualifications have weights of 3, 2, and 1. Repeated topic mentions count once. Those weights express drafting priorities and have no employer ranking meaning.
- It uses a curated catalog in [resume_entries.json](resume_entries.json) only for replacement entries. Each maps back to the achievement inventory, and held achievement IDs are blocked. Review each new bullet and its contribution scope. Aim for a replacement with comparable wrapped length and keep three bullets per experience or two per project. Bold achievement numbers in `main.tex`. The workflow bolds numbers in replacement bullets automatically and also accepts `**` to include units or context in the emphasis. [Achievement bank](Aaditya_Gajula_Master_Achievement_Bank.md)
- Page fill starts with the full approved content in `main.tex`. Change the replacement’s level of supported detail if the PDF leaves too much space or overflows. Keep the other entries, skills, and page geometry as supplied. The draft consolidates the duplicate `hyperref` import for compilation.
- Treat keyword matching as an initial read. Check implied requirements, negation, unusual section headings, multi-skill alternatives, and tool-specific gaps against the original posting. Confirm eligibility separately. [System design](Resume_Intelligence_System_Design.md) · [Format specification](Resume_Overleaf_Format_Specification.md)

## Improve the workflow with outcomes

Keep a private log of the company, requisition, job family, application date, referral, submitted manifest, and dates of any assessment, recruiter response, interview, rejection, or offer. Use the selected IDs in the manifest to compare drafts that kept the baseline with drafts that used a swap. Compare similar role families and track whether an interview arrived within 30 days. Early on, use evidence quality, page fit, and review time to improve drafts. Once enough comparable applications have had a full 30 days, review interview outcomes alongside referral and posting age before changing the swap threshold.
