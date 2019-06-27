import re
import requests
import config


def get_persisted_refresh_token() -> str:
    with open("persist/strava_refresh_token") as f:
        return f.read()


def persist_refresh_token(refresh_token: str) -> None:
    if re.match("^[a-f0-9]+$", refresh_token) is None:
        raise ValueError("refresh_token should contain only 0-9 and a-f")
    with open("persist/strava_refresh_token", "w") as f:
        f.write(refresh_token)


def request_access_token() -> str:
    """
    This one is a bit inefficient because it always refreshes the access
    token. We should actually store the access_token as well and only refresh if
    it is expired.
    """

    params = {
        "client_id": config.strava_client_id,
        "client_secret": config.strava_client_secret,
        "grant_type": "refresh_token",
        "refresh_token": get_persisted_refresh_token(),
    }

    # The request may change the refresh token, so first check that we'll be
    # able to persist it.
    persist_refresh_token(params["refresh_token"])

    response = requests.post("https://www.strava.com/oauth/token", params)
    json = response.json()

    # Json should be something like:
    # {
    #    'token_type': 'Bearer',
    #    'access_token': 'abcdef01234567890',
    #    'expires_at': 1560649171,
    #    'expires_in': 19837,
    #    'refresh_token': 'abcdef01234567890'
    # }
    persist_refresh_token(json["refresh_token"])
    return json["access_token"]


def authorize_with_code(code: str) -> str:
    """
    See https://developers.strava.com/docs/authentication/ under 'Token
    exchange'.

    First go to the uri to authorize this app with scope=read_all, then use the
    code with this function.

    """
    params = {
        "client_id": config.strava_client_id,
        "client_secret": config.strava_client_secret,
        "grant_type": "authorization_code",
        "code": code,
    }

    response = requests.post("https://www.strava.com/oauth/token", params)
    json = response.json()

    persist_refresh_token(json["refresh_token"])
    return json
