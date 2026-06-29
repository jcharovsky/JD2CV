---
name: jd2cv
description: Use when the user provides a job posting URL and wants to create a Trello application card, analyze the role, tailor a generic ATS CV template, generate the final PDF, upload it to Trello, and clean up local output files. Trigger for job application, CV, resume, vacancy, role, position, job description, or JD URLs.
---

# JD2CV

## Purpose

Create a Trello application card and tailor an ATS-safe CV template for a job posting URL in English or Spanish. Always preserve the template's simple, single-column, text-based PDF format.

## Assets

- English template set: `assets/en/`
- Spanish template set: `assets/es/`
- English files: `ATS_CV_Template_en.pdf`, `ATS_CV_Template_en.md`, and `generate_ats_cv_en.py`.
- Spanish files: `ATS_CV_Template_es.pdf`, `ATS_CV_Template_es.md`, and `generate_ats_cv_es.py`.
- Render helper: `scripts/render_cv.sh`
- Work directory: `~/.codex/tmp/jd2cv/`
- Final output: `~/.codex/tmp/jd2cv/ATS_CV_Template.pdf`, unless the user requests a different candidate-specific filename.
- Do not write generated CV files to Desktop.

## Required Workflow

1. Receive a job posting URL.
2. Access the URL, read the posting, and extract:
   - company name
   - position name
   - seniority, responsibilities, requirements, preferred qualifications, keywords, location, and domain context
   - posting language: English or Spanish
3. Select the CV language before creating the proposal:
   - Use `assets/en/` when the posting is primarily in English.
   - Use `assets/es/` when the posting is primarily in Spanish.
   - If the posting mixes languages, choose the language used for the main job description unless the user asks otherwise.
   - The tailoring proposal, generated CV content, and final PDF should use the selected language.
4. Create the Trello card before CV creation. Read `references/trello-api.md` and use `scripts/trello_job_card.py create-card`.
   - Board: `Job Applications`, or `JD2CV_TRELLO_BOARD` when set
   - List: `Doing`, or `JD2CV_TRELLO_LIST` when set
   - Position: bottom
   - Card name: `[COMPANY NAME] - [POSITION NAME]`
   - Description: `[Job posting](provided URL)`
   - Checklist name: `General`
   - Checklist items, all unchecked: `CV.`, `Application.`, `Interview.`, `Contract.`
5. Prepare a tailoring proposal before editing the CV. Include:
   - replacement Professional Summary / Perfil Profesional for the template summary placeholder
   - for `Experience` / `Experiencia`: items to keep and items to remove
   - for `Skills` / `Habilidades`: skills to keep and skills to remove from the template skills list
   - any additional skills not in the template only when the job clearly requires them
   - for `Honors & Awards` / `Honores y Premios`: items to keep and items to remove
   - state that all other sections remain unchanged from the selected base PDF
   - short justification for every decision
6. If the user already provided some tailoring decisions with the URL, evaluate them:
   - implement them if they fit the job posting and ATS strategy
   - correct them if needed, explaining why
7. Wait for confirmation before applying tailoring edits.
8. Copy the selected language source/generator into `~/.codex/tmp/jd2cv/work/`, edit only the temp copies, and generate review PDFs directly under `~/.codex/tmp/jd2cv/` until the user approves. Use `scripts/render_cv.sh` to render PDFs; it creates a temp venv under `~/.codex/tmp/jd2cv/venv` if needed.
9. After confirmation, create the final PDF exactly at:
   - `~/.codex/tmp/jd2cv/ATS_CV_Template.pdf`, unless the user requests a different candidate-specific filename
   - Never create a generated CV on Desktop.
10. Validate the final PDF. Read `references/ats-rules.md` and verify:
   - PDF text extracts correctly
   - section order and tailored content are present
   - no tables, sidebars, images, icons, text boxes, or multi-column layout were introduced
   - output remains a text-based ATS-safe PDF
11. Ask for final confirmation:
   - If the user requests changes, apply them and return to validation.
   - If the user confirms the final document is OK, proceed to upload.
12. Upload and clean up. Read `references/trello-api.md` and use `scripts/trello_job_card.py upload-cv --delete`.
   - Upload the final PDF from `~/.codex/tmp/jd2cv/` to the Trello card created earlier.
   - Read the card after upload and verify the file is attached.
   - Mark checklist item `CV.` complete.
   - Delete the final temp PDF only after upload verification succeeds.
13. Delete temporary generated files from `~/.codex/tmp/jd2cv/` after successful upload, except `trello-card.json` may be kept during the active workflow if needed for recovery.

## Tailoring Rules

- Do not invent experience, education, certifications, awards, or tools.
- Prefer removing less relevant roles over rewriting facts aggressively.
- Keep role descriptions truthful to the existing CV unless the user explicitly provides new facts.
- Skills must normally be a subset of the selected template's `Skills` / `Habilidades` list.
- Additional non-template skills require explicit justification from the job posting.
- Keep `Honors & Awards` only if innovation, entrepreneurship, media, journalism, creativity, competitions, or early-career distinction are relevant to the role.
- Education, Certifications, Languages, Volunteering, contact details, and other non-tailored sections must remain as they are in the selected base PDF unless the user explicitly asks for a change.
- Use the selected posting language for the CV and tailoring proposal unless the user asks otherwise.

## Trello Notes

- The Trello helper uses credentials from `~/.trello-cli/default/config.json`.
- Never print the Trello API key or token.
- If Trello card creation succeeds, preserve the generated card state path in the working notes for later upload.
