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


class Operation(enum.Enum):
    GET_POWER_STATUS = auto()
    SET_POWER_STATUS_ON = auto()
    SET_POWER_STATUS_OFF = auto()
    GET_WOL_MODE = auto()
    SET_WOL_MODE_ON = auto()
    SET_WOL_MODE_OFF = auto()
    GET_CURRENT_TIME = auto()
    GET_VOLUME = auto()
    SET_VOLUME_UP = auto()
    SET_VOLUME_DOWN = auto()
    SET_MUTE_ON = auto()
    SET_MUTE_OFF = auto()


properties_map = {
    Operation.GET_POWER_STATUS: Properties("system", "getPowerStatus", 50, {}, "1.0"),
    Operation.SET_POWER_STATUS_ON: Properties("system", "setPowerStatus", 55, {"status": True}, "1.0"),
    Operation.SET_POWER_STATUS_OFF: Properties("system", "setPowerStatus", 55, {"status": False}, "1.0"),
    Operation.GET_WOL_MODE: Properties("system", "getWolMode", 50, {}, "1.0"),
    Operation.SET_WOL_MODE_ON: Properties("system", "setWolMode", 55, {"enabled": True}, "1.0"),
    Operation.SET_WOL_MODE_OFF: Properties("system", "setWolMode", 55, {"enabled": False}, "1.0"),
    Operation.GET_CURRENT_TIME: Properties("system", "getCurrentTime", 51, {}, "1.1"),
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
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("resource",
                            choices=[
                                "power-status",
                                "wol-mode",
                                "current-time",
                                "volume",
                            ])

    set_parser = subparsers.add_parser("set")
    set_subparsers = set_parser.add_subparsers(dest="resource", required=True)
    power_parser = set_subparsers.add_parser("power")
    power_parser.add_argument("value", choices=["on", "off"])
    wol_parser = set_subparsers.add_parser("wol")
    wol_parser.add_argument("value", choices=["on", "off"])
    volume_parser = set_subparsers.add_parser("volume")
    volume_parser.add_argument("value", choices=["up", "down"])
    mute_parser = set_subparsers.add_parser("mute")
    mute_parser.add_argument("value", choices=["on", "off"])
    args = parser.parse_args()

    match args.command:
        case "get":
            content = {}
            match args.resource:
                case "power-status":
                    content = call_api(Operation.GET_POWER_STATUS)
                case "wol-mode":
                    content = call_api(Operation.GET_WOL_MODE)
                case "current-time":
                    content = call_api(Operation.GET_CURRENT_TIME)
                case "volume":
                    content = call_api(Operation.GET_VOLUME)
            print(content)
        case "set":
            match args.resource:
                case "power":
                    match args.value:
                        case "on":
                            call_api(Operation.SET_POWER_STATUS_ON)
                        case "off":
                            call_api(Operation.SET_POWER_STATUS_OFF)
                case "wol":
                    match args.value:
                        case "on":
                            call_api(Operation.SET_WOL_MODE_ON)
                        case "off":
                            call_api(Operation.SET_WOL_MODE_OFF)
                case "volume":
                    match args.value:
                        case "up":
                            call_api(Operation.SET_VOLUME_UP)
                        case "down":
                            call_api(Operation.SET_VOLUME_DOWN)
                case "mute":
                    match args.value:
                        case "on":
                            call_api(Operation.SET_MUTE_ON)
                        case "off":
                            call_api(Operation.SET_MUTE_OFF)


if __name__ == "__main__":
    main()
