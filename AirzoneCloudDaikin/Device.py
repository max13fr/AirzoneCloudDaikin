import logging
from .contants import MODES_CONVERTER

_LOGGER = logging.getLogger(__name__)


class Device:
    """Manage a AirzoneCloudDaikin device"""

    _api = None
    _installation = {}
    _data = {}

    def __init__(self, api, installation, data):
        self._api = api
        self._installation = installation
        self._data = data

        # log
        _LOGGER.info("Init {}".format(self.str_complete))
        _LOGGER.debug(data)

    def __str__(self):
        return "Device(name={}, is_on={}, mode={}, current_temp={}, target_temp={})".format(
            self.name,
            self.is_on,
            self.mode,
            self.current_temperature,
            self.target_temperature,
        )

    @property
    def str_complete(self):
        return "Device(name={}, is_on={}, mode={}, current_temp={}, target_temp={}, id={}, mac={})".format(
            self.name,
            self.is_on,
            self.mode,
            self.current_temperature,
            self.target_temperature,
            self.id,
            self.mac,
        )

    #
    # getters
    #

    @property
    def id(self):
        """ Return device id """
        return self._data.get("id")

    @property
    def name(self):
        """ Return device name """
        return self._data.get("name")

    @property
    def status(self):
        """ Return device status """
        return self._data.get("status")

    @property
    def mac(self):
        """ Return device mac """
        return self._data.get("mac")

    @property
    def pin(self):
        """ Return device pin code """
        return self._data.get("pin")

    @property
    def is_on(self):
        return bool(int(self._data.get("power", 0)))

    @property
    def mode(self):
        """ Return device current mode name """
        return MODES_CONVERTER[self.mode_raw]["name"]

    @property
    def mode_description(self):
        """ Return device current mode description """
        return MODES_CONVERTER[self.mode_raw]["description"]

    @property
    def mode_raw(self):
        """ Return device current raw mode (from API) """
        return self._data.get("mode")

    @property
    def heat_cold_mode(self):
        """ Return device current heat/cold mode """
        return MODES_CONVERTER[self.mode_raw]["type"]

    @property
    def current_temperature(self):
        """ Return device current temperature """
        return self._data.get("local_temp")

    @property
    def target_temperature(self):
        """ Return device target temperature """
        if self.heat_cold_mode == "heat":
            return self.target_temperature_heat
        else:
            return self.target_temperature_cold

    @property
    def target_temperature_heat(self):
        """ Return device target temperature in heat mode """
        return self._data.get("heat_consign")

    @property
    def target_temperature_cold(self):
        """ Return device target temperature in cold mode """
        return self._data.get("cold_consign")

    @property
    def min_temperature(self):
        """ Return device minimal temperature """
        if self.heat_cold_mode == "heat":
            return self.min_temperature_heat
        else:
            return self.min_temperature_cold

    @property
    def min_temperature_heat(self):
        """ Return device min temperature limit in heat mode """
        if self._data.get("min_limit_heat") is not None:
            return float(self._data.get("min_limit_heat"))
        return None

    @property
    def min_temperature_cold(self):
        """ Return device min temperature limit in cold mode """
        if self._data.get("min_limit_cold") is not None:
            return float(self._data.get("min_limit_cold"))
        return None

    @property
    def max_temperature(self):
        """ Return device maximal temperature """
        if self.heat_cold_mode == "heat":
            return self.max_temperature_heat
        else:
            return self.max_temperature_cold

    @property
    def max_temperature_heat(self):
        """ Return device max temperature limit in heat mode """
        if self._data.get("max_limit_heat") is not None:
            return float(self._data.get("max_limit_heat"))
        return None

    @property
    def max_temperature_cold(self):
        """ Return device max temperature limit in cold mode """
        if self._data.get("max_limit_cold") is not None:
            return float(self._data.get("max_limit_cold"))
        return None

    @property
    def firmware(self):
        """ Return webserver firmware """
        return self._data.get("firmware")

    @property
    def brand(self):
        """ Return webserver brand """
        return self._data.get("brand")

    #
    # setters
    #

    def turn_on(self):
        """ Turn device on """
        _LOGGER.info("call turn_on() on {}".format(self.str_complete))
        self._send_event("P1", 1)
        self._data["power"] = "1"
        return True

    def turn_off(self):
        """ Turn device off """
        _LOGGER.info("call turn_off() on {}".format(self.str_complete))
        self._send_event("P1", 0)
        self._data["power"] = "0"
        return True

    def set_mode(self, mode_name):
        """ Set mode of the device """
        _LOGGER.info("call set_mode({}) on {}".format(mode_name, self.str_complete))
        mode_id_found = None
        for mode_id, mode in MODES_CONVERTER.items():
            if mode["name"] == mode_name:
                mode_id_found = mode_id
                break
        if mode_id_found is None:
            raise ValueError('mode name "{}" not found'.format(mode_name))

        # send event
        self._send_event("P2", mode_id_found)

        # update mode
        self._data["mode"] = mode_id_found

        return True

    def set_temperature(self, temperature):
        """ Set target_temperature for current heat/cold mode on this device """
        _LOGGER.info(
            "call set_temperature({}) on {}".format(temperature, self.str_complete)
        )
        temperature = float(temperature)
        if self.min_temperature is not None and temperature < self.min_temperature:
            temperature = self.min_temperature
        if self.max_temperature is not None and temperature > self.max_temperature:
            temperature = self.max_temperature

        if self.heat_cold_mode == "heat":
            self._send_event("P8", temperature)
            self._data["heat_consign"] = str(temperature)
        else:
            self._send_event("P7", temperature)
            self._data["cold_consign"] = str(temperature)
        return True

    #
    # parent installation
    #

    @property
    def installation(self):
        """ Get parent installation """
        return self._installation

    #
    # Refresh
    #

    def ask_airzone_update(self):
        """
        Ask an update to the airzone hardware (airzone cloud don't autopull data like current temperature)
        The update should be available in airzone cloud after 3 to 5 secs in average
        """
        self._send_event("", "")

    def refresh(self):
        """ Refresh current device data (call refresh_devices on parent AirzoneCloudDaikin) """

        # ask airzone to update its data in airzone cloud (there is some delay so current update will be available on next refresh)
        self.ask_airzone_update()

        # refresh all devices (including current) from parent installation
        self.installation.refresh_devices()

    #
    # private
    #

    def _send_event(self, option, value):
        """ Send an event for current device """
        payload = {
            "event": {
                "cgi": "modmaquina",
                "device_id": self.id,
                "option": option,
                "value": value,
            }
        }
        return self._api._send_event(payload)

    def _set_data_refreshed(self, data):
        """ Set data refreshed (call by parent AirzoneCloudDaikin on refresh_devices()) """
        self._data = data
        _LOGGER.info("Data refreshed for {}".format(self.str_complete))


