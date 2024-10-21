import click
import json
import re
import sqlite_utils
from typing import List, Dict
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
    artifact_versions = {}
    with click.progressbar(conversations) as bar:
        for conversation in bar:
            conversation["account_id"] = conversation.pop("account")["uuid"]
            messages = conversation.pop("chat_messages")
            conversation_id = conversation["uuid"]
            db["conversations"].insert(
                conversation, pk="uuid", alter=True, replace=True
            )
            for message in messages:
                to_insert = dict(message, conversation_id=conversation_id)
                db["messages"].insert(
                    to_insert,
                    pk="uuid",
                    foreign_keys=("conversation_id",),
                    alter=True,
                    replace=True,
                )
                artifacts = []
                if to_insert["sender"] == "assistant":
                    artifacts = extract_artifacts(
                        to_insert["text"],
                        conversation_id=conversation_id,
                        message_id=to_insert["uuid"],
                        versions=artifact_versions,
                    )
                    db["artifacts"].insert_all(
                        [
                            dict(artifact, message_id=to_insert["uuid"])
                            for artifact in artifacts
                        ],
                        pk="id",
                        foreign_keys=("message_id", "conversation_id"),
                        alter=True,
                        replace=True,
                    )

thinking_re = r"<antThinking>(.*?)</antThinking>"
artifact_re = r"<antArtifact\s+(.*?)>(.*?)</antArtifact>"
attr_re = r'(\w+)="([^"]*)"'


def extract_artifacts(
    text: str, conversation_id: str, message_id: str, versions: dict
) -> List[Dict[str, str]]:
    # Find all artifacts and thinking tags with their positions
    artifacts = [
        (m.start(), m.group(1), m.group(2))
        for m in re.finditer(artifact_re, text, re.DOTALL)
    ]
    thinking_tags = [
        (m.start(), m.group(1)) for m in re.finditer(thinking_re, text, re.DOTALL)
    ]

    # Combine and sort all tags by their position in the text
    all_tags = sorted(
        [(pos, "artifact", attr, content) for pos, attr, content in artifacts]
        + [(pos, "thinking", content, "") for pos, content in thinking_tags]
    )

    result = []
    current_thinking = None

    for _, tag_type, attr_or_content, content in all_tags:
        if tag_type == "thinking":
            current_thinking = attr_or_content.strip()
        elif tag_type == "artifact":
            # Parse attributes
            attributes = dict(re.findall(attr_re, attr_or_content))

            identifier = attributes.get("identifier", "")
            artifact_id = f"{conversation_id}-{identifier}"

            # Increment version for this identifier
            version = (versions.get(artifact_id) or 0) + 1
            versions[artifact_id] = version

            thinking = None
            if current_thinking:
                thinking = current_thinking
                current_thinking = None

            artifact_dict = {
                "id": f"{artifact_id}-{version}",
                "artifact": artifact_id,
                "identifier": identifier,
                "version": version,
                "type": attributes.get("type", ""),
                "language": attributes.get("language", ""),
                "title": attributes.get("title", ""),
                "content": content.strip(),
                "thinking": thinking,
                "conversation_id": conversation_id,
                "message_id": message_id,
            }
            result.append(artifact_dict)

    return result


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
