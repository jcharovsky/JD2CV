# Trello API

Optional. Resolve preference before URL/CV work. Use only `scripts/trello_job_card.py`; no third-party Trello tools.

## Preference

Check:

```text
~/.codex/jd2cv/preferences.json
```

If it exists and includes a board, use it unless the user asks to change it. If absent, ask once. If enabled, save `trello_enabled` first, then discover the board after credentials work:

```json
{
  "trello_enabled": true,
  "trello_board": "Job Applications"
}
```

If disabled:

```json
{
  "trello_enabled": false
}
```

## Account/API Setup

If Trello is enabled, immediately ask whether they have:

- a Trello account
- a Trello API key and token pair

If account is missing, tell them to create it in Trello UI. If key/token is missing:

1. Open the Trello API key page while logged into Trello:
   `https://trello.com/power-ups/admin`
2. Create or select a Power-Up/admin entry and copy the API key shown there.
3. Generate an API token for that key using Trello's token authorization flow.
4. Keep both private. Do not paste them into chat.

- Trello REST API introduction: `https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/`
- Trello authorization guide: `https://developer.atlassian.com/cloud/trello/guides/rest-api/authorization/`

## Secure Local Credentials

Create scaffold, `chmod 600`, then tell the user to fill values locally. Do not ask them to paste credentials or print file contents after they fill it.

```text
~/.config/jd2cv/trello.json
```

```json
{
  "apiKey": "",
  "token": ""
}
```

```bash
mkdir -p ~/.config/jd2cv
printf '{\n  "apiKey": "",\n  "token": ""\n}\n' > ~/.config/jd2cv/trello.json
chmod 600 ~/.config/jd2cv/trello.json
nano ~/.config/jd2cv/trello.json
```

The helper refuses to use the file if group or other users have permissions on it.

After creating the scaffold, stop and wait for the user to confirm they filled it. Do not read the job URL or start CV work until confirmed. After confirmation, verify the file exists, has `600` permissions, and has non-empty `apiKey` and `token` values.

## Board Selection

After credential verification, list open boards:

```bash
python scripts/trello_job_card.py list-boards
```

Show the board names to the user and ask them to pick one. Save:

```json
{
  "trello_enabled": true,
  "trello_board": "chosen board"
}
```

## Card Creation

Use the saved board:

```bash
python scripts/trello_job_card.py create-card \
  --job-url "https://example.com/job" \
  --company "Company" \
  --position "Position" \
  --board "Job Applications"
```

Creates card `[COMPANY] - [POSITION]` at the bottom of the board's `CV` list, sets description `[Job posting](URL)`, and writes `~/.codex/tmp/jd2cv/trello-card.json`. The card has no checklist. The user moves it between progress lists manually.

## Final Upload

```bash
python scripts/trello_job_card.py upload-cv \
  --file "$HOME/.codex/tmp/jd2cv/ATS_CV_Template.pdf" \
  --delete
```

Uploads the PDF, verifies the attachment, and deletes the temp PDF only after verification when `--delete` is used. The card remains in the `CV` list.
