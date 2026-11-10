from schedule_of_classes_scraper import soc_scraper
from helping_files import constants
import csv
import pandas as pd

# Written by course_prefixes_dataset_creation/main_course_prefixes_scraper.py, which runs first.
COURSE_PREFIXES_PATH = "../course_prefixes_dataset_creation/umd_course_prefixes.csv"


def update_current_semester_coursework_data(file_path='umd_schedule_of_classes_courses.csv',
                                            course_prefixes_path=COURSE_PREFIXES_PATH):
    with open(file_path, mode='w', newline='') as file:
        csv.writer(file).writerow(constants.CSV_SOC_HEADER)
        for course_acronym in pd.read_csv(course_prefixes_path)["COURSE PREFIX"]:
            soc_scraper.scrape_course_data(course_acronym, file)


if __name__ == "__main__":
    update_current_semester_coursework_data()
