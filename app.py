import json
import os
import time
import pymsteams
import threading

from dotenv import load_dotenv
import boto3
from flask import Flask, jsonify

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
AWS_QUEUE = os.getenv("AWS_Q1")
TEAMS_WEBHOOK = os.getenv("TEAMS_WEBHOOK")
sqs = boto3.client('sqs', region_name=AWS_REGION)

app = Flask(__name__)

def create_app():

    # http://localhost:5001/health
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status":"Healthy"}), 200

    return app

def get_messages():
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

            body = message['Body']
            json_body = eval(body)
            print(f"Message contents {json_body}")

            if json_body.get('title') is None or json_body.get('desc') is None or json_body.get('prio') is None:
                continue


            print(send_teams_alert(json_body))

        except:
            pass
        time.sleep(1)

def send_teams_alert(json_body):
    myTeamsMessage = pymsteams.connectorcard(TEAMS_WEBHOOK)
    myTeamsMessage.title(f"{json_body.get('title')}")
    myTeamsMessage.text(f"{json_body.get('desc')}")
    return myTeamsMessage.send()

def background_thread():
    thread = threading.Thread(target=get_messages, daemon=True)
    thread.start()
    return thread

bg_thread = background_thread()


#Docker: docker run --env-file ./.env -p 8081:8081 p1service-flask-app
if __name__ == '__main__':
    print("Running as main")
    app = create_app()
    threading.Thread(target=lambda: app.run()).start()
