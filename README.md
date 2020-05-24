# Airzone Cloud Daikin

- [Airzone Cloud Daikin](#airzone-cloud-daikin)
  - [Presentation](#presentation)
    - [Abstract](#abstract)
    - [Module classes](#module-classes)
  - [Usage](#usage)
    - [Install](#install)
    - [Start API](#start-api)
    - [Get installations](#get-installations)
    - [Get devices from installations](#get-devices-from-installations)
    - [Get all devices shortcut](#get-all-devices-shortcut)
    - [Control a device](#control-a-device)
    - [HVAC mode](#hvac-mode)
      - [Available modes](#available-modes)
      - [Set HVAC mode on a system (and its sub-zones)](#set-hvac-mode-on-a-system-and-its-sub-zones)
  - [API doc](#api-doc)
    - [Constructor](#constructor)

## Presentation

### Abstract

Allow to communicate easily with Daikin Airzone Cloud to retrieve information or to send commands (on/off, temperature, HVAC mode, ...)

This API is specific to Daikin implementation (try to connect to [dkn.airzonecloud.com](https://dkn.airzonecloud.com) to be sure).

If you are looking for the main Airzone Cloud API (try to connect to [www.airzonecloud.com](https://www.airzonecloud.com)), you should use this package : [AirzoneCloud](https://github.com/max13fr/AirzoneCloud)

### Module classes

- **AirzoneCloudDaikin** : represent your Daikin AirzoneCloud account. Contains a list of your **installations** :
  - **Installation**: represent one of your installation (like your home, an office, ...). Contains a list of its **devices** :
    - **Device** : represent your climate equipement to control

## Usage

### Install

```bash
pip3 install AirzoneCloudDaikin
```

### Start API

```python
from AirzoneCloudDaikin import AirzoneCloudDaikin
api = AirzoneCloudDaikin("email@domain.com", "password")
```

### Get installations

```python
for installation in api.installations:
    print(
        "Installation(name={}, type={}, scenary={}, id={})".format(
            installation.name, installation.type, installation.scenary, installation.id
        )
    )
```

Output :

<pre>
Installation(name=My home, type=home, scenary=occupied, id=5d592c14646b6d798ccc2aaa)
</pre>

### Get devices from installations

```python
for installation in api.installations:
    for device in installation.devices:
        print(
            "Device(name={}, is_on={}, mode={}, current_temp={}, target_temp={}, id={}, mac={})".format(
                device.name,
                device.is_on,
                device.mode,
                device.current_temperature,
                device.target_temperature,
                device.id,
                device.mac,
            )
        )
```

Output :

<pre>
Device(name=Dknwserver, is_on=False, mode=cool, current_temp=25.0, target_temp=26.0, id=5ab1875a651241708814575681, mac=AA:BB:CC:DD:EE:FF)
</pre>

### Get all devices shortcut

```python
for device in api.all_devices:
    print(
        "Device(name={}, is_on={}, mode={}, current_temp={}, target_temp={}, id={}, mac={})".format(
            device.name,
            device.is_on,
            device.mode,
            device.current_temperature,
            device.target_temperature,
            device.id,
            device.mac,
        )
    )
```

Output :

<pre>
Device(name=Dknwserver, is_on=False, mode=cool, current_temp=25.0, target_temp=26.0, id=5ab1875a651241708814575681, mac=AA:BB:CC:DD:EE:FF)
</pre>

### Control a device

```python
device = api.all_devices[0]
print(device)

# start device
device.turn_on()

# set temperature
device.set_temperature(26)

print(device)

# stopping device
device.turn_off()

print(device)
```

Output :

<pre>
Device(name=Dknwserver, is_on=False, mode=cool, current_temp=25.0, target_temp=30.0)
Device(name=Dknwserver, is_on=True, mode=cool, current_temp=25.0, target_temp=26.0)
Device(name=Dknwserver, is_on=False, mode=cool, current_temp=25.0, target_temp=26.0)
</pre>

### HVAC mode

#### Available modes

- **cool** : Cooling mode
- **heat** : Heating mode
- **ventilate** : Ventilation
- **dehumidify** : Dry
- **heat-cold-auto** : Auto heat/cold mode

#### Set HVAC mode on a system (and its sub-zones)

```python
device = api.all_devices[0]
print(device)

# set mode to heat
device.set_mode("heat")

print(device)
```

Output :

<pre>
Device(name=Dknwserver, is_on=False, mode=cool, current_temp=25.0, target_temp=26.0)
Device(name=Dknwserver, is_on=False, mode=heat, current_temp=25.0, target_temp=23.0)
</pre>

> :warning: Daikin climate equipment has 2 consigns : one for heat & one of cold.
> Its visible in the previous example, the target temperature has change from 26 to 23 just by changing the mode from cool to heat.
> So don't forget to do your set_temperature() AFTER the set_mode() and not before

## API doc

[API full doc](API.md)

### Constructor

```python
AirzoneCloudDaikin(username, password, user_agent=None, base_url=None)
```

- **username** : you're username used to connect on Daikin Airzone Cloud website or app
- **password** : you're password used to connect on Daikin Airzone Cloud website or app
- **user_agent** : allow to change default user agent if set
- **base_url** : allow to change base url of the Daikin Airzone Cloud API if set
  - default value : _https://dkn.airzonecloud.com_
