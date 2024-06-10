import requests
from bs4 import BeautifulSoup
from helping_files import helper
import csv


def scrape_course_data(course_acronym, file):
    base_url = "https://academiccatalog.umd.edu/undergraduate/approved-courses/"
    url = f"{base_url}{course_acronym.lower()}/"

    response = requests.get(url)
    if response.status_code != 200:
        return

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all courses listed on the page
    courses = soup.find_all('div', class_='courseblock')

    # Iterate over each course and extract details
    for course_block in courses:
        course_dict = {
            "COURSE PREFIX" : course_acronym,
            "COURSE NUMBER": None,
            "NAME": None,
            "CREDITS": None,
            "DESCRIPTION": None,
            "PREREQUISITE": None,
            "RESTRICTION": None,
            "FORMERLY NAMED": None,
            "RECOMMENDED": None,
            "CREDIT ONLY GRANTED FOR": None,
            "REPEATABLE TO": None,
            "CROSS-LISTED": None,
            'COREQUISITE': None
            # Add more keys for other miscellaneous data if needed
        }


        course_title = course_block.find('p', class_='courseblocktitle noindent').strong.text.strip()
        course_dict["COURSE NUMBER"], course_dict["NAME"], course_dict["CREDITS"] = helper.parse_course_string(course_title)
        course_dict["DESCRIPTION"] = course_block.find('p', class_='courseblockdesc noindent').text.strip()

        extras = course_block.find_all('p', class_='courseblockextra noindent')
        for extra in extras:
            extra_description = extra.text
            label, description = helper.parse_extra(extra_description)

            if course_dict["CROSS-LISTED"]:
                course_dict[label.upper()] = helper.remove_period_end(description)
            else:
                course_dict[label.upper()], course_dict["CROSS-LISTED"] = (
                    helper.string_without_delimiter(helper.remove_period_end(description), "Cross-listed with") )

        writer = csv.writer(file)
        writer.writerow([
            course_dict["COURSE PREFIX"],
            course_dict["COURSE NUMBER"],
            course_dict["NAME"],
            course_dict["CREDITS"],
            course_dict["DESCRIPTION"],
            course_dict["PREREQUISITE"],
            course_dict["RESTRICTION"],
            course_dict["FORMERLY NAMED"],
            course_dict["RECOMMENDED"],
            course_dict["CREDIT ONLY GRANTED FOR"],
            course_dict["REPEATABLE TO"],
            course_dict["CROSS-LISTED"],
            course_dict["COREQUISITE"]
            # Add more fields as needed
        ])
