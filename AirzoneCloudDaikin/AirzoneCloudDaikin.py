#!/usr/bin/python3

import logging
import requests
import urllib
import urllib.parse
import json

from .contants import (
    API_LOGIN,
    API_INSTALLATION_RELATIONS,
    API_DEVICES,
    API_EVENTS,
)
from .Installation import Installation

_LOGGER = logging.getLogger(__name__)


class AirzoneCloudDaikin:
    """Allow to connect to AirzoneCloudDaikin API"""

    _session = None
    _username = None
    _password = None
    _base_url = "https://dkn.airzonecloud.com"
    _user_agent = "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 7 Build/MOB30X; wv) AppleWebKit/537.26 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Safari/537.36"
    _token = None
    _installations = []

    def __init__(
        self, username, password, user_agent=None, base_url=None,
    ):
        """Initialize API connection"""
        self._session = requests.Session()
        self._username = username
        self._password = password
        if user_agent is not None and isinstance(user_agent, str):
            self._user_agent = user_agent
        if base_url is not None and isinstance(base_url, str):
            self._base_url = base_url
        # login
        self._login()
        # load installations
        self._load_installations()

    #
    # getters
    #

    @property
    def installations(self):
        """Get installations list (same order as in app)"""
        return self._installations

    @property
    def all_devices(self):
        """Get all devices from all installations (same order as in app)"""
        result = []
        for installation in self.installations:
            for device in installation.devices:
                result.append(device)
        return result

    #
    # Refresh
    #

    def refresh_installations(self):
        """Refresh installations"""
        self._load_installations()

    #
    # private
    #

    def _login(self):
        """Login to Daikin AirzoneCloud and return token"""

        try:
            url = "{}{}".format(self._base_url, API_LOGIN)
            login_payload = {"email": self._username, "password": self._password}
            headers = {"User-Agent": self._user_agent}
            response = self._session.post(
                url, headers=headers, json=login_payload
            ).json()
            self._token = response.get("user").get("authentication_token")
        except (RuntimeError, AttributeError):
            raise Exception("Unable to login to Daikin AirzoneCloud") from None

        _LOGGER.info("Login success as {}".format(self._username))

        return self._token

    def _load_installations(self):
        """Load all installations for this account"""
        current_installations = self._installations
        self._installations = []
        try:
            for installation_relation in self._get_installation_relations():
                installation_data = installation_relation.get("installation")
                installation = None
                # search installation in current_installations (if where are refreshing installations)
                for current_installation in current_installations:
                    if current_installation.id == installation_data.get("id"):
                        installation = current_installation
                        installation._set_data_refreshed(installation_data)
                        break
                # installation not found => instance new installation
                if installation is None:
                    installation = Installation(self, installation_data)
                self._installations.append(installation)
        except RuntimeError:
            raise Exception("Unable to load installations from AirzoneCloud")
        return self._installations

    def _get_installation_relations(self):
        """Http GET to load installations relations"""
        _LOGGER.debug("get_installation_relations()")
        return self._get(API_INSTALLATION_RELATIONS).get("installation_relations")

    def _get_devices(self, installation_id):
        """Http GET to load devices"""
        _LOGGER.debug("get_devices(installation_id={})".format(installation_id))
        return self._get(API_DEVICES, {"installation_id": installation_id}).get(
            "devices"
        )

    def _send_event(self, payload):
        """Http POST to send an event"""
        _LOGGER.debug("Send event with payload: {}".format(json.dumps(payload)))
        try:
            result = self._post(API_EVENTS, payload)
            _LOGGER.debug("Result event: {}".format(json.dumps(result)))
            return result
        except RuntimeError:
            _LOGGER.error("Unable to send event to AirzoneCloud")
            return None

    def _get(self, api_endpoint, params={}):
        """Do a http GET request on an api endpoint"""
        params["format"] = "json"

        return self._request(method="GET", api_endpoint=api_endpoint, params=params)

    def _post(self, api_endpoint, payload={}):
        """Do a http POST request on an api endpoint"""
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
        }

        return self._request(
            method="POST", api_endpoint=api_endpoint, headers=headers, json=payload
        )

    def _request(
        self, method, api_endpoint, params={}, headers={}, json=None, autoreconnect=True
    ):
        # generate url with auth
        params["user_email"] = self._username
        params["user_token"] = self._token
        url = "{}{}/?{}".format(
            self._base_url, api_endpoint, urllib.parse.urlencode(params)
        )

        # set user agent
        headers["User-Agent"] = self._user_agent

        # make call
        call = self._session.request(method=method, url=url, headers=headers, json=json)

        if call.status_code == 401 and autoreconnect:  # unauthorized error
            # log
            _LOGGER.info(
                "Get unauthorized error (token expired ?), trying to reconnect..."
            )

            # try to reconnect
            self._login()

            # retry get without autoreconnect (to avoid infinite loop)
            return self._request(
                method=method,
                api_endpoint=api_endpoint,
                params=params,
                headers=headers,
                json=json,
                autoreconnect=False,
            )

        # raise other error if needed
        call.raise_for_status()

        return call.json()
