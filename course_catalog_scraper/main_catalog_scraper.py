import csv
from helping_files import constants
import scraper

with open('umd_catalog_courses.csv', mode='w', newline='') as file:
    # Create a CSV writer object
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(constants.CSV_CATALOG_COURSES_HEADER)

    # Iterate over each course acronym
    for course_acronym in constants.course_acronyms:
        scraper.scrape_course_data(course_acronym, file)

print("Course data has been written to umd_catalog_courses.csv")
