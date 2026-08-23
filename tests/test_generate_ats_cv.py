import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "scripts" / "generate_ats_cv.py"


def find_template(language: str) -> Path:
    templates = tuple((ROOT / "assets" / language).glob("*.md"))
    if len(templates) != 1:
        raise RuntimeError(
            f"Expected one Markdown template in assets/{language}, found {len(templates)}"
        )
    return templates[0]


TEMPLATES = (
    (find_template("en"), "Example:", "Skills"),
    (find_template("es"), "Ejemplo:", "Habilidades"),
)


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_ats_cv", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_flowables(source: Path):
    generator = load_generator()
    base_doc_template = generator.BaseDocTemplate

    class RecordingDocTemplate(base_doc_template):
        last_instance = None

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.text_flowables = []
            RecordingDocTemplate.last_instance = self

        def afterFlowable(self, flowable):
            get_plain_text = getattr(flowable, "getPlainText", None)
            if get_plain_text:
                self.text_flowables.append((self.page, get_plain_text()))

    generator.BaseDocTemplate = RecordingDocTemplate
    try:
        generator.build(source)
        return RecordingDocTemplate.last_instance.text_flowables
    finally:
        generator.BaseDocTemplate = base_doc_template


class TemplateLayoutTests(unittest.TestCase):
    def test_example_markers_have_one_blank_line_on_each_side(self):
        for source, marker, _ in TEMPLATES:
            with self.subTest(source=source.name):
                lines = source.read_text(encoding="utf-8").splitlines()
                marker_indexes = [
                    index for index, line in enumerate(lines) if line.startswith(marker)
                ]

                for index in marker_indexes:
                    self.assertEqual(lines[index], marker)
                    self.assertEqual(lines[index - 1], "")
                    self.assertNotEqual(lines[index - 2], "")
                    self.assertEqual(lines[index + 1], "")
                    self.assertNotEqual(lines[index + 2], "")

    def test_skills_heading_stays_with_first_section_paragraph(self):
        for source, _, heading in TEMPLATES:
            with self.subTest(source=source.name):
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_source = Path(temp_dir) / source.name
                    shutil.copyfile(source, temp_source)
                    flowables = render_flowables(temp_source)

                heading_index = next(
                    index
                    for index, (_, text) in enumerate(flowables)
                    if text == heading
                )
                heading_page = flowables[heading_index][0]
                first_content_page = flowables[heading_index + 1][0]
                self.assertEqual(heading_page, first_content_page)

    def test_section_heading_stays_with_content_at_page_boundaries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "boundary.md"

            for paragraph_count in range(20, 80):
                filler = "\n".join(
                    f"Filler paragraph {index}." for index in range(paragraph_count)
                )
                source.write_text(
                    "---\n"
                    "language: en\n"
                    "title: Boundary test\n"
                    "---\n\n"
                    "# Test Name\n\n"
                    "Test headline\n\n"
                    "test@example.com\n\n"
                    "## Filler\n\n"
                    f"{filler}\n"
                    "## Target Section\n\n"
                    "First target paragraph.\n",
                    encoding="utf-8",
                )
                flowables = render_flowables(source)
                heading_index = next(
                    index
                    for index, (_, text) in enumerate(flowables)
                    if text == "Target Section"
                )
                heading_page = flowables[heading_index][0]
                first_content_page = flowables[heading_index + 1][0]
                self.assertEqual(
                    heading_page,
                    first_content_page,
                    f"Heading orphaned with {paragraph_count} filler paragraphs",
                )


if __name__ == "__main__":
    unittest.main()
