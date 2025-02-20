import os
import pytest
import boto3
from moto import mock_aws

os.environ['AWS_REGION'] = 'eu-west-2'
os.environ['AWS_Q1'] = 'testing'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'

from app import create_app, send_teams_alert

@pytest.fixture(scope='function')
def app():

    with mock_aws():
        sqs = boto3.client('sqs', region_name='eu-west-2')

        app = create_app()
        app.config.update({
            "TESTING": True,
        })

        queue_url = sqs.create_queue(
            QueueName='testing'
        )['QueueUrl']

        yield app


@pytest.fixture(scope='function')
def client(app):
    with app.app_context():
        return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    return app.test_cli_runner()

def test_get_health(client):
    response = client.get("/health")
    assert b'{"status":"Healthy"}\n' in response.data

# @mock_aws()
# def test_send_teams_alert():
#     with mock_aws():
#         data = {"title": "pytest", "desc": "pytest desc", "prio": 0}
#         response = send_teams_alert(data)
#         assert response == True