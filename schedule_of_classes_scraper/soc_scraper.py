import pandas as pd
from bs4 import BeautifulSoup
import csv
from term_id_functions import update_term_id

from helping_files import helper, http_utils

KNOWN_CLASS_TYPES = ("LECTURE", "DISCUSSION", "LAB")

term_id = update_term_id()

# Base URL for the UMD schedule of classes search
base_url = "https://app.testudo.umd.edu/soc/search"


def find_message_div(time):
    # Find all divs that have 'class' in their class name
    message_divs = time.find_all('div', class_=lambda x: x and 'class' in x.lower())

    # Return the text of the first matching div, or None if none found
    if message_divs:
        return message_divs[0].text.strip()
    return None


def free_meeting_slot(section_data, class_type):
    """The first unused CSV slot for a meeting type ("LAB", then "2ND LISTED LAB", ...), or None."""
    if class_type not in KNOWN_CLASS_TYPES:
        return None
    for ordinal in ("", "2ND LISTED ", "3RD LISTED "):
        slot = f"{ordinal}{class_type}"
        if section_data.get(f"HAS {slot}") == 0:
            return slot
    return None


def room_text(room):
    """'ESJ 0202', just the building, or the raw text (e.g. 'ONLINE') of a class-building span."""
    if room is None:
        return None
    building = helper.text_of(room, 'span', 'building-code')
    if not building:
        return room.text.strip() or None
    room_number = helper.text_of(room, 'span', 'class-room')
    return f"{building} {room_number}" if room_number else building


