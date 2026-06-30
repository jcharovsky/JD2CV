# Trello API Workflow

Trello is optional. Resolve the user's Trello preference before reading the job URL or starting CV tailoring.

JD2CV uses its own Python helper, `scripts/trello_job_card.py`, to call the Trello REST API. It must not use third-party Trello tools.

## Preference

Before asking the user about Trello, check:

```text
~/.codex/jd2cv/preferences.json
```

If the file exists, use its values unless the user explicitly asks to change them. If it does not exist, ask once whether to use Trello integration.

If the user enables Trello, ask for the board name and list/column name where application cards should be created, then save non-secret preferences:

```json
{
  "trello_enabled": true,
  "trello_board": "Job Applications",
  "trello_list": "Doing"
}
```

If the user disables Trello, save:

```json
{
  "trello_enabled": false
}
```

## Account And API Setup

If the user chooses Trello, immediately ask whether they already have:

- a Trello account
- a target Trello board
- a Trello API key and token pair

If they do not have a Trello account or board, instruct them to create those in Trello's web UI before continuing.

If they do not have an API key/token pair:

1. Open the Trello API key page while logged into Trello:
   `https://trello.com/power-ups/admin`
2. Create or select a Power-Up/admin entry and copy the API key shown there.
3. Generate an API token for that key using Trello's token authorization flow.
4. Keep both values private. Do not paste them into chat.

Official references:

- Trello REST API introduction: `https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/`
- Trello authorization guide: `https://developer.atlassian.com/cloud/trello/guides/rest-api/authorization/`

## Secure Local Credentials

Create the credentials file scaffold for the user, then tell the user to fill the values themselves in a terminal editor. Do not ask them to paste credentials into chat, and do not print the file contents after they fill it.

Path:

```text
~/.config/jd2cv/trello.json
```

Scaffold contents:

```json
{
  "apiKey": "",
  "token": ""
}
```

Recommended setup:

```bash
mkdir -p ~/.config/jd2cv
printf '{\n  "apiKey": "",\n  "token": ""\n}\n' > ~/.config/jd2cv/trello.json
chmod 600 ~/.config/jd2cv/trello.json
nano ~/.config/jd2cv/trello.json
```

The user must fill `apiKey` and `token` locally and save the file. Never ask them to paste those values into chat.

The helper refuses to use the file if group or other users have permissions on it.

## Card Creation

Use the board/list names saved in `~/.codex/jd2cv/preferences.json`:

```bash
python scripts/trello_job_card.py create-card \
  --job-url "https://example.com/job" \
  --company "Company" \
  --position "Position" \
  --board "Job Applications" \
  --list "Doing"
```

The command:

1. Finds the open Trello board by name.
2. Finds the open list by name.
3. Creates a card named `[COMPANY NAME] - [POSITION NAME]`.
4. Adds description `[Job posting](URL)`.
5. Creates checklist `General`.
6. Adds unchecked checklist items: `CV.`, `Application.`, `Interview.`, `Contract.`
7. Writes card state to `~/.codex/tmp/jd2cv/trello-card.json`.

## Final Upload

```bash
python scripts/trello_job_card.py upload-cv \
  --file "$HOME/.codex/tmp/jd2cv/ATS_CV_Template.pdf" \
  --delete
```

The upload command:

1. Uploads the PDF as a Trello card attachment.
2. Reads the card back and verifies the attachment is visible.
3. Marks `CV.` complete in checklist `General`.
4. Deletes the final temp PDF only after upload verification succeeds.
