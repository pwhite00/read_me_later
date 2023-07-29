# Read_me_later : A tool for sending a message or url to a slack channel from a terminal shell


Uses python3 and slack webhooks

python3 Requirements:
```
certifi==2023.7.22
charset-normalizer==3.2.0
idna==3.4
requests==2.31.0
urllib3==2.0.4
```

Slack Webhook can be configured in a few ways
* Configure the SLACK_WEBHOOK global variable
* pass the webhook URL in on the commandline using the --webhook argument
* confgure the webhook in a JSON file and pass it  in using the --creds-file argument

Example JSON:
```
{
  "webhook" : "webhook URL
}

```
