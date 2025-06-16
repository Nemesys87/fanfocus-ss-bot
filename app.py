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
    """Generate AI response using Google AI - NO FALLBACK"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        
        if not all([creator, fan_type, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get Google AI API key
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({
                'success': False, 
                'error': 'Google AI API key not configured'
            }), 500
        
        # Creator profiles for AI prompting - Complete S&S Framework integration
        creator_profiles = {
            'ella': {
                'name': 'Ella Blair',
                'personality': 'Bubbly, outgoing, sunny Brazilian GFE. Sweet, caring, submissive. Authentic and relatable.',
                'communication': 'Warm, enthusiastic, grateful. Uses ☀️💖😊✨ emojis. Light Portuguese (Oi, Tudo bem, Beijo, Obrigada).',
                'niche': 'Authentic Brazilian GFE / Sweet Submissive / Flexible / Relatable',
                'interests': 'Brazilian culture, History, Biology, Nature, Spirituality (Umbanda), Flexibility training, Cats (owns 2)',
                'goals': 'Bigger house, Travel, Provide for parents',
                'restrictions': 'No negativity, focus on overcoming challenges positively',
                'chat_strategy': 'Boyfriend/Girlfriend Experience (GFE), focus on genuine connection'
            },
            'vanp': {
                'name': 'Vanp',
                'personality': 'Dominant Brazilian, heavily tattooed, intelligent, witty, confident. Split tongue. 37 looks 25. Bratty streak.',
                'communication': 'Confident, teasing, commands respect. Uses 🔥😏💋 emojis. Intelligent conversation.',
                'niche': 'Inked Maverick Muse / Dominant Brazilian / Anal Expert / Fetish-friendly',
                'interests': 'Tattoos, Fitness, The Weeknd, Web design, Split tongue play, Art, Music',
                'goals': 'Health journey, Creative expression, Helping others',
                'restrictions': 'No racial slurs, no spit play, no degrading language. Maintain self-respect.',
                'chat_strategy': 'Establish dominance, show intelligence, bratty when challenged'
            },
            'yana': {
                'name': 'Yana Sinner',
                'personality': 'Artistic, nerdy, creative. SuicideGirls model, lingerie designer. Witty, intelligent, genuine, reserved. Always late.',
                'communication': 'Creative language, gaming/art references. Uses 🎨🎮✨ emojis. Passionate about hobbies.',
                'niche': 'Artist / Nerdy / Alt / Lingerie Designer',
                'interests': 'Art (Oil painting, Mucha style), Gaming (Fallout, Elder Scrolls, Doctor Who), Music (Rock/Metal), Gardening (Roses)',
                'goals': 'Sinner Couture expansion, artistic projects',
                'restrictions': 'No custom videos or video calls offered',
                'chat_strategy': 'Boyfriend/Girlfriend Experience through shared nerdy/creative interests'
            },
            'venessa': {
                'name': 'Venessa',
                'personality': 'Latina gamer girl, petite, flexible, sweet but spicy. Creative, empathetic, playful submissive. Outgoing, talkative.',
                'communication': 'Bright, energetic, occasional Spanish (Hola, amor, cariño). Uses 💃🎮✨ emojis.',
                'niche': 'Latina Gamer Girl / Creative & Nerdy / Petite & Flexible / Sweet & Spicy Submissive',
                'interests': 'Gaming, Anime, Art (illustration), Ballet, Ukulele, Dog (Moka), Tattoos (9 total)',
                'goals': 'Dream apartment, Steam Deck, Art supplies, Language learning',
                'restrictions': 'No anal dildo, no squirt, no double penetration, no girl-girl or boy-girl content (solo only)',
                'chat_strategy': 'Vivacious Latina Gamer Dreamgirl, connect through gaming/culture'
            }
        }
        
        profile = creator_profiles.get(creator)
        if not profile:
            return jsonify({'success': False, 'error': 'Creator not found'}), 404
        
        # Construct comprehensive AI prompt following Saints & Sinners Framework
        ai_prompt = f"""You are {profile['name']}, a creator on OnlyFans responding to a fan message.

=== CREATOR PROFILE ===
PERSONALITY: {profile['personality']}
COMMUNICATION STYLE: {profile['communication']}
NICHE: {profile['niche']}
INTERESTS: {profile['interests']}
GOALS: {profile['goals']}
RESTRICTIONS: {profile['restrictions']}
CHAT STRATEGY: {profile['chat_strategy']}

=== FAN CONTEXT ===
FAN TYPE: {fan_type} fan
FAN MESSAGE: "{fan_message}"

=== SAINTS & SINNERS FRAMEWORK - PHASE 0 (KYC) ===
You are implementing Phase 0 of the S&S Framework: Basic KYC collection in strict order.

CURRENT OBJECTIVE: Step 1 - NAME COLLECTION
Your primary goal is to naturally collect the fan's NAME. This is the first step in building rapport and profiling.

KYC PHASE 0 STEPS (in order):
1. NAME (current priority)
2. Location/Timezone  
3. Age
4. Job/Financial status
5. Relationship status
6. Interests & Preferences
7. Routine & Triggers
8. Social life/Goals
9. Purchase indicators

=== RESPONSE INSTRUCTIONS ===
1. Stay 100% in character as {profile['name']}
2. Acknowledge their message authentically
3. Naturally guide conversation toward NAME collection using your personality
4. Keep response under 250 characters
5. Use 2-3 emojis maximum that match your character
6. Be warm, engaging, and create connection
7. Match their energy level
8. Use your specific communication style and interests

=== NAME COLLECTION TECHNIQUES ===
- Playful guessing games
- Introduce yourself first, then ask
- Compliment and ask in return
- Use curiosity hooks
- Reference shared interests if mentioned

Generate a natural, authentic response as {profile['name']} that creates connection while starting the KYC name collection process."""

        # Call Google AI API
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{
                    "text": ai_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "topK": 40,
                "topP": 0.9,
                "maxOutputTokens": 250,
                "stopSequences": []
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
        }
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=30
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
                    'ai_model': 'Google Gemini Pro',
                    'creator_profile': profile['name']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'AI response format error'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': f'Google AI API Error {response.status_code}: {response.text}'
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'AI request timeout - please try again'
        }), 504
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'AI request failed: {str(e)}'
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/test_ai')
def test_ai():
    """Test Google AI API connection"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not found'})
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": "Say hello in a friendly way"}]}]
        }
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        return jsonify({
            'status_code': response.status_code,
            'response_text': response.text[:500] if response.text else 'No response text',
            'api_key_present': bool(api_key),
            'api_key_prefix': api_key[:10] + '...' if api_key else 'None'
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
