"""Check the built notebook's navigation, catalog, and plot accessibility.

Run after build_site.py: python scripts/check_site.py --expect-notes 13
Add --strict-assets after local vendor assets have been installed. This check
reads generated files only; it does not import or invoke the website builder.
"""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
# The public subject taxonomy deliberately differs from one source directory.
SUBJECT_FOR_FOLDER = {
    "statistics": "statistics",
    "statistical-learning": "learning",
    "nlp": "nlp",
    "finance": "finance",
    "econometrics": "econometrics",
    "bayesian-statistics": "bayesian",
    "machine-setup": "setup",
}


def normalized(text):
    return " ".join(text.split())


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.images = []
        self.h1s = []
        self.description = ""
        self.h1_buffer = None
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        line = self.getpos()[0]
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        for attribute in ("href", "src"):
            if attrs.get(attribute):
                self.links.append((tag, attribute, attrs[attribute], line))
        if tag == "img":
            self.images.append((attrs, line))
        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content", "")
        if tag == "h1":
            self.h1_buffer = []

    def handle_endtag(self, tag):
        if tag == "h1" and self.h1_buffer is not None:
            self.h1s.append(normalized("".join(self.h1_buffer)))
            self.h1_buffer = None

    def handle_data(self, text):
        if self.h1_buffer is not None:
            self.h1_buffer.append(text)


def local_target(page_path, url):
    """Return a local path, ignoring external URLs and client-side fragments."""
    parts = urlsplit(url)
    if parts.scheme or parts.netloc or not parts.path:
        return None
    decoded = unquote(parts.path)
    if decoded.startswith("/"):
        return (ROOT / decoded.lstrip("/")).resolve()
    return (page_path.parent / decoded).resolve()


def check(expect_notes=None, strict_assets=False):
    errors, warnings = [], set()
    note_paths = sorted(
        path for path in (ROOT / "notes").rglob("*.html")
        if path.name != "template_note.html"
    )
    if expect_notes is not None and len(note_paths) != expect_notes:
        errors.append(f"Expected {expect_notes} notes; found {len(note_paths)}.")
    if not note_paths:
        errors.append("No note pages found.")
    paths = [ROOT / "index.html", ROOT / "all-notes.html", *note_paths]
    pages = {}
    reference_count = 0
    for path in paths:
        label = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            errors.append(f"Missing generated page: {label}")
            continue
        try:
            page = Page(path.read_text(encoding="utf-8"))
        except (UnicodeError, ValueError) as exc:
            errors.append(f"Cannot parse {label}: {exc}")
            continue
        pages[path] = page
        for identifier, count in Counter(page.ids).items():
            if count > 1:
                errors.append(f"{label}: duplicate id {identifier!r} ({count} occurrences)")
        if len(page.h1s) != 1:
            errors.append(f"{label}: expected one h1; found {len(page.h1s)}")
        for tag, attr, url, line in page.links:
            try:
                target = local_target(path, url)
            except ValueError:
                errors.append(f"{label}:{line}: invalid {attr} URL {url!r}")
                continue
            if target is None:
                continue
            reference_count += 1
            if not target.is_relative_to(ROOT):
                errors.append(f"{label}:{line}: {attr} escapes the site directory: {url}")
                continue
            if not target.exists():
                missing = target.relative_to(ROOT).as_posix()
                if missing.startswith("assets/vendor/") and not strict_assets:
                    warnings.add(f"Vendor asset pending: {missing}")
                else:
                    errors.append(f"{label}:{line}: missing {attr} target {url}")
        for attrs, line in page.images:
            if "/plots/" in attrs.get("src", "") and not attrs.get("alt", "").strip():
                errors.append(f"{label}:{line}: plot image needs descriptive alt text")

    try:
        manifest = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"Cannot read content.json: {exc}")
        manifest = {}
    if not isinstance(manifest, dict):
        errors.append("content.json must contain an object of subjects.")
        manifest = {}
    manifest_links = []
    for subject, area in manifest.items():
        if not isinstance(area, dict) or not isinstance(area.get("sections"), list):
            errors.append(f"Manifest subject {subject!r} needs a sections list.")
            continue
        sections = area["sections"]
        if area.get("has_notes") is not bool(sections):
            errors.append(f"Manifest subject {subject!r}: has_notes contradicts sections.")
        for item in sections:
            if not isinstance(item, dict) or not isinstance(item.get("link"), str):
                errors.append(f"Manifest subject {subject!r} contains an invalid note entry.")
                continue
            link = item["link"]
            manifest_links.append(link)
            target = local_target(ROOT / "index.html", link)
            if target is None or not target.is_relative_to(ROOT / "notes"):
                errors.append(f"Manifest note must link to a local note page: {link}")
                continue
            relative = target.relative_to(ROOT / "notes")
            expected_subject = SUBJECT_FOR_FOLDER.get(relative.parts[0], relative.parts[0])
            if subject != expected_subject:
                errors.append(f"{link}: belongs in {expected_subject!r}, not {subject!r}.")
            note = pages.get(target)
            if note is None:
                errors.append(f"Manifest note does not resolve to a parsed note: {link}")
                continue
            if note.h1s and normalized(item.get("title", "")) != note.h1s[0]:
                errors.append(f"{link}: catalog title differs from article h1; rebuild the site.")
            if normalized(item.get("summary", "")) != normalized(note.description):
                errors.append(f"{link}: catalog summary differs from article description.")
            if not isinstance(item.get("reading_minutes"), int) or item["reading_minutes"] < 1:
                errors.append(f"{link}: reading_minutes must be a positive integer.")

    expected_links = {path.relative_to(ROOT).as_posix() for path in note_paths}
    for link, count in Counter(manifest_links).items():
        if count > 1:
            errors.append(f"Manifest duplicates note {link} ({count} entries)")
    for missing in sorted(expected_links - set(manifest_links)):
        errors.append(f"Manifest omits note: {missing}")
    for extra in sorted(set(manifest_links) - expected_links):
        errors.append(f"Manifest includes unexpected note: {extra}")

    directory = pages.get(ROOT / "all-notes.html")
    if directory:
        listed = Counter()
        for tag, attr, url, _line in directory.links:
            if tag == "a" and attr == "href":
                target = local_target(ROOT / "all-notes.html", url)
                if target is not None and target.is_relative_to(ROOT / "notes"):
                    listed[target.relative_to(ROOT).as_posix()] += 1
        if listed != Counter({link: 1 for link in expected_links}):
            errors.append("all-notes.html must link to every note exactly once.")

    index_path = ROOT / "index.html"
    if index_path.is_file():
        index = index_path.read_text(encoding="utf-8")
        match = re.search(r"\bconst\s+areaContent\s*=\s*", index)
        if not match:
            errors.append("index.html is missing its embedded note catalog.")
        else:
            try:
                embedded, _end = json.JSONDecoder().raw_decode(index[match.end():])
                if embedded != manifest:
                    errors.append("index.html embedded catalog differs from content.json; rebuild.")
            except ValueError as exc:
                errors.append(f"index.html has an invalid embedded catalog: {exc}")

    for warning in sorted(warnings):
        print(f"WARN: {warning}")
    for error in errors:
        print(f"FAIL: {error}")
    print(
        f"Checked {len(pages)} pages, {len(note_paths)} notes, "
        f"{reference_count} local references: {len(errors)} error(s), "
        f"{len(warnings)} warning(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect-notes", type=int, help="Optional expected published note count")
    parser.add_argument("--strict-assets", action="store_true", help="Treat missing vendor assets as errors")
    args = parser.parse_args()
    sys.exit(check(args.expect_notes, args.strict_assets))
