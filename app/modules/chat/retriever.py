from __future__ import annotations

import re


class EvidenceRetriever:
    """Rank case findings by lexical overlap with a question."""

    def __init__(self, records: list[dict] | None = None):
        self.records = records or []

    def search(self, query: str, limit: int = 5) -> list[dict]:
        query_terms = set(re.findall(r"\w+", query.casefold()))
        if not query_terms:
            return []

        ranked = []
        for record in self.records:
            text = " ".join(
                (
                    str(record.get("label", "")),
                    str(record.get("description", "")),
                    str(record.get("source_type", "")),
                    str(record.get("original_filename", "")),
                )
            )
            matched_terms = query_terms.intersection(re.findall(r"\w+", text.casefold()))
            if matched_terms:
                ranked.append((len(matched_terms), record))

        ranked.sort(key=lambda item: item[0], reverse=True)
        return [record for _, record in ranked[:limit]]
