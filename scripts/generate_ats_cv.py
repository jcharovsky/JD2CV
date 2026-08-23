import argparse
import html
import re
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Render an ATS CV Markdown file as an adjacent PDF."
    )
    parser.add_argument("source", type=Path, help="Markdown CV to render")
    return parser.parse_args()


def read_document(source: Path):
    lines = source.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("Markdown must start with YAML front matter")

    try:
        metadata_end = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration as error:
        raise ValueError("Markdown front matter is missing its closing ---") from error

    metadata = {}
    for line in lines[1:metadata_end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"Invalid front matter entry: {line}")
        metadata[key.strip()] = value.strip().strip("\"'")

    missing = [key for key in ("language", "title") if not metadata.get(key)]
    if missing:
        raise ValueError(f"Front matter is missing: {', '.join(missing)}")

    return lines[metadata_end + 1 :], metadata


def inline(text: str) -> str:
    text = html.escape(text.strip())
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


class NonSplittingParagraph(Paragraph):
    def split(self, avail_width, avail_height):
        return []


def p(text: str, style):
    return NonSplittingParagraph(inline(text), style)


def section(story, title, styles):
    story.append(Spacer(1, 8))
    story.append(p(title, styles["Section"]))
    content_gap = Spacer(1, 3)
    content_gap.keepWithNext = True
    story.append(content_gap)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Name", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=16, leading=19, spaceAfter=8))
    styles.add(ParagraphStyle(name="Headline", parent=styles["Normal"], fontName="Helvetica", fontSize=10, leading=13, spaceAfter=6))
    styles.add(ParagraphStyle(name="Section", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=13, leading=15, spaceBefore=8, spaceAfter=4, keepWithNext=True))
    styles.add(ParagraphStyle(name="Role", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=12, spaceBefore=3, spaceAfter=1, keepWithNext=True))
    styles.add(ParagraphStyle(name="Meta", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=9, leading=11, textColor="#333333", spaceAfter=2, keepWithNext=True))
    styles.add(ParagraphStyle(name="Body", parent=styles["Normal"], fontName="Helvetica", fontSize=9.4, leading=11.5, spaceAfter=1))
    styles.add(ParagraphStyle(name="BodyKeep", parent=styles["Body"], keepWithNext=True))
    styles.add(ParagraphStyle(name="BulletKeep", parent=styles["Body"], keepWithNext=True))
    return styles


def build(source: Path) -> Path:
    source = source.expanduser().resolve()
    if source.suffix.lower() != ".md":
        raise ValueError("Source must be a Markdown file with a .md extension")
    if not source.is_file():
        raise ValueError(f"Source Markdown does not exist: {source}")

    output = source.with_suffix(".pdf")
    lines, metadata = read_document(source)
    styles = build_styles()
    story = []
    in_body = False
    previous_role = False
    blank_pending = False
    last_kind = None

    for index, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            blank_pending = True
            continue
        if (
            blank_pending
            and last_kind in {"body", "bullet"}
        ):
            story.append(Spacer(1, 6))
        blank_pending = False
        if line.startswith("# "):
            story.append(p(line[2:], styles["Name"]))
            last_kind = "name"
            continue
        if line.startswith("## "):
            section(story, line[3:], styles)
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
            next_line = next((candidate.strip() for candidate in lines[index + 1:] if candidate.strip()), "")
            style = styles["BulletKeep"] if next_line.startswith("- ") else styles["Body"]
            story.append(p(line, style))
            last_kind = "bullet"
            continue
        style = styles["BodyKeep"] if line.endswith(":") else styles["Body"]
        story.append(p(line, style))
        last_kind = "body"

    doc = BaseDocTemplate(
        str(output),
        pagesize=LETTER,
        leftMargin=0.72 * inch,
        rightMargin=0.72 * inch,
        topMargin=0.58 * inch,
        bottomMargin=0.58 * inch,
        title=metadata["title"],
        author="JD2CV",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="SingleColumn", frames=[frame])])
    doc.build(story)
    return output


def main():
    args = parse_arguments()
    try:
        output = build(args.source)
    except (OSError, ValueError) as error:
        raise SystemExit(f"Error: {error}") from error
    print(output)


if __name__ == "__main__":
    main()
