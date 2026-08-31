import io
import json
import os
import unittest
from argparse import Namespace
from unittest.mock import patch

import bravia


class FakeResponse:
    def __init__(self, content):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.content


class CallApiTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(
            os.environ,
            {"BRAVIA_IP": "192.0.2.1", "BRAVIA_PSK": "test-psk"},
            clear=True,
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)

    @patch("bravia.urllib.request.urlopen")
    def test_call_api_builds_request(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"result": [{"status": "active"}]}')

        result = bravia.call_api(bravia.Operation.GET_POWER_STATUS)

        self.assertEqual(result["result"][0]["status"], "active")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://192.0.2.1/sony/system")
        self.assertEqual(request.get_header("X-auth-psk"), "test-psk")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 5)
        body = json.loads(request.data)
        self.assertEqual(body["method"], "getPowerStatus")
        self.assertEqual(body["id"], 50)
        self.assertEqual(body["params"], [])

    @patch("bravia.urllib.request.urlopen")
    def test_call_api_raises_for_api_error(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"error": [500, "Failed"]}')

        with self.assertRaises(SystemExit) as error:
            bravia.call_api(bravia.Operation.GET_POWER_STATUS)

        self.assertIn("BRAVIA API error", str(error.exception))

    def test_call_api_raises_when_configuration_is_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as error:
                bravia.call_api(bravia.Operation.GET_POWER_STATUS)

        self.assertIn("BRAVIA_IP", str(error.exception))


class CommandTests(unittest.TestCase):
    def test_removed_led_indicator_alias_is_rejected(self):
        parser = bravia.build_parser()

        with patch("sys.stderr", new=io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["get", "led-indicator"])

    @patch("bravia.call_api")
    def test_set_volume_up_sends_increment(self, call_api):
        bravia.handle_set(
            Namespace(resource="volume", value="up")
        )

        call_api.assert_called_once_with(
            bravia.Operation.SET_AUDIO_VOLUME,
            {"volume": "+1", "target": "speaker"},
        )

    @patch("bravia.call_api")
    def test_set_mute_off_sends_false(self, call_api):
        bravia.handle_set(Namespace(resource="mute", value="off"))

        call_api.assert_called_once_with(
            bravia.Operation.SET_AUDIO_MUTE,
            {"status": False},
        )


if __name__ == "__main__":
    unittest.main()
