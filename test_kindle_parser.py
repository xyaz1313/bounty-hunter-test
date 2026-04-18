"""Tests for the Kindle My Clippings.txt parser."""
from __future__ import annotations

from pathlib import Path

import pytest

from parser.kindle_parser import KindleClippingsParser, is_kindle_clippings

FIXTURES = Path(__file__).parent / "fixtures"


class TestKindleClippingsParser:
    parser = KindleClippingsParser()

    def _load(self) -> list[dict]:
        content = (FIXTURES / "sample_kindle_clippings.txt").read_text()
        return self.parser.parse(content)

    def test_parses_multiple_books(self):
        results = self._load()
        book_titles = {r["book_title"] for r in results}
        assert "Atomic Habits" in book_titles
        assert "Deep Work" in book_titles
        assert "Sapiens: A Brief History of Humankind" in book_titles

    def test_extracts_author(self):
        results = self._load()
        atomic = [r for r in results if r["book_title"] == "Atomic Habits"]
        assert atomic[0]["author"] == "James Clear"

    def test_extracts_author_from_deep_work(self):
        results = self._load()
        deep = [r for r in results if r["book_title"] == "Deep Work"]
        assert deep[0]["author"] == "Cal Newport"

    def test_highlight_kind(self):
        results = self._load()
        highlights = [r for r in results if r["kind"] == "highlight"]
        assert len(highlights) >= 3

    def test_note_kind(self):
        results = self._load()
        notes = [r for r in results if r["kind"] == "note"]
        assert len(notes) == 1
        assert "Csikszentmihalyi" in notes[0]["text"]

    def test_bookmark_parsed_as_highlight(self):
        """Bookmarks without text are skipped (no text after metadata line)."""
        results = self._load()
        # The bookmark entry has no text body, so it should be skipped
        bookmarks_with_text = [
            r for r in results
            if r.get("location") and "Page 105" in (r.get("location") or "")
        ]
        assert len(bookmarks_with_text) == 0

    def test_deduplication(self):
        """Same (book, text) pair appears twice — should be deduplicated."""
        results = self._load()
        atomic_highlights = [
            r for r in results
            if r["book_title"] == "Atomic Habits" and r["kind"] == "highlight"
        ]
        # The fixture has the same highlight duplicated
        texts = [r["text"][:50] for r in atomic_highlights]
        assert len(texts) == len(set(texts)), "Duplicate annotations should be removed"

    def test_location_format(self):
        results = self._load()
        with_location = [r for r in results if r.get("location")]
        assert any("Location" in (r["location"] or "") for r in with_location)

    def test_created_at_parsed(self):
        results = self._load()
        with_dates = [r for r in results if r.get("created_at")]
        assert len(with_dates) >= 3

    def test_text_not_empty(self):
        results = self._load()
        for r in results:
            assert r["text"].strip(), "Annotation text should not be empty"

    def test_source_name(self):
        assert self.parser.source_name == "kindle_clippings"


class TestIsKindleClippings:
    def test_detects_kindle_format(self):
        content = (FIXTURES / "sample_kindle_clippings.txt").read_text()
        assert is_kindle_clippings(content) is True

    def test_rejects_kobo_txt(self):
        content = (FIXTURES / "sample_export.txt").read_text()
        assert is_kindle_clippings(content) is False

    def test_rejects_empty(self):
        assert is_kindle_clippings("") is False

    def test_rejects_random_text(self):
        assert is_kindle_clippings("Just some random text without separators") is False

    def test_rejects_has_separators_but_no_kindle_meta(self):
        content = "Book Title\n==========\nSome text\n==========\n"
        assert is_kindle_clippings(content) is False


class TestKindleParserNoAuthor:
    """Entries without (author) in the header should still parse."""

    parser = KindleClippingsParser()

    def test_no_author(self):
        content = (
            "Some Book Title\n"
            "- Your Highlight on page 10 | Location 100-101 | Added on Monday, January 1, 2024 10:00:00 AM\n"
            "\n"
            "The highlighted text.\n"
            "==========\n"
        )
        results = self.parser.parse(content)
        assert len(results) == 1
        assert results[0]["book_title"] == "Some Book Title"
        assert results[0]["author"] is None
        assert results[0]["text"] == "The highlighted text."


class TestKindleParserMultilineText:
    """Multi-line annotation text should be preserved."""

    parser = KindleClippingsParser()

    def test_multiline(self):
        content = (
            "Book (Author)\n"
            "- Your Highlight on page 5 | Location 50-52 | Added on Tuesday, February 2, 2024 3:00:00 PM\n"
            "\n"
            "First line of text.\n"
            "Second line of text.\n"
            "Third line of text.\n"
            "==========\n"
        )
        results = self.parser.parse(content)
        assert len(results) == 1
        assert "First line" in results[0]["text"]
        assert "Third line" in results[0]["text"]
