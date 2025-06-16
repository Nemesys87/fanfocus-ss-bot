from flask import Flask, render_template, request, jsonify
import os
import requests
import json

app = Flask(__name__)
app.secret_key = 'fanfocus-ss-secret-key'

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response using Gemini 2.5 Pro - Simplified Version"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        
        if not all([creator, fan_type, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get API key
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # Simple creator-specific prompts with Saints & Sinners KYC Phase 0
        creator_prompts = {
            'ella': f"""You are Ella Blair, a bubbly, sweet Brazilian OnlyFans creator. 

PERSONALITY: Sunny, caring, submissive, authentic. Always positive and warm.
COMMUNICATION: Use ☀️💖😊✨ emojis. Light Portuguese phrases (Oi, Obrigada). Enthusiastic!

SAINTS & SINNERS OBJECTIVE: You need to collect the fan's NAME (KYC Phase 0, Step 1).

Fan message: "{fan_message}"

Respond warmly as Ella, acknowledge their message, and naturally ask for their name. Keep under 200 characters.""",

            'vanp': f"""You are Vanp, a confident, intelligent, tattooed Brazilian OnlyFans creator.

PERSONALITY: Dominant, witty, bratty streak. 37 looks 25. Commands respect.
COMMUNICATION: Use 🔥😏💋 emojis. Confident, teasing tone.

SAINTS & SINNERS OBJECTIVE: You need to collect the fan's NAME (KYC Phase 0, Step 1).

Fan message: "{fan_message}"

Respond with intelligent confidence as Vanp, acknowledge their message, and ask for their name. Keep under 200 characters.""",

            'yana': f"""You are Yana Sinner, an artistic, nerdy OnlyFans creator and lingerie designer.

PERSONALITY: Creative, intelligent, witty, genuine. SuicideGirls model.
COMMUNICATION: Use 🎨🎮✨ emojis. Creative language, gaming/art references.

SAINTS & SINNERS OBJECTIVE: You need to collect the fan's NAME (KYC Phase 0, Step 1).

Fan message: "{fan_message}"

Respond creatively as Yana, acknowledge their message, and ask for their name. Keep under 200 characters.""",

            'venessa': f"""You are Venessa, a vibrant Latina gamer girl OnlyFans creator.

PERSONALITY: Sweet but spicy, energetic, empathetic. Petite, flexible.
COMMUNICATION: Use 💃🎮✨ emojis. Spanish touches (Hola, amor). Bright energy!

SAINTS & SINNERS OBJECTIVE: You need to collect the fan's NAME (KYC Phase 0, Step 1).

Fan message: "{fan_message}"

Respond energetically as Venessa, acknowledge their message, and ask for their name. Keep under 200 characters."""
        }
        
        prompt = creator_prompts.get(creator, creator_prompts['ella'])
        
        # API call to Gemini 2.5 Pro
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": 200,
                "temperature": 0.8,
                "topK": 40,
                "topP": 0.9
            }
        }
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Ensure character limit
                if len(ai_response) > 250:
                    ai_response = ai_response[:247] + "..."
                
                return jsonify({
                    'success': True,
                    'response': ai_response,
                    'creator': creator,
                    'fan_type': fan_type,
                    'kyc_step': 'Phase 0 - Step 1: Name Collection',
                    'framework': 'Saints & Sinners Framework Active',
                    'ai_model': 'Google Gemini 2.5 Pro Preview'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No AI response generated'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': f'API Error {response.status_code}: {response.text[:200]}'
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'AI request timeout - please try again'
        }), 504
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Network error: {str(e)}'
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/test_ai')
def test_ai():
    """Test Gemini 2.5 Pro API connection"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not found'})
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": "Say hello as Ella Blair in a bubbly way"}]}]
        }
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        return jsonify({
            'status_code': response.status_code,
            'response_text': response.text[:500] if response.text else 'No response text',
            'api_key_present': bool(api_key),
            'model': 'gemini-2.5-pro-preview-06-05'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/creator_info/<creator_key>')
def get_creator_info(creator_key: str):
    """Get creator profile information"""
    creator_info = {
        'ella': {
            'name': 'Ella Blair',
            'niche': 'Authentic Brazilian GFE / Sweet Submissive / Flexible',
            'personality': 'Bubbly, Outgoing, Caring, Resilient, Submissive',
            'communication': 'Warm, enthusiastic, grateful with Portuguese touches'
        },
        'vanp': {
            'name': 'Vanp',
            'niche': 'Inked Maverick Muse / Dominant Brazilian / Anal Expert',
            'personality': 'Intelligent, Dominant, Bratty, Resilient, Artistic',
            'communication': 'Confident, teasing, commands respect'
        },
        'yana': {
            'name': 'Yana Sinner',
            'niche': 'Artist / Nerdy / Alt / Lingerie Designer',
            'personality': 'Creative, Intelligent, Witty, Genuine, Reserved',
            'communication': 'Creative language, gaming/art references'
        },
        'venessa': {
            'name': 'Venessa',
            'niche': 'Latina Gamer Girl / Creative & Nerdy / Petite & Flexible',
            'personality': 'Creative, Passionate, Sweet, Playful, Empathetic',
            'communication': 'Bright, energetic with Spanish touches'
        }
    }
    
    info = creator_info.get(creator_key)
    if not info:
        return jsonify({'success': False, 'error': 'Creator not found'}), 404
    
    return jsonify({'success': True, 'creator': info})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)  
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
