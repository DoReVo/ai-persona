from enum import Enum
from typing import List
from pydantic import BaseModel


class OutputType(Enum):
    JSONL = "jsonl"
    CSV = "csv"


class SenderTransform(BaseModel):
    original: str
    transform: str


SenderList = List[str]
SenderTransformList = List[SenderTransform]


class Config(BaseModel):
    skip_sender: SenderList
    sender_transform: SenderTransformList