def scrape_course_data(course_acronym, file):
    url = f"{base_url}?courseId={course_acronym}&sectionId=&termId={term_id}&creditCompare=%3E%3D&credits=0.0&courseLevelFilter=UGRAD&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"

    # Fetch the web page
    response = http_utils.fetch(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    courses = soup.find_all('div', class_='course')

    for course in courses:
        course_number = helper.text_of(course, 'div', 'course-id')
        if not course_number:
            continue

        section_title = helper.text_of(course, 'span', 'course-title')
        section_min_credits = helper.parse_int(helper.text_of(course, 'span', 'course-min-credits'))
        section_max_credits = helper.parse_int(helper.text_of(course, 'span', 'course-max-credits'))
        if section_max_credits is None:
            section_max_credits = section_min_credits
        section_grading = helper.text_of(course, 'span', 'grading-method')

        description_fields = {
            "GEN_EDS FULFILLED": "",
            "PREREQUISITE":None,
            "COREQUISITE":None,
            "RESTRICTION":None,
            "CREDIT ONLY GRANTED FOR":None,
            "FORMERLY":None,
            "RECOMMENDED":None,
            "CROSS-LISTED WITH": None,
            "DESCRIPTION": None,
        }

        descriptions = course.find('div', class_='approved-course-texts-container')
        if descriptions:
            descriptions = course.find_all('div', class_='approved-course-text')

            for description in descriptions:
                description_fields = helper.extract_course_details(html_content=str(description),
                                                                   existing_dict=description_fields,
                                                                   actual_html=description)

        descriptions = course.find('div', class_='course-texts-container')
        if descriptions:
            description_fields = helper.extract_abnormal_course_details(existing_dict=description_fields,
                                                                        actual_html=descriptions)

        gen_eds = course.find('div', class_='gen-ed-codes-group six columns')

        if gen_eds and str(gen_eds.text).strip():
            description_fields["GEN_EDS FULFILLED"] = helper.remove_all_whitespace(gen_eds.text.strip())


        # Normal Classes
        open_sections = course.find_all('div', class_='section delivery-f2f')
        update_classes_data(course_number, open_sections,
                            class_name="section-day-time-group push_two five columns",
                            file_path=file, class_setting="NORMAL",
                            section_title=section_title,
                            section_min_credits=section_min_credits,
                            section_max_credits=section_max_credits,
                            section_grading=section_grading,
                            description_fields=description_fields)

        # Blended Classes
        open_sections = course.find_all('div', class_='section delivery-blended')
        update_classes_data(course_number, open_sections,
                            class_name="section-day-time-group push_one five columns",
                            file_path=file, class_setting="BLENDED",
                            section_title=section_title,
                            section_min_credits=section_min_credits,
                            section_max_credits=section_max_credits,
                            section_grading=section_grading,
                            description_fields=description_fields)

        # Online Classes
        open_sections = course.find_all('div', class_='section delivery-online')
        update_classes_data(course_number, open_sections,
                            class_name="section-day-time-group push_one five columns",
                            file_path=file, class_setting="ONLINE",
                            section_title=section_title,
                            section_min_credits=section_min_credits,
                            section_max_credits=section_max_credits,
                            section_grading=section_grading,
                            description_fields=description_fields)


def update_classes_data(course_number, open_sections, class_name, file_path, class_setting, section_title, section_min_credits, section_max_credits, section_grading, description_fields):

    data = []
    if open_sections:
        for section in open_sections:
            section_data = {
                "COURSE NUMBER": course_number,
                "COURSE TITLE": section_title,
                "MINIMUM CREDITS": section_min_credits,
                "MAXIMUM CREDITS": section_max_credits,
                "GRADING METHOD": section_grading,
                "GEN_EDS FULFILLED": description_fields["GEN_EDS FULFILLED"],
                "SECTION ID": None,
                "INSTRUCTOR": None,
                "TOTAL SEATS": None,
                "OPEN SEATS": None,
                "WAITLIST COUNT": None,
                "LECTURE TIME": None,
                "2ND LISTED LECTURE TIME": None,
                "3RD LISTED LECTURE TIME": None,
                "DISCUSSION TIME": None,
                "2ND LISTED DISCUSSION TIME": None,
                "LAB TIME": None,
                "2ND LISTED LAB TIME": None,
                "LECTURE ROOM": None,
                "2ND LISTED LECTURE ROOM": None,
                "3RD LISTED LECTURE ROOM": None,
                "DISCUSSION ROOM": None,
                "2ND LISTED DISCUSSION ROOM": None,
                "LAB ROOM": None,
                "2ND LISTED LAB ROOM": None,
                "UNSPECIFIED TIME MESSAGE": None,
                "HAS LECTURE": 0,
                "HAS 2ND LISTED LECTURE": 0,
                "HAS 3RD LISTED LECTURE": 0,
                "HAS DISCUSSION": 0,
                "HAS 2ND LISTED DISCUSSION": 0,
                "HAS LAB": 0,
                "HAS 2ND LISTED LAB": 0,
                "IS NORMAL": 0,
                "IS BLENDED (NORMAL AND ONLINE)": 0,
                "IS ONLINE": 0,
                "SPECIAL RESTRICTION": None,
                "PREREQUISITE": description_fields["PREREQUISITE"],
                "COREQUISITE": description_fields["COREQUISITE"],
                "RESTRICTION": description_fields["RESTRICTION"],
                "CREDIT ONLY GRANTED FOR": description_fields["CREDIT ONLY GRANTED FOR"],
                "FORMERLY": description_fields["FORMERLY"],
                "RECOMMENDED": description_fields["RECOMMENDED"],
                "CROSS-LISTED WITH": description_fields["CROSS-LISTED WITH"],
                "DESCRIPTION": description_fields["DESCRIPTION"],
            }

            if class_setting == 'NORMAL':
                section_data["IS NORMAL"] = 1
            elif class_setting == 'ONLINE':
                section_data["IS ONLINE"] = 1
            else:
                section_data["IS NORMAL"] = 1
                section_data["IS ONLINE"] = 1
                section_data["IS BLENDED (NORMAL AND ONLINE)"] = 1


            section_id = helper.text_of(section, 'span', 'section-id')
            if not section_id:
                continue
            section_data["SECTION ID"] = section_id

            instructors = [span.text.strip() for span in section.find_all('span', class_='section-instructor') if span.text.strip()]
            section_data["INSTRUCTOR"] = ", ".join(instructors) or None

            section_data["TOTAL SEATS"] = helper.text_of(section, 'span', 'total-seats-count')
            section_data["OPEN SEATS"] = helper.text_of(section, 'span', 'open-seats-count')
            section_data["WAITLIST COUNT"] = helper.text_of(section, 'span', 'waitlist-count') or "0"

            times_container = section.find('div', class_="class-days-container")
            times = times_container.find_all('div', class_='row') if times_container else []

            for time in times:
                days = helper.text_of(time, 'span', 'section-days')
                has_specific_time = False
                start_time = ""
                end_time = ""

                if days:
                    start_time = helper.text_of(time, 'span', 'class-start-time')
                    end_time = helper.text_of(time, 'span', 'class-end-time')
                    if "TBA" in days.upper() or not (start_time and end_time):
                        section_data["UNSPECIFIED TIME MESSAGE"] = days
                    else:
                        has_specific_time = True
                else:
                    message = find_message_div(time)
                    if message is None:
                        # Handle case where no matching div was found
                        message = "No class message found"

                    section_data["UNSPECIFIED TIME MESSAGE"] = message
                    days = message

                class_type = time.find('div', class_='two columns')
                class_type = class_type.text.strip().upper() if class_type else "LECTURE"
                detail = f"{days} {start_time}-{end_time}" if has_specific_time else days
                room = room_text(time.find('span', class_='class-building'))

                slot = free_meeting_slot(section_data, class_type)
                if slot is None:
                    # An unusual type (e.g. SEMINAR), or more meetings of a type than the CSV has columns for.
                    note = f"{class_type}: {detail}" + (f" in {room}" if room else "")
                    current = section_data["UNSPECIFIED TIME MESSAGE"]
                    section_data["UNSPECIFIED TIME MESSAGE"] = f"{current}; {note}" if current else note
                    continue

                section_data[f"HAS {slot}"] = 1
                section_data[f"{slot} TIME"] = detail
                if room:
                    section_data[f"{slot} ROOM"] = room

            # Iterating through section-texts-container
            restrictions = section.find('div', class_="section-texts-container")

            if restrictions:
                restrictions = restrictions.find_all('div', class_='section-text')

                full_restriction = ""
                for i, restriction in enumerate(restrictions):
                    link = helper.extract_link_from_html(str(restriction))

                    new_line = "\n"

                    if i + 1 == len(restrictions):
                        new_line = ""

                    if link:
                        full_restriction += f"{restriction.text}: {link}{new_line}"
                    else:
                        full_restriction += f"{restriction.text}{new_line}"

                section_data["SPECIAL RESTRICTION"] = full_restriction


            data.append(section_data)
    else:
        return

    if data:
        df = pd.DataFrame(data)
        df.to_csv(file_path, mode='a', header=False, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
