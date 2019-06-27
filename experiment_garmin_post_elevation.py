from pprint import pprint

import config
import garmin.course
from garmin.client import GarminClient

import examples.garmin_import_response
import examples.garmin_elevation_response

course = examples.garmin_import_response.get()
course["activityTypePk"] = 10
course["courseName"] = "hello"

elevation_tuples = garmin.course.geopoints_to_elevation_tuples(course["geoPoints"])

with GarminClient(config.garmin_user, config.garmin_password) as client:
    r = client.post_elevation(elevation_tuples)
    pprint(r)
    pprint(r.text)
    pprint(r.json())

    # course['geoPoints'] = client.post_elevation(geopoints).json()

    # r = client.post_course(course)

    # pprint(r)
    # pprint(r.text)
    # pprint(r.json())

    # activities = client.list_activities()
    # pprint(activities)
