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


MEETINGS_HTML = """
<div class="section delivery-f2f">
  <span class="section-id">0101</span>
  <div class="class-days-container">{rows}</div>
</div>
"""
MEETING_ROW = """
<div class="row">
  <span class="section-days">{days}</span>
  <span class="class-start-time">9:00am</span><span class="class-end-time">9:50am</span>
  {class_type}
  <span class="class-building"><span class="building-code">ESJ</span><span class="class-room">{room}</span></span>
</div>
"""


def scrape_meetings(*meetings):
    """meetings: (days, class type or None, room) tuples, in page order."""
    rows = "".join(MEETING_ROW.format(
        days=days, room=room,
        class_type=f'<div class="two columns">{class_type}</div>' if class_type else "",
    ) for days, class_type, room in meetings)
    section = BeautifulSoup(MEETINGS_HTML.format(rows=rows), "html.parser").find("div", class_="section")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "out.csv"
        soc_scraper.update_classes_data(
            "TEST101", [section], "unused", str(path), "NORMAL", "Test Course", 3, 3, "Reg",
            dict.fromkeys(["PREREQUISITE", "COREQUISITE", "RESTRICTION", "CREDIT ONLY GRANTED FOR", "FORMERLY",
                           "RECOMMENDED", "CROSS-LISTED WITH", "DESCRIPTION"], None) | {"GEN_EDS FULFILLED": ""},
        )
        with open(path, newline="") as file:
            return dict(zip(_columns(), next(csv.reader(file))))


class MeetingSlotTests(unittest.TestCase):
    def test_three_lectures_fill_three_slots(self):
        row = scrape_meetings(("M", None, "0101"), ("W", None, "0102"), ("F", "Lecture", "0103"))
        self.assertEqual(
            [row["LECTURE TIME"], row["2ND LISTED LECTURE TIME"], row["3RD LISTED LECTURE TIME"]],
            ["M 9:00am-9:50am", "W 9:00am-9:50am", "F 9:00am-9:50am"],
        )
        self.assertEqual(row["3RD LISTED LECTURE ROOM"], "ESJ 0103")

    def test_third_discussion_is_kept_instead_of_overwriting_the_second(self):
        row = scrape_meetings(
            ("M", None, "0101"), ("Tu", "Discussion", "1"), ("W", "Discussion", "2"), ("Th", "Discussion", "3"),
        )
        self.assertEqual(row["DISCUSSION TIME"], "Tu 9:00am-9:50am")
        self.assertEqual(row["2ND LISTED DISCUSSION TIME"], "W 9:00am-9:50am")
        self.assertEqual(row["2ND LISTED DISCUSSION ROOM"], "ESJ 2")
        self.assertEqual(row["UNSPECIFIED TIME MESSAGE"], "DISCUSSION: Th 9:00am-9:50am in ESJ 3")


CATALOG_HTML = """
<div class="courseblock">
  <p class="courseblocktitle noindent"><strong>ENGL274 Introduction to African American Literature (3 Credits)</strong></p>
  <p class="courseblockdesc noindent">A survey of African American literature.</p>
  <p class="courseblockextra noindent">Prerequisite:  Must have completed ENGL101.</p>
  <p class="courseblockextra noindent">Credit Only Granted for: AASP274 or ENGL274.</p>
  <p class="courseblockextra noindent">Formerly:  ENGL289M.</p>
  <p class="courseblockextra noindent">Cross-listed with: AASP274.</p>
  <p class="courseblockextra noindent">Jointly offered with: ENGL388C.</p>
  <p class="courseblockextra noindent">Additional Information:  Minimum grade of C- required.</p>
  <p class="courseblockextra noindent">Also offered as: ENGL674.</p>
</div>
"""


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("catalog_scraper", ROOT / "course_catalog_scraper" / "scraper.py")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_every_extra_line_reaches_a_column(self):
        block = BeautifulSoup(CATALOG_HTML, "html.parser").find("div", class_="courseblock")
        course = self.module.parse_course_block("ENGL", block)
        self.assertEqual(list(course), constants.CSV_CATALOG_COURSES_HEADER)
        self.assertEqual((course["COURSE NUMBER"], course["CREDITS"]), ("ENGL274", "3"))
        self.assertEqual(course["PREREQUISITE"], "Must have completed ENGL101")
        self.assertEqual(course["CREDIT ONLY GRANTED FOR"], "AASP274 or ENGL274")
        self.assertEqual(course["FORMERLY NAMED"], "ENGL289M")
        self.assertEqual(course["CROSS-LISTED"], "AASP274; ENGL388C")
        self.assertEqual(course["ADDITIONAL INFORMATION"], "Minimum grade of C- required; Also offered as: ENGL674")

    def test_cross_listing_inside_another_line_is_split_out(self):
        from helping_files import helper
        fields = helper.catalog_extra_fields(["Restriction: Junior standing. Cross-listed with: MATH475."])
        self.assertEqual(fields, {"RESTRICTION": "Junior standing", "CROSS-LISTED": "MATH475"})

    def test_line_without_a_label_is_kept(self):
        from helping_files import helper
        self.assertEqual(helper.catalog_extra_fields(["Field trips required."]),
                         {"ADDITIONAL INFORMATION": "Field trips required"})


class PrefixScraperTests(unittest.TestCase):
    PAGE = """<div class="course-prefix row"><span class="prefix-abbrev push_one two columns">CMSC</span>
              <span class="prefix-name nine columns">Computer Science</span></div>"""

    def run_scraper(self, html):
        """Run soc_scraper over a file holding an older list; return (requested URL, file contents, error)."""
        from course_prefixes_dataset_creation import course_prefixes_scraper
        response = requests.Response()
        response.status_code = 200
        response._content = html.encode()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prefixes.csv"
            path.write_text("COURSE PREFIX,FULL FORM\nOLD,Previous list\n")
            error = None
            with mock.patch.object(course_prefixes_scraper.http_utils, "fetch", return_value=response) as fetch:
                try:
                    course_prefixes_scraper.soc_scraper(str(path), "202701")
                except RuntimeError as raised:
                    error = raised
            return fetch.call_args.args[0], path.read_text().splitlines(), error

    def test_scrapes_the_requested_term(self):
        url, lines, error = self.run_scraper(self.PAGE)
        self.assertIsNone(error)
        self.assertEqual(url, "https://app.testudo.umd.edu/soc/202701")
        self.assertEqual(lines, ["COURSE PREFIX,FULL FORM", "CMSC,Computer Science"])

    def test_empty_page_raises_and_keeps_the_old_list(self):
        _, lines, error = self.run_scraper("<html></html>")
        self.assertIsInstance(error, RuntimeError)
        self.assertEqual(lines, ["COURSE PREFIX,FULL FORM", "OLD,Previous list"])


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
