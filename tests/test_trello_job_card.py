import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = ROOT / "scripts" / "trello_job_card.py"


def load_helper():
    spec = importlib.util.spec_from_file_location("trello_job_card", HELPER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TrelloJobCardTests(unittest.TestCase):
    def test_create_card_uses_cv_list_without_creating_a_checklist(self):
        helper = load_helper()
        board = {"id": "board-1", "name": "Applications"}
        cv_list = {"id": "list-cv", "name": "CV"}
        card = {"id": "card-1", "shortUrl": "https://trello.test/card-1"}

        with tempfile.TemporaryDirectory() as temp_dir:
            args = argparse.Namespace(
                config=Path(temp_dir) / "trello.json",
                workdir=Path(temp_dir),
                board="Applications",
                company="Example Co",
                position="Engineer",
                job_url="https://example.test/jobs/engineer",
            )
            with (
                patch.object(helper, "load_auth", return_value=("key", "token")),
                patch.object(
                    helper,
                    "request",
                    side_effect=[[board], [cv_list], card],
                ) as request,
                patch("builtins.print"),
            ):
                helper.create_card(args)

            self.assertEqual(request.call_count, 3)
            create_request = request.call_args_list[2]
            self.assertEqual(create_request.args[:2], ("POST", "/cards"))
            self.assertEqual(create_request.kwargs["data"]["idList"], "list-cv")
            state = json.loads((Path(temp_dir) / "trello-card.json").read_text())
            self.assertEqual(set(state), {"board", "list", "card"})

    def test_upload_verifies_attachment_without_updating_progress(self):
        helper = load_helper()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            state_path = temp_path / "trello-card.json"
            state_path.write_text(json.dumps({"card": {"id": "card-1"}}))
            pdf_path = temp_path / "cv.pdf"
            pdf_path.write_bytes(b"pdf")
            args = argparse.Namespace(
                config=temp_path / "trello.json",
                state=state_path,
                file=pdf_path,
                delete=False,
            )
            with (
                patch.object(helper, "load_auth", return_value=("key", "token")),
                patch.object(helper, "multipart_upload", return_value={"id": "attachment-1"}),
                patch.object(
                    helper,
                    "request",
                    side_effect=[
                        [{"id": "attachment-1", "name": "cv.pdf"}],
                        {
                            "attachments": [{"id": "attachment-1", "name": "cv.pdf"}],
                            "shortUrl": "https://trello.test/card-1",
                        },
                    ],
                ) as request,
                patch("builtins.print"),
            ):
                helper.upload_cv(args)

            self.assertEqual([call.args[0] for call in request.call_args_list], ["GET", "GET"])
            self.assertTrue(pdf_path.exists())


if __name__ == "__main__":
    unittest.main()
