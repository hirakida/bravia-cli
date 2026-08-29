# bravia-cli

A simple command-line tool for controlling Sony BRAVIA TVs through the Remote Display Control API.

Support for additional APIs is added over time. See Sony's official reference for API details.

<https://pro-bravia.sony.net/remote-display-control/rest-api/reference/>

## Requirements

- Python 3.10 or later
- Remote Display Control enabled on the BRAVIA TV

## Setup

Set the BRAVIA's IP address and authentication Pre-Shared Key (PSK) as environment variables:

```sh
export BRAVIA_IP="192.168.1.100"
export BRAVIA_PSK="your-pre-shared-key"
```

Then run `bravia.py`. Use the following command to see the available options:

```sh
python3 bravia.py -h
```
