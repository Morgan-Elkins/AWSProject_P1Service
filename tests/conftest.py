import os

import pytest
from flask import jsonify

os.environ['AWS_REGION'] = 'eu-west-2'
os.environ['AWS_Q1'] = 'testing'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'

from app import create_app, send_teams_alert

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture()
def client(app):
    with app.app_context():
        return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_get_health(client):
    response = client.get("/health")
    assert b'{"status":"Healthy"}\n' in response.data

def test_send_teams_alert(client):
    data = {"title": "pytest", "desc": "pytest desc", "prio": 0}
    response = send_teams_alert(data)
    assert response == True