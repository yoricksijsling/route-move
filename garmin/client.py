"""
A module for authenticating against and communicating with selected
parts of the Garmin Connect REST API.

Mostly stolen from
https://github.com/petergardfjall/garminexport/blob/master/garminexport/garminclient.py.
"""

import json
import logging
import os
import re
import requests
from io import BytesIO
import sys
import zipfile
import dateutil
import dateutil.parser
import os.path
from functools import wraps
from builtins import range

#
# Note: For more detailed information about the API services
# used by this module, log in to your Garmin Connect account
# through the web browser and visit the API documentation page
# for the REST service of interest. For example:
#   https://connect.garmin.com/proxy/activity-service-1.3/index.html
#   https://connect.garmin.com/proxy/activity-search-service-1.2/index.html
#

#
# Other useful references:
#   https://github.com/cpfair/tapiriik/blob/master/tapiriik/services/GarminConnect/garminconnect.py
#   https://forums.garmin.com/showthread.php?72150-connect-garmin-com-signin-question/page2
#

log = logging.getLogger(__name__)

# reduce logging noise from requests library
logging.getLogger("requests").setLevel(logging.ERROR)

SSO_LOGIN_URL = "https://sso.garmin.com/sso/signin"
"""The Garmin Connect Single-Sign On login URL."""


def require_session(client_function):
    """Decorator that is used to annotate :class:`GarminClient`
    methods that need an authenticated session before being called.
    """

    @wraps(client_function)
    def check_session(*args, **kwargs):
        client_object = args[0]
        if not client_object.session:
            raise Exception(
                "Attempt to use GarminClient without being connected. Call connect() before first use.'"
            )
        return client_function(*args, **kwargs)

    return check_session


class GarminClient(object):
    """A client class used to authenticate with Garmin Connect and
    extract data from the user account.
    Since this class implements the context manager protocol, this object
    can preferably be used together with the with-statement. This will
    automatically take care of logging in to Garmin Connect before any
    further interactions and logging out after the block completes or
    a failure occurs.
    Example of use: ::
      with GarminClient("my.sample@sample.com", "secretpassword") as client:
          ids = client.list_activity_ids()
          for activity_id in ids:
               gpx = client.get_activity_gpx(activity_id)
    """

    def __init__(self, username, password):
        """Initialize a :class:`GarminClient` instance.
        :param username: Garmin Connect user name or email address.
        :type username: str
        :param password: Garmin Connect account password.
        :type password: str
        """
        self.username = username
        self.password = password
        self.session = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def connect(self):
        self.session = requests.Session()
        self._authenticate()

    def disconnect(self):
        if self.session:
            self.session.close()
            self.session = None

    def _authenticate(self):
        log.info("authenticating user ...")
        form_data = {
            "username": self.username,
            "password": self.password,
            "embed": "false",
        }
        request_params = {"service": "https://connect.garmin.com/modern"}
        headers = {"origin": "https://sso.garmin.com"}
        auth_response = self.session.post(
            SSO_LOGIN_URL, headers=headers, params=request_params, data=form_data
        )
        log.debug("got auth response: %s", auth_response.text)
        if auth_response.status_code != 200:
            raise ValueError("authentication failure: did you enter valid credentials?")
        auth_ticket_url = self._extract_auth_ticket_url(auth_response.text)
        log.debug("auth ticket url: '%s'", auth_ticket_url)

        log.info("claiming auth ticket ...")
        response = self.session.get(auth_ticket_url)
        if response.status_code != 200:
            raise RuntimeError(
                "auth failure: failed to claim auth ticket: %s: %d\n%s"
                % (auth_ticket_url, response.status_code, response.text)
            )

        # appears like we need to touch base with the old API to initiate
        # some form of legacy session. otherwise certain downloads will fail.
        self.session.get("https://connect.garmin.com/legacy/session")

    def _extract_auth_ticket_url(self, auth_response):
        """Extracts an authentication ticket URL from the response of an
        authentication form submission. The auth ticket URL is typically
        of form:
          https://connect.garmin.com/modern?ticket=ST-0123456-aBCDefgh1iJkLmN5opQ9R-cas
        :param auth_response: HTML response from an auth form submission.
        """
        match = re.search(r'response_url\s*=\s*"(https:[^"]+)"', auth_response)
        if not match:
            raise RuntimeError(
                "auth failure: unable to extract auth ticket URL. did you provide a correct username/password?"
            )
        auth_ticket_url = match.group(1).replace("\\", "")
        return auth_ticket_url

    @require_session
    def import_course(self, byte_data):
        data = {}
        files = {"file": ("my-upload.tcx", byte_data, "application/octet-stream")}
        response = self.session.post(
            "https://connect.garmin.com/modern/proxy/course-service/course/import",
            data=data,
            files=files,
            headers={"nk": "NT"},
        )
        return response

    @require_session
    def post_elevation(self, elevation_tuples):
        response = self.session.post(
            "https://connect.garmin.com/modern/proxy/course-service/course/elevation",
            json=elevation_tuples,
            headers={"nk": "NT"},
        )
        return response

    @require_session
    def post_course(self, course):

        response = self.session.post(
            "https://connect.garmin.com/modern/proxy/course-service/course/",
            json=course,
            headers={"nk": "NT"},
        )
        return response
