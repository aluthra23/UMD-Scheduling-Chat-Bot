from helping_files import constants
import csv
import requests
from bs4 import BeautifulSoup
from term_id_functions import update_term_id

with open('gen_eds.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(constants.CSV_GEN_EDS_HEADER)
    url = f"https://app.testudo.umd.edu/soc/gen-ed/{update_term_id()}/"

    response = requests.get(url)
    if response.status_code != 200:
        exit()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all courses listed on the page
    gen_eds = soup.find_all('div', class_='subcategory')

    data = []
    # Iterate over each course acronym
    for entry in gen_eds:
        gen_ed = entry.text.strip()

        words = gen_ed.split('(')

        full_form = f"{words[0].strip()}"
        acronym = f"{words[1][:-1].strip()}"

        writer.writerow([acronym, full_form])