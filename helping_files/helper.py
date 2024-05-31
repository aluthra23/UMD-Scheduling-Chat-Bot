
def parse_course_string(course_string):
    # Split the string by spaces
    parts = course_string.split()

    # Extract the course acronym (first word)
    course_acronym = parts[0]

    # Extract the course name (middle part)
    course_name = ' '.join(parts[1:-2])  # Adjusted to exclude the last 3 words

    # Extract the number of credits (last word, excluding parentheses)
    credits = str(parts[-2][1:]).strip()  # Remove the parentheses

    return course_acronym, course_name, credits


def remove_period_end(string):
    if string[-1] == '.':
        return string[:-1]
    else:
        return string

# print(remove_period_end("Hi there."))


def parse_extra(example_string):
    # Find the index of the first colon
    first_colon_index = example_string.find(':')

    # Extract the label (before the first colon)
    label = example_string[:first_colon_index].strip()

    # Extract the description (after the first colon)
    description = example_string[first_colon_index + 1:].strip()

    return label, description

def string_without_delimiter(input_string, delimiter):
    index = input_string.lower().find(delimiter.lower())
    if index != -1:
        before = input_string[:index].strip()
        after = input_string[index + len(delimiter):].strip()
        return before, remove_period_end(after)
    else:
        return input_string, None


import re


import re


def extract_link_from_html(html_content):
    # Define the regular expression pattern to find the <a> tag with href attribute inside a div with class "section-text"

    pattern = r'\s*<a href="([^"]+)">'

    # Search the pattern in the provided HTML content
    match = re.search(pattern, html_content)

    if match:
        # Extract the URL from the match
        link = match.group(1)
        return link
    else:
        return None


def extract_course_details(html_content:str, existing_dict, actual_html):
    fields = {
        "PREREQUISITE": r"<strong>Prerequisite:</strong>\s*(.*?)\s*</div>",
        "COREQUISITE": r"<strong>Corequisite:</strong>\s*(.*?)\s*</div>",
        "RESTRICTION": r"<strong>Restriction:</strong>\s*(.*?)\s*</div>",
        "CREDIT ONLY GRANTED FOR": r"<strong>Credit only granted for:</strong>\s*(.*?)\s*</div>",
        "FORMERLY": r"<strong>Formerly:</strong>\s*(.*?)\s*</div>",
        "RECOMMENDED": r"<strong>Recommended:</strong>\s*(.*?)\s*</div>",
        "CROSS-LISTED WITH": r"<strong>Cross-listed with:</strong>\s*(.*?)\s*</div>",
    }

    description = existing_dict.get("DESCRIPTION")

    if not description:
        description = ""

    edited_specific_fields = False

    for field, pattern in fields.items():
        match = re.search(pattern, html_content)
        if match:
            existing_dict[field] = remove_period_end(match.group(1).strip())
            edited_specific_fields = True

    if not edited_specific_fields:
        description += actual_html.text.strip()

    existing_dict["DESCRIPTION"] = description.strip()

    return existing_dict


def extract_abnormal_course_details(existing_dict, actual_html):
    content = actual_html.text.strip()

    fields = {
        "PREREQUISITE": r"Prerequisite:\s*(.*?)\.",
        "COREQUISITE": r"Corequisite:\s*(.*?)\.",
        "RESTRICTION": r"Restriction:\s*(.*?)\.",
        "CREDIT ONLY GRANTED FOR": r"Credit only granted for\s*(.*?)\.",
        "FORMERLY": r"Formerly:\s*(.*?)\.",
        "CROSS-LISTED WITH": [r"Cross-listed with\s*(.*?)\.", r"Jointly offered with\s*(.*?)\."]
    }

    description = existing_dict["DESCRIPTION"]

    if not description:
        description = ""

    for field, patterns in fields.items():
        if isinstance(patterns, list):
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    existing_dict[field] = remove_period_end(match.group(1).strip())
                    content = re.sub(pattern, '', content)
        else:
            match = re.search(patterns, content)
            if match:
                existing_dict[field] = remove_period_end(match.group(1).strip())
                # Remove the matched section from the HTML content
                content = re.sub(patterns, '', content)

    description += content.strip()


    all_course_texts = actual_html.find_all('div', class_='course-text')
    if all_course_texts:
        link = extract_link_from_html(html_content=str(all_course_texts[-1]))
        if link:
            # print("THIS HAPPENED")
            description += f" {link}"

    existing_dict["DESCRIPTION"] = description.strip()

    return existing_dict

def remove_all_whitespace(input_string):
    return ("".join(input_string.split()).replace("\n", "").strip()
            .replace("or", " or ").replace("iftakenwith", "if taken with ")
            .replace("GenEd:", ""))

# input_string = "GenEd:\n\n\n\n\nDSHS, \n\n\n\n\nDVUP"
# result = remove_whitespace(input_string)
# print("Result:", result)
