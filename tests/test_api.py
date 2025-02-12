import pytest
import json
from unittest.mock import patch
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code2 import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def valid_payload():
    return {
        "machine_id": "TEST001",
        "temperature": 75.0,
        "vibration": 50.0,
        "pression": 5.0
    }

class TestAPI:
    def test_analyse_endpoint_success(self, client, valid_payload):
        with patch('google.generativeai.GenerativeModel') as mock_model:
            # Mock the Gemini model responses
            mock_instance = mock_model.return_value
            mock_instance.generate_content.side_effect = [
                type('Response', (), {'text': 'Analysis result'}),
                type('Response', (), {'text': 'Maintenance plan'})
            ]

            response = client.post('/analyse', 
                                json=valid_payload,
                                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert 'analysis' in data
            assert 'maintenance_plan' in data

    def test_analyse_endpoint_missing_data(self, client):
        response = client.post('/analyse',
                             json={},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'error' in data

    def test_analyse_endpoint_invalid_data(self, client):
        invalid_payload = {
            "machine_id": "TEST001",
            "temperature": "invalid",
            "vibration": 50.0,
            "pression": 5.0
        }
        
        response = client.post('/analyse',
                             json=invalid_payload,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'error' in data

    def test_analyse_endpoint_missing_fields(self, client):
        incomplete_payload = {
            "machine_id": "TEST001",
            "temperature": 75.0
            # missing vibration and pression
        }
        
        response = client.post('/analyse',
                             json=incomplete_payload,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'error' in data 