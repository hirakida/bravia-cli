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
    params: dict | None
    version: str


class Operation(enum.Enum):
    # guide
    GET_SUPPORTED_API_INFO = auto()
    # audio
    GET_VOLUME_INFO = auto()
    SET_AUDIO_VOLUME = auto()
    SET_AUDIO_MUTE = auto()
    GET_SPEAKER_SETTINGS = auto()
    # encryption
    GET_PUBLIC_KEY = auto()
    # system
    GET_LED_INDICATOR_STATUS = auto()
    SET_LED_INDICATOR_STATUS = auto()
    GET_POWER_STATUS = auto()
    SET_POWER_STATUS = auto()
    GET_POWER_SAVING_MODE = auto()
    SET_POWER_SAVING_MODE = auto()
    GET_REMOTE_CONTROLLER_INFO = auto()
    GET_SYSTEM_SUPPORTED_FUNCTION = auto()
    GET_WOL_MODE = auto()
    SET_WOL_MODE = auto()
    GET_CURRENT_TIME = auto()
    GET_NETWORK_SETTINGS = auto()
    GET_INTERFACE_INFO = auto()
    GET_REMOTE_DEVICE_SETTINGS = auto()
    GET_SYSTEM_INFO = auto()
    REQUEST_REBOOT = auto()
    # video
    GET_PICTURE_QUALITY_SETTINGS = auto()
    # videoScreen
    GET_SCENE_SETTING = auto()
    SET_SCENE_SETTING = auto()


properties_map = {
    # guide
    Operation.GET_SUPPORTED_API_INFO: Properties("guide", "getSupportedApiInfo", 5, {"services": None}, "1.0"),
    # audio
    Operation.GET_VOLUME_INFO: Properties("audio", "getVolumeInformation", 33, None, "1.0"),
    Operation.SET_AUDIO_VOLUME: Properties("audio", "setAudioVolume", 601, {}, "1.2"),
    Operation.SET_AUDIO_MUTE: Properties("audio", "setAudioMute", 601, {}, "1.0"),
    Operation.GET_SPEAKER_SETTINGS: Properties("audio", "getSpeakerSettings", 67, {"target": ""}, "1.0"),
    # encryption
    Operation.GET_PUBLIC_KEY: Properties("encryption", "getPublicKey", 1, None, "1.0"),
    # system
    Operation.GET_LED_INDICATOR_STATUS: Properties("system", "getLEDIndicatorStatus", 45, None, "1.0"),
    Operation.SET_LED_INDICATOR_STATUS: Properties("system", "setLEDIndicatorStatus", 53, {}, "1.1"),
    Operation.GET_POWER_STATUS: Properties("system", "getPowerStatus", 50, None, "1.0"),
    Operation.SET_POWER_STATUS: Properties("system", "setPowerStatus", 55, {}, "1.0"),
    Operation.GET_POWER_SAVING_MODE: Properties("system", "getPowerSavingMode", 51, None, "1.0"),
    Operation.SET_POWER_SAVING_MODE: Properties("system", "setPowerSavingMode", 52, None, "1.0"),
    Operation.GET_REMOTE_CONTROLLER_INFO: Properties("system", "getRemoteControllerInfo", 54, None, "1.0"),
    Operation.GET_SYSTEM_SUPPORTED_FUNCTION: Properties("system", "getSystemSupportedFunction", 55, None, "1.0"),
    Operation.GET_WOL_MODE: Properties("system", "getWolMode", 50, None, "1.0"),
    Operation.SET_WOL_MODE: Properties("system", "setWolMode", 55, {}, "1.0"),
    Operation.GET_CURRENT_TIME: Properties("system", "getCurrentTime", 51, None, "1.1"),
    Operation.GET_NETWORK_SETTINGS: Properties("system", "getNetworkSettings", 2, {"netif": ""}, "1.0"),
    Operation.GET_INTERFACE_INFO: Properties("system", "getInterfaceInformation", 33, None, "1.0"),
    Operation.GET_REMOTE_DEVICE_SETTINGS: Properties("system", "getRemoteDeviceSettings", 44, {"target": ""}, "1.0"),
    Operation.GET_SYSTEM_INFO: Properties("system", "getSystemInformation", 33, None, "1.0"),
    Operation.REQUEST_REBOOT: Properties("system", "requestReboot", 10, None, "1.0"),
    # video
    Operation.GET_PICTURE_QUALITY_SETTINGS: Properties("video", "getPictureQualitySettings", 52, {"target": ""}, "1.0"),
    # videoScreen
    Operation.GET_SCENE_SETTING: Properties("videoScreen", "getSceneSetting", 79, None, "1.0"),
    Operation.SET_SCENE_SETTING: Properties("videoScreen", "setSceneSetting", 40, None, "1.0")
}


