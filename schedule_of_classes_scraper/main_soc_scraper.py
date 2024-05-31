import soc_scraper
from helping_files import constants
import csv
import time

with open('umd_schedule_of_classes_courses.csv', mode='w', newline='') as file:
    start_time = time.time()
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(constants.CSV_SOC_HEADER)

    # Iterate over each course acronym
    for course_acronym in constants.course_acronyms:
        soc_scraper.scrape_course_data(course_acronym, file)

    print("Data collection complete. Data has been saved to umd_schedule_of_classes_courses.csv")
    print("--- %s seconds ---" % (time.time() - start_time))
