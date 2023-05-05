import argparse

import requests
from decouple import config as env


def send_message_to_slack():
    parser = argparse.ArgumentParser()
    parser.add_argument("message", type=str)
    args = parser.parse_args()
    requests.post(env("SLACK_MESSAGE_URL"), json={"text": args.message})


if __name__ == "__main__":
    send_message_to_slack()  # pragma: no cover
