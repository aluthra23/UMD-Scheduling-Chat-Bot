from course_prefixes_dataset_creation.course_prefixes_scraper import soc_scraper
from course_prefixes_dataset_creation.course_prefixes_scraper import course_catalog_scraper
from term_id_functions import update_term_id
import pandas as pd


def update_umd_courses(file_path='umd_course_prefixes.csv', term_id=None):
    """Rebuild the prefix list: the term's Testudo prefixes plus any catalog-only prefixes, sorted."""
    soc_scraper(file_path, term_id)
    course_catalog_scraper("https://academiccatalog.umd.edu/undergraduate/approved-courses/", file_path=file_path)

    df = pd.read_csv(file_path)
    df.sort_values(by='COURSE PREFIX').to_csv(file_path, index=False)


if __name__ == "__main__":
    update_umd_courses(term_id=update_term_id())
