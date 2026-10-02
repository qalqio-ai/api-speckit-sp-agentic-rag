from typing import TypedDict


class SourceRecord(TypedDict):
    source_id: str
    title: str


USE_CASE_SOURCES: dict[str, list[SourceRecord]] = {
    "sample-use-case": [
        {"source_id": "sample-source-1", "title": "Sample source"},
    ],
    "empty-use-case": [],
}
