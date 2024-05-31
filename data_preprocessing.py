# data_preprocessing.py
import pandas as pd


def load_datasets():
    courses_df = pd.read_csv('./schedule_of_classes_scraper/umd_schedule_of_classes_courses.csv')
    course_catalog_df = pd.read_csv('./course_catalog_scraper/umd_catalog_courses.csv')
    prefixes_df = pd.read_csv('./course_prefixes_dataset_creation/umd_course_prefixes.csv')
    gen_eds_df = pd.read_csv('./gen_eds/gen_eds.csv')
    return courses_df, course_catalog_df, prefixes_df, gen_eds_df

