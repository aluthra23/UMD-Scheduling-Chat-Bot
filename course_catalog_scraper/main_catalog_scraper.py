import csv

from helping_files import constants
import scraper
import pandas as pd

# Written by course_prefixes_dataset_creation/main_course_prefixes_scraper.py, which runs first.
COURSE_PREFIXES_PATH = "../course_prefixes_dataset_creation/umd_course_prefixes.csv"

if __name__ == "__main__":
    with open('umd_catalog_courses.csv', mode='w', newline='') as file:
        csv.writer(file).writerow(constants.CSV_CATALOG_COURSES_HEADER)
        for course_acronym in pd.read_csv(COURSE_PREFIXES_PATH)["COURSE PREFIX"]:
            scraper.scrape_course_data(course_acronym, file)
