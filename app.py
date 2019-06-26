# Run with:
# FLASK_APP=app.py flask run

from flask import Flask, render_template, request
from pprint import pprint

import config
import swagger_client
import strava.tokens
from garmin.client import GarminClient

app = Flask(__name__)

@app.route("/")
def routes():
    # api_client = swagger_client.ApiClient()
    # api_client.configuration.access_token = strava.tokens.request_access_token()
    # routes_api = swagger_client.RoutesApi(api_client = api_client)
    # routes = routes_api.get_routes_by_athlete_id(config.strava_athlete_id, page=1, per_page=200)

    # MOCK ROUTES:
    import examples.strava_routes
    routes = examples.strava_routes.get()

    # Only cycling routes
    routes = list(route for route in routes if route['type'] == 1)

    return render_template('routes.html', routes=routes)

@app.route("/copy", methods=['POST'])
def copy():
    route_id = request.form['route_id']
    route_name = request.form['route_name']

    api_client = swagger_client.ApiClient()
    api_client.configuration.access_token = strava.tokens.request_access_token()
    tcx_response = api_client.call_api(
        f'/routes/{route_id}/export_tcx', 'GET',
        {}, [], {},
        post_params=[], files={},
        response_type='file',
        auth_settings=['strava_oauth'],
        _return_http_data_only=True,
        _preload_content=False
    )
    tcx_bytes = tcx_response.data

    with GarminClient(config.garmin_user, config.garmin_password) as client:
        import_response = client.import_course(tcx_bytes)
        pprint(import_response.json())

    # e.g. 19295497 '32km zuiderwind'
    return (f'Copying {route_id}  {route_name}')
