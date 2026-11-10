from bs4 import BeautifulSoup
from helping_files import constants, helper, http_utils
import csv

BASE_URL = "https://academiccatalog.umd.edu/undergraduate/approved-courses/"


def parse_course_block(course_acronym, course_block):
    """One catalog course as a dict keyed by CSV_CATALOG_COURSES_HEADER, or None if it has no title."""
    title = course_block.find('p', class_='courseblocktitle noindent')
    if title is None or title.strong is None:
        return None

    course = dict.fromkeys(constants.CSV_CATALOG_COURSES_HEADER)
    course["COURSE PREFIX"] = course_acronym
    course["COURSE NUMBER"], course["NAME"], course["CREDITS"] = helper.parse_course_string(title.strong.text.strip())
    course["DESCRIPTION"] = helper.text_of(course_block, 'p', 'courseblockdesc noindent')

    extras = [extra.text for extra in course_block.find_all('p', class_='courseblockextra noindent')]
    course.update(helper.catalog_extra_fields(extras))
    return course


def scrape_course_data(course_acronym, file):
    response = http_utils.fetch(f"{BASE_URL}{course_acronym.lower()}/", allow_not_found=True)
    if response is None:
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    writer = csv.writer(file)
    for course_block in soup.find_all('div', class_='courseblock'):
        course = parse_course_block(course_acronym, course_block)
        if course:
            writer.writerow([course[column] for column in constants.CSV_CATALOG_COURSES_HEADER])
