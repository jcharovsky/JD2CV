#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import ssl
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


API = "https://api.trello.com/1"
DEFAULT_CONFIG = Path.home() / ".config" / "jd2cv" / "trello.json"
DEFAULT_WORKDIR = Path.home() / ".codex" / "tmp" / "jd2cv"
DEFAULT_CHECKLIST = "General"
DEFAULT_ITEMS = ["CV.", "Application.", "Interview.", "Contract."]


def check_config_permissions(config_path: Path):
    mode = stat.S_IMODE(config_path.stat().st_mode)
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise RuntimeError(
            f"Trello config file is too permissive: {config_path}. "
            f"Run `chmod 600 {config_path}` before using it."
        )


def load_auth(config_path: Path):
    if not config_path.exists():
        raise RuntimeError(
            f"Trello config file not found: {config_path}. "
            "Create it manually and protect it with chmod 600. "
            "Never paste Trello credentials into chat."
        )
    check_config_permissions(config_path)
    data = json.loads(config_path.read_text())
    try:
        key = data["apiKey"].strip()
        token = data["token"].strip()
    except KeyError as exc:
        raise RuntimeError(f"Trello config is missing required key: {exc.args[0]}") from exc
    if not key or not token:
        raise RuntimeError("Trello config has empty apiKey or token. Fill ~/.config/jd2cv/trello.json locally before continuing.")
    return key, token


def request(method, path, key, token, params=None, data=None, headers=None):
    params = dict(params or {})
    params["key"] = key
    params["token"] = token
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context()) as resp:
            payload = resp.read().decode()
            return json.loads(payload) if payload else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"Trello API {method} {path} failed: {exc.code} {detail}") from exc


def multipart_upload(path, fields, file_field, file_path, key, token):
    boundary = f"----jd2cv-{uuid.uuid4().hex}"
    chunks = []
    for name, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        chunks.append(str(value).encode())
        chunks.append(b"\r\n")
    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    chunks.append(f"--{boundary}\r\n".encode())
    chunks.append(
        (
            f'Content-Disposition: form-data; name="{file_field}"; '
            f'filename="{file_path.name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode()
    )
    chunks.append(file_path.read_bytes())
    chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    body = b"".join(chunks)
    params = urllib.parse.urlencode({"key": key, "token": token})
    req = urllib.request.Request(
        f"{API}{path}?{params}",
        data=body,
        method="POST",
        headers={"Accept": "application/json", "Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context()) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"Trello API multipart upload failed: {exc.code} {detail}") from exc


def find_named(items, name, kind):
    matches = [item for item in items if item.get("name") == name]
    if not matches:
        raise RuntimeError(f"Could not find Trello {kind} named {name!r}")
    return matches[0]


def create_card(args):
    key, token = load_auth(args.config)
    boards = request("GET", "/members/me/boards", key, token, {"fields": "name", "filter": "open"})
    board = find_named(boards, args.board, "board")
    lists = request("GET", f"/boards/{board['id']}/lists", key, token, {"fields": "name", "filter": "open"})
    trello_list = find_named(lists, args.list, "list")
    card = request(
        "POST",
        "/cards",
        key,
        token,
        data={
            "idList": trello_list["id"],
            "name": f"{args.company} - {args.position}",
            "desc": f"[Job posting]({args.job_url})",
            "pos": "bottom",
        },
    )
    checklist = request("POST", f"/cards/{card['id']}/checklists", key, token, data={"name": DEFAULT_CHECKLIST})
    check_items = []
    for item_name in DEFAULT_ITEMS:
        item = request(
            "POST",
            f"/checklists/{checklist['id']}/checkItems",
            key,
            token,
            data={"name": item_name, "pos": "bottom", "checked": "false"},
        )
        check_items.append(item)
    state = {
        "board": board,
        "list": trello_list,
        "card": card,
        "checklist": checklist,
        "check_items": check_items,
    }
    args.workdir.mkdir(parents=True, exist_ok=True)
    state_path = args.workdir / "trello-card.json"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    print(json.dumps({"state_path": str(state_path), "card_id": card["id"], "card_url": card.get("shortUrl")}, indent=2))


def upload_cv(args):
    key, token = load_auth(args.config)
    state = json.loads(args.state.read_text())
    card_id = state["card"]["id"]
    pdf = args.file
    if not pdf.exists():
        raise RuntimeError(f"File does not exist: {pdf}")
    upload = multipart_upload(
        f"/cards/{card_id}/attachments",
        {"name": pdf.name},
        "file",
        pdf,
        key,
        token,
    )
    attachments = request("GET", f"/cards/{card_id}/attachments", key, token)
    if not any(att.get("id") == upload.get("id") or att.get("name") == pdf.name for att in attachments):
        raise RuntimeError("Upload verification failed: attachment not found on card")
    cv_item = next((item for item in state["check_items"] if item.get("name") == "CV."), None)
    if not cv_item:
        raise RuntimeError("Could not find checklist item named 'CV.' in saved card state")
    request("PUT", f"/cards/{card_id}/checkItem/{cv_item['id']}", key, token, data={"state": "complete"})
    card = request(
        "GET",
        f"/cards/{card_id}",
        key,
        token,
        {"attachments": "true", "checklists": "all", "fields": "name,shortUrl"},
    )
    if not any(att.get("name") == pdf.name for att in card.get("attachments", [])):
        raise RuntimeError("Final card read failed: uploaded file is not visible in card attachments")
    if args.delete:
        pdf.unlink()
    print(json.dumps({"uploaded": pdf.name, "deleted": args.delete, "card_url": card.get("shortUrl")}, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Create Trello job cards and upload CV PDFs.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    sub = parser.add_subparsers(dest="cmd", required=True)

    create = sub.add_parser("create-card")
    create.add_argument("--job-url", required=True)
    create.add_argument("--company", required=True)
    create.add_argument("--position", required=True)
    create.add_argument("--board", required=True)
    create.add_argument("--list", required=True)
    create.add_argument("--workdir", type=Path, default=DEFAULT_WORKDIR)
    create.set_defaults(func=create_card)

    upload = sub.add_parser("upload-cv")
    upload.add_argument("--state", type=Path, default=DEFAULT_WORKDIR / "trello-card.json")
    upload.add_argument("--file", type=Path, required=True)
    upload.add_argument("--delete", action="store_true")
    upload.set_defaults(func=upload_cv)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
