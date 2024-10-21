from click.testing import CliRunner
from claude_to_sqlite.cli import cli
import io
import json
import pathlib
import pytest
import sqlite_utils
import zipfile

EXAMPLE = json.loads((pathlib.Path(__file__).parent / "example.json").read_text())


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
