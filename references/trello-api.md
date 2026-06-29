# Trello Workflow

Use `scripts/trello_job_card.py` for card creation and final CV upload.

Credentials:

- The script reads Trello credentials from `~/.trello-cli/default/config.json`.
- Do not print, quote, or expose the API key or token.

Card creation:

```bash
python ~/.codex/skills/jd2cv/scripts/trello_job_card.py create-card \
  --job-url "https://example.com/job" \
  --company "Company" \
  --position "Position"
```

Defaults:

- Board: `Job Applications`, or `JD2CV_TRELLO_BOARD` when set
- List: `Doing`, or `JD2CV_TRELLO_LIST` when set
- Card position: bottom
- Description: `[Job posting](URL)`
- Checklist: `General`
- Checklist items, initially unchecked:
  - `CV.`
  - `Application.`
  - `Interview.`
  - `Contract.`

The script writes card state to:

```text
~/.codex/tmp/jd2cv/trello-card.json
```

Final upload:

```bash
python ~/.codex/skills/jd2cv/scripts/trello_job_card.py upload-cv \
  --file "$HOME/.codex/tmp/jd2cv/ATS_CV_Template.pdf" \
  --delete
```

The upload command:

1. Uploads the PDF as a Trello card attachment.
2. Reads the card back and verifies the attachment is visible.
3. Marks `CV.` complete in checklist `General`.
4. Deletes the final temp PDF only after upload verification succeeds.
