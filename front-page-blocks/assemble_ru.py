#!/usr/bin/env python3
"""Assemble the Russian PurpleShire.uk front page from block partials.

Stitches front-page-blocks/ru/01-*.html ... 07-*.html into a complete
ru/index.html (doctype, head with the analytics placeholder, shared CSS).
The head block is written verbatim on every run, so the analytics placeholder
comment is always preserved.

Usage: python3 assemble_ru.py
Output: ../purpleshireuk/ru/index.html (Russian front page; mirrors the EN
front page built by assemble.py).
"""

import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ru")
OUT = os.path.join(os.path.dirname(os.path.dirname(BASE)), "purpleshireuk", "ru", "index.html")

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
  assemble_ru.py preserves this comment verbatim on every build. -->"""

HEAD = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PurpleShire.uk — Одна платформа, три направления</title>
%s
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
""" % ANALYTICS_PLACEHOLDER

TAIL = """<script src="../assets/site.js"></script>
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
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("assembled %s (%d bytes, %d blocks)" % (OUT, len(page), len(BLOCKS)))


if __name__ == "__main__":
    main()
