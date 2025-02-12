import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code2 import MachineData, AgentCapteur, AgentAnalyseur, AgentPlanificateur, TextCleaner

@pytest.fixture
def sample_machine_data():
    return MachineData(
        machine_id="TEST001",
        temperature=75.0,
        vibration=50.0,
        pressure=5.0
    )

@pytest.fixture
def mock_gemini_response():
    mock_response = Mock()
    mock_response.text = "Test response from Gemini"
    return mock_response

class TestTextCleaner:
    def test_clean_text_empty(self):
        assert TextCleaner.clean_text("") == ""

    def test_clean_text_markdown_removal(self):
        text = "**Bold** and *italic* text"
        cleaned = TextCleaner.clean_text(text)
        assert "**" not in cleaned
        assert "*" not in cleaned

    def test_clean_text_planification_section(self):
        text = "Some text Planification/recommandation: do this"
        cleaned = TextCleaner.clean_text(text)
        assert "\nPlanification/recommandation" in cleaned

class TestAgentCapteur:
    def test_collect_data_valid(self, sample_machine_data):
        result = AgentCapteur.collect_data(sample_machine_data)
        assert result["MachineID"] == "TEST001"
        assert result["Température"] == 75.0
        assert result["Vibration"] == 50.0
        assert result["Pression"] == 5.0

    def test_collect_data_invalid(self):
        invalid_data = MachineData(
            machine_id="TEST001",
            temperature="invalid",
            vibration=50.0,
            pressure=5.0
        )
        with pytest.raises(ValueError):
            AgentCapteur.collect_data(invalid_data)

class TestAgentAnalyseur:
    @patch('google.generativeai.GenerativeModel')
    def test_init_success(self, mock_model):
        agent = AgentAnalyseur()
        assert agent.model is not None

    @patch('google.generativeai.GenerativeModel')
    def test_init_failure(self, mock_model):
        mock_model.side_effect = Exception("API Error")
        with pytest.raises(Exception):
            AgentAnalyseur()

    @patch('google.generativeai.GenerativeModel')
    def test_analyze_data(self, mock_model, sample_machine_data, mock_gemini_response):
        mock_instance = Mock()
        mock_instance.generate_content.return_value = mock_gemini_response
        mock_model.return_value = mock_instance

        agent = AgentAnalyseur()
        sensor_data = AgentCapteur.collect_data(sample_machine_data)
        result = agent.analyze_data(sensor_data)
        
        assert isinstance(result, str)
        assert result == "Test response from Gemini"

class TestAgentPlanificateur:
    @patch('google.generativeai.GenerativeModel')
    def test_init_success(self, mock_model):
        agent = AgentPlanificateur()
        assert agent.model is not None

    @patch('google.generativeai.GenerativeModel')
    def test_init_failure(self, mock_model):
        mock_model.side_effect = Exception("API Error")
        with pytest.raises(Exception):
            AgentPlanificateur()

    @patch('google.generativeai.GenerativeModel')
    def test_plan_maintenance(self, mock_model, mock_gemini_response):
        mock_instance = Mock()
        mock_instance.generate_content.return_value = mock_gemini_response
        mock_model.return_value = mock_instance

        agent = AgentPlanificateur()
        result = agent.plan_maintenance("Test analysis", "TEST001")
        
        assert isinstance(result, str)
        assert result == "Test response from Gemini" 