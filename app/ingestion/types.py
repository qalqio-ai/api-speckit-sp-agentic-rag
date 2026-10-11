"""F1 shared records and injected ports."""
from dataclasses import dataclass, field
from typing import Protocol


class IngestionError(Exception):
    def __init__(self, code="invalid_input", fatal=False):
        self.code = code
        self.fatal = fatal
        super().__init__(code)


@dataclass(frozen=True)
class SourceDocument:
    use_case_id: str
    source_id: str
    title: str
    revision: str
    text: str


@dataclass
class SourceState:
    current_verified_revision: str | None = None
    attempted_revision: str | None = None
    source_status: str = "unseen"
    ready: bool = False
    expected_count: int | None = 0
    current_count: int | None = 0
    expected_ids: set = field(default_factory=set)
    expected_payload_hashes: dict = field(default_factory=dict)


class Embedder(Protocol):
    def encode(self, chunks, deadline): ...


class IndexStore(Protocol):
    def replace(self, scope, desired, deadline): ...
