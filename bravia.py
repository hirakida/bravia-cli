#!/usr/local/bin/python3
# coding=utf-8

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request

import enum


class Properties:
    def __init__(self, path, method, id, params):
        self.path = path
        self.method = method
        self.id = id
        self.params = params


class VolumeOperation(enum.Enum):
    INCREMENT = 1
    DECREMENT = 2


properties_dict = {
    'get_power': Properties('system', 'getPowerStatus', 50, {}),
    'set_power_on': Properties('system', 'setPowerStatus', 55, {'status': True}),
    'set_power_off': Properties('system', 'setPowerStatus', 55, {'status': False}),
    'get_volume': Properties('audio', 'getVolumeInformation', 33, {}),
    'set_volume': Properties('audio', 'setAudioVolume', 601, {}),
    'set_mute_on': Properties('audio', 'setAudioMute', 601, {'status': True}),
    'set_mute_off': Properties('audio', 'setAudioMute', 601, {'status': False})
}


def has_result(content):
    return content is not None and 'result' in content


def print_content(content):
    if has_result(content):
        print('%s' % content['result'])


def call_api(properties):
    ip = os.environ['BRAVIA_IP']
    psk = os.environ['BRAVIA_PSK']

    url = urllib.parse.urlunsplit(('http', ip, f'/sony/{properties.path}', None, None))
    data = {
        'method': properties.method,
        'id': properties.id,
        'params': [properties.params],
        'version': '1.0'
    }
    headers = {
        'X-Auth-PSK': psk,
        'Content-Type': 'application/json'
    }

    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    try:
        with urllib.request.urlopen(req) as response:
            content = json.loads(response.read().decode('utf8'))
            if 'error' in content:
                print('error: %s' % content['error'])
                print('id: %d' % content['id'])
            return content
    except urllib.error.URLError as err:
        print('error: %s' % err.reason)


def set_volume(operation):
    target = 'speaker'
    content = call_api(properties_dict['get_volume'])

    if has_result(content):
        for element in content['result'][0]:
            if element['target'] == target:
                volume = element['volume']
                if operation == VolumeOperation.INCREMENT:
                    volume += 1
                elif operation == VolumeOperation.DECREMENT:
                    volume -= 1

                properties = properties_dict['set_volume']
                properties.params = {'volume': str(volume), 'target': target}
                call_api(properties)
                break
    return


def main():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['show-power', 'on', 'off',
                                       'show-volume', 'up', 'down', 'mute', 'unmute'])
    args = p.parse_args()

    if args.command == 'show-power':
        content = call_api(properties_dict['get_power'])
        print_content(content)
    elif args.command == 'on':
        call_api(properties_dict['set_power_on'])
    elif args.command == 'off':
        call_api(properties_dict['set_power_off'])
    elif args.command == 'show-volume':
        content = call_api(properties_dict['get_volume'])
        print_content(content)
    elif args.command == 'up':
        set_volume(VolumeOperation.INCREMENT)
    elif args.command == 'down':
        set_volume(VolumeOperation.DECREMENT)
    elif args.command == 'mute':
        call_api(properties_dict['set_mute_on'])
    elif args.command == 'unmute':
        call_api(properties_dict['set_mute_off'])


if __name__ == '__main__':
    main()