def call_api(operation: Operation, params: dict | None = None) -> dict:
    ip = os.environ["BRAVIA_IP"]
    psk = os.environ["BRAVIA_PSK"]
    properties = properties_map[operation]
    request_params = properties.params if params is None else params

    url = urllib.parse.urlunsplit(("http", ip, f"/sony/{properties.path}", None, None))
    data = {
        "method": properties.method,
        "id": properties.id,
        "params": [] if request_params is None else [request_params],
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
                                # guide
                                "api",
                                "api-info",
                                "supported-api-info",
                                # audio
                                "volume",
                                "volume-information",
                                "speaker",
                                "speaker-settings",
                                # encryption
                                "public-key",
                                # system
                                "led",
                                "led-indicator",
                                "led-indicator-status",
                                "power",
                                "power-status",
                                "power-saving",
                                "power-saving-mode",
                                "remote-controller",
                                "remote-controller-info",
                                "system-supported-function",
                                "supported-function",
                                "wol",
                                "wol-mode",
                                "current-time",
                                "network",
                                "network-settings",
                                "interface",
                                "interface-information",
                                "remote-device",
                                "remote-device-settings",
                                "system",
                                "system-information",
                                # video
                                "picture-quality",
                                "picture-quality-settings",
                                # videoScreen
                                "scene",
                                "scene-setting",
                            ])

    set_parser = subparsers.add_parser("set")
    set_subparsers = set_parser.add_subparsers(dest="resource", required=True)
    # audio
    volume_parser = set_subparsers.add_parser("volume", aliases=["audio-volume"])
    volume_parser.add_argument("value", choices=["up", "down"])
    mute_parser = set_subparsers.add_parser("mute", aliases=["audio-mute"])
    mute_parser.add_argument("value", choices=["on", "off"])
    # system
    led_parser = set_subparsers.add_parser(
        "led",
        aliases=["led-indicator", "led-indicator-status"],
    )
    led_parser.add_argument(
        "mode",
        choices=["Demo", "AutoBrightnessAdjust", "Dark", "SimpleResponse", "Off"],
    )
    power_parser = set_subparsers.add_parser("power", aliases=["power-status"])
    power_parser.add_argument("value", choices=["on", "off"])
    power_saving_parser = set_subparsers.add_parser(
        "power-saving",
        aliases=["power-saving-mode"],
    )
    power_saving_parser.add_argument(
        "mode",
        choices=["off", "low", "high", "pictureOff"],
    )
    wol_parser = set_subparsers.add_parser("wol", aliases=["wol-mode"])
    wol_parser.add_argument("value", choices=["on", "off"])
    # videoScreen
    scene_parser = set_subparsers.add_parser(
        "scene",
        aliases=["scene-setting"],
    )
    scene_parser.add_argument(
        "value",
        choices=["auto", "auto24pSync", "general"],
    )

    request_parser = subparsers.add_parser("request")
    request_parser.add_argument("action", choices=["reboot"])

    args = parser.parse_args()
    match args.command:
        case "get":
            content = {}
            match args.resource:
                # guide
                case "api" | "api-info" | "supported-api-info":
                    content = call_api(Operation.GET_SUPPORTED_API_INFO)
                # audio
                case "volume" | "volume-information":
                    content = call_api(Operation.GET_VOLUME_INFO)
                case "speaker" | "speaker-settings":
                    content = call_api(Operation.GET_SPEAKER_SETTINGS)
                # encryption
                case "public-key":
                    content = call_api(Operation.GET_PUBLIC_KEY)
                # system
                case "led" | "led-indicator-status":
                    content = call_api(Operation.GET_LED_INDICATOR_STATUS)
                case "power" | "power-status":
                    content = call_api(Operation.GET_POWER_STATUS)
                case "power-saving" | "power-saving-mode":
                    content = call_api(Operation.GET_POWER_SAVING_MODE)
                case "remote-controller" | "remote-controller-info":
                    content = call_api(Operation.GET_REMOTE_CONTROLLER_INFO)
                case "system-supported-function" | "supported-function":
                    content = call_api(Operation.GET_SYSTEM_SUPPORTED_FUNCTION)
                case "wol" | "wol-mode":
                    content = call_api(Operation.GET_WOL_MODE)
                case "current-time":
                    content = call_api(Operation.GET_CURRENT_TIME)
                case "network" | "network-settings":
                    content = call_api(Operation.GET_NETWORK_SETTINGS)
                case "interface" | "interface-information":
                    content = call_api(Operation.GET_INTERFACE_INFO)
                case "remote-device" | "remote-device-settings":
                    content = call_api(Operation.GET_REMOTE_DEVICE_SETTINGS)
                case "system" | "system-information":
                    content = call_api(Operation.GET_SYSTEM_INFO)
                # video
                case "picture-quality" | "picture-quality-settings":
                    content = call_api(Operation.GET_PICTURE_QUALITY_SETTINGS)
                # videoScreen
                case "scene" | "scene-setting":
                    content = call_api(Operation.GET_SCENE_SETTING)
            print(json.dumps(content, indent=2))
        case "set":
            match args.resource:
                # audio
                case "volume" | "audio-volume":
                    match args.value:
                        case "up":
                            call_api(Operation.SET_AUDIO_VOLUME, {"volume": "+1", "target": "speaker"})
                        case "down":
                            call_api(Operation.SET_AUDIO_VOLUME, {"volume": "-1", "target": "speaker"})
                case "mute" | "audio-mute":
                    match args.value:
                        case "on":
                            call_api(Operation.SET_AUDIO_MUTE, {"status": True})
                        case "off":
                            call_api(Operation.SET_AUDIO_MUTE, {"status": False})
                # system
                case "led" | "led-indicator-status":
                    call_api(Operation.SET_LED_INDICATOR_STATUS, {"mode": args.mode})
                case "power" | "power-status":
                    match args.value:
                        case "on":
                            call_api(Operation.SET_POWER_STATUS, {"status": True})
                        case "off":
                            call_api(Operation.SET_POWER_STATUS, {"status": False})
                case "power-saving" | "power-saving-mode":
                    call_api(Operation.SET_POWER_SAVING_MODE, {"mode": args.mode})
                case "wol" | "wol-mode":
                    match args.value:
                        case "on":
                            call_api(Operation.SET_WOL_MODE, {"enabled": True})
                        case "off":
                            call_api(Operation.SET_WOL_MODE, {"enabled": False})
                # videoScreen
                case "scene" | "scene-setting":
                    call_api(Operation.SET_SCENE_SETTING, {"value": args.value})
        case "request":
            match args.action:
                case "reboot":
                    call_api(Operation.REQUEST_REBOOT)


if __name__ == "__main__":
    main()
