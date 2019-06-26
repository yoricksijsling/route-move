from pprint import pprint
import geopy.distance

import garmin.course

import examples.garmin_course_post
import examples.garmin_elevation_response
import examples.garmin_import_response


def dict_diff(first, second):
    """ Return a dict of keys that differ with another config object.  If a value is
        not found in one fo the configs, it will be represented by KEYNOTFOUND.
        @param first:   Fist dictionary to diff.
        @param second:  Second dicationary to diff.
        @return diff:   Dict of Key => (first.val, second.val)
    """
    KEYNOTFOUND = "<KEYNOTFOUND>"
    diff = {}
    # Check all keys in first dict
    for key in first.keys():
        if key not in second:
            diff[key] = (first[key], KEYNOTFOUND)
        elif first[key] != second[key]:
            diff[key] = (first[key], second[key])
    # Check all keys in second dict to find missing
    for key in second.keys():
        if key not in first:
            diff[key] = (KEYNOTFOUND, second[key])
    return diff


course = examples.garmin_import_response.get()
reference = examples.garmin_course_post.get()

elevation_data = examples.garmin_elevation_response.get()

garmin.course.add_course_info(course, "32km zuiderwind", elevation_data)

course["geoPoints"] = course["geoPoints"][565:]
reference["geoPoints"] = reference["geoPoints"][565:]

# There are some rounding differences and the start point is different.
pprint(dict_diff(course, reference))
