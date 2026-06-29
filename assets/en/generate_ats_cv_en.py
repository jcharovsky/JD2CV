import html
import os
import re
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer


ROOT = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get("CV_SOURCE", ROOT / "ATS_CV_Template_en.md"))
OUTPUT = Path(os.environ.get("CV_OUTPUT", str(Path.home() / ".codex" / "tmp" / "jd2cv" / "ATS_CV_Template_en.pdf")))


def inline(text: str) -> str:
    text = html.escape(text.strip())
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def p(text: str, style):
    return Paragraph(inline(text), style)


def section(story, title, styles):
    story.append(Spacer(1, 8))
    story.append(p(title, styles["Section"]))
    story.append(Spacer(1, 3))


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Name", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=16, leading=19, spaceAfter=8))
    styles.add(ParagraphStyle(name="Headline", parent=styles["Normal"], fontName="Helvetica", fontSize=10, leading=13, spaceAfter=6))
    styles.add(ParagraphStyle(name="Section", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=13, leading=15, spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle(name="Role", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=12, spaceBefore=3, spaceAfter=1))
    styles.add(ParagraphStyle(name="Meta", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=9, leading=11, textColor="#333333", spaceAfter=2))
    styles.add(ParagraphStyle(name="Body", parent=styles["Normal"], fontName="Helvetica", fontSize=9.4, leading=11.5, spaceAfter=1))
    return styles


def build():
    styles = build_styles()
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    story = []
    in_body = False
    previous_role = False
    blank_pending = False
    last_kind = None
    current_section = None
    compact_sections = {"Education", "Certifications", "Languages"}
    previous_text = ""

    for raw in lines:
        line = raw.strip()
        if not line:
            blank_pending = True
            continue
        if (
            blank_pending
            and last_kind in {"body", "bullet"}
            and current_section not in compact_sections
            and not (last_kind == "body" and previous_text.endswith(":"))
        ):
            story.append(Spacer(1, 6))
        blank_pending = False
        if line.startswith("# "):
            story.append(p(line[2:], styles["Name"]))
            last_kind = "name"
            continue
        if line.startswith("## "):
            current_section = line[3:]
            section(story, current_section, styles)
            in_body = True
            previous_role = False
            last_kind = "section"
            continue
        if not in_body and len(story) == 1:
            story.append(p(line, styles["Headline"]))
            last_kind = "headline"
            continue
        if not in_body and len(story) == 2:
            story.append(p(line, styles["Body"]))
            last_kind = "body"
            continue
        if line.startswith("**") and line.endswith("**"):
            story.append(p(line, styles["Role"]))
            previous_role = True
            last_kind = "role"
            continue
        if previous_role:
            story.append(p(line, styles["Meta"]))
            previous_role = False
            last_kind = "meta"
            continue
        if line.startswith("- "):
            story.append(p(line, styles["Body"]))
            last_kind = "bullet"
            continue
        story.append(p(line, styles["Body"]))
        last_kind = "body"
        previous_text = line

    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        leftMargin=0.72 * inch,
        rightMargin=0.72 * inch,
        topMargin=0.58 * inch,
        bottomMargin=0.58 * inch,
        title="ATS CV Template",
        author="JD2CV",
        subject="ATS-friendly CV",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="SingleColumn", frames=[frame])])
    doc.build(story)


if __name__ == "__main__":
    build()
