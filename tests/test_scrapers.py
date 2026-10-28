import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import requests
from bs4 import BeautifulSoup

from helping_files import constants
from schedule_of_classes_scraper import soc_scraper

ROOT = Path(__file__).resolve().parents[1]

SECTION_HTML = """
<div class="section delivery-f2f">
  <span class="section-id">0101</span>
  <span class="section-instructor">Ada Lovelace</span>
  <span class="total-seats-count">30</span>
  <span class="open-seats-count">10</span>
  <div class="class-days-container">
    <div class="row">
      <span class="section-days">MWF</span>
      <span class="class-start-time">9:00am</span>
      <span class="class-end-time">9:50am</span>
      <div class="two columns">{class_type}</div>
    </div>
  </div>
</div>
"""


def scrape_section(class_type):
    section = BeautifulSoup(SECTION_HTML.format(class_type=class_type), "html.parser").find("div", class_="section")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "out.csv"
        soc_scraper.update_classes_data(
            "TEST101", [section], "unused", str(path), "NORMAL", "Test Course", 3, 3, "Reg",
            {"GEN_EDS FULFILLED": "", "PREREQUISITE": None, "COREQUISITE": None, "RESTRICTION": None,
             "CREDIT ONLY GRANTED FOR": None, "FORMERLY": None, "RECOMMENDED": None,
             "CROSS-LISTED WITH": None, "DESCRIPTION": None},
        )
        with open(path, newline="") as file:
            rows = list(csv.reader(file))
    assert len(rows) == 1
    return dict(zip(_columns(), rows[0]))


def _columns():
    # to_csv writes columns in section_data key order, which the header constant mirrors.
    return [column for column in constants.CSV_SOC_HEADER]


class ClassTypeTests(unittest.TestCase):
    def test_known_class_type_is_recorded(self):
        row = scrape_section("Lecture")
        self.assertEqual(row["LECTURE TIME"], "MWF 9:00am-9:50am")

    def test_unknown_class_type_does_not_crash(self):
        row = scrape_section("Seminar")
        self.assertIn("SEMINAR: MWF 9:00am-9:50am", row["UNSPECIFIED TIME MESSAGE"])


COURSES_HTML = """
<div class="course">
  <div class="course-id">TEST101</div><span class="course-title">Has Credits</span>
  <span class="course-min-credits">4</span><span class="grading-method">Reg</span>
  <div class="section delivery-f2f">
    <span class="section-id">0101</span>
    <span class="section-instructor">Sujeong Kim</span><span class="section-instructor">William Regli</span>
    <span class="total-seats-count">30</span><span class="open-seats-count">10</span>
    <div class="class-days-container"><div class="row">
      <span class="section-days">TuTh</span><span class="class-start-time">2:00pm</span><span class="class-end-time">3:15pm</span>
    </div></div>
  </div>
</div>
<div class="course">
  <div class="course-id">TEST102</div><span class="course-title">No Credits Listed</span>
  <div class="section delivery-online"><span class="section-id">FC01</span></div>
</div>
<div class="course"><span class="course-title">Missing course id is skipped</span></div>
"""


class ScheduleScraperTests(unittest.TestCase):
    def scrape(self):
        response = requests.Response()
        response.status_code = 200
        response._content = COURSES_HTML.encode()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "out.csv"
            with open(path, "w", newline="") as file, mock.patch.object(soc_scraper.http_utils, "fetch", return_value=response):
                soc_scraper.scrape_course_data("TEST", file)
            with open(path, newline="") as file:
                return {row["COURSE NUMBER"]: row for row in (dict(zip(_columns(), values)) for values in csv.reader(file))}

    def test_keeps_every_instructor(self):
        self.assertEqual(self.scrape()["TEST101"]["INSTRUCTOR"], "Sujeong Kim, William Regli")

    def test_max_credits_defaults_to_min(self):
        row = self.scrape()["TEST101"]
        self.assertEqual((row["MINIMUM CREDITS"], row["MAXIMUM CREDITS"]), ("4", "4"))

    def test_credits_do_not_leak_into_the_next_course(self):
        row = self.scrape()["TEST102"]
        self.assertEqual((row["MINIMUM CREDITS"], row["MAXIMUM CREDITS"]), ("", ""))

    def test_missing_fields_do_not_crash(self):
        row = self.scrape()["TEST102"]
        self.assertEqual(row["SECTION ID"], "FC01")
        self.assertEqual(row["INSTRUCTOR"], "")
        self.assertEqual(row["WAITLIST COUNT"], "0")
        self.assertEqual(row["IS ONLINE"], "1")

    def test_course_without_id_is_skipped(self):
        self.assertEqual(set(self.scrape()), {"TEST101", "TEST102"})


class GenEdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("main_gen_ed", ROOT / "gen_eds" / "main_gen_ed.py")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def scrape(self, html):
        response = requests.Response()
        response.status_code = 200
        response._content = html.encode()
        with mock.patch("helping_files.http_utils.fetch", return_value=response):
            return self.module.scrape_gen_eds("202701")

    def test_parses_categories(self):
        rows = self.scrape('<div class="subcategory">Fine Arts (FSAR)</div><div class="subcategory">Math (FSMA)</div>')
        self.assertEqual(rows, [["FSAR", "Fine Arts"], ["FSMA", "Math"]])

    def test_empty_page_raises_instead_of_writing_an_empty_file(self):
        with self.assertRaises(RuntimeError):
            self.scrape("<html></html>")

    def test_fetch_failure_propagates(self):
        with mock.patch("helping_files.http_utils.fetch", side_effect=requests.HTTPError("503")):
            with self.assertRaises(requests.HTTPError):
                self.module.scrape_gen_eds("202701")


if __name__ == "__main__":
    unittest.main()
