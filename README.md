# JD2CV

JD2CV is a Codex skill for turning a job description URL into a tailored, ATS-friendly CV workflow.

It helps an agent:

- Read a job posting URL and extract company, position, requirements, responsibilities, keywords, and posting language.
- Create a Trello application card for the opportunity.
- Select the English or Spanish ATS CV template.
- Propose CV tailoring decisions before editing.
- Generate review PDFs and a final text-based, single-column ATS PDF.
- Upload the final PDF to the Trello card, verify the attachment, mark the CV checklist item complete, and clean up temporary files.

## Included Files

- `SKILL.md`: Codex skill instructions.
- `assets/en/ATS_CV_Template_en.md`: English generic ATS CV Markdown template.
- `assets/en/ATS_CV_Template_en.pdf`: Rendered English sample PDF.
- `assets/en/generate_ats_cv_en.py`: English Markdown-to-PDF generator.
- `assets/es/ATS_CV_Template_es.md`: Spanish generic ATS CV Markdown template.
- `assets/es/ATS_CV_Template_es.pdf`: Rendered Spanish sample PDF.
- `assets/es/generate_ats_cv_es.py`: Spanish Markdown-to-PDF generator.
- `scripts/render_cv.sh`: Helper that creates a local virtual environment, installs ReportLab if needed, and renders a PDF.
- `scripts/trello_job_card.py`: Trello card creation and CV upload helper.
- `references/ats-rules.md`: ATS validation rules.
- `references/trello-api.md`: Trello helper usage notes.

## Requirements

- Codex with local skills support.
- Python 3 with `venv`.
- `pip`, used by `scripts/render_cv.sh` to install `reportlab` in a temporary virtual environment.
- Network access when installing `reportlab` or calling Trello.
- Trello API credentials at `~/.trello-cli/default/config.json` for Trello card creation and upload.

The Trello config file must contain:

```json
{
  "apiKey": "your-trello-api-key",
  "token": "your-trello-token"
}
```

No extra Python package is required for the Trello helper; it uses the Python standard library.

## Trello Defaults

The Trello helper defaults to:

- Board: `Job Applications`
- List: `Doing`
- Checklist: `General`
- Checklist items: `CV.`, `Application.`, `Interview.`, `Contract.`

Override the board and list with environment variables:

```bash
export JD2CV_TRELLO_BOARD="Your Board"
export JD2CV_TRELLO_LIST="Your List"
```

You can also pass `--board` and `--list` directly to `scripts/trello_job_card.py create-card`.

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
