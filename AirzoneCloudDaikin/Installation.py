import logging
from .Device import Device

_LOGGER = logging.getLogger(__name__)


class Installation:
    """Manage a Daikin AirzoneCloud installation"""

    _api = None
    _data = {}
    _devices = []

    def __init__(self, api, data):
        self._api = api

        self._data = data

        # log
        _LOGGER.info("Init {}".format(self.str_complete))
        _LOGGER.debug(data)

        # load all devices
        self._load_devices()

    def __str__(self):
        return "Installation(name={}, type={})".format(self.name, self.type)

    @property
    def str_complete(self):
        return "Installation(name={}, type={}, scenary={}, id={})".format(
            self.name, self.type, self.scenary, self.id
        )

    #
    # getters
    #

    @property
    def id(self):
        """ Return installation id """
        return self._data.get("id")

    @property
    def name(self):
        """ Return installation name """
        return self._data.get("name")

    @property
    def type(self):
        """ Return installation type """
        return self._data.get("type")

    @property
    def scenary(self):
        """ Return installation scenary """
        return self._data.get("scenary")

    @property
    def location(self):
        """ Return installation location """
        return self._data.get("complete_name")

    @property
    def gps_location(self):
        """ Return installation gps location : { latitude: ..., longitude: ... } """
        return self._data.get("location")

    @property
    def time_zone(self):
        """ Return the timezone """
        return self._data.get("time_zone")

    #
    # children
    #

    @property
    def devices(self):
        return self._devices

    #
    # Refresh
    #

    def refresh(self, refresh_devices=True):
        """ Refresh current installation data (call refresh_installations on parent AirzoneCloudDaikin) """
        self._api.refresh_installations()
        if refresh_devices:
            self.refresh_devices()

    def refresh_devices(self):
        """ Refresh all devices of this installation """
        self._load_devices()

    #
    # private
    #

    def _load_devices(self):
        """Load all devices for this installation"""
        current_devices = self._devices
        self._devices = []
        try:
            for device_data in self._api._get_devices(self.id):
                device = None
                # search device in current_devices (if where are refreshing devices)
                for current_device in current_devices:
                    if current_device.id == device_data.get("id"):
                        device = current_device
                        device._set_data_refreshed(device_data)
                        break
                # device not found => instance new device
                if device is None:
                    device = Device(self._api, self, device_data)
                self._devices.append(device)
        except RuntimeError:
            raise Exception(
                "Unable to load devices of installation {} ({}) from AirzoneCloudDaikin".format(
                    self.name, self.id
                )
            )
        return self._devices

    def _set_data_refreshed(self, data):
        """ Set data refreshed (call by parent AirzoneCloudDaikin on refresh_installations()) """
        self._data = data
        _LOGGER.info("Data refreshed for {}".format(self.str_complete))


#
# installation raw data example
#

# {
#     "id": "...",
#     "name": "Casa Eros",
#     "icon": 2,
#     "spot_name": "Madrid",
#     "installer_name": null,
#     "installer_phone": null,
#     "installer_email": null,
#     "scenary": "occupied",
#     "type": "home",
#     "postal_code": "28045",
#     "time_zone": "Europe/Madrid",
#     "owner_id": "...",
#     "role": "advanced",
#     "complete_name": "Madrid,Madrid,Community of Madrid,Spain",
#     "location": {"latitude": 10.4155754, "longitude": -2.4037901998979576},
#     "device_ids": ["..."],
# }
