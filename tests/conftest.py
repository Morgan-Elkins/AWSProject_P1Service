import os
import pytest
import boto3
from moto import mock_aws

os.environ['AWS_REGION'] = 'eu-west-2'
os.environ['AWS_Q1'] = 'testing'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'

from app import send_teams_alert, app

@pytest.fixture(scope='function')
def client():

    with mock_aws():
        sqs = boto3.client('sqs', region_name='eu-west-2')

        queue_url = sqs.create_queue(
            QueueName='testing'
        )['QueueUrl']

        yield sqs

def test_get_health(client):
    response = app.test_client().get("/health")
    assert b'{"status":"Healthy"}\n' in response.data

@mock_aws()
def test_send_teams_alert():
    with mock_aws():
        data = {"title": "pytest", "desc": "pytest desc", "prio": 0}
        response = send_teams_alert(data)
        assert response == True