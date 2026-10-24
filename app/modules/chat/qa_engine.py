from __future__ import annotations


class QuestionAnswerEngine:
    """Create a concise answer only from retrieved evidence records."""

    def answer(self, query: str, records: list[dict]) -> str:
        if not records:
            return "No matching findings were found in this case."

        citations = []
        for record in records:
            timestamp = record.get("source_time_sec")
            time_text = f" at {timestamp:.2f}s in the source" if timestamp is not None else ""
            citations.append(
                f"{record.get('label', 'finding')}{time_text} "
                f"[finding {record.get('finding_id')}, evidence {record.get('evidence_id')}]: "
                f"{record.get('description', '')}"
            )
        return (
            "Matching case findings (AI-generated leads; human verification required):\n"
            + "\n".join(citations)
        )
