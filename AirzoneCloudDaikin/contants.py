API_LOGIN = "/users/sign_in"
API_INSTALLATION_RELATIONS = "/installation_relations"
API_DEVICES = "/devices"
API_EVENTS = "/events"

# 2020-05-23: extracted from website and saved copy in reverse/application.js

MODES_CONVERTER = {
    "1": {"name": "cool", "type": "cold", "description": "Cooling mode"},
    "2": {"name": "heat", "type": "heat", "description": "Heating mode"},
    "3": {
        "name": "ventilate",
        "type": "cold",
        "description": "Ventilation in cold mode",
    },
    "4": {"name": "heat-cold-auto", "type": "cold", "description": "Auto mode"},
    "5": {"name": "dehumidify", "type": "cold", "description": "Dry mode"},
    "6": {"name": "cool-air", "type": "cold", "description": "Automatic cooling"},
    "7": {"name": "heat-air", "type": "heat", "description": "Automatic heating"},
    "8": {
        "name": "ventilate",
        "type": "heat",
        "description": "Ventilation in heating mode",
    },
}
