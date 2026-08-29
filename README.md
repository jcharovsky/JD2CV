# JD2CV

JD2CV (Job Description to Curriculum Vitae) is a Codex skill for turning a job description URL into a tailored, ATS-friendly CV workflow.

It helps an agent:

- Read a job posting URL and extract company, position, requirements, responsibilities, keywords, and posting language.
- Handle inaccessible job URLs from any site by asking for pasted job-description text when the page cannot be reliably read.
- Handle image-based JDs from any site by using accessible page images, direct image URLs, or confirmed OCR/vision text.
- Optionally create a Trello application card in the board's `CV` list through JD2CV's custom Trello API helper.
- Select the English or Spanish ATS CV template.
- Propose CV tailoring decisions before editing.
- Track skills demanded across job postings and classify them as known or unknown to the candidate.
- Synchronize known skills from the candidate's English and Spanish CV templates.
- Generate review PDFs and a final text-based, single-column ATS PDF.
- Optionally upload the final PDF to the Trello card and verify the attachment.

## Included Files

- `SKILL.md`: Codex skill instructions.
- `assets/en/`: English Markdown CV and its rendered PDF.
- `assets/es/`: Spanish Markdown CV and its rendered PDF.
- `assets/demanded-skills.template.json`: Blank schema for the user's demanded-skills dataset.
- `scripts/generate_ats_cv.py`: Shared metadata-aware Markdown-to-PDF generator.
- `scripts/render_cv.sh`: Helper that runs the PDF generator through the locked `uv` environment.
- `scripts/trello_job_card.py`: Optional Trello card and CV upload helper that uses the Trello REST API.
- `tests/test_generate_ats_cv.py`: Template-spacing and PDF-pagination regression tests.
- `references/ats-rules.md`: ATS validation rules.
- `references/trello-api.md`: Trello API helper usage notes.

## Requirements

- Codex with local skills support.
- `uv`, which manages the Python interpreter and isolated environment.
- Network access during the initial `uv` synchronization or when using Trello.
- Trello API key/token only if using the optional Trello integration.

No Trello setup is required for local-only CV generation.

No extra Python package is required for the Trello helper; it uses the Python standard library.

## Installation

Codex installs GitHub-hosted skills through its built-in `$skill-installer`. In Codex, enter:

```text
$skill-installer Install the skill from https://github.com/jcharovsky/JD2CV. The skill is at the repository root and should be named jd2cv.
```

The installer places the skill under `$CODEX_HOME/skills/jd2cv`, using `~/.codex/skills/jd2cv` when `CODEX_HOME` is unset. Install `uv` before continuing, then confirm that it is available:

```bash
uv --version
```

Synchronize the locked environment, initialize the demanded-skills dataset, and run the validation suite:

```bash
JD2CV_SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/jd2cv"
JD2CV_DATA_DIR="$HOME/.codex/jd2cv"

cd "$JD2CV_SKILL_DIR"
uv sync --locked
mkdir -p "$JD2CV_DATA_DIR"
if [ ! -e "$JD2CV_DATA_DIR/demanded-skills.json" ]
then
  cp assets/demanded-skills.template.json "$JD2CV_DATA_DIR/demanded-skills.json"
fi
uv run python -m unittest discover -s tests -v
```

The initialization preserves an existing `~/.codex/jd2cv/demanded-skills.json` when updating JD2CV.

Replace the instructional content in both Markdown files under `assets/en/` and `assets/es/` with the candidate's real facts. Then recreate both base PDFs using the commands under **Rendering the Sample PDFs** and synchronize the known-skills dataset in Codex:

```text
$jd2cv Sync known skills from the English and Spanish CV templates.
```

Review and confirm the proposed bilingual mappings before JD2CV writes the JSON. Repeat the synchronization whenever either template's skills change. Trello setup remains optional and is covered under **Optional Trello Integration**.

