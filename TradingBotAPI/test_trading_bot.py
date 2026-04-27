import pytest
import json
from unittest.mock import patch
import sys
import os

# Ensure the app can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from TradingBot import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Reset state before each test if needed
        yield client

def test_bot_status_get(client):
    """Test getting the bot status."""
    response = client.get('/bot-status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "RUNNING" in data
    assert "Status" in data

def test_bot_config_get(client):
    """Test getting the default configuration."""
    response = client.get('/bot-config')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "Config" in data
    assert "stop_loss" in data["Config"]

def test_bot_config_post_valid(client):
    """Test updating the configuration with valid payload."""
    payload = {
        "stop_loss": 6.0,
        "take_profit": 3.0,
        "max_volume": 2.0,
        "min_volume": 0.05,
        "max_trades": 5
    }
    response = client.post('/bot-config', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["Message"] == "Config updated."
    assert data["Config"]["stop_loss"] == 6.0

def test_bot_config_post_missing_fields(client):
    """Test updating the configuration with a missing required field."""
    # Missing 'stop_loss'
    payload = {
        "take_profit": 3.0,
        "max_volume": 2.0,
        "min_volume": 0.05,
        "max_trades": 5
    }
    response = client.post('/bot-config', json=payload)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Missing fields" in data["Message"]

def test_bot_config_post_invalid_types(client):
    """Test updating the configuration with bad data types (string instead of float)."""
    payload = {
        "stop_loss": "invalid_string", 
        "take_profit": 3.0,
        "max_volume": 2.0,
        "min_volume": 0.05,
        "max_trades": 5
    }
    response = client.post('/bot-config', json=payload)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "must be a number" in data["Message"]

@patch('TradingBot.main')
def test_start_and_stop_bot(mock_main, client):
    """Test starting and stopping the bot, mocking the main thread loop."""
    # Ensure bot is stopped initially
    client.post('/stop-bot')

    # Start the bot
    response = client.post('/start-bot')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["Status"] == 1
    assert "started" in data["Message"].lower()
    
    # Allow mock thread to spin up
    import time
    time.sleep(0.1)

    # Check that status is updating correctly to True
    stat_response = client.get('/bot-status')
    stat_data = json.loads(stat_response.data)
    assert stat_data["RUNNING"] is True

    # Stop the bot
    response_stop = client.post('/stop-bot')
    assert response_stop.status_code == 200
    data_stop = json.loads(response_stop.data)
    assert data_stop["Status"] == 0
    assert "stopping" in data_stop["Message"].lower()
