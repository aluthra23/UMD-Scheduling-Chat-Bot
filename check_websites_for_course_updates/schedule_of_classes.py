import requests
from bs4 import BeautifulSoup
from helping_files import constants

base_url = "https://app.testudo.umd.edu/soc/"
url = f"{base_url}"

def ensure_no_extra_elements(array : list):
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data ")
        exit()

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all courses listed on the page
    courses = soup.find_all('span', class_='prefix-abbrev push_one two columns')

    for course in courses:
        course_prefix = course.text.strip()

        if course_prefix in constants.course_acronyms:
            array.remove(course_prefix)

    return array


def check_soc():
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data ")
        exit()

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all courses listed on the page
    courses = soup.find_all('span', class_='prefix-abbrev push_one two columns')

    count = 0
    for course in courses:
        course_prefix = course.text.strip()

        if course_prefix not in constants.course_acronyms:
            if count == 0:
                print("From the Schedule of Classes, the following course prefixes are not in the course_acronyms array:")

            print(course_prefix)
            count += 1

    if count == 0:
        print("The course_acronyms array contains all course prefixes displayed in the Schedule of Classes!")