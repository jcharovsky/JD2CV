---
name: jd2cv
description: Use when the user provides a job posting URL and wants to analyze the role, tailor a generic ATS CV template, generate the final PDF, and optionally create a Trello application card through JD2CV's custom Trello API helper. Trigger for job application, CV, resume, vacancy, role, position, job description, or JD URLs.
---

# JD2CV

## Purpose

Tailor an ATS-safe CV template for an English or Spanish job URL, with optional Trello tracking through JD2CV's Python API helper. Preserve the simple, single-column, text-based PDF format.

## Assets

- English template set: `assets/en/`
- Spanish template set: `assets/es/`
- English files: `ATS_CV_Template_en.pdf`, `ATS_CV_Template_en.md`, and `generate_ats_cv_en.py`.
- Spanish files: `ATS_CV_Template_es.pdf`, `ATS_CV_Template_es.md`, and `generate_ats_cv_es.py`.
- Render helper: `scripts/render_cv.sh`
- Work directory: `~/.codex/tmp/jd2cv/`
- Trello preference file: `~/.codex/jd2cv/preferences.json`
- Final output: `~/.codex/tmp/jd2cv/ATS_CV_Template.pdf`, unless the user requests a different candidate-specific filename.
- Do not write generated CV files to Desktop.

## Required Workflow

1. Receive a job posting URL.
2. Before reading the URL or discussing CV tailoring, resolve Trello:
   - If the request explicitly enables/disables Trello, follow it and update `~/.codex/jd2cv/preferences.json`.
   - Otherwise read that file; if absent, ask once whether to use Trello.
   - Save only non-secrets, e.g. `{"trello_enabled": true, "trello_board": "Job Applications", "trello_list": "Doing"}` or `{"trello_enabled": false}`.
   - If disabled, skip Trello. If enabled, ask immediately whether the user has a Trello account and API key/token. If not, read `references/trello-api.md` and guide setup before URL/CV work.
   - Create `~/.config/jd2cv/trello.json` scaffold with empty `apiKey`/`token`, run `chmod 600`, and tell the user to fill it locally. Never request or print credentials.
   - After creating the credential scaffold, stop and wait for the user to confirm they filled it. Do not read the job URL, create a Trello card, or start CV work until the user confirms the credential file is ready.
   - After confirmation, verify the credential file exists, has `600` permissions, and does not contain empty `apiKey` or `token` values.
   - Then run `scripts/trello_job_card.py list-boards`, show the open boards, ask the user to pick one, run `scripts/trello_job_card.py list-lists --board "..."`, show that board's open lists, ask the user to pick one, and save `trello_board`/`trello_list` in `~/.codex/jd2cv/preferences.json`.
3. Access the URL:
   - Try to read once. If inaccessible, login-gated, anti-bot, incomplete, or uncertain, ask the user to paste the full JD text in chat.
   - If the JD is image-based on any site, inspect the image or extract/download its direct URL to `~/.codex/tmp/jd2cv/`, OCR/vision it, show extracted text, and ask for confirmation.
   - If the image is visible but not downloadable, OCR/vision the visible image. If unreliable or inaccessible, ask the user for the direct image URL; LinkedIn image URLs often use `media.licdn.com`.
   - Do not infer missing details from URL/title/snippets. Continue only with confirmed posting text.
4. Extract company, position, seniority, responsibilities, requirements, preferred qualifications, keywords, location, domain context, and posting language.
5. Select the CV language before creating the proposal:
   - Use `assets/en/` when the posting is primarily in English.
   - Use `assets/es/` when the posting is primarily in Spanish.
   - If the posting mixes languages, choose the language used for the main job description unless the user asks otherwise.
   - The tailoring proposal, generated CV content, and final PDF should use the selected language.
