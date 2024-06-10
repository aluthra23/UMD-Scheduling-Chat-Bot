import csv

from course_prefixes_dataset_creation.main_course_prefixes_scraper import update_umd_courses
from helping_files import constants
import scraper
import pandas as pd

with open('umd_catalog_courses.csv', mode='w', newline='') as file:
    # Create a CSV writer object
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(constants.CSV_CATALOG_COURSES_HEADER)

    update_umd_courses("../course_prefixes_dataset_creation/umd_course_prefixes.csv")
    df = pd.read_csv("../course_prefixes_dataset_creation/umd_course_prefixes.csv")

    # Iterate over each course acronym
    for course_acronym in df["COURSE PREFIX"]:
        scraper.scrape_course_data(course_acronym, file)

print("Course data has been written to umd_catalog_courses.csv")
