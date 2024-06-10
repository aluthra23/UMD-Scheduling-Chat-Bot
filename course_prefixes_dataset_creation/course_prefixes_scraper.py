import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd


def soc_scraper(file_path='umd_course_prefixes.csv'):
    # URL of the University of Maryland's approved courses page
    url = 'https://app.testudo.umd.edu/soc/'

    # Send a GET request to the page
    response = requests.get(url)
    response.raise_for_status()  # Check that the request was successful

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all course prefixes and their descriptions
    course_prefixes = soup.find_all('div', class_='course-prefix row')

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['COURSE PREFIX', 'FULL FORM'])

        for entry in course_prefixes:
            course_prefix = entry.find('span', class_='prefix-abbrev push_one two columns').text.strip()
            full_form = entry.find('span', class_='prefix-name nine columns').text.strip()
            writer.writerow([course_prefix, full_form])


def course_catalog_scraper(url: str, file_path='umd_course_prefixes.csv'):
    # Send a GET request to the page
    response = requests.get(url)
    response.raise_for_status()  # Check that the request was successful

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

            if course_prefix not in existing_course_prefixes:
                writer.writerow([course_prefix, full_form])


def separate_course_prefix(full_course_prefix: str):
    words = full_course_prefix.split(' - ')
    return words[0], words[1]
