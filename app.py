import json
import os
import time
import pymsteams
import threading

from dotenv import load_dotenv
import boto3
from flask import Flask, jsonify

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import BedrockChat
import streamlit as st

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
AWS_QUEUE = os.getenv("AWS_Q1")
TEAMS_WEBHOOK = os.getenv("TEAMS_WEBHOOK")
sqs = boto3.client('sqs', region_name=AWS_REGION)

app = Flask(__name__)

# Bedrock client

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="eu-west-2"
)

modelID = "anthropic.claude-3-sonnet-20240229-v1:0"

llm = BedrockChat(
    model_id=modelID,
    client=bedrock_client,
    # model_kwargs={"max_tokens_to_sample": 2000,"temperature":0.9}
)

def my_helpbot(language, freeform_text):
    prompt = PromptTemplate(
        input_variables=["language", "freeform_text"],
        template="You are a help bot to help suggest a fit for an issue. You are in {language}.\n\n{freeform_text}"
    )

    bedrock_chain = LLMChain(llm=llm, prompt=prompt)

    response = bedrock_chain({'language': language, 'freeform_text': freeform_text})
    return response


# http://localhost:5001/health
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"Healthy"}), 200

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
                WaitTimeSeconds=2
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

            print(json_body.get('title'))

            # if json_body.get('title') is None or json_body.get('desc') is None or json_body.get('prio') is None:
            #     continue

            print("Sending teams alert, :")

            print(send_teams_alert(json_body))

        except:
            pass

def send_teams_alert(json_body):
    myTeamsMessage = pymsteams.connectorcard(TEAMS_WEBHOOK)
    myTeamsMessage.title(f"{json_body.get('title')}")
    myTeamsMessage.text(f"{json_body.get('desc')}")
    myTeamsMessage.text(f"\n A suggested improvement is: {my_helpbot("english", str(json_body.get('desc'))).get('text')}")
    try:
        myTeamsMessage.send()
    except Exception as e:
        print("An error occurred:", e, e.args)

    return "Sents"

def background_thread():
    thread = threading.Thread(target=get_messages, daemon=True)
    thread.start()
    return thread

bg_thread = background_thread()

# Docker build p1service-flask-app
#Docker: docker run --env-file ./.env -p 8081:8081 --rm p1service-flask-app
if __name__ == '__main__':
    threading.Thread(target=lambda: app.run()).start()