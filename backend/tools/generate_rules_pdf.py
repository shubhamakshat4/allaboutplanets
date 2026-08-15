"""Render docs/RULES.md to a printable PDF for astrologers.

Single source of truth: the Markdown file. This script converts it, styles it
for print, and drives a headless browser to produce the PDF.

    python -m tools.generate_rules_doc     # first, refresh the Markdown
    python -m tools.generate_rules_pdf     # then, render it

Outputs docs/RULES.pdf (and docs/RULES.html, which the PDF is rendered from and
which is also readable on its own).
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown2

DOCS = Path(__file__).resolve().parents[2] / "docs"
SRC = DOCS / "RULES.md"
HTML_OUT = DOCS / "RULES.html"
PDF_OUT = DOCS / "RULES.pdf"

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

# Only fonts that ship with Windows and macOS are named, so the PDF renders
# identically offline with no downloaded assets.
CSS = """
@page {
  size: A4;
  margin: 18mm 16mm 16mm 16mm;
}

* { box-sizing: border-box; }

html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }

body {
  font-family: Cambria, Georgia, "Times New Roman", serif;
  font-size: 10.5pt;
  line-height: 1.5;
  color: #1b1b19;
  margin: 0;
}

/* ---------- Title block ---------- */
.cover { text-align: center; padding: 46mm 0 0 0; break-after: page; }
.cover h1 {
  font-size: 30pt; line-height: 1.15; margin: 0 0 6mm 0;
  font-weight: 700; letter-spacing: -0.4pt; border: 0; padding: 0;
}
.cover .sub { font-size: 13pt; color: #57574e; margin: 0 0 22mm 0; font-style: italic; }
.cover .rule { width: 46mm; height: 2px; background: #bf5919; margin: 0 auto 22mm auto; }
.cover .meta { font-size: 10pt; color: #57574e; line-height: 1.9; }
.cover .meta strong { color: #1b1b19; }

/* ---------- Contents ---------- */
.toc { break-after: page; }
.toc h2 { border: 0; margin-top: 0; }
.toc ol { list-style: none; padding: 0; margin: 0; counter-reset: toc; }
.toc li {
  padding: 2.6mm 0; border-bottom: 1px dotted #d2d2cc;
  font-size: 11pt; display: flex; gap: 4mm;
}
.toc li .n { color: #bf5919; font-weight: 700; min-width: 9mm; }
.toc li .t { flex: 1; }

/* ---------- Headings ---------- */
h1, h2, h3 { font-family: Cambria, Georgia, serif; font-weight: 700; }

h1 {
  font-size: 21pt; margin: 0 0 4mm 0; padding-bottom: 3mm;
  border-bottom: 2px solid #1b1b19; letter-spacing: -0.2pt;
}

h2 {
  font-size: 15pt; margin: 0 0 4mm 0; padding-bottom: 2mm;
  border-bottom: 1px solid #b0b0a6; break-before: page; break-after: avoid;
}
/* The first section must not push a blank page after the contents. */
.body > h2:first-child { break-before: auto; }

h3 {
  font-size: 12pt; margin: 7mm 0 2.5mm 0;
  color: #474741; break-after: avoid;
}

p { margin: 0 0 3mm 0; orphans: 3; widows: 3; }

hr { display: none; }

strong { font-weight: 700; }
em { font-style: italic; }

/* ---------- Rule tags ---------- */
code {
  font-family: Consolas, "Courier New", monospace;
  font-size: 8.5pt; color: #80351a;
  background: #fdf6ed; border: 1px solid #f2cd9c;
  border-radius: 2px; padding: 0.3mm 1.2mm;
  white-space: nowrap;
}

/* ---------- Tables ---------- */
table {
  width: 100%; border-collapse: collapse;
  margin: 3mm 0 5mm 0; font-size: 9pt;
  break-inside: auto;
}
thead { display: table-header-group; }
tr { break-inside: avoid; }

th {
  background: #1b1b19; color: #ffffff;
  text-align: left; font-weight: 600;
  padding: 2mm 2.2mm; font-size: 8.5pt;
  letter-spacing: 0.2pt;
}

td {
  padding: 1.8mm 2.2mm; border-bottom: 1px solid #e7e7e4;
  vertical-align: top;
}

tbody tr:nth-child(even) { background: #f6f6f5; }

td code { font-size: 8pt; }

/* ---------- Lists ---------- */
ul, ol { margin: 0 0 3mm 0; padding-left: 6mm; }
li { margin-bottom: 1.4mm; }

/* ---------- Callout for the two sections that matter most ---------- */
.callout {
  border-left: 3px solid #bf5919; background: #fdf6ed;
  padding: 3mm 4mm; margin: 0 0 4mm 0; break-inside: avoid;
}
.callout p:last-child { margin-bottom: 0; }

/* ---------- Closing note ---------- */
.colophon {
  margin-top: 8mm; padding-top: 3mm; border-top: 1px solid #d2d2cc;
  font-size: 9pt; color: #57574e; font-style: italic;
}
"""


def find_browser() -> str | None:
    for path in BROWSERS:
        if Path(path).is_file():
            return path
    for name in ("chrome", "msedge", "chromium"):
        found = shutil.which(name)
        if found:
            return found
    return None


def split_front_matter(md: str):
    """Peel the title and the introductory paragraphs off the top."""
    lines = md.splitlines()
    title = lines[0].lstrip("# ").strip()
    rest = lines[1:]
    # Everything before the first '---' is the introduction.
    for i, line in enumerate(rest):
        if line.strip() == "---":
            return title, "\n".join(rest[:i]).strip(), "\n".join(rest[i + 1:])
    return title, "", "\n".join(rest)


def build_toc(body_md: str) -> str:
    items = []
    for line in body_md.splitlines():
        if not line.startswith("## "):
            continue
        heading = line[3:].strip()
        match = re.match(r"^(\d+)\.\s*(.+)$", heading)
        if match:
            items.append((match.group(1), match.group(2)))
        else:
            items.append(("", heading))
    rows = "\n".join(
        f'      <li><span class="n">{n}</span><span class="t">{t}</span></li>'
        for n, t in items
    )
    return (
        '  <section class="toc">\n'
        "    <h2>Contents</h2>\n"
        "    <ol>\n" + rows + "\n    </ol>\n"
        "  </section>\n"
    )


def source_fingerprint() -> str:
    """SHA-256 of RULES.md. Stamped into the PDF and the HTML so a later check
    can tell whether either was rendered from the current Markdown, without
    needing a browser to re-render them."""
    return hashlib.sha256(SRC.read_bytes()).hexdigest()


def render_html() -> str:
    md = SRC.read_text(encoding="utf-8")
    title, intro_md, body_md = split_front_matter(md)

    convert = lambda text: markdown2.markdown(
        text, extras=["tables", "cuddled-lists", "break-on-newline"]
    )

    intro_html = convert(intro_md)
    body_html = convert(body_md)

    # Emphasise the two sections an astrologer should read first.
    body_html = body_html.replace(
        "<p>These are the places where the classics do not speak with one voice.",
        '<div class="callout"><p>These are the places where the classics do not '
        "speak with one voice.",
    ).replace(
        "<strong>These are the points most worth your attention.</strong></p>",
        "<strong>These are the points most worth your attention.</strong></p></div>",
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="source-sha256" content="{source_fingerprint()}">
<style>{CSS}</style>
</head>
<body>

<section class="cover">
  <h1>{title}</h1>
  <p class="sub">A reference for verification by astrologers</p>
  <div class="rule"></div>
  <div class="meta">
    <div><strong>Framework</strong> &nbsp; Parashari</div>
    <div><strong>Zodiac</strong> &nbsp; Sidereal (Nirayana)</div>
    <div><strong>Ayanamsha</strong> &nbsp; Lahiri</div>
    <div><strong>Ephemeris</strong> &nbsp; Swiss Ephemeris</div>
  </div>
</section>

{build_toc(body_md)}

<section class="body">
<h2>About this document</h2>
{intro_html}
{body_html}
</section>

</body>
</html>
"""


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: {SRC} not found. Run: python -m tools.generate_rules_doc")
        return 1

    html = render_html()
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {HTML_OUT} ({os.path.getsize(HTML_OUT):,} bytes)")

    browser = find_browser()
    if browser is None:
        print("No Chrome or Edge found; the PDF was not rendered.")
        print(f"Open {HTML_OUT} in a browser and print to PDF instead.")
        return 1

    # Headless printing writes into the profile directory, so give it a scratch
    # one rather than touching the user's real browser profile.
    #
    # ignore_cleanup_errors is required on Windows: Chrome keeps a handle on
    # CrashpadMetrics-active.pma inside the profile, and without it the cleanup
    # raises PermissionError before the PDF is finished.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--user-data-dir={profile}",
            f"--print-to-pdf={PDF_OUT}",
            HTML_OUT.as_uri(),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

    if not PDF_OUT.exists() or PDF_OUT.stat().st_size == 0:
        print("PDF rendering failed.")
        print(result.stdout[-2000:])
        print(result.stderr[-2000:])
        return 1

    finish(PDF_OUT)

    print(f"Wrote {PDF_OUT} ({os.path.getsize(PDF_OUT):,} bytes)")
    print(f"Rendered with {Path(browser).name}")
    return 0


def finish(pdf_path: Path) -> None:
    """Add page numbers and clickable section bookmarks.

    A headless browser cannot number pages, and a 24-page reference is awkward
    to cite or navigate without numbers. Both are stamped on afterwards. If
    PyMuPDF is unavailable the PDF is still perfectly usable, just unnumbered.
    """
    try:
        import pymupdf
    except ImportError:
        print("PyMuPDF not installed — skipping page numbers and bookmarks.")
        return

    doc = pymupdf.open(pdf_path)
    total = doc.page_count

    # Record which Markdown this was rendered from.
    meta = doc.metadata or {}
    meta["keywords"] = f"rules-source-sha256={source_fingerprint()}"
    meta["subject"] = "Rules used by the Planetary Status Analyzer"
    doc.set_metadata(meta)

    # --- bookmarks, from the section headings actually laid out on each page
    outline = []
    heading = re.compile(r"^(\d{1,2})\.\s+(.{3,80})$")
    for index, page in enumerate(doc):
        for line in page.get_text().splitlines()[:3]:
            line = line.strip()
            if not line:
                continue
            match = heading.match(line)
            if match:
                outline.append([1, f"{match.group(1)}. {match.group(2)}", index + 1])
            elif line in ("Contents", "About this document", "Full list of rule tags"):
                outline.append([1, line, index + 1])
            break
    if outline:
        doc.set_toc(outline)

    # --- footer on every page but the cover
    grey = (0.42, 0.42, 0.38)
    for index, page in enumerate(doc):
        if index == 0:
            continue
        width, height = page.rect.width, page.rect.height
        y = height - 30
        page.draw_line(pymupdf.Point(46, y - 10), pymupdf.Point(width - 46, y - 10),
                       color=(0.85, 0.85, 0.83), width=0.5)
        # A middle dot, not an em dash: the base-14 fonts PyMuPDF stamps with
        # do not carry an em dash and would substitute silently.
        page.insert_text(pymupdf.Point(46, y + 2),
                         "Planetary Status Analyzer · Rules",
                         fontname="times-italic", fontsize=8, color=grey)
        label = f"{index + 1} of {total}"
        page.insert_text(
            pymupdf.Point(width - 46 - pymupdf.get_text_length(
                label, fontname="times-roman", fontsize=8), y + 2),
            label, fontname="times-roman", fontsize=8, color=grey)

    # PyMuPDF refuses a full rewrite over the file it has open, so write beside
    # it and replace.
    staged = pdf_path.with_suffix(".tmp.pdf")
    doc.save(staged, deflate=True, garbage=3)
    doc.close()
    os.replace(staged, pdf_path)
    print(f"Added page numbers and {len(outline)} bookmarks.")


if __name__ == "__main__":
    sys.exit(main())
