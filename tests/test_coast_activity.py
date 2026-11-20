"""Regression checks for GitHub's padded weeks and both calendar layouts."""
from datetime import date, timedelta
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import coast_activity as coast


class CalendarTests(unittest.TestCase):
    def setUp(self):
        self.last = date(2026, 11, 20)
        self.first = self.last - timedelta(days=364)
        self.records = []
        for delta in range(-3, 367):
            day = self.first + timedelta(days=delta)
            self.records.append({"date": day.isoformat(), "contributionCount": 0, "contributionLevel": "NONE"})
        self.response = {"data": {"user": {
            "login": coast.LOGIN,
            "contributionsCollection": {"contributionCalendar": {"weeks": [{"contributionDays": self.records}]}},
        }}}

    def test_padding_trimmed_and_every_returned_date_drawn_once(self):
        self.records[3].update(contributionCount=8, contributionLevel="THIRD_QUARTILE")
        days = coast.read_calendar(self.response, self.first, self.last)
        self.assertEqual(len(days), 365)
        for compact in (False, True):
            root = ET.fromstring(coast.render(days, compact))
            cells = [cell for cell in root.findall(".//{*}rect") if cell.find("{*}title") is not None]
            self.assertEqual(len({(cell.get("x"), cell.get("y")) for cell in cells}), 365)
            self.assertEqual(cells[0].find("{*}title").text, f"{self.first} · 8")
            self.assertEqual(cells[-1].find("{*}title").text, f"{self.last} · 0")
            self.assertEqual(cells[0].get("fill"), coast.PALETTE[3])
            self.assertIn("8 contributions", root.find("{*}desc").text)

    def test_missing_day_fails_instead_of_publishing_an_empty_square(self):
        del self.records[len(self.records) // 2]
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            coast.read_calendar(self.response, self.first, self.last)
