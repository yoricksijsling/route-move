from pprint import pprint

from garmin.client import GarminClient
import config

from garmin.example_import_response import example_import_response
from garmin.example_elevation_response import example_elevation_response

course = example_import_response()
course['activityTypePk'] = 10
course['courseName'] = 'hello'

geopoints = list(
    [point['latitude'], point['longitude'], None]
    for point
    in course['geoPoints']
)

with GarminClient(config.garmin_user, config.garmin_password) as client:
    # r = client.post_elevation(geopoints)
    # course['geoPoints'] = client.post_elevation(geopoints).json()

    r = client.post_course(course)

    pprint(r)
    pprint(r.text)
    pprint(r.json())

    # activities = client.list_activities()
    # pprint(activities)
