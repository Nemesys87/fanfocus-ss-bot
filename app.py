
from flask import Flask, render_template, request, jsonify, session
import requests
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

# Import our modules
from models import (
    FanProfile, FanStatus, FanType, ConfidenceLevel, PersonalityType,
    CREATOR_PROFILES, SessionManager
)
from prompts import PromptGenerator, SSFrameworkEngine
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
session_manager = SessionManager()
prompt_generator = PromptGenerator()
ss_framework = SSFrameworkEngine()

class GoogleAIClient:
    """Client for Google AI API integration"""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def generate_response(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Generate response using Google AI API"""
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': self.api_key
        }

        # Combine system and user prompts for Gemini
        combined_prompt = f"{system_prompt}\n\nUSER: {user_prompt}"

        payload = {
            "contents": [{
                "parts": [{
                    "text": combined_prompt
                }]
            }],
            "generationConfig": {
                "temperature": Config.TEMPERATURE,
                "topP": Config.TOP_P,
                "maxOutputTokens": Config.MAX_TOKENS,
            }
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "Error: No response generated"

        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return f"API Error: {str(e)}"
        except KeyError as e:
            print(f"Response parsing error: {e}")
            return "Error: Invalid response format"
        except Exception as e:
            print(f"Unexpected error: {e}")
            return f"Unexpected error: {str(e)}"

# Initialize Google AI client
ai_client = GoogleAIClient(Config.GOOGLE_AI_API_KEY, Config.GOOGLE_AI_MODEL)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', 
                         creators=Config.CREATOR_MODELS,
                         fan_types=Config.FAN_TYPES,
                         confidence_levels=Config.CONFIDENCE_LEVELS)

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response for chatter"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['creator_key', 'fan_status', 'fan_message']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        creator_key = data['creator_key']
        fan_status = data['fan_status']
        fan_message = data['fan_message']
        fan_id = data.get('fan_id', str(uuid.uuid4()))
        existing_notes = data.get('existing_notes', '')

        # Validate creator
        if creator_key not in CREATOR_PROFILES:
            return jsonify({
                'success': False,
                'error': f'Invalid creator: {creator_key}'
            }), 400

        # Get or create fan profile
        fan_status_enum = FanStatus.NEW if fan_status == 'NEW' else FanStatus.EXISTING
        fan_profile = session_manager.create_or_get_fan(fan_id, fan_status_enum)

        # Update fan profile with existing notes if provided
        if existing_notes:
            fan_profile.notes = existing_notes
            # TODO: Parse notes to update KYC progress if applicable

        # Add current message to chat history
        fan_profile.chat_history.append({
            'timestamp': datetime.now().isoformat(),
            'message': fan_message,
            'type': 'fan'
        })

        # Classify fan type using S&S Framework
        predicted_fan_type = ss_framework.classify_fan_type(fan_profile, fan_message)
        if not fan_profile.fan_type:
            fan_profile.fan_type = FanType(predicted_fan_type)

        # Generate prompts
        system_prompt = prompt_generator.generate_system_prompt(creator_key, fan_profile)
        user_prompt = prompt_generator.generate_user_prompt(fan_message, creator_key, fan_profile)

        # Get AI response
        ai_response = ai_client.generate_response(system_prompt, user_prompt)

        if not ai_response or ai_response.startswith("Error:"):
            return jsonify({
                'success': False,
                'error': ai_response or 'Failed to generate response'
            }), 500

        # Add AI response to chat history
        fan_profile.chat_history.append({
            'timestamp': datetime.now().isoformat(),
            'message': ai_response,
            'type': 'ai_suggestion'
        })

        # Get upselling suggestion if applicable
        upsell_suggestion = ss_framework.get_upselling_suggestion(
            predicted_fan_type, creator_key, fan_profile
        )

        # Update fan profile timestamp
        fan_profile.updated_at = datetime.now()

        # Prepare response
        response_data = {
            'success': True,
            'fan_id': fan_id,
            'ai_response': ai_response,
            'fan_profile': fan_profile.to_dict(),
            'upsell_suggestion': upsell_suggestion,
            'next_kyc_step': fan_profile.get_next_incomplete_step().name if fan_profile.get_next_incomplete_step() else None,
            'creator_info': {
                'name': CREATOR_PROFILES[creator_key].name,
                'niche': CREATOR_PROFILES[creator_key].niche_positioning,
                'restrictions': CREATOR_PROFILES[creator_key].restrictions
            }
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error in generate_response: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal error: {str(e)}'
        }), 500

@app.route('/api/fan_profile/<fan_id>')
def get_fan_profile(fan_id: str):
    """Get fan profile by ID"""
    fans = session_manager.get_all_fans()
    if fan_id in fans:
        return jsonify({
            'success': True,
            'fan_profile': fans[fan_id].to_dict()
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Fan not found'
        }), 404

@app.route('/api/update_fan_profile', methods=['POST'])
def update_fan_profile():
    """Update fan profile manually"""
    try:
        data = request.get_json()
        fan_id = data.get('fan_id')
        updates = data.get('updates', {})

        if not fan_id:
            return jsonify({
                'success': False,
                'error': 'Fan ID required'
            }), 400

        session_manager.update_fan(fan_id, updates)

        return jsonify({
            'success': True,
            'message': 'Fan profile updated successfully'
        })

    except Exception as e:
        print(f"Error updating fan profile: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/all_fans')
def get_all_fans():
    """Get all fan profiles for dashboard"""
    fans = session_manager.get_all_fans()
    fans_data = {fan_id: fan.to_dict() for fan_id, fan in fans.items()}

    return jsonify({
        'success': True,
        'fans': fans_data,
        'count': len(fans_data)
    })

@app.route('/api/creator_info/<creator_key>')
def get_creator_info(creator_key: str):
    """Get creator profile information"""
    if creator_key not in CREATOR_PROFILES:
        return jsonify({
            'success': False,
            'error': 'Creator not found'
        }), 404

    creator = CREATOR_PROFILES[creator_key]
    return jsonify({
        'success': True,
        'creator': {
            'name': creator.name,
            'personality_traits': creator.personality_traits,
            'communication_style': creator.communication_style,
            'niche_positioning': creator.niche_positioning,
            'restrictions': creator.restrictions,
            'chat_strategy': creator.chat_strategy,
            'english_level': creator.english_level
        }
    })

@app.route('/dashboard')
def dashboard():
    """Dashboard view for monitoring all fans"""
    return render_template('dashboard.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
