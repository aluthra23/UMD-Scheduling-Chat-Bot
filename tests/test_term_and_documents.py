import os
import unittest
from datetime import datetime
from unittest import mock

import requests

from scripts import check_term
from sync_utils import document_key, document_text
from term_id_functions import default_term_id, update_term_id


class DefaultTermTests(unittest.TestCase):
    def test_boundaries(self):
        cases = {
            (2027, 1, 1): "202701",
            (2027, 1, 25): "202701",  # used to return 202708
            (2027, 2, 20): "202701",
            (2027, 2, 21): "202708",
            (2027, 9, 30): "202708",
            (2027, 10, 1): "202801",
            (2027, 12, 31): "202801",
        }
        for (year, month, day), expected in cases.items():
            with self.subTest(date=f"{year}-{month}-{day}"):
                self.assertEqual(default_term_id(datetime(year, month, day)), expected)

    def test_environment_override_wins(self):
        with mock.patch.dict(os.environ, {"UMD_TERM_ID": " 202701 "}):
            self.assertEqual(update_term_id(), "202701")


SCHEDULE_COLUMNS = ["COURSE NUMBER", "SECTION ID", "INSTRUCTOR", "OPEN SEATS", "HAS LECTURE", "HAS LAB",
                    "IS NORMAL", "IS BLENDED (NORMAL AND ONLINE)", "IS ONLINE", "SPECIAL RESTRICTION", "DESCRIPTION"]


def schedule_row(**overrides):
    row = {column: "" for column in SCHEDULE_COLUMNS}
    row.update({"COURSE NUMBER": "CMSC131", "SECTION ID": "0101", "INSTRUCTOR": "Ada Lovelace, Alan Turing",
                "OPEN SEATS": "10", "HAS LECTURE": "1", "HAS LAB": "0", "IS NORMAL": "1", "IS ONLINE": "0",
                "IS BLENDED (NORMAL AND ONLINE)": "0", "DESCRIPTION": "Intro to\n  programming."})
    row.update(overrides)
    return row


class DocumentTests(unittest.TestCase):
    def test_keys_keep_leading_zeros(self):
        self.assertEqual(document_key("schedule", schedule_row()), "schedule:CMSC131:0101")
        self.assertEqual(document_key("catalog", {"COURSE NUMBER": "cmsc131"}), "catalog:CMSC131")
        self.assertEqual(document_key("prefix", {"COURSE PREFIX": "CMSC"}), "prefix:CMSC")
        self.assertEqual(document_key("gen_ed", {"GENERAL EDUCATION ACRONYM": "FSAW"}), "gen_ed:FSAW")

    def test_schedule_text_replaces_flags_with_delivery(self):
        text = document_text("schedule", schedule_row(), SCHEDULE_COLUMNS)
        self.assertEqual(
            text,
            "COURSE NUMBER: CMSC131 SECTION ID: 0101 INSTRUCTOR: Ada Lovelace, Alan Turing DELIVERY: Face-to-face "
            "OPEN SEATS: 10 DESCRIPTION: Intro to programming.",
        )

    def test_delivery_modes(self):
        for flags, expected in [
            ({"IS ONLINE": "1", "IS NORMAL": "0"}, "DELIVERY: Online"),
            ({"IS ONLINE": "1", "IS NORMAL": "1", "IS BLENDED (NORMAL AND ONLINE)": "1"}, "DELIVERY: Blended"),
        ]:
            with self.subTest(expected=expected):
                self.assertIn(expected, document_text("schedule", schedule_row(**flags), SCHEDULE_COLUMNS))

    def test_other_sources_keep_every_column(self):
        text = document_text("catalog", {"COURSE NUMBER": "CMSC131", "HAS LECTURE": "0"}, ["COURSE NUMBER", "HAS LECTURE"])
        self.assertEqual(text, "COURSE NUMBER: CMSC131 HAS LECTURE: 0")


def http_error(status, body):
    response = requests.Response()
    response.status_code = status
    response._content = body.encode()
    return requests.HTTPError(f"{status}", response=response)


class CheckTermTests(unittest.TestCase):
    def test_published_term(self):
        response = requests.Response()
        response.status_code = 200
        response._content = b'[{"course_number": "CMSC351"}]'
        self.assertTrue(check_term.term_is_available("202701", fetch=lambda *a, **k: response))

    def test_api_not_found_means_unpublished(self):
        def fetch(*args, **kwargs):
            raise http_error(404, '{"detail": "Course not found!"}')
        self.assertFalse(check_term.term_is_available("202708", fetch=fetch))

    def test_unexpected_404_raises(self):
        def fetch(*args, **kwargs):
            raise http_error(404, '{"detail": "Not Found"}')
        with self.assertRaises(RuntimeError):
            check_term.term_is_available("202708", fetch=fetch)

    def test_server_errors_propagate(self):
        def fetch(*args, **kwargs):
            raise http_error(500, "Internal Server Error")
        with self.assertRaises(requests.HTTPError):
            check_term.term_is_available("202708", fetch=fetch)

    def test_uses_long_timeout_for_cold_starts(self):
        calls = []
        def fetch(url, **kwargs):
            calls.append(kwargs)
            raise http_error(404, '{"detail": "Course not found!"}')
        check_term.term_is_available("202708", fetch=fetch)
        self.assertEqual(calls[0]["timeout"], check_term.API_TIMEOUT)


if __name__ == "__main__":
    unittest.main()
