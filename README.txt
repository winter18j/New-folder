Machine Monitoring System
======================

A Flask-based industrial machine monitoring system that uses Google's Gemini AI to analyze sensor data and provide maintenance recommendations.

Features
--------
- Real-time machine sensor data analysis
- AI-powered risk assessment
- Automated maintenance recommendations
- RESTful API interface
- Comprehensive test suite

Prerequisites
------------
- Python 3.7 or higher
- pip (Python package installer)
- Virtual environment (recommended)

Installation
------------
1. Clone the repository or download the source code.

2. Create and activate a virtual environment (recommended):
   Windows:
   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```
   
   Linux/Mac:
   ```
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the package and its dependencies:
   ```
   pip install -e .
   ```

4. Install test dependencies (if you want to run tests):
   ```
   pip install pytest pytest-cov pytest-mock
   ```

Configuration
------------
1. The application uses Google's Gemini AI API. Make sure you have a valid API key.

2. The API key is currently hardcoded in the code2.py file. For production, it's recommended to use environment variables:
   Create a .env file in the root directory and add:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

Running the Application
---------------------
1. Start the Flask server:
   ```
   python code2.py
   ```
   The server will start on http://localhost:5000

2. The API endpoint is available at:
   POST http://localhost:5000/analyse

API Usage
--------
Send POST requests to /analyse with JSON payload:
```json
{
    "machine_id": "MACHINE001",
    "temperature": 75.0,
    "vibration": 50.0,
    "pression": 5.0
}
```

Response format:
```json
{
    "status": "success",
    "analysis": "Analysis result...",
    "maintenance_plan": "Maintenance recommendations..."
}
```

Running Tests
------------
1. Run all tests with coverage report:
   ```
   pytest
   ```

2. Run specific test file:
   ```
   pytest tests/test_api.py
   ```

3. Run tests with verbose output:
   ```
   pytest -v
   ```

Project Structure
---------------
- code2.py: Main application file
- tests/: Test directory
  - test_agents.py: Unit tests for agents
  - test_api.py: API integration tests
- requirements.txt: Project dependencies
- setup.py: Package configuration
- pytest.ini: Pytest configuration

Components
---------
1. TextCleaner: Formats and cleans AI responses
2. AgentCapteur: Handles sensor data collection
3. AgentAnalyseur: Analyzes machine data using Gemini AI
4. AgentPlanificateur: Generates maintenance plans

Error Handling
------------
The API returns appropriate HTTP status codes:
- 200: Successful analysis
- 400: Invalid input data
- 500: Internal server error

Each error response includes a descriptive message in the response body.

Monitoring Thresholds
-------------------
The system monitors these parameters with the following thresholds:
- Temperature > 85°C: Risk of thermal failure
- Vibration > 100 units: Risk of mechanical failure
- Pressure < 1 bar or > 10 bars: Risk of equipment failure

Development
----------
To contribute to the project:
1. Install development dependencies:
   ```
   pip install -e ".[dev]"
   ```
2. Run tests before submitting changes:
   ```
   pytest
   ```
3. Ensure code coverage remains high:
   ```
   pytest --cov=.
   ```

Security Notes
------------
1. Never commit API keys to version control
2. Use environment variables for sensitive data
3. Keep dependencies updated
4. Run with debug=False in production

Support
-------
For issues and questions, please create an issue in the repository or contact the maintainers.

License
-------
This project is licensed under the MIT License - see the LICENSE file for details. 