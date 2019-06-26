import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

import config
import strava.tokens

api_client = swagger_client.ApiClient()
api_client.configuration.access_token = strava.tokens.request_access_token()
routes_api = swagger_client.RoutesApi(api_client = api_client)

# def get_routes():
#     routes_api

try:
    # List Athlete Routes
    # api_response = routes_api.get_routes_by_athlete_id(config.strava_athlete_id, page=1, per_page=200)
    # pprint(api_response)
    # print(len(api_response))

    route_id=19295497
    api_response = api_client.call_api(
        f'/routes/{route_id}/export_tcx', 'GET',
        {}, [], {},
        body=None, post_params=[], files={},
        response_type='file',
        auth_settings=['strava_oauth'],
        async_req=None,
        _return_http_data_only=True,
        _preload_content=False
    )
    response_bytes = api_response.data


except ApiException as e:
    print("Exception when calling RoutesApi->getRoutesByAthleteId: %s\n" % e)
