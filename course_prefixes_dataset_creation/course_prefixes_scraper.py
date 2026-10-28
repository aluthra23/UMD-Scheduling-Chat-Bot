from bs4 import BeautifulSoup
import csv
import pandas as pd

from helping_files import helper, http_utils


def soc_scraper(file_path='umd_course_prefixes.csv'):
    response = http_utils.fetch('https://app.testudo.umd.edu/soc/')

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all course prefixes and their descriptions
    course_prefixes = soup.find_all('div', class_='course-prefix row')

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['COURSE PREFIX', 'FULL FORM'])

        for entry in course_prefixes:
            course_prefix = helper.text_of(entry, 'span', 'prefix-abbrev push_one two columns')
            full_form = helper.text_of(entry, 'span', 'prefix-name nine columns')
            if course_prefix:
                writer.writerow([course_prefix, full_form])


def course_catalog_scraper(url: str, file_path='umd_course_prefixes.csv'):
    response = http_utils.fetch(url)

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    courses = soup.find('div', class_='az_sitemap')
    courses = courses.find_all('li')

    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        df = pd.read_csv(file_path)
        existing_course_prefixes = set(df["COURSE PREFIX"])

        for course in courses:
            if len(course.text) == 1:
                continue

            course_prefix, full_form = separate_course_prefix(course.text.strip())

            if full_form is not None and course_prefix not in existing_course_prefixes:
                writer.writerow([course_prefix, full_form])


def separate_course_prefix(full_course_prefix: str):
    prefix, separator, full_form = full_course_prefix.partition(' - ')
    return (prefix.strip(), full_form.strip()) if separator else (prefix.strip(), None)
