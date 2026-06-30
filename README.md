# JD2CV

JD2CV (short for Job Description to Curriculum Vitae) is a Codex skill for turning a job description URL into a tailored, ATS-friendly CV workflow.

It helps an agent:

- Read a job posting URL and extract company, position, requirements, responsibilities, keywords, and posting language.
- Handle inaccessible job URLs by asking for pasted job-description text when the page cannot be reliably read.
- Handle LinkedIn job posts and image-based JDs by using accessible page images, direct `media.licdn.com` image URLs, or confirmed OCR/vision text.
- Optionally create a Trello application card for the opportunity through JD2CV's custom Trello API helper.
- Select the English or Spanish ATS CV template.
- Propose CV tailoring decisions before editing.
- Generate review PDFs and a final text-based, single-column ATS PDF.
- Optionally upload the final PDF to the Trello card, verify the attachment, and mark the CV checklist item complete.

## Included Files

- `SKILL.md`: Codex skill instructions.
- `assets/en/ATS_CV_Template_en.md`: English generic ATS CV Markdown template.
- `assets/en/ATS_CV_Template_en.pdf`: Rendered English sample PDF.
- `assets/en/generate_ats_cv_en.py`: English Markdown-to-PDF generator.
- `assets/es/ATS_CV_Template_es.md`: Spanish generic ATS CV Markdown template.
- `assets/es/ATS_CV_Template_es.pdf`: Rendered Spanish sample PDF.
- `assets/es/generate_ats_cv_es.py`: Spanish Markdown-to-PDF generator.
- `scripts/render_cv.sh`: Helper that creates a local virtual environment, installs ReportLab if needed, and renders a PDF.
- `scripts/trello_job_card.py`: Optional Trello card/checklist/upload helper that uses the Trello REST API.
- `references/ats-rules.md`: ATS validation rules.
- `references/trello-api.md`: Trello API helper usage notes.

## Requirements

- Codex with local skills support.
- Python 3 with `venv`.
- `pip`, used by `scripts/render_cv.sh` to install `reportlab` in a temporary virtual environment.
- Network access when installing `reportlab` or using Trello.
- Trello API key/token only if using the optional Trello integration.

No Trello setup is required for local-only CV generation.

No extra Python package is required for the Trello helper; it uses the Python standard library.

## Job URL And Image Handling

JD2CV tries to read the provided job URL directly. If the page is inaccessible, login-gated, blocked, incomplete, or unreliable, the skill asks the user to paste the full job description text before tailoring.

For LinkedIn posts, the skill tries the page once. If the JD is in an image, it first tries to inspect the image or extract/download the direct image URL itself. If that fails, the user can provide the image address, often from `media.licdn.com`.

Downloaded JD images go to `~/.codex/tmp/jd2cv/`. JD2CV extracts visible text with available vision/OCR, asks the user to confirm or correct the extracted text, and deletes downloaded images after the workflow.

## Optional Trello Integration

JD2CV's Trello integration is optional. The skill asks whether to use Trello before reading the job URL or starting CV work.

If Trello is enabled, the skill first handles credentials, then uses the Trello API to list the user's open boards and asks the user to choose one. It then lists the open lists in that board and asks the user to choose the destination list. The selected board/list are saved as non-secret preferences.

The helper reads credentials from a local config file:

```text
~/.config/jd2cv/trello.json
```

The skill creates this scaffold:

```json
{
  "apiKey": "",
  "token": ""
}
```

Then the user fills it locally, outside the chat, and keeps it protected:

```bash
mkdir -p ~/.config/jd2cv
printf '{\n  "apiKey": "",\n  "token": ""\n}\n' > ~/.config/jd2cv/trello.json
chmod 600 ~/.config/jd2cv/trello.json
nano ~/.config/jd2cv/trello.json
```

Do not paste Trello credentials into chat. The helper refuses to use the credential file if group or other users can read it.

JD2CV stores the user's Trello preference outside the repo at:

```text
~/.codex/jd2cv/preferences.json
```

The skill asks whether to use Trello only when this preference is missing, or when the user explicitly asks to change it. The file stores only non-secret preference data, such as:

```json
{
  "trello_enabled": true,
  "trello_board": "Job Applications",
  "trello_list": "Doing"
}
```

Delete or edit that file to reset the preference.

When Trello is enabled, JD2CV creates the card in the selected list, adds checklist `General`, adds `CV.`, `Application.`, `Interview.`, and `Contract.`, uploads the final PDF, verifies the attachment, and marks `CV.` complete.

## Rendering the Sample PDFs

From this folder:

```bash
./scripts/render_cv.sh ./assets/en/generate_ats_cv_en.py ./assets/en/ATS_CV_Template_en.pdf
./scripts/render_cv.sh ./assets/es/generate_ats_cv_es.py ./assets/es/ATS_CV_Template_es.pdf
```

The render helper uses `~/.codex/tmp/jd2cv/venv` by default. Override the work directory with:

```bash
export JD2CV_WORKDIR="/path/to/workdir"
```

## Template Editing

The Markdown templates are intentionally generic. Replace the instructional content with the candidate's real facts before using the skill for applications. Keep the section structure simple and avoid tables, sidebars, images, icons, text boxes, or multi-column layouts.

The summary section is a placeholder. During normal skill usage, the agent fills it from the job posting and the candidate facts already present in the selected template.
