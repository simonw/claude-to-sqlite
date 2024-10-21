from click.testing import CliRunner
from claude_to_sqlite.cli import cli
import io
import json
import pathlib
import pytest
import sqlite_utils
import zipfile

TEST_DIR = pathlib.Path(__file__).parent
EXAMPLE = json.loads((TEST_DIR / "example.json").read_text())


@pytest.mark.parametrize("use_zip", (False, True))
@pytest.mark.parametrize("is_valid_json", (True, False))
def test_import(use_zip, is_valid_json):
    runner = CliRunner()
    bytes = json.dumps(EXAMPLE).encode("utf-8")
    if not is_valid_json:
        bytes = b"x" + bytes
    if use_zip:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("conversations.json", bytes)
        bytes = zip_buffer.getvalue()
    with runner.isolated_filesystem():
        with open("export", "wb") as fp:
            fp.write(bytes)
        result = runner.invoke(cli, ["export", "export.db"])
        if is_valid_json:
            assert result.exit_code == 0
            db = sqlite_utils.Database("export.db")
            assert set(db.table_names()) == {"conversations", "messages"}
        else:
            assert result.exit_code != 0
            assert (
                result.output
                == "Error: File is neither a valid ZIP nor a valid JSON file\n"
            )


def test_import_artifacts():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli, [str(TEST_DIR / "artifacts.json"), "export.db"], catch_exceptions=False
        )
        assert result.exit_code == 0
        db = sqlite_utils.Database("export.db")
    assert set(db.table_names()) == {"conversations", "messages", "artifacts"}
    assert db["artifacts"].count == 10
    actual = []
    for row in db["artifacts"].rows:
        actual.append(
            dict(
                row,
                content=row["content"][:10] + "...",
                thinking=row["thinking"][:10] + "...",
            )
        )
    expected = [
        {
            "id": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator-1",
            "artifact": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator",
            "identifier": "llm-pricing-calculator",
            "version": 1,
            "type": "text/html",
            "language": "",
            "title": "LLM Pricing Calculator",
            "content": "<!DOCTYPE ...",
            "conversation_id": "91098bc8-f2c4-427b-b71b-1e25efa2e871",
            "message_id": "5e3e08cb-7e91-44fc-a2bb-6abacba3cb71",
            "thinking": "This reque...",
        },
        {
            "id": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator-2",
            "artifact": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator",
            "identifier": "llm-pricing-calculator",
            "version": 2,
            "type": "text/html",
            "language": "",
            "title": "LLM Pricing Calculator",
            "content": "<!DOCTYPE ...",
            "conversation_id": "91098bc8-f2c4-427b-b71b-1e25efa2e871",
            "message_id": "7d4445e2-4473-45f8-86d5-1c96473b32f6",
            "thinking": "This reque...",
        },
        {
            "id": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator-3",
            "artifact": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator",
            "identifier": "llm-pricing-calculator",
            "version": 3,
            "type": "text/html",
            "language": "",
            "title": "LLM Pricing Calculator",
            "content": "<!DOCTYPE ...",
            "conversation_id": "91098bc8-f2c4-427b-b71b-1e25efa2e871",
            "message_id": "5fd78d7e-e9fa-4a99-998c-bcfd31374670",
            "thinking": "This is an...",
        },
        {
            "id": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator-4",
            "artifact": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator",
            "identifier": "llm-pricing-calculator",
            "version": 4,
            "type": "text/html",
            "language": "",
            "title": "LLM Pricing Calculator with Presets",
            "content": "<!DOCTYPE ...",
            "conversation_id": "91098bc8-f2c4-427b-b71b-1e25efa2e871",
            "message_id": "abcb904f-d092-418f-96f8-cd1c76601376",
            "thinking": "This reque...",
        },
        {
            "id": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator-5",
            "artifact": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator",
            "identifier": "llm-pricing-calculator",
            "version": 5,
            "type": "text/html",
            "language": "",
            "title": "LLM Pricing Calculator with Detailed Presets",
            "content": "<!DOCTYPE ...",
            "conversation_id": "91098bc8-f2c4-427b-b71b-1e25efa2e871",
            "message_id": "4f0bbc81-c4fb-4379-acbb-c90e17bda248",
            "thinking": "This reque...",
        },
        {
            "id": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator-6",
            "artifact": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator",
            "identifier": "llm-pricing-calculator",
            "version": 6,
            "type": "text/html",
            "language": "",
            "title": "LLM Pricing Calculator with Corrected and Extended Presets",
            "content": "<!DOCTYPE ...",
            "conversation_id": "91098bc8-f2c4-427b-b71b-1e25efa2e871",
            "message_id": "67427317-da19-4fa1-a9b1-d3264caaa2c6",
            "thinking": "This reque...",
        },
        {
            "id": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator-7",
            "artifact": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator",
            "identifier": "llm-pricing-calculator",
            "version": 7,
            "type": "text/html",
            "language": "",
            "title": "LLM Pricing Calculator with Extended Gemini Presets",
            "content": "<!DOCTYPE ...",
            "conversation_id": "91098bc8-f2c4-427b-b71b-1e25efa2e871",
            "message_id": "10f71281-2371-4e2d-bcf9-a2c868e4189a",
            "thinking": "This reque...",
        },
        {
            "id": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator-8",
            "artifact": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator",
            "identifier": "llm-pricing-calculator",
            "version": 8,
            "type": "text/html",
            "language": "",
            "title": "LLM Pricing Calculator with Extended Gemini Presets and Disclaimer",
            "content": "<!DOCTYPE ...",
            "conversation_id": "91098bc8-f2c4-427b-b71b-1e25efa2e871",
            "message_id": "6ec5a54c-dd6a-48ea-aea9-5d6bc35f6a9e",
            "thinking": "This reque...",
        },
        {
            "id": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator-9",
            "artifact": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator",
            "identifier": "llm-pricing-calculator",
            "version": 9,
            "type": "text/html",
            "language": "",
            "title": "LLM Pricing Calculator with Responsive Layout",
            "content": "<!DOCTYPE ...",
            "conversation_id": "91098bc8-f2c4-427b-b71b-1e25efa2e871",
            "message_id": "ee5c339f-3550-43c6-b09d-e0cfe9a38bd3",
            "thinking": "This reque...",
        },
        {
            "id": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator-10",
            "artifact": "91098bc8-f2c4-427b-b71b-1e25efa2e871-llm-pricing-calculator",
            "identifier": "llm-pricing-calculator",
            "version": 10,
            "type": "text/html",
            "language": "",
            "title": "LLM Pricing Calculator with Responsive Layout and Refined Output",
            "content": "<!DOCTYPE ...",
            "conversation_id": "91098bc8-f2c4-427b-b71b-1e25efa2e871",
            "message_id": "f976a5e8-7642-474f-82c6-e9a2abf5883c",
            "thinking": "This reque...",
        },
    ]
    assert actual == expected
