---
name: jd2cv
description: Use when the user provides a job posting URL and wants to analyze the role, tailor a generic ATS CV template, generate the final PDF, and optionally create a Trello application card through JD2CV's custom Trello API helper. Trigger for job application, CV, resume, vacancy, role, position, job description, or JD URLs.
---

# JD2CV

## Purpose

Tailor an ATS-safe CV template for a job posting URL in English or Spanish, with optional Trello card tracking through JD2CV's custom Python Trello API helper. Always preserve the template's simple, single-column, text-based PDF format.

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
2. Before reading the URL or discussing CV tailoring, resolve the optional Trello integration preference and setup:
   - If the user explicitly says to use or not use Trello in the current request, follow that instruction and update `~/.codex/jd2cv/preferences.json`.
   - Otherwise, read `~/.codex/jd2cv/preferences.json` if it exists.
   - If no Trello preference exists, ask once whether the user wants to use Trello integration for JD2CV.
   - Store only non-secret preference data, for example `{"trello_enabled": true, "trello_board": "Job Applications", "trello_list": "Doing"}` or `{"trello_enabled": false}`.
   - If Trello is disabled, continue local-only and skip all Trello steps.
   - If Trello is enabled, immediately ask whether the user already has: a Trello account, a target board, and a Trello API key/token pair.
   - If any answer is no, read `references/trello-api.md` and provide the needed setup instructions before doing any URL/CV work.
   - After the user confirms they have an account, board, key, and token, ask for the board name and list/column name where cards should be created, then save them in `~/.codex/jd2cv/preferences.json`.
   - Explain secure auth setup from `references/trello-api.md`. Create `~/.config/jd2cv/trello.json` with empty `apiKey` and `token` fields, set it to `chmod 600`, and instruct the user to fill those values locally in their editor. Never ask the user to paste Trello credentials into chat, and never print Trello credential file contents after the user fills it.
3. Access the URL, handling LinkedIn postings conservatively:
   - If the URL is a LinkedIn URL, try to open/read it once.
   - If the LinkedIn page is inaccessible, requires login, shows anti-bot/interstitial content, omits the job description, or cannot be confidently extracted, stop and ask the user to paste the full job description text in chat.
   - If the accessible LinkedIn page contains the job description only or partly as an image, first try to inspect the image directly or extract its direct image URL from the page.
   - If a direct image URL is available, download it to `~/.codex/tmp/jd2cv/`, extract the visible text using available vision/OCR capabilities, show the extracted job description text to the user, and ask for confirmation or corrections before continuing.
   - If the image is visible but cannot be downloaded, use available vision/OCR directly on the visible image and ask the user to confirm the extracted text.
   - If the LinkedIn page or image cannot be accessed reliably, ask the user to right-click the image and provide the direct image address, usually from `media.licdn.com`.
   - Do not ask the user to manually download and re-upload LinkedIn images unless direct image URL download and direct visual inspection both fail.
   - Do not infer missing LinkedIn job details from the URL, title, or partial snippets.
   - Continue only after the posting content is available from the URL or from user-pasted text.
4. Read the posting and extract:
   - company name
   - position name
   - seniority, responsibilities, requirements, preferred qualifications, keywords, location, and domain context
   - posting language: English or Spanish
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
   - for `Experience` / `Experiencia`: items to keep and items to remove
   - for `Skills` / `Habilidades`: skills to keep and skills to remove from the template skills list
   - any additional skills not in the template only when the job clearly requires them
   - for `Honors & Awards` / `Honores y Premios`: items to keep and items to remove
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
   - no tables, sidebars, images, icons, text boxes, or multi-column layout were introduced
   - output remains a text-based ATS-safe PDF
13. Ask for final confirmation:
   - If the user requests changes, apply them and return to validation.
   - If the user confirms the final document is OK and Trello is enabled, proceed to upload.
14. If Trello is enabled, read `references/trello-api.md` and use `scripts/trello_job_card.py upload-cv --delete`.
   - Upload the final PDF from `~/.codex/tmp/jd2cv/` to the Trello card created earlier.
   - Read the card after upload and verify the file is attached.
   - Mark checklist item `CV.` complete.
   - Delete the final temp PDF only after upload verification succeeds.
15. Delete temporary generated files from `~/.codex/tmp/jd2cv/` after the workflow is complete, including downloaded LinkedIn job-description images. `trello-card.json` may be kept during the active workflow if needed for recovery.

## Tailoring Rules

- Do not invent experience, education, certifications, awards, or tools.
- Prefer removing less relevant roles over rewriting facts aggressively.
- Keep role descriptions truthful to the existing CV unless the user explicitly provides new facts.
- Skills must normally be a subset of the selected template's `Skills` / `Habilidades` list.
- Additional non-template skills require explicit justification from the job posting.
- Keep `Honors & Awards` only if innovation, entrepreneurship, media, journalism, creativity, competitions, or early-career distinction are relevant to the role.
- Education, Certifications, Languages, Volunteering, contact details, and other non-tailored sections must remain as they are in the selected base PDF unless the user explicitly asks for a change.
- Use the selected posting language for the CV and tailoring proposal unless the user asks otherwise.
- For image-based job descriptions, always confirm extracted OCR/vision text with the user before using it for Trello card creation, CV tailoring, keyword selection, or language detection.

## Trello Notes

- Trello is optional. If the user declines Trello, complete the CV workflow locally.
- Ask about Trello only when no saved preference exists or when the user explicitly asks to change it.
- Save the Trello preference at `~/.codex/jd2cv/preferences.json`; do not save it inside the skill folder or repository.
- The Trello helper is a custom Python script that uses the Trello REST API directly.
- It reads credentials only from `~/.config/jd2cv/trello.json`; create the empty scaffold for the user, protect it with `chmod 600`, and have the user fill credentials locally outside chat.
- Never print the Trello API key or token.
- If Trello card creation succeeds, preserve the generated card state path in the working notes for later upload.
