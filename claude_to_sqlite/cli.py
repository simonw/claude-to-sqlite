import click
import json
import sqlite_utils
import zipfile


@click.command()
@click.argument(
    "export_path",
    type=click.Path(exists=True, readable=True, file_okay=True, dir_okay=False),
)
@click.argument(
    "db_path", type=click.Path(writable=True, file_okay=True, dir_okay=False)
)
@click.version_option()
def cli(export_path, db_path):
    """
    Convert a Claude.ai export to SQLite

    Example usage:

    claude-to-sqlite claude.zip claude.db
    """
    db = sqlite_utils.Database(db_path)
    conversations = parse_file(export_path)
    with click.progressbar(conversations) as bar:
        for conversation in bar:
            conversation["account_id"] = conversation.pop("account")["uuid"]
            messages = conversation.pop("chat_messages")
            conversation_id = conversation["uuid"]
            db["conversations"].insert(
                conversation, pk="uuid", alter=True, replace=True
            )
            db["messages"].insert_all(
                [
                    dict(message, conversation_id=conversation_id)
                    for message in messages
                ],
                pk="uuid",
                foreign_keys=("conversation_id",),
                alter=True,
                replace=True,
            )


def parse_file(file_path):
    json_data = None
    with open(file_path, "rb") as f:
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(f) as z:
                if "conversations.json" in z.namelist():
                    with z.open("conversations.json") as json_file:
                        json_data = json_file.read()
                else:
                    raise click.ClickException(
                        "No 'conversations.json' file found in the ZIP archive"
                    )
        else:
            f.seek(0)
            json_data = f.read()
    try:
        return json.loads(json_data)
    except json.JSONDecodeError:
        raise click.ClickException("File is neither a valid ZIP nor a valid JSON file")
