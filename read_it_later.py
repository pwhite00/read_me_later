#!/usr/bin/env python3
import requests
import json
import os
import sys
import argparse
import contextlib

# Edit SLACK_WEBHOOK with your intended Slack Webhook URL
SLACK_WEBHOOK = "Add your Slack webhook URL here"
EXAMPLE_JSON = {"webhook": "https://hooks.slack.com/services/YourWebHookURL"}
SCRIPT_NAME = sys.argv[0]
VERSION = 1.0

def process_message(args):
    """
    take a message and process it into slack
    :param args:
    :return: 0 ok, 1+ errors
    """

    if args.creds_file:
        creds = load_json_file(args.creds_file)
    elif args.webhook:
        creds = args.webhook
    else:
        creds = SLACK_WEBHOOK

    print(creds)

    if not creds:
        print("unable to find slack credentials, post will fail")
        return 2

    if not call_slack(args.message, creds):
        return 3
    else:
        return 0


def call_slack(msg, slack_url):
    if not (msg) or not (slack_url):
        print("missing data")
        return None
    try:
        result = requests.post(slack_url, json={"text": msg})
    except Exception as err:
        print("Unable to POST [{}] to slack, error: [{}]".format(msg, err))
        return None

    print("Successful POST to slack. response [{}]".format(msg, result.status_code))
    return result.status_code


def load_json_file(filename):
    """
    consumes a json formated file extracts the  value of "webhook": VALUE
    :param filename:
    :return: VALUE or None
    """
    if not os.path.isfile(filename):
        print("{} not found".format(filename))

    with contextlib.closing(open(filename)) as file_open:
        try:
            creds = json.load(file_open)
        except (IOError, OSError, json.JSONDecodeError) as err:
            print("unable to parse json credentials file. {}".format(err))
            return None

    if ('webhook' in creds.keys()) and creds['webhook']:
        return creds['webhook']
    else:
        print("no slack webhook provided")
        return None


def cli_parser(args):
    """
    command line argument parser
    :param args:
    :return: args.Namespace
    """

    parser = argparse.ArgumentParser(
        description='{}, version {}: a tool for posting messages to a slack channel'.format(SCRIPT_NAME, VERSION))
    parser.add_argument('-f', '--creds-file', dest="creds_file", default=None,
                        help="You can pass slack creds in as a  JSON file [OPTIONAL] Exmaple JSON: {}".format(
                            EXAMPLE_JSON))
    parser.add_argument('-m', '--message', dest="message", default=None, required=True,
                        help="the string you wish to post to slack")
    parser.add_argument('-w', '--webhook', dest='webhook', default=None, help='Pass Slack webhook in directly [OPTIONAL] Exmaple: "https://yourwebhookhere.com"')
    args = parser.parse_args()

    return args


def main():
    args = cli_parser(sys.argv[:1])
    if not args:
        print("failed to parse arguments")
        return 1

    return process_message(args)


if __name__ == '__main__':
    sys.exit(main())
