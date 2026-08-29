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
    SET_VOLUME = auto()
    SET_MUTE_ON = auto()
    SET_MUTE_OFF = auto()


class VolumeOperation(enum.Enum):
    INCREMENT = auto()
    DECREMENT = auto()


properties_map = {
    Operation.GET_POWER_STATUS: Properties("system", "getPowerStatus", 50, {}),
    Operation.SET_POWER_STATUS_ON: Properties("system", "setPowerStatus", 55, {"status": True}),
    Operation.SET_POWER_STATUS_OFF: Properties("system", "setPowerStatus", 55, {"status": False}),
    Operation.GET_VOLUME: Properties("audio", "getVolumeInformation", 33, {}),
    Operation.SET_VOLUME: Properties("audio", "setAudioVolume", 601, {}),
    Operation.SET_MUTE_ON: Properties("audio", "setAudioMute", 601, {"status": True}),
    Operation.SET_MUTE_OFF: Properties("audio", "setAudioMute", 601, {"status": False})
}


def call_api(operation: Operation) -> dict:
    ip = os.environ["BRAVIA_IP"]
    psk = os.environ["BRAVIA_PSK"]
    properties = properties_map[operation]

    url = urllib.parse.urlunsplit(("http", ip, f"/sony/{properties.path}", None, None))
    data = {
        "method": properties.method,
        "id": properties.id,
        "params": [properties.params],
        "version": "1.0"
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


def set_volume(operation: VolumeOperation):
    target = "speaker"
    content = call_api(Operation.GET_VOLUME)
    if content:
        for result in content["result"][0]:
            if result["target"] == target:
                volume = result["volume"]
                if operation == VolumeOperation.INCREMENT:
                    volume += 1
                elif operation == VolumeOperation.DECREMENT:
                    volume -= 1
                properties_map[Operation.SET_VOLUME].params = {"volume": str(volume), "target": target}
                call_api(Operation.SET_VOLUME)
                break


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
            set_volume(VolumeOperation.INCREMENT)
        case Command.TURN_DOWN:
            set_volume(VolumeOperation.DECREMENT)
        case Command.MUTE:
            call_api(Operation.SET_MUTE_ON)
        case Command.UNMUTE:
            call_api(Operation.SET_MUTE_OFF)


if __name__ == "__main__":
    main()
