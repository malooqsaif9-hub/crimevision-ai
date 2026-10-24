from __future__ import annotations

from html import escape
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


class PDFReportGenerator:
    """Create a professional PDF summary from timeline and evidence data."""

    def build(self, case_title: str, sections: list[str], output_path: str | Path) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        document = SimpleDocTemplate(str(path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(escape(case_title), styles["Title"]), Spacer(1, 24)]

        for section in sections:
            story.append(Paragraph(escape(section).replace("\n", "<br/>"), styles["BodyText"]))
            story.append(Spacer(1, 12))

        document.build(story)
        return str(path)
