import json
import pathlib
from typing import Any, Dict, List, Optional, Union

import click

from llm.config import Config, OutputType, SenderList, SenderTransformList
from llm.helper import get_unique_senders, save_grouped_message, save_messages
from llm.model.message import Message, ProcessingSummary


def extract_sender(message: Dict[str, Any]) -> str | None:
    name: Optional[str] = message.get("from")

    if not name or not isinstance(name, str):
        name = message.get("actor")

    if not name or not isinstance(name, str):
        name = None

    return name


def should_skip_message(skip_sender_list: SenderList, name: str) -> bool:
    if name in skip_sender_list:
        return True

    return False


def transform_sender(transform: SenderTransformList, name: str):
    find_value_generator = (item for item in transform if item.original == name)
    match = next(find_value_generator, None)

    if match is None:
        return name
    else:
        return match.transform


def extract_text(message: Dict[str, Any]):
    text_content: Union[str, List[Union[str, Dict[str, Any]]], None] = message.get(
        "text"
    )

    if isinstance(text_content, str) and text_content.strip():
        return text_content.strip()
    elif isinstance(text_content, list):
        full_text_parts: List[str] = []
        for item in text_content:
            if isinstance(item, str):
                full_text_parts.append(item)
            elif (
                isinstance(item, dict)
                and "text" in item
                and isinstance(item["text"], str)
            ):
                full_text_parts.append(item.get("text", ""))
        return "".join(full_text_parts).strip()
    elif text_content is None:
        return None


def process_data(
    config: Config,
    summary: ProcessingSummary,
    data: Dict[str, Any],
):
    messages: List[Message] = []

    for message in data["messages"]:
        # Skip anything else other than message type
        if not isinstance(message, dict) or message.get("type") != "message":
            continue

        # Get sender name
        sender = extract_sender(message)

        if sender is None:
            summary.name_not_found += 1
            continue

        if should_skip_message(config.skip_sender, sender) is True:
            amount = summary.skipped_message.get(sender, 0)
            summary.skipped_message[sender] = amount + 1
            continue

        new_sender = transform_sender(config.sender_transform, sender)

        if new_sender != sender:
            amount = summary.transformed_sender.get(sender, 0)
            summary.transformed_sender[sender] = amount + 1

        text = extract_text(message)

        if text is None:
            summary.text_not_found += 1
            continue

        summary.ok += 1
        messages.append(Message(text=text, sender=new_sender))

    return messages


output_jsonl_file: str = "combined.jsonl"
raw_data_dir = "raw-data/telegram"


@click.command("process.telegram", help="Process telegram group chat export")
@click.pass_context
@click.option(
    "--output-type",
    "-ot",
    "output_type",
    required=True,
    type=click.Choice([e.value for e in OutputType], case_sensitive=False),
    help="Format to save the processed message",
)
@click.option(
    "--split-persona",
    "-sp",
    "split_persona",
    is_flag=True,
    show_default=True,
    help="Split output file by persona",
)
def process_telegram_exports(
    ctx: click.Context, output_type: OutputType, split_persona: bool
):
    config: Config = ctx.obj["CONFIG"]
    click.echo(f"Running telegram export - {ctx.params}")
    json_files = [
        f
        for f in pathlib.Path(__file__).parent.resolve().glob(f"{raw_data_dir}/*.json")
    ]

    final_messages: List[Message] = []
    summary = ProcessingSummary()

    for file_path in json_files:
        with open(file_path) as file:
            json_data = json.load(file)
            messages = process_data(config, summary, json_data)
            final_messages.extend(messages)

    click.echo(f"Summary for telegram: {summary}")
    click.echo(f"Unique sender for telegram: {get_unique_senders(final_messages)}")

    save_messages(OutputType(output_type), split_persona, final_messages)