JD2CV becomes available on the next Codex turn. If it does not appear, restart Codex and invoke it with `$jd2cv` and a job posting URL. See the [official OpenAI skill documentation](https://learn.chatgpt.com/docs/build-skills) for skill discovery and installation behavior.

## Demanded Skills Tracking

JD2CV records skills explicitly requested by confirmed job postings in `~/.codex/jd2cv/demanded-skills.json`. Each entry contains the canonical bilingual skill name, the number of distinct positions that demand it, the corresponding `COMPANY - POSITION` labels, and a `Known` or `Unknown` status.

The `$jd2cv Sync known skills from the English and Spanish CV templates.` command merges actual skills from both templates into the dataset as `Known`. It ignores instructional examples, preserves existing demand history, upgrades matched `Unknown` skills to `Known`, and asks for confirmation before writing. Skills missing from a template remain unchanged.

Skills already marked `Known` are available for tailoring proposals. When a posting introduces a new skill or requests one previously marked `Unknown`, JD2CV asks whether the candidate possesses it. Confirmed skills become `Known` and are proposed for the current CV and both language templates. Skills the candidate does not possess remain `Unknown` while still contributing market-demand data.

Position labels are deduplicated before storage, and each skill's demand count always equals its number of recorded positions. The repository keeps the empty schema in `assets/demanded-skills.template.json`; the populated file remains outside the repository.

## Job URL And Image Handling

JD2CV tries to read the provided job URL directly. If the page is inaccessible, login-gated, blocked, incomplete, or unreliable, the skill asks the user to paste the full job description text before tailoring.

If the JD is in an image, JD2CV first tries to inspect the image or extract/download the direct image URL itself. If that fails, the user can provide the image address. LinkedIn is a common case, and those image URLs often point to `media.licdn.com`, but the same flow applies to any site.

Downloaded JD images go to `~/.codex/tmp/jd2cv/`. JD2CV extracts visible text with available vision/OCR, asks the user to confirm or correct the extracted text, and deletes downloaded images after the workflow.

## Optional Trello Integration

JD2CV's Trello integration is optional. The skill asks whether to use Trello before reading the job URL or starting CV work.

If Trello is enabled, the skill first handles credentials, then uses the Trello API to list the user's open boards and asks the user to choose one. The selected board is saved as a non-secret preference. Cards are created in the board's existing `CV` list.

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
  "trello_board": "Job Applications"
}
```

Delete or edit that file to reset the preference.

When Trello is enabled, JD2CV creates a checklist-free card in the board's `CV` list, uploads the final PDF, and verifies the attachment. The card remains in `CV` until the user moves it manually to another progress list.

## Rendering the Sample PDFs

From this folder:

```bash
find ./assets/en -maxdepth 1 -name '*.md' -exec ./scripts/render_cv.sh {} \;
find ./assets/es -maxdepth 1 -name '*.md' -exec ./scripts/render_cv.sh {} \;
```

Each language directory contains exactly one Markdown CV. The generated PDF is written beside that file with the same name and a `.pdf` extension. The generator reads `language` and `title` from the Markdown front matter and uses `title` as the PDF title.

The render helper synchronizes the environment from `pyproject.toml` and `uv.lock` when needed. Generated Markdown and PDF files remain in the location supplied to the helper.

## Development

Synchronize the environment and run the tests from the repository root:

```bash
uv sync
uv run python -m unittest discover -s tests -v
```

## Template Editing

The Markdown templates are intentionally generic. Replace the instructional content with the candidate's real facts before using the skill for applications. Keep the section structure simple and avoid tables, sidebars, images, icons, text boxes, or multi-column layouts.

Blank lines between body items add vertical spacing in the PDF. Keep consecutive lines together when a section should remain compact.

Keep exactly one blank line before and after every standalone `Example:` or `Ejemplo:` marker. Section headings stay on the same page as their first body paragraph.

The summary section is a placeholder. During normal skill usage, the agent fills it from the job posting and the candidate facts already present in the selected template.
