from dataclasses import dataclass


@dataclass
class SearchResult:
    path: str
    content: str
    rank: float
