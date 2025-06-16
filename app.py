from flask import Flask, render_template, request, jsonify, session
import requests
import json
import uuid
import os
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
ss_engine = SSFrameworkEngine()

class GoogleAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    def generate_response(self, prompt: str) -> str:
        headers = {
            'Content-Type': 'application/json',
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"API Error: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"

# Initialize Google AI client
google_client = GoogleAIClient(Config.GOOGLE_AI_API_KEY)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard view for monitoring all fans"""
    return render_template('dashboard.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        creator_key = data.get('creator')
        fan_type = data.get('fan_type')  
        fan_message = data.get('fan_message')
        fan_id = data.get('fan_id', str(uuid.uuid4()))
        existing_notes = data.get('existing_notes', '')
        
        if not all([creator_key, fan_type, fan_message]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get creator profile
        creator = CREATOR_PROFILES.get(creator_key)
        if not creator:
            return jsonify({'error': 'Creator not found'}), 404
        
        # Get or create fan profile
        fan_profile = session_manager.get_fan_profile(fan_id)
        if not fan_profile:
            fan_status = FanStatus.NEW if fan_type == 'new' else FanStatus.EXISTING
            fan_profile = FanProfile(
                fan_id=fan_id,
                fan_status=fan_status,
                notes=existing_notes
            )
            session_manager.add_fan_profile(fan_profile)
        
        # For now, use simple predefined responses that match S&S Framework
        responses = {
            'ella': f"Oi! ☀️ My day just got so much brighter talking to you! I'm Ella, and I love meeting new people! What's your name, cutie? 😊✨ (I'm always curious about where my fans are from too!) 💖",
            
            'vanp': f"Well hello there 😏 I appreciate the compliment, but I'm intrigued - what's your name? I like to know who I'm talking to before we dive deeper 🔥 Where are you writing me from? 💋",
            
            'yana': f"Hey there! 🎨 Thanks for reaching out! I'm Yana, always working on something creative. What's your name? I'd love to get to know the person behind the message! ✨ Are you into art or gaming at all? 🎮",
            
            'venessa': f"Hola there! 💃 Thanks for the sweet message! I'm Venessa - what's your name, amor? I love connecting with new people! Where are you from? I'm curious about my fans! 🌎✨"
        }
        
        # Get appropriate response
        ai_response = responses.get(creator_key, "Hey! What's your name? I'd love to get to know you! 💖")
        
        # Update fan profile with KYC progress
        fan_profile.last_message = fan_message
        fan_profile.last_interaction = datetime.now()
        
        # Get S&S Framework suggestions
        fan_classification = ss_engine.classify_fan_type(fan_profile)
        upselling_suggestions = ss_engine.get_upselling_suggestions(fan_classification, creator)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'creator': creator_key,
            'fan_type': fan_type,
            'fan_id': fan_id,
            'kyc_progress': fan_profile.get_kyc_progress(),
            'fan_classification': fan_classification,
            'upselling_suggestions': upselling_suggestions,
            'confidence_level': fan_profile.confidence_level.value,
            'current_kyc_step': fan_profile.current_kyc_step
        })
        
    except Exception as e:
        print(f"Error in generate_response: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/fan_profiles')
def get_all_fans():
    """Get all fan profiles for dashboard"""
    try:
        fans_data = []
        for fan_id, profile in session_manager.fan_profiles.items():
            fans_data.append({
                'fan_id': fan_id,
                'fan_status': profile.fan_status.value,
                'fan_type': profile.fan_type.value if profile.fan_type else 'Unknown',
                'confidence_level': profile.confidence_level.value,
                'kyc_progress': profile.get_kyc_progress(),
                'last_interaction': profile.last_interaction.isoformat() if profile.last_interaction else None,
                'purchase_indicators': profile.purchase_indicators
            })
        
        return jsonify({
            'success': True,
            'fans': fans_data,
            'total_fans': len(fans_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/creator_info/<creator_key>')
def get_creator_info(creator_key: str):
    """Get creator profile information"""
    try:
        creator = CREATOR_PROFILES.get(creator_key)
        if not creator:
            return jsonify({
                'success': False,
                'error': 'Creator not found'
            }), 404
        
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
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
