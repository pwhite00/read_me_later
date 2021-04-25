###read_me_later : A tool for sending a message or url to a slack channel


Uses python3 and slack webhooks

python3 Requirements:
```
certifi==2020.12.5
chardet==4.0.0
idna==2.10
requests==2.25.1
urllib3==1.26.4
```

Slack Webhook can be configured one of  3 ways
* Configure the SLACK_WEBHOOK global variable
* pass the webhook URL in on the commandline using the --webhook argument
* confgure the webhook in a JSON file and pass it  in using the --creds-file argument

Exmaple JSON:
```
{
  "webhook" : "webhook URL
}

```