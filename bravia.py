#!/usr/bin/env python3

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import enum
from dataclasses import dataclass
from enum import auto


@dataclass(frozen=True)
class ApiSpec:
    path: str
    method: str
    request_id: int
    params: dict[str, object] | None
    version: str


class Operation(enum.Enum):
    # guide
    GET_SUPPORTED_API_INFO = auto()
    # appControl
    GET_APPLICATION_LIST = auto()
    GET_WEB_APP_STATUS = auto()
    GET_APPLICATION_STATUS_LIST = auto()
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


API_SPECS = {
    # guide
    Operation.GET_SUPPORTED_API_INFO: ApiSpec("guide", "getSupportedApiInfo", 5, {"services": None}, "1.0"),
    # appControl
    Operation.GET_APPLICATION_LIST: ApiSpec("appControl", "getApplicationList", 60, None, "1.0"),
    Operation.GET_WEB_APP_STATUS: ApiSpec("appControl", "getWebAppStatus", 1, None, "1.0"),
    Operation.GET_APPLICATION_STATUS_LIST: ApiSpec("appControl", "getApplicationStatusList", 55, None, "1.0"),
    # audio
    Operation.GET_VOLUME_INFO: ApiSpec("audio", "getVolumeInformation", 33, None, "1.0"),
    Operation.SET_AUDIO_VOLUME: ApiSpec("audio", "setAudioVolume", 601, {}, "1.2"),
    Operation.SET_AUDIO_MUTE: ApiSpec("audio", "setAudioMute", 601, {}, "1.0"),
    Operation.GET_SPEAKER_SETTINGS: ApiSpec("audio", "getSpeakerSettings", 67, {"target": ""}, "1.0"),
    # encryption
    Operation.GET_PUBLIC_KEY: ApiSpec("encryption", "getPublicKey", 1, None, "1.0"),
    # system
    Operation.GET_LED_INDICATOR_STATUS: ApiSpec("system", "getLEDIndicatorStatus", 45, None, "1.0"),
    Operation.SET_LED_INDICATOR_STATUS: ApiSpec("system", "setLEDIndicatorStatus", 53, {}, "1.1"),
    Operation.GET_POWER_STATUS: ApiSpec("system", "getPowerStatus", 50, None, "1.0"),
    Operation.SET_POWER_STATUS: ApiSpec("system", "setPowerStatus", 55, {}, "1.0"),
    Operation.GET_POWER_SAVING_MODE: ApiSpec("system", "getPowerSavingMode", 51, None, "1.0"),
    Operation.SET_POWER_SAVING_MODE: ApiSpec("system", "setPowerSavingMode", 52, None, "1.0"),
    Operation.GET_REMOTE_CONTROLLER_INFO: ApiSpec("system", "getRemoteControllerInfo", 54, None, "1.0"),
    Operation.GET_SYSTEM_SUPPORTED_FUNCTION: ApiSpec("system", "getSystemSupportedFunction", 55, None, "1.0"),
    Operation.GET_WOL_MODE: ApiSpec("system", "getWolMode", 50, None, "1.0"),
    Operation.SET_WOL_MODE: ApiSpec("system", "setWolMode", 55, {}, "1.0"),
    Operation.GET_CURRENT_TIME: ApiSpec("system", "getCurrentTime", 51, None, "1.1"),
    Operation.GET_NETWORK_SETTINGS: ApiSpec("system", "getNetworkSettings", 2, {"netif": ""}, "1.0"),
    Operation.GET_INTERFACE_INFO: ApiSpec("system", "getInterfaceInformation", 33, None, "1.0"),
    Operation.GET_REMOTE_DEVICE_SETTINGS: ApiSpec("system", "getRemoteDeviceSettings", 44, {"target": ""}, "1.0"),
    Operation.GET_SYSTEM_INFO: ApiSpec("system", "getSystemInformation", 33, None, "1.0"),
    Operation.REQUEST_REBOOT: ApiSpec("system", "requestReboot", 10, None, "1.0"),
    # video
    Operation.GET_PICTURE_QUALITY_SETTINGS: ApiSpec("video", "getPictureQualitySettings", 52, {"target": ""}, "1.0"),
    # videoScreen
    Operation.GET_SCENE_SETTING: ApiSpec("videoScreen", "getSceneSetting", 79, None, "1.0"),
    Operation.SET_SCENE_SETTING: ApiSpec("videoScreen", "setSceneSetting", 40, None, "1.0")
}

GET_OPERATIONS = {
    "api": Operation.GET_SUPPORTED_API_INFO,
    "supported-api-info": Operation.GET_SUPPORTED_API_INFO,
    "application-list": Operation.GET_APPLICATION_LIST,
    "web-app-status": Operation.GET_WEB_APP_STATUS,
    "application-status-list": Operation.GET_APPLICATION_STATUS_LIST,
    "volume": Operation.GET_VOLUME_INFO,
    "volume-information": Operation.GET_VOLUME_INFO,
    "speaker": Operation.GET_SPEAKER_SETTINGS,
    "speaker-settings": Operation.GET_SPEAKER_SETTINGS,
    "public-key": Operation.GET_PUBLIC_KEY,
    "led": Operation.GET_LED_INDICATOR_STATUS,
    "led-indicator-status": Operation.GET_LED_INDICATOR_STATUS,
    "power": Operation.GET_POWER_STATUS,
    "power-status": Operation.GET_POWER_STATUS,
    "power-saving": Operation.GET_POWER_SAVING_MODE,
    "power-saving-mode": Operation.GET_POWER_SAVING_MODE,
    "remote-controller": Operation.GET_REMOTE_CONTROLLER_INFO,
    "remote-controller-info": Operation.GET_REMOTE_CONTROLLER_INFO,
    "system-supported-function": Operation.GET_SYSTEM_SUPPORTED_FUNCTION,
    "supported-function": Operation.GET_SYSTEM_SUPPORTED_FUNCTION,
    "wol": Operation.GET_WOL_MODE,
    "wol-mode": Operation.GET_WOL_MODE,
    "current-time": Operation.GET_CURRENT_TIME,
    "network": Operation.GET_NETWORK_SETTINGS,
    "network-settings": Operation.GET_NETWORK_SETTINGS,
    "interface": Operation.GET_INTERFACE_INFO,
    "interface-information": Operation.GET_INTERFACE_INFO,
    "remote-device": Operation.GET_REMOTE_DEVICE_SETTINGS,
    "remote-device-settings": Operation.GET_REMOTE_DEVICE_SETTINGS,
    "system": Operation.GET_SYSTEM_INFO,
    "system-information": Operation.GET_SYSTEM_INFO,
    "picture-quality": Operation.GET_PICTURE_QUALITY_SETTINGS,
    "picture-quality-settings": Operation.GET_PICTURE_QUALITY_SETTINGS,
    "scene": Operation.GET_SCENE_SETTING,
    "scene-setting": Operation.GET_SCENE_SETTING,
}


