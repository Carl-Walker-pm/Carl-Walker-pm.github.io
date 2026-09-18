#!/usr/bin/env python3
"""Assemble the PurpleShire.uk front page from block partials.

Stitches front-page-blocks/01-*.html ... 07-*.html into a complete index.html
(doctype, head with the analytics placeholder, shared CSS). The head block is
written verbatim on every run, so the analytics placeholder comment is always
preserved.

Usage: python3 assemble.py
Output: ../purpleshireuk/index.html (front page of the PurpleShire.uk site;
projects/ subpages and assets/ are untouched).
"""

import os

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(BASE), "purpleshireuk", "index.html")

BLOCKS = [
    "01-header.html",
    "02-hero.html",
    "03-manifesto.html",
    "04-pillars.html",
    "05-flagships.html",
    "06-portfolio.html",
    "07-footer.html",
]

ANALYTICS_PLACEHOLDER = """<!-- ANALYTICS PLACEHOLDER
  GA4, Microsoft Clarity, and PostHog snippets go here.
  Standing rule: every page keeps its analytics counters.
  assemble.py preserves this comment verbatim on every build. -->"""

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PurpleShire.uk — One platform, three directions</title>
%s
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
""" % ANALYTICS_PLACEHOLDER

TAIL = """<script src="assets/site.js"></script>
</body>
</html>
"""


def main():
    parts = []
    for name in BLOCKS:
        path = os.path.join(BASE, name)
        if not os.path.isfile(path):
            raise SystemExit("missing block: %s" % path)
        with open(path, encoding="utf-8") as f:
            parts.append(f.read().rstrip("\n"))
    page = HEAD + "\n".join(parts) + "\n" + TAIL
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("assembled %s (%d bytes, %d blocks)" % (OUT, len(page), len(BLOCKS)))


if __name__ == "__main__":
    main()
