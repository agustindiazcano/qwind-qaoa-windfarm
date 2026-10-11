"""The public demo video (YouTube) is linked from the README and the website."""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VIDEO = "https://youtu.be/UGVkgYGXkF4"
EMBED = "https://www.youtube-nocookie.com/embed/UGVkgYGXkF4"


def _read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def test_readme_links_the_video_and_has_no_pending_video_todo():
    for name in ("README.md", "qollab/README.md"):
        text = _read(name)
        assert VIDEO in text, name
        assert "add the public YouTube link" not in text, name
    assert _read("README.md").count(VIDEO) >= 2  # top banner and the "How do I run it" section


def test_website_nav_and_footer_link_the_video_instead_of_the_pending_marks():
    for page in ("index.html", "references.html", "team.html"):
        html = _read(f"web/{page}")
        assert f'href="{VIDEO}"' in html, page
        assert "btn-todo" not in html and "icon-pending" not in html, page
    for partial in ("web-src/partials/footer.html", "web-src/partials/nav.html"):
        assert "TODO(owner): replace with the public demo video URL" not in _read(partial)
        assert "TODO(owner): turn into" not in _read(partial)


def test_home_embeds_the_video_with_a_title_and_privacy_friendly_host():
    html = _read("web/index.html")
    assert f'src="{EMBED}"' in html
    assert 'title="' in html[html.index(EMBED) - 400:html.index(EMBED) + 400]
