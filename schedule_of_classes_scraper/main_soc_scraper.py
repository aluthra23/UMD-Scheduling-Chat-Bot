from schedule_of_classes_scraper import soc_scraper
from helping_files import constants
import csv


def update_current_semester_coursework_data(file_path='umd_schedule_of_classes_courses.csv'):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(constants.CSV_SOC_HEADER)

        # Iterate over each course acronym
        for course_acronym in constants.course_acronyms:
            soc_scraper.scrape_course_data(course_acronym, file)
