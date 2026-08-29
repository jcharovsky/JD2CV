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
- Each language directory contains exactly one base Markdown CV and its matching PDF.
- Template filenames may be generic or candidate-specific. Select the sole Markdown file in the chosen language directory.
- Shared generator: `scripts/generate_ats_cv.py`
- Render helper: `scripts/render_cv.sh`
- Demanded-skills schema template: `assets/demanded-skills.template.json`
- Work directory: `~/.codex/tmp/jd2cv/`
- Trello preference file: `~/.codex/jd2cv/preferences.json`
- Demanded-skills data file: `~/.codex/jd2cv/demanded-skills.json`
- Final source and output: copies under `~/.codex/tmp/jd2cv/` that preserve the selected Markdown asset's base filename. A user-requested candidate-specific base name replaces it for both files.
- Do not write generated CV files to Desktop.

## Required Workflow

1. Receive a job posting URL.
2. Before reading the URL or discussing CV tailoring, resolve Trello:
   - If the request explicitly enables/disables Trello, follow it and update `~/.codex/jd2cv/preferences.json`.
   - Otherwise read that file; if absent, ask once whether to use Trello.
   - Save only non-secrets, e.g. `{"trello_enabled": true, "trello_board": "Job Applications"}` or `{"trello_enabled": false}`.
   - If disabled, skip Trello. If enabled, ask immediately whether the user has a Trello account and API key/token. If not, read `references/trello-api.md` and guide setup before URL/CV work.
   - Create `~/.config/jd2cv/trello.json` scaffold with empty `apiKey`/`token`, run `chmod 600`, and tell the user to fill it locally. Never request or print credentials.
   - After creating the credential scaffold, stop and wait for the user to confirm they filled it. Do not read the job URL, create a Trello card, or start CV work until the user confirms the credential file is ready.
   - After confirmation, verify the credential file exists, has `600` permissions, and does not contain empty `apiKey` or `token` values.
   - Then run `scripts/trello_job_card.py list-boards`, show the open boards, ask the user to pick one, and save `trello_board` in `~/.codex/jd2cv/preferences.json`.
3. Access the URL:
   - Try to read once. If inaccessible, login-gated, anti-bot, incomplete, or uncertain, ask the user to paste the full JD text in chat.
   - If the JD is image-based on any site, inspect the image or extract/download its direct URL to `~/.codex/tmp/jd2cv/`, OCR/vision it, show extracted text, and ask for confirmation.
   - If the image is visible but not downloadable, OCR/vision the visible image. If unreliable or inaccessible, ask the user for the direct image URL; LinkedIn image URLs often use `media.licdn.com`.
   - Do not infer missing details from URL/title/snippets. Continue only with confirmed posting text.
4. Extract company, position, seniority, responsibilities, requirements, preferred qualifications, keywords, location, domain context, and posting language.
5. Track every explicitly demanded skill from the confirmed posting in `~/.codex/jd2cv/demanded-skills.json`. Follow **Demanded Skills Tracking** below and use `[COMPANY NAME] - [POSITION NAME]` as the position label. Finish when every demanded skill has a confirmed status and the position is recorded once.
6. Select the CV language before creating the proposal:
   - Use `assets/en/` when the posting is primarily in English.
   - Use `assets/es/` when the posting is primarily in Spanish.
   - If the posting mixes languages, choose the language used for the main job description unless the user asks otherwise.
   - The tailoring proposal, generated CV content, and final PDF should use the selected language.
   - Preserve the selected template's `language` and `title` front matter. The shared generator uses `title` as the PDF title.
7. If Trello is enabled, create the Trello card before CV creation using `scripts/trello_job_card.py create-card`.
   - Board: value from `~/.codex/jd2cv/preferences.json`
   - List: `CV`
   - Card name: `[COMPANY NAME] - [POSITION NAME]`
   - Description: `[Job posting](provided URL)`
   - Leave the card in `CV`; the user moves it between progress lists manually.
8. Prepare a tailoring proposal before editing the CV. Include:
   - replacement Professional Summary / Perfil Profesional for the template summary placeholder
   - `Experience` / `Experiencia`: keep/remove
   - `Skills` / `Habilidades`: keep/remove from template skills and job-demanded skills marked `Known`
   - any `Known` skill absent from the selected template only when the job clearly requires it
   - for every newly confirmed `Known` skill, separate proposals to add it to the current CV and to both language templates
   - `Honors & Awards` / `Honores y Premios`: keep/remove
   - state that all other sections remain unchanged from the selected base PDF
   - short justification for every decision
9. If the user already provided some tailoring decisions with the URL, evaluate them:
   - implement them if they fit the job posting and ATS strategy
   - correct them if needed, explaining why
