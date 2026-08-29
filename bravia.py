#!/usr/bin/env python3

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import enum
from dataclasses import dataclass
from enum import auto


@dataclass
class Properties:
    path: str
    method: str
    id: int
    params: dict
    version: str


class Command(enum.Enum):
    SHOW_POWER = "show-power"
    POWER_ON = "power-on"
    POWER_OFF = "power-off"
    SHOW_VOLUME = "show-volume"
    TURN_UP = "turn-up"
    TURN_DOWN = "turn-down"
    MUTE = "mute"
    UNMUTE = "unmute"


class Operation(enum.Enum):
    GET_POWER_STATUS = auto()
    SET_POWER_STATUS_ON = auto()
    SET_POWER_STATUS_OFF = auto()
    GET_VOLUME = auto()
    SET_VOLUME_UP = auto()
    SET_VOLUME_DOWN = auto()
    SET_MUTE_ON = auto()
    SET_MUTE_OFF = auto()


properties_map = {
    Operation.GET_POWER_STATUS: Properties("system", "getPowerStatus", 50, {}, "1.0"),
    Operation.SET_POWER_STATUS_ON: Properties("system", "setPowerStatus", 55, {"status": True}, "1.0"),
    Operation.SET_POWER_STATUS_OFF: Properties("system", "setPowerStatus", 55, {"status": False}, "1.0"),
    Operation.GET_VOLUME: Properties("audio", "getVolumeInformation", 33, {}, "1.0"),
    Operation.SET_VOLUME_UP: Properties("audio", "setAudioVolume", 601, {"volume": "+1", "target": "speaker"}, "1.2"),
    Operation.SET_VOLUME_DOWN: Properties("audio", "setAudioVolume", 601, {"volume": "-1", "target": "speaker"}, "1.2"),
    Operation.SET_MUTE_ON: Properties("audio", "setAudioMute", 601, {"status": True}, "1.0"),
    Operation.SET_MUTE_OFF: Properties("audio", "setAudioMute", 601, {"status": False}, "1.0")
}


def call_api(operation: Operation, params: dict | None = None) -> dict:
    ip = os.environ["BRAVIA_IP"]
    psk = os.environ["BRAVIA_PSK"]
    properties = properties_map[operation]

    url = urllib.parse.urlunsplit(("http", ip, f"/sony/{properties.path}", None, None))
    data = {
        "method": properties.method,
        "id": properties.id,
        "params": [params or properties.params],
        "version": properties.version,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "X-Auth-PSK": psk,
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(request) as response:
            content = json.loads(response.read())
            if "error" in content:
                print(f"error: {content['error']}.")
            return content
    except urllib.error.URLError as e:
        print(f"Failed to call {url}. {e}")
        sys.exit(1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command",
                   choices=[
                       Command.SHOW_POWER.value,
                       Command.POWER_ON.value,
                       Command.POWER_OFF.value,
                       Command.SHOW_VOLUME.value,
                       Command.TURN_UP.value,
                       Command.TURN_DOWN.value,
                       Command.MUTE.value,
                       Command.UNMUTE.value,
                   ])
    args = p.parse_args()

    match Command(args.command):
        case Command.SHOW_POWER:
            content = call_api(Operation.GET_POWER_STATUS)
            print(content)
        case Command.POWER_ON:
            call_api(Operation.SET_POWER_STATUS_ON)
        case Command.POWER_OFF:
            call_api(Operation.SET_POWER_STATUS_OFF)
        case Command.SHOW_VOLUME:
            content = call_api(Operation.GET_VOLUME)
            print(content)
        case Command.TURN_UP:
            call_api(Operation.SET_VOLUME_UP)
        case Command.TURN_DOWN:
            call_api(Operation.SET_VOLUME_DOWN)
        case Command.MUTE:
            call_api(Operation.SET_MUTE_ON)
        case Command.UNMUTE:
            call_api(Operation.SET_MUTE_OFF)


if __name__ == "__main__":
    main()
