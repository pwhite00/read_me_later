###read_me_later : A tool for sending a message or url to a slack channel


Uses python3 and slack webhooks

python3 Requirements:
```
appdirs==1.4.4
certifi==2020.12.5
chardet==4.0.0
distlib==0.3.1
filelock==3.0.12
idna==2.10
protobuf==3.15.5
PyAFF==0.1
requests==2.25.1
six==1.15.0
urllib3==1.26.4
virtualenv==20.4.4
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