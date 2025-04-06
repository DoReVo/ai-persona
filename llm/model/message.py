from pydantic import BaseModel


class Message(BaseModel):
    text: str
    sender: str


class ProcessingSummary(BaseModel):
    name_not_found: int = 0
    skipped_message: dict[str, int] = {}
    transformed_sender: dict[str, int] = {}
    text_not_found: int = 0
    ok: int = 0
