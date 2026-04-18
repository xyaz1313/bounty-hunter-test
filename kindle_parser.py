"""Parser for Amazon Kindle's My Clippings.txt file.

Kindle stores all highlights, notes, and bookmarks in a single file called
``My Clippings.txt`` located at the root of the device.  The format:

.. code-block:: text

    Book Title (Author Name)
    - Your Highlight on page 42 | Location 639-641 | Added on Monday, March 15, 2024 12:34:56 PM

    The actual highlighted text goes here.
    ==========

Each entry is separated by ``==========``.  Entry types include highlights,
notes, and bookmarks.
"""
from __future__ import annotations

import re
from typing import Any

from parser.base import BaseParser

# Kindle separator
_SEPARATOR = re.compile(r"^={10}\s*$", re.MULTILINE)

# Header line: "Book Title (Author Name)"
# Author is optional — some entries have no parens.
_TITLE_AUTHOR_RE = re.compile(r"^(.+?)\s*\(([^)]+)\)\s*$")

# Metadata line: "- Your Highlight on page 42 | Location 639-641 | Added on ..."
_META_LINE_RE = re.compile(
    r"^-\s*Your\s+(Highlight|Note|Bookmark)"
    r"(?:\s+on\s+page\s+(\S+))?"
    r"(?:\s*\|\s*Location\s+(\S+?(?:-\S+)?))?"
    r"(?:\s*\|\s*Added on\s+(.+))?\s*$",
    re.IGNORECASE,
)

# Common Kindle date formats
_DATE_FORMATS = (
    "%A, %B %d, %Y %I:%M:%S %p",   # Monday, March 15, 2024 12:34:56 PM
    "%B %d, %Y %I:%M:%S %p",        # March 15, 2024 12:34:56 PM
    "%A, %B %d, %Y %H:%M:%S",       # Monday, March 15, 2024 12:34:56 (24h)
    "%B %d, %Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
)


def _parse_kindle_date(raw: str | None) -> str | None:
    """Try to parse Kindle's verbose date string into ISO format."""
    if not raw:
        return None
    raw = raw.strip()
    for fmt in _DATE_FORMATS:
        try:
            from datetime import datetime
            dt = datetime.strptime(raw, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    return None


class KindleClippingsParser(BaseParser):
    """Parse a Kindle ``My Clippings.txt`` file."""

    source_name = "kindle_clippings"

    def parse(self, content: str) -> list[dict[str, Any]]:
        blocks = _SEPARATOR.split(content)
        results: list[dict[str, Any]] = []
        seen: set[str] = set()  # dedup by (book, text)

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            lines = [l.rstrip("\ufeff") for l in block.splitlines()]
            lines = [l for l in lines if l.strip()]
            if len(lines) < 2:
                continue

            # First line: title (author)
            header = lines[0].strip()
            book_title, author = _parse_header(header)

            # Second line: metadata
            meta_line = lines[1].strip()
            meta = _META_LINE_RE.match(meta_line)
            if meta is None:
                # Not a Kindle clippings entry — skip
                continue

            kind = meta.group(1).lower()
            page = meta.group(2)
            location = meta.group(3)
            created_at = _parse_kindle_date(meta.group(4))

            # Remaining lines: annotation text
            text = "\n".join(lines[2:]).strip()
            if not text:
                continue

            # Dedup: same book + same text = duplicate
            dedup_key = f"{book_title}|{text[:200]}"
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            # Normalize kind
            if kind == "highlight":
                kind = "highlight"
            elif kind == "note":
                kind = "note"
            elif kind == "bookmark":
                kind = "highlight"  # bookmarks are effectively highlights
            else:
                kind = "unknown"

            loc_str: str | None = None
            if location:
                loc_str = f"Location {location}"
            elif page:
                loc_str = f"Page {page}"

            results.append(
                {
                    "book_title": book_title,
                    "author": author,
                    "kind": kind,
                    "text": text,
                    "chapter": None,
                    "location": loc_str,
                    "created_at": created_at,
                }
            )

        return results


def _parse_header(header: str) -> tuple[str, str | None]:
    """Extract (title, author) from a Kindle clippings header line."""
    m = _TITLE_AUTHOR_RE.match(header)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return header.strip(), None


def is_kindle_clippings(content: str) -> bool:
    """Heuristic: detect if a .txt file is a Kindle clippings file.

    Kindle clippings use ``==========`` separators and contain metadata lines
    starting with ``- Your Highlight`` / ``- Your Note`` / ``- Your Bookmark``.
    Kobo TXT exports use ``----------`` separators with different metadata.
    """
    # Quick check: must have Kindle separator pattern
    if "==========" not in content:
        return False
    # Must have Kindle-style metadata line
    if not re.search(r"-\s*Your\s+(Highlight|Note|Bookmark)", content, re.IGNORECASE):
        return False
    return True
