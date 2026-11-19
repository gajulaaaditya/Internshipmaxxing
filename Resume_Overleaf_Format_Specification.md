# Required résumé format
**Design amendment · November 19, 2026**

Every tailored résumé uses one approved Overleaf/LaTeX template based on [ResumeAaditya.pdf](</Users/aadityagajula/Desktop/ResumeAaditya.pdf>). This requirement replaces Word-based rendering, editable DOCX export, and alternate layouts in the earlier system design. Each approved version will export a compiled PDF and the matching editable Overleaf source, including any files needed to compile it.

The [baseline-first workflow](README.md) treats [main.tex](main.tex) as applicant-approved for its wording, claims, and layout. It preserves that full baseline, uses the confirmed graduation date for the application, and takes wording from the achievement catalog only for an evidence-backed replacement. This workflow governs entry selection.

The PDF establishes the design. The achievement bank and approved claim records establish the content. Dates, metrics, skill lists, and project descriptions in the reference PDF carry no approval into new résumés.

## Fixed layout

- **Page and typography.** One US Letter page (612 × 792 pt), single column, black text on white, with Computer Modern typography. The PDF identifies pdfTeX and hyperref as its compiler and link tooling. Use pdfLaTeX as the default for the approved template.
- **Header.** Large, centered bold serif name. One centered contact line beneath it, with the location, phone, email and relevant profile links separated by vertical bars. Preserve clickable links.
- **Section order and styling.** Education → Experience → Projects & Research → Technical Skills. Keep the small-caps headings, thin horizontal rules, compact spacing and consistent left edge across all role families.
- **Education and experience.** Bold institution/organization names on the left, location on the right, italic degree or role underneath, and dates aligned to the right. Keep the reference’s compact indented bullets and its bold labels for optional details such as relevant coursework.
- **Projects.** Bold project title, italic technology/context metadata separated by vertical bars, optional link, and a right-aligned date. Put the approved contribution bullets directly below.
- **Skills.** Group skills on compact lines with bold category labels. Tailor the skills and their order within these lines.
- **Template fidelity.** [The reusable LaTeX template](templates/resume.tex) uses the supplied Overleaf preamble, page geometry and layout macros. Its `%% RESUME_*` lines mark where the renderer inserts approved, LaTeX-escaped content. Replace an entire marker line with the corresponding content, and keep the surrounding layout commands. Load `hyperref` once with `hidelinks` to avoid the duplicate package load in the supplied source.

## Graduation date selection

- Record the applicant-confirmed expected graduation date with each application and use it consistently on the résumé and application form. Use the term equivalent when the form asks for a term.
- For Princess Cruises requisition **14311**, Aaditya confirmed **Expected May 2028**. For other postings, apply the applicant's preference for May 2028 by default and December 2028 for postings explicitly targeting sophomores or first-year students when the date reflects the applicable degree plan. Flag any conflict with the posting’s graduation window or class-year requirement for review.

## Generation and release

The planner can change which experiences, projects, bullets and skills are included. It can prioritize selected projects and skills within their sections and preserve reverse chronology for employment. Use **three bullets per experience** and **two per project or research entry**. Bold the achievement metric or verified scope in each bullet when the record supports one. Retain a factual qualitative bullet when the evidence has no number and flag the gap for review.

Use the available space on the one-page résumé. If a preview has substantial unused space, add a relevant entry with enough evidence for its full bullet count or add supported detail to existing bullets. If the draft runs long, shorten approved wording or replace lower-priority entries while keeping the bullet counts. Keep the template’s page geometry, font sizes and spacing fixed.

Render the structured résumé into a versioned Overleaf source using fixed macros and escaped content. Compile locally with a pinned pdfLaTeX toolchain compatible with the approved Overleaf project. Keep the LaTeX source editable and capture the template version, compiler version, paper size and PDF/source hashes in the export manifest. A template change creates a new version and requires a new preview.

Before release, verify one-page output, visual fit and working links. Compare text extraction to the intended heading and reading order, particularly organization/location pairs, right-aligned dates, and punctuation-sensitive skills. The reference PDF has yielded “Florida International UniversityMiami, FL” in local extraction. Preserve the visual alignment while checking that the two fields extract separately. Confirm the rendered PDF and the editable source belong to the same approved content version.

Approve one compiled visual proof against the reference before reusing the template for released résumés.