#
# device raw data example
#

# {
#     "id": "...",
#     "mac": "AA:BB:CC:DD:EE:FF",
#     "pin": "1234",
#     "name": "Dknwserver",
#     "status": "activated",
#     "mode": "1",
#     "state": null,
#     "power": "0",
#     "units": "0",
#     "availables_speeds": "2",
#     "local_temp": "26.0",
#     "ver_state_slats": "0",
#     "ver_position_slats": "0",
#     "hor_state_slats": "0",
#     "hor_position_slats": "0",
#     "max_limit_cold": "32.0",
#     "min_limit_cold": "16.0",
#     "max_limit_heat": "32.0",
#     "min_limit_heat": "16.0",
#     "update_date": null,
#     "progs_enabled": false,
#     "scenary": "sleep",
#     "sleep_time": 60,
#     "min_temp_unoccupied": "16",
#     "max_temp_unoccupied": "32",
#     "connection_date": "2020-05-23T05:37:22.000+00:00",
#     "last_event_id": "...",
#     "firmware": "1.1.1",
#     "brand": "Daikin",
#     "cold_consign": "26.0",
#     "heat_consign": "24.0",
#     "cold_speed": "2",
#     "heat_speed": "2",
#     "machine_errors": null,
#     "ver_cold_slats": "0001",
#     "ver_heat_slats": "0000",
#     "hor_cold_slats": "0000",
#     "hor_heat_slats": "0000",
#     "modes": "11101000",
#     "installation_id": "...",
#     "time_zone": "Europe/Madrid",
#     "spot_name": "Madrid",
#     "complete_name": "Madrid,Madrid,Community of Madrid,Spain",
#     "location": {"latitude": 10.4155754, "longitude": -2.4037901998979576},
# }
