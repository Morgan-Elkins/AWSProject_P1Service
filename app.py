import copy
import json
import os
import time
import requests

from dotenv import load_dotenv
import boto3
from flask import Flask

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
AWS_QUEUE = os.getenv("AWS_Q1")
TEAMS_WEBHOOK = os.getenv("TEAMS_WEBHOOK")
sqs = boto3.client('sqs', region_name=AWS_REGION)

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def home():
        print(f"{AWS_REGION} {AWS_QUEUE}")
        return "<h1>test</h1>", 200

    return app

def get_messages():
    print("TEST")
    print(f"{AWS_REGION} {AWS_QUEUE}")
    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=AWS_QUEUE,
                AttributeNames=[
                    'SentTimestamp'
                ],
                MaxNumberOfMessages=1,
                MessageAttributeNames=[
                    'All'
                ],
                VisibilityTimeout=0,
                WaitTimeSeconds=0
            )

            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']

            # Delete received message from queue
            sqs.delete_message(
                QueueUrl=AWS_QUEUE,
                ReceiptHandle=receipt_handle
            )
            print('Received and deleted message: %s' % message)

            body = message['Body']
            body = body.replace("\'", "\"") # WHY?????
            json_body = json.loads(body)
            print(f"Message contents {json_body}")
            print(f"Title: {json_body.get("title")}")

            send_teams_alert(json_body)

        except:
            pass
        time.sleep(1)

def send_teams_alert(json_body):
    headers = {'Content-Type': 'application/json'}
    data = {
        "text": f"{json_body.get("title")}"
    }
    response = requests.post(TEAMS_WEBHOOK, headers=headers, data=json.dumps(data))
    return response.status_code

if __name__ == '__main__':
    # app = create_app()
    # app.run()
    get_messages()
