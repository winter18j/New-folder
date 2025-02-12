from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import re
import logging
from dataclasses import dataclass
from typing import Dict, Any
from http import HTTPStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
genai.configure(api_key="AIzaSyAMb8XwbuahlC6xH4bk-gfdjOy3NUbYJPI")

# Constants
TEMPERATURE_THRESHOLD = 85.0
VIBRATION_THRESHOLD = 100.0
PRESSURE_MIN_THRESHOLD = 1.0
PRESSURE_MAX_THRESHOLD = 10.0

@dataclass
class MachineData:
    machine_id: str
    temperature: float
    vibration: float
    pressure: float

class TextCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and format the text response from the model."""
        if not text:
            return ""
            
        # Remove markdown symbols
        text = re.sub(r'[*]+', '', text)
        
        # Add newline before "Planification" section
        text = re.sub(r'(\s*[\W]+)?(Planification/recommandation)', r'\n\2', text)
        
        # Remove extra whitespace
        text = re.sub(r'(\n\s*)+', '\n', text)
        
        return text.strip()

class AgentCapteur:
    @staticmethod
    def collect_data(data: MachineData) -> Dict[str, Any]:
        """Collect and validate machine sensor data."""
        try:
            return {
                "MachineID": data.machine_id,
                "Température": float(data.temperature),
                "Vibration": float(data.vibration),
                "Pression": float(data.pressure),
            }
        except ValueError as e:
            logger.error(f"Error converting sensor data: {e}")
            raise ValueError("Invalid sensor data format")

class AgentAnalyseur:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise

    def _create_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create the analysis prompt for the model."""
        formatted_data = (
            f"Température = {data['Température']}°C, "
            f"Vibration = {data['Vibration']} unités, "
            f"Pression = {data['Pression']} bars"
        )
        
        return (
            "Tu es un expert en maintenance industrielle et en gestion des risques dans des environnements critiques, "
            "où la sécurité et la fiabilité des machines sont des priorités absolues. "
            f"Ton objectif est d'analyser les données suivantes collectées par les capteurs de la machine : {formatted_data}. "
            "Les données suivent un format 'Paramètre = Valeur', où chaque paramètre représente une mesure critique pour le fonctionnement de la machine. "
            "Voici la signification et l'importance des paramètres : "
            "'Vibration = X', où X représente l'amplitude de la vibration en unités standard. "
            "Les vibrations excessives peuvent être un indicateur immédiat d'une défaillance mécanique imminente. "
            "'Température = X', où X représente la température en degrés Celsius. "
            "Une température élevée peut entraîner des risques de surchauffe ou de défaillance thermique. "
            "'Pression = X', où X représente la pression en bars. "
            "Des variations anormales de pression peuvent indiquer des fuites ou des risques de rupture de tuyauterie. "
            "Analyse les valeurs des paramètres et détermine s'il existe un risque immédiat pour la machine ou pour la sécurité des opérateurs. "
            "Tient compte des seuils de sécurité suivants pour chaque paramètre : "
            "- Vibration > 100 unités : risque élevé de défaillance mécanique. "
            "- Température > 85°C : risque immédiat de surchauffe ou de défaillance thermique. "
            "- Pression < 1 bar ou > 10 bars : risque de défaillance de l'équipement ou d'accident. "
            "Si l'une de ces conditions est remplie, recommande une action urgente, comme un arrêt immédiat de la machine, un contrôle approfondi ou une intervention d'urgence. "
            "Si aucune condition critique n'est détectée, indique clairement qu'aucune action immédiate n'est nécessaire, mais recommande un suivi régulier. "
            "Réponds de manière très concise, avec un degré élevé de professionnalisme, en indiquant précisément s'il existe un risque, "
            "le type de risque (par exemple, surchauffe, défaillance mécanique, fuite, etc.), et l'action d'urgence recommandée si nécessaire."
            "Réponds de manière concise et précise sans fournir de valeurs spécifiques ni de recommandations d'action, n'afficher pas les valeurs"
        ).format(data=formatted_data)

    def analyze_data(self, data: Dict[str, Any]) -> str:
        """Analyze machine data using the Gemini model."""
        try:
            prompt = self._create_analysis_prompt(data)
            response = self.model.generate_content(prompt)
            return TextCleaner.clean_text(response.text)
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            raise RuntimeError("Failed to analyze machine data")

class AgentPlanificateur:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise

    def _create_planning_prompt(self, analysis: str, machine_id: str) -> str:
        """Create the maintenance planning prompt."""
        return (
            "Tu es un expert en gestion de maintenance industrielle, "
            f"spécialisé dans l'analyse des risques liés aux machines et équipements critiques. "
            f"En fonction des données et de l'analyse suivantes, tu dois proposer un plan de maintenance détaillé et précis. "
            f"Voici l'analyse de la machine {machine_id}: {analysis}\n"
            "Explication des risques :\n"
            "- Si le risque est *élevé*, recommande une *intervention immédiate* pour éviter des dommages importants, accompagné d'un emoji d'alerte ⚠️.\n"
            "- Si le risque est *modéré*, recommande une *inspection approfondie* dans un délai raisonnable, accompagné d'un emoji d'outil 🔧.\n"
            "- Si le risque est *faible*, recommande une *surveillance continue* avec des vérifications régulières, accompagné d'un emoji de coche ✅.\n"
            "Dans chaque situation, il faut afficher un seul risque. Sois précis dans tes recommandations : explique clairement ce qui doit être fait, et si une action immédiate est nécessaire, indique-la clairement avec un plan d'action."
            "Sois direct et précis dans tes réponses."
            "Réponds sous la forme suivante :\n\n"
            "Risque : xxxxxxxxxxxxxx \n\n\n "
            " Planification/recommandation : xxxxxxxxxxxxx\n\n"
        ).format(machine_id=machine_id, analysis=analysis)

    def plan_maintenance(self, analysis: str, machine_id: str) -> str:
        """Generate maintenance plan based on analysis."""
        try:
            prompt = self._create_planning_prompt(analysis, machine_id)
            response = self.model.generate_content(prompt)
            return TextCleaner.clean_text(response.text)
        except Exception as e:
            logger.error(f"Maintenance planning error: {e}")
            raise RuntimeError("Failed to generate maintenance plan")

@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler for the application."""
    logger.error(f"Unhandled error: {error}")
    return jsonify({
        'error': str(error),
        'status': 'error'
    }), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/analyse', methods=['POST'])
def analyse():
    """Main endpoint for machine analysis."""
    try:
        data = request.get_json()
        if not data:
            raise ValueError("No data provided")

        # Validate input data
        required_fields = ['machine_id', 'temperature', 'vibration', 'pression']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")

        # Create machine data object
        machine_data = MachineData(
            machine_id=data['machine_id'],
            temperature=data['temperature'],
            vibration=data['vibration'],
            pressure=data['pression']
        )

        # Process data through agents
        sensor_data = AgentCapteur.collect_data(machine_data)
        
        agent_analyseur = AgentAnalyseur()
        analysis = agent_analyseur.analyze_data(sensor_data)
        
        agent_planificateur = AgentPlanificateur()
        maintenance_plan = agent_planificateur.plan_maintenance(analysis, machine_data.machine_id)

        return jsonify({
            'status': 'success',
            'analysis': analysis,
            'maintenance_plan': maintenance_plan
        }), HTTPStatus.OK

    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), HTTPStatus.BAD_REQUEST
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({
            'status': 'error',
            'error': 'An internal error occurred'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == '__main__':
    app.run(debug=False)  # Set to False for production