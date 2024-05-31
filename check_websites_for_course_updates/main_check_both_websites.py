import schedule_of_classes
import course_catalog
from helping_files import constants

schedule_of_classes.check_soc()
course_catalog.check_catalog()

array = constants.course_acronyms

array = schedule_of_classes.ensure_no_extra_elements(array)
array = course_catalog.ensure_no_extra_elements(array)

if len(array) > 0:
    print("The following courses are surplus to our course_acronyms array:")
    print(array)
else:
    print("Our course_acronyms contains the right amount of elements!")