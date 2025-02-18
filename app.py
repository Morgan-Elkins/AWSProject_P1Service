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

def create_app():
    app = Flask(__name__)

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
            body = body.replace("\'", "\"")
            json_body = json.loads(body)
            print(f"Message contents {json_body}")

            # if body.get('title') is None or body.get('desc') is None or body.get('prio') is None:
            #     print("Error in ")
            #     continue
            #
            # if body.get("title") == "" or body.get("desc") == "" or body.get("prio") == "":
            #     print("Error in ")
            #     continue

            print(send_teams_alert(json_body))

        except:
            pass
        time.sleep(1)

def send_teams_alert(json_body):
    myTeamsMessage = pymsteams.connectorcard(TEAMS_WEBHOOK)
    myTeamsMessage.title(f"{json_body.get("title")}")
    myTeamsMessage.text(f"{json_body.get("desc")}")
    return myTeamsMessage.send()

#Docker: docker run --env-file ./.env -p 8081:8081 p1service-flask-app
if __name__ == '__main__':
    print("Running as main")
    app = create_app()
    threading.Thread(target=lambda: app.run( port=5001)).start()
    threading.Thread(target=lambda: get_messages()).start()
else:
    print("Running not main")
    app = create_app()
    threading.Thread(target=lambda: get_messages()).start()
