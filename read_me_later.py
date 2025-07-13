#!/usr/bin/env python3
import requests
import json
import os
import sys
import argparse
import contextlib
import time
import re
from pathlib import Path

# Default webhook (can be overridden via command line or config file)
SLACK_WEBHOOK = None
EXAMPLE_JSON = {"webhook": "https://hooks.slack.com/services/YourWebHookURL"}
SCRIPT_NAME = sys.argv[0]
VERSION = 1.2

# Security constants
MAX_MESSAGE_LENGTH = 3000  # Slack's limit
RATE_LIMIT_FILE = os.path.expanduser("~/.read_me_later_rate_limit")
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 10  # max requests per window

def validate_webhook_url(url):
    """
    Validate that the webhook URL is a legitimate Slack webhook
    :param url: The webhook URL to validate
    :return: True if valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    # Check if it's a valid Slack webhook URL
    slack_webhook_pattern = r'^https://hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[a-zA-Z0-9]+$'
    if not re.match(slack_webhook_pattern, url):
        return False
    
    return True

def validate_message_length(message):
    """
    Validate that the message is within acceptable length limits
    :param message: The message to validate
    :return: True if valid, False otherwise
    """
    if not message or not isinstance(message, str):
        return False
    
    if len(message) > MAX_MESSAGE_LENGTH:
        return False
    
    return True

def check_rate_limit():
    """
    Basic rate limiting using a file-based approach
    :return: True if within rate limit, False if rate limited
    """
    try:
        current_time = time.time()
        
        # Read existing rate limit data
        if os.path.exists(RATE_LIMIT_FILE):
            with open(RATE_LIMIT_FILE, 'r') as f:
                data = json.load(f)
                timestamps = data.get('timestamps', [])
        else:
            timestamps = []
        
        # Remove timestamps outside the window
        timestamps = [ts for ts in timestamps if current_time - ts < RATE_LIMIT_WINDOW]
        
        # Check if we're within the rate limit
        if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
            oldest_request = min(timestamps)
            time_until_reset = RATE_LIMIT_WINDOW - (current_time - oldest_request)
            print(f"Rate limit exceeded. Try again in {int(time_until_reset)} seconds.")
            return False
        
        # Add current timestamp
        timestamps.append(current_time)
        
        # Save updated timestamps
        with open(RATE_LIMIT_FILE, 'w') as f:
            json.dump({'timestamps': timestamps}, f)
        
        return True
        
    except Exception as e:
        # If rate limiting fails, allow the request (fail open)
        print(f"Warning: Rate limiting failed: {e}")
        return True

def process_message(args):
    """
    take a message and process it into slack
    :param args:
    :return: 0 ok, 1+ errors
    """

    # Security validation: Check message length
    if not validate_message_length(args.message):
        print(f"Error: Message too long. Maximum length is {MAX_MESSAGE_LENGTH} characters.")
        return 4

    # Security validation: Check rate limit
    if not check_rate_limit():
        return 5

    if args.creds_file:
        creds = load_json_file(args.creds_file)
    elif args.webhook:
        creds = args.webhook
    else:
        # Try to load from default location ~/.read_me_later.json
        default_config = os.path.expanduser("~/.read_me_later.json")
        if os.path.exists(default_config):
            print(f"Loading webhook from {default_config}")
            creds = load_json_file(default_config)
        else:
            # Also try the current directory for Docker mounts
            current_dir_config = "/app/.read_me_later.json"
            if os.path.exists(current_dir_config):
                print(f"Loading webhook from {current_dir_config}")
                creds = load_json_file(current_dir_config)
            else:
                creds = SLACK_WEBHOOK

    if not creds:
        print("unable to find slack credentials, post will fail")
        print("Please provide webhook via --webhook, --creds-file, or create ~/.read_me_later.json")
        return 2

    # Security validation: Validate webhook URL
    if not validate_webhook_url(creds):
        print("Error: Invalid Slack webhook URL. Please check your configuration.")
        return 6

    if not call_slack(args.message, creds):
        return 3
    else:
        return 0


def call_slack(msg, slack_url):
    if not (msg) or not (slack_url):
        print("missing data")
        return None
    
    # Add timeout and user-agent for better security
    headers = {
        'User-Agent': f'read_me_later/{VERSION}',
        'Content-Type': 'application/json'
    }
    
    try:
        result = requests.post(
            slack_url, 
            json={"text": msg}, 
            headers=headers,
            timeout=10  # 10 second timeout
        )
    except requests.exceptions.Timeout:
        print("Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as err:
        print("Unable to POST [{}] to slack, error: [{}]".format(msg, err))
        return None

    print("Successful POST to slack. Status code: {}".format(result.status_code))
    return result.status_code


def load_json_file(filename):
    """
    consumes a json formated file extracts the  value of "webhook": VALUE
    :param filename:
    :return: VALUE or None
    """
    if not os.path.isfile(filename):
        print("{} not found".format(filename))
        return None

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
