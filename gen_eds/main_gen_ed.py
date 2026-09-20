from helping_files import constants, http_utils
import csv
from bs4 import BeautifulSoup
from term_id_functions import update_term_id


def scrape_gen_eds(term_id):
    response = http_utils.fetch(f"https://app.testudo.umd.edu/soc/gen-ed/{term_id}/")
    soup = BeautifulSoup(response.text, 'html.parser')

    rows = []
    for entry in soup.find_all('div', class_='subcategory'):
        words = entry.text.strip().split('(')
        full_form = words[0].strip()
        acronym = words[1][:-1].strip()
        rows.append([acronym, full_form])

    if not rows:
        raise RuntimeError(f"No gen-ed categories found for term {term_id}")
    return rows


if __name__ == "__main__":
    rows = scrape_gen_eds(update_term_id())

    with open('gen_eds.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(constants.CSV_GEN_EDS_HEADER)
        writer.writerows(rows)
