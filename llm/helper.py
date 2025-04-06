from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, List

from llm.config import OutputType
from llm.model.message import Message

PERSONA_MESSAGE_DIR = Path(__file__).parent.resolve() / "raw-data/persona"
RAW_DATA_DIR = Path(__file__).parent.resolve() / "raw-data"
COMBINED_MESSAGE_FILENAME = "combined"


def save_to_jsonl(data: List[Message], output_file_path: Path) -> bool:
    with open(output_file_path, "w", encoding="utf-8") as f:
        for entry in data:
            json_record = entry.model_dump_json()
            f.write(json_record + "\n")
    return True


def get_unique_senders(messages: List[Message]):
    return {item.sender for item in messages if item.sender.strip()}


def split_messages_by_sender(messages: List[Message]):
    grouped_messages: DefaultDict[str, List[Message]] = defaultdict(list)

    for message in messages:
        grouped_messages[message.sender].append(message)

    return dict(grouped_messages)


def save_grouped_message(messages: List[Message]):
    grouped = split_messages_by_sender(messages)

    for name, value in grouped.items():
        save_to_jsonl(value, PERSONA_MESSAGE_DIR / f"{name}.jsonl")


def save_messages(
    output_type: OutputType, split_persona: bool, messages: List[Message]
):
    if output_type == OutputType.JSONL:
        if split_persona:
            save_grouped_message(messages)
        else:
            save_to_jsonl(messages, RAW_DATA_DIR / f"{COMBINED_MESSAGE_FILENAME}.jsonl")

    elif output_type == OutputType.CSV:
        raise Exception("NOT SUPPORTED")
