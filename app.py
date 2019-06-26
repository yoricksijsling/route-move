# Run with:
# FLASK_APP=app.py flask run

from flask import Flask, render_template, request
from pprint import pprint

import config
import garmin.course
import swagger_client
import strava.tokens
from garmin.client import GarminClient

app = Flask(__name__)

@app.route("/")
def routes():
    strava_client = swagger_client.ApiClient()
    strava_client.configuration.access_token = strava.tokens.request_access_token()
    routes_api = swagger_client.RoutesApi(api_client = strava_client)
    routes = routes_api.get_routes_by_athlete_id(config.strava_athlete_id, page=1, per_page=200)

    # Only cycling routes
    routes = list(r for r in routes if r.type == 1)

    return render_template('routes.html', routes=routes)

@app.route("/copy", methods=['POST'])
def copy():
    route_id = request.form['route_id']
    route_name = request.form['route_name']

    # Get tcx from strava
    strava_client = swagger_client.ApiClient()
    strava_client.configuration.access_token = strava.tokens.request_access_token()
    tcx_response = strava_client.call_api(
        f'/routes/{route_id}/export_tcx', 'GET',
        {}, [], {},
        post_params=[], files={},
        response_type='file',
        auth_settings=['strava_oauth'],
        _return_http_data_only=True,
        _preload_content=False
    )
    tcx_bytes = tcx_response.data

    # Connect to Garmin
    with GarminClient(config.garmin_user, config.garmin_password) as garmin_client:
        import_response = garmin_client.import_course(tcx_bytes)
        course = import_response.json()

        elevation_response = garmin_client.post_elevation(
            garmin.course.geopoints_to_elevation_tuples(course['geoPoints'])
        )
        elevation_tuples = elevation_response.json()
        garmin.course.add_course_info(course, route_name, elevation_tuples)

        course_response = garmin_client.post_course(course)
        saved_course = course_response.json()

    return render_template('copy.html', garmin_route_id=saved_course['courseId'])
