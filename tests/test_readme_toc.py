import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _readme():
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
        return f.read()


def _slug(heading):
    """GitHub's anchor for a heading: lowercase, drop punctuation, spaces to hyphens."""
    s = re.sub(r"[^a-z0-9 _-]", "", heading.strip().lower())
    return s.replace(" ", "-")


def _headings(text):
    return [m.group(1).strip() for m in re.finditer(r"^## (.+)$", text, re.M)]


def _contents(text):
    """The links of the Contents block (between the bold 'Contents' line and the first section)."""
    block = text.split("**Contents**", 1)[1].split("\n## ", 1)[0]
    return re.findall(r"\[([^\]]+)\]\(#([^)]+)\)", block)


def test_contents_lists_every_section_once_with_a_working_anchor():
    text = _readme()
    headings = _headings(text)
    links = _contents(text)
    assert [slug for _, slug in links] == [_slug(h) for h in headings], "Contents must list every ## section, in order"
    assert [label for label, _ in links] == headings, "the link text must be the section title"


def test_every_anchor_in_the_readme_points_to_an_existing_section():
    text = _readme()
    slugs = {_slug(h) for h in _headings(text)}
    for anchor in re.findall(r"\]\(#([^)]+)\)", text):
        assert anchor in slugs, f"broken anchor: #{anchor}"


def test_the_top_says_it_ran_on_ionq_hardware_and_links_to_the_section():
    top = "\n".join(_readme().splitlines()[:12])
    assert "[IonQ Forte 1 (36q)](#run-on-real-quantum-hardware)" in top
    assert "real quantum hardware" in top and "Qollab" in top
    assert "Run on real quantum hardware" in _headings(_readme())


def test_the_required_qollab_line_is_still_first():
    assert _readme().splitlines()[0] == "**This effort is supported by Qollab & IonQ**"