6. If Trello is enabled, create the Trello card before CV creation using `scripts/trello_job_card.py create-card`.
   - Board: value from `~/.codex/jd2cv/preferences.json`
   - List: value from `~/.codex/jd2cv/preferences.json`
   - Card name: `[COMPANY NAME] - [POSITION NAME]`
   - Description: `[Job posting](provided URL)`
7. Prepare a tailoring proposal before editing the CV. Include:
   - replacement Professional Summary / Perfil Profesional for the template summary placeholder
   - `Experience` / `Experiencia`: keep/remove
   - `Skills` / `Habilidades`: keep/remove from template skills
   - any additional skills not in the template only when the job clearly requires them
   - `Honors & Awards` / `Honores y Premios`: keep/remove
   - state that all other sections remain unchanged from the selected base PDF
   - short justification for every decision
8. If the user already provided some tailoring decisions with the URL, evaluate them:
   - implement them if they fit the job posting and ATS strategy
   - correct them if needed, explaining why
9. Wait for confirmation before applying tailoring edits.
10. Copy the selected language source/generator into `~/.codex/tmp/jd2cv/work/`, edit only the temp copies, and generate review PDFs directly under `~/.codex/tmp/jd2cv/` until the user approves. Use `scripts/render_cv.sh` to render PDFs; it creates a temp venv under `~/.codex/tmp/jd2cv/venv` if needed.
11. After confirmation, create the final PDF exactly at:
   - `~/.codex/tmp/jd2cv/ATS_CV_Template.pdf`, unless the user requests a different candidate-specific filename
   - Never create a generated CV on Desktop.
12. Validate the final PDF. Read `references/ats-rules.md` and verify:
   - PDF text extracts correctly
   - section order and tailored content are present
   - no tables, sidebars, images, icons, text boxes, or multi-column layout
   - output is text-based and ATS-safe
13. Ask for final confirmation:
   - If the user requests changes, apply them and return to validation.
   - If the user confirms the final document is OK and Trello is enabled, proceed to upload.
14. If Trello is enabled, read `references/trello-api.md` and use `scripts/trello_job_card.py upload-cv --delete`.
   - Upload the final PDF from `~/.codex/tmp/jd2cv/` to the Trello card created earlier.
   - Read the card after upload and verify the file is attached.
   - Mark checklist item `CV.` complete.
   - Delete the final temp PDF only after upload verification succeeds.
15. Delete temporary generated files from `~/.codex/tmp/jd2cv/` after the workflow is complete, including downloaded job-description images. `trello-card.json` may be kept during the active workflow if needed for recovery.

## Tailoring Rules

- When asking for confirmation, use natural phrasing such as "Please confirm whether..." Do not require a specific reply like "type confirmed"; any clear user confirmation is enough.
- Do not invent experience, education, certifications, awards, or tools.
- Prefer removing less relevant roles over rewriting facts aggressively.
- Keep role descriptions truthful to the existing CV unless the user explicitly provides new facts.
- Skills must normally be a subset of the selected template's `Skills` / `Habilidades` list.
- Additional non-template skills require explicit justification from the job posting.
- Keep `Honors & Awards` only if innovation, entrepreneurship, media, journalism, creativity, competitions, or early-career distinction are relevant to the role.
- Education, Certifications, Languages, Volunteering, contact details, and other non-tailored sections must remain as they are in the selected base PDF unless the user explicitly asks for a change.
- Use the selected posting language for the CV and tailoring proposal unless the user asks otherwise.
- For image-based job descriptions from any site, always confirm extracted OCR/vision text before using it for Trello card creation, CV tailoring, keyword selection, or language detection.

## Trello Notes

- Trello is optional; ask only when no saved preference exists or the user asks to change it.
- Save non-secret preferences in `~/.codex/jd2cv/preferences.json`, never in the repo/skill.
- The helper calls Trello REST API and reads credentials only from `~/.config/jd2cv/trello.json`; scaffold it, `chmod 600`, have user fill it locally, and never print/request key or token.
- If Trello card creation succeeds, preserve the generated card state path in the working notes for later upload.
