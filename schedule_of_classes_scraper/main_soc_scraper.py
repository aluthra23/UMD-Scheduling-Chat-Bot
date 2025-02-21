from course_prefixes_dataset_creation.main_course_prefixes_scraper import update_umd_courses
from schedule_of_classes_scraper import soc_scraper
from helping_files import constants
import csv
import pandas as pd


def update_current_semester_coursework_data(file_path='umd_schedule_of_classes_courses.csv',
                            course_prefixes_path="../course_prefixes_dataset_creation/umd_course_prefixes.csv"):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(constants.CSV_SOC_HEADER)

        update_umd_courses(file_path)
        df = pd.read_csv(course_prefixes_path)

        # Iterate over each course acronym
        for course_acronym in df["COURSE PREFIX"]:
            soc_scraper.scrape_course_data(course_acronym, file)

update_current_semester_coursework_data()