def call_api(operation: Operation, params: dict[str, object] | None = None) -> dict:
    ip = os.getenv("BRAVIA_IP")
    psk = os.getenv("BRAVIA_PSK")
    if not ip or not psk:
        raise SystemExit("Both BRAVIA_IP and BRAVIA_PSK must be set as environment variables.")

    spec = API_SPECS[operation]
    request_params = spec.params if params is None else params

    url = urllib.parse.urlunsplit(("http", ip, f"/sony/{spec.path}", None, None))
    data = {
        "method": spec.method,
        "id": spec.request_id,
        "params": [] if request_params is None else [request_params],
        "version": spec.version,
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
        with urllib.request.urlopen(request, timeout=5) as response:
            try:
                content = json.loads(response.read())
            except json.JSONDecodeError as e:
                raise SystemExit(f"Received an invalid JSON response from BRAVIA ({url}): {e}") from e

            if not isinstance(content, dict):
                raise SystemExit(f"Received an unexpected response from BRAVIA ({url}).")
            if "error" in content:
                raise SystemExit(f"BRAVIA API error: {content['error']}")
            return content
    except urllib.error.HTTPError as e:
        raise SystemExit(f"BRAVIA request failed (HTTP {e.code}: {e.reason})") from e
    except urllib.error.URLError as e:
        raise SystemExit(f"Could not connect to BRAVIA ({url}): {e.reason}") from e
    except TimeoutError as e:
        raise SystemExit(f"Connection to BRAVIA timed out ({url})") from e


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("resource",
                            choices=[
                                # guide
                                "api",
                                "supported-api-info",
                                # appControl
                                "application-list",
                                "web-app-status",
                                "application-status-list",
                                # audio
                                "volume",
                                "volume-information",
                                "speaker",
                                "speaker-settings",
                                # encryption
                                "public-key",
                                # system
                                "led",
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
    led_parser = set_subparsers.add_parser("led", aliases=["led-indicator-status"])
    led_parser.add_argument(
        "mode",
        choices=["Demo", "AutoBrightnessAdjust", "Dark", "SimpleResponse", "Off"],
    )
    power_parser = set_subparsers.add_parser("power", aliases=["power-status"])
    power_parser.add_argument("value", choices=["on", "off"])
    power_saving_parser = set_subparsers.add_parser("power-saving", aliases=["power-saving-mode"])
    power_saving_parser.add_argument("mode", choices=["off", "low", "high", "pictureOff"])
    wol_parser = set_subparsers.add_parser("wol", aliases=["wol-mode"])
    wol_parser.add_argument("value", choices=["on", "off"])
    # videoScreen
    scene_parser = set_subparsers.add_parser("scene", aliases=["scene-setting"])
    scene_parser.add_argument("value", choices=["auto", "auto24pSync", "general"])

    request_parser = subparsers.add_parser("request")
    request_parser.add_argument("action", choices=["reboot"])

    return parser


def handle_get(resource: str) -> None:
    content = call_api(GET_OPERATIONS[resource])
    print(json.dumps(content, indent=2))


def handle_set(args: argparse.Namespace) -> None:
    match args.resource:
        # audio
        case "volume" | "audio-volume":
            volume = "+1" if args.value == "up" else "-1"
            call_api(Operation.SET_AUDIO_VOLUME, {"volume": volume, "target": "speaker"})
        case "mute" | "audio-mute":
            call_api(Operation.SET_AUDIO_MUTE, {"status": args.value == "on"})
        # system
        case "led" | "led-indicator-status":
            call_api(Operation.SET_LED_INDICATOR_STATUS, {"mode": args.mode})
        case "power" | "power-status":
            call_api(Operation.SET_POWER_STATUS, {"status": args.value == "on"})
        case "power-saving" | "power-saving-mode":
            call_api(Operation.SET_POWER_SAVING_MODE, {"mode": args.mode})
        case "wol" | "wol-mode":
            call_api(Operation.SET_WOL_MODE, {"enabled": args.value == "on"})
        # videoScreen
        case "scene" | "scene-setting":
            call_api(Operation.SET_SCENE_SETTING, {"value": args.value})


def handle_request(action: str) -> None:
    if action == "reboot":
        call_api(Operation.REQUEST_REBOOT)


def main() -> None:
    args = build_parser().parse_args()
    match args.command:
        case "get":
            handle_get(args.resource)
        case "set":
            handle_set(args)
        case "request":
            handle_request(args.action)


if __name__ == "__main__":
    main()