10. Wait for confirmation before applying tailoring edits.
11. After confirmation, first apply any approved persistent skill additions as defined under **Demanded Skills Tracking**. Then copy the selected Markdown source into `~/.codex/tmp/jd2cv/` with its filename unchanged, and apply all application-specific tailoring only to that temp copy. If the user requests a candidate-specific base name, apply it to the temp Markdown file before editing. Use `scripts/render_cv.sh <source.md>` to generate review PDFs until the user approves. The helper runs the generator through the skill's locked `uv` environment. The PDF is always written beside the Markdown source with the same base name.
12. After confirmation, the approved render is the final PDF exactly at:
   - `~/.codex/tmp/jd2cv/{selected-stem}.pdf`, where `{selected-stem}` is the selected asset Markdown stem or the user-requested candidate-specific base name
   - Never create a generated CV on Desktop.
13. Validate the final PDF. Read `references/ats-rules.md` and verify:
   - PDF text extracts correctly
   - section order and tailored content are present
   - no tables, sidebars, images, icons, text boxes, or multi-column layout
   - output is text-based and ATS-safe
14. Ask for final confirmation:
   - If the user requests changes, apply them and return to validation.
   - If the user confirms the final document is OK and Trello is enabled, proceed to upload.
15. If Trello is enabled, read `references/trello-api.md` and use `scripts/trello_job_card.py upload-cv --delete`.
   - Upload the final PDF from `~/.codex/tmp/jd2cv/` to the Trello card created earlier.
   - Read the card after upload and verify the file is attached.
   - Delete the final temp PDF only after upload verification succeeds.
16. Delete temporary generated files from `~/.codex/tmp/jd2cv/` after the workflow is complete, including downloaded job-description images. `trello-card.json` may be kept during the active workflow if needed for recovery.

## Demanded Skills Tracking

Read `~/.codex/jd2cv/demanded-skills.json` and preserve this schema:

```json
{
  "skills": [
    {
      "skill": "English name / Spanish name",
      "demand_count": 1,
      "positions": ["COMPANY - POSITION"],
      "status": "Known"
    }
  ]
}
```

- Track every skill, tool, technology, methodology, or domain competency explicitly requested in the confirmed posting. Include required and preferred qualifications. Do not infer unstated demand.
- Match existing entries case-insensitively against either side of a bilingual name. Merge clear translations and spelling variants only when they denote the same skill, and preserve the existing canonical name.
- Store language-neutral names once. Store names that differ between English and Spanish as `English name / Spanish name`.
- Split demanded skills into existing `Known`, existing `Unknown`, and unlisted skills. Ask whether the user now possesses each `Unknown` or unlisted skill before updating its status.
- Use only `Known` or `Unknown` for `status`. Change an existing `Unknown` entry to `Known` when the user confirms they acquired it.
- For every demanded skill, compare position labels after trimming, collapsing whitespace, and ignoring case. Append the canonical `[COMPANY NAME] - [POSITION NAME]` label only when no normalized match exists.
- Set `demand_count` to the length of `positions` after every update. Never increment it independently.
- Add a newly confirmed skill whether its status is `Known` or `Unknown`. Propose `Known` skills for the current CV. Exclude `Unknown` skills from all CV content.
- For every newly confirmed `Known` skill, ask separately whether to add its English and Spanish names to both base Markdown templates. On approval, update both templates, recreate their matching PDFs, and preserve the templates' bilingual equivalence.

## Tailoring Rules

- When asking for confirmation, use natural phrasing such as "Please confirm whether..." Do not require a specific reply like "type confirmed"; any clear user confirmation is enough.
- Do not invent experience, education, certifications, awards, or tools.
- Prefer removing less relevant roles over rewriting facts aggressively.
- Keep role descriptions truthful to the existing CV unless the user explicitly provides new facts.
- Skills must be present in the selected template or marked `Known` in `~/.codex/jd2cv/demanded-skills.json`.
- Additional non-template skills require explicit justification from the job posting and `Known` status.
- Keep `Honors & Awards` only if innovation, entrepreneurship, media, journalism, creativity, competitions, or early-career distinction are relevant to the role.
- Education, Certifications, Languages, Volunteering, contact details, and other non-tailored sections must remain as they are in the selected base PDF unless the user explicitly asks for a change.
- Use the selected posting language for the CV and tailoring proposal unless the user asks otherwise.
- Blank lines between body items add vertical spacing in the PDF. Keep consecutive lines together where compact spacing is intended.
- Keep exactly one blank line before and after every standalone `Example:` or `Ejemplo:` marker.
- For image-based job descriptions from any site, always confirm extracted OCR/vision text before using it for Trello card creation, CV tailoring, keyword selection, or language detection.

## Maintenance Notes

- Whenever the base Markdown files are updated and the base PDFs are recreated from them, remind the user to upload the new Markdown versions to Google Drive.

## Trello Notes

- Trello is optional; ask only when no saved preference exists or the user asks to change it.
- Save non-secret preferences in `~/.codex/jd2cv/preferences.json`, never in the repo/skill.
- The helper calls Trello REST API and reads credentials only from `~/.config/jd2cv/trello.json`; scaffold it, `chmod 600`, have user fill it locally, and never print/request key or token.
- If Trello card creation succeeds, preserve the generated card state path in the working notes for later upload.
- Create cards without checklists in the board's `CV` list. The user manages later progress by moving cards manually.
