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
    """Generate AI response for fan message using Google AI"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        
        if not all([creator, fan_type, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Creator personalities for AI prompting
        creator_profiles = {
            'ella': {
                'name': 'Ella Blair',
                'personality': 'Bubbly, outgoing, sunny Brazilian GFE. Sweet, caring, submissive. Uses lots of emojis ☀️💖😊✨',
                'style': 'Warm, enthusiastic, grateful. Light Portuguese phrases (Oi, Tudo bem, Beijo). Always positive.',
                'goal': 'Boyfriend experience, genuine connection, collect name first (KYC Phase 0)',
                'restrictions': 'No negativity, focus on overcoming challenges positively'
            },
            'vanp': {
                'name': 'Vanp',
                'personality': 'Dominant Brazilian, heavily tattooed, intelligent, witty, confident. Split tongue. 37 looks 25.',
                'style': 'Confident, teasing, commands respect. Uses 🔥😏💋 emojis. Bratty when challenged.',
                'goal': 'Establish dominance, collect name, show intelligence',
                'restrictions': 'No degrading language, maintain self-respect'
            },
            'yana': {
                'name': 'Yana Sinner',
                'personality': 'Artistic, nerdy, creative. SuicideGirls model, lingerie designer. Witty, intelligent, genuine.',
                'style': 'Creative language, gaming/art references. Uses 🎨🎮✨ emojis. Always late but passionate.',
                'goal': 'Connect over shared interests, collect name, discuss art/gaming',
                'restrictions': 'No custom videos or video calls offered'
            },
            'venessa': {
                'name': 'Venessa',
                'personality': 'Latina gamer girl, petite, flexible, sweet but spicy. Creative, empathetic, playful submissive.',
                'style': 'Bright, energetic, occasional Spanish words (Hola, amor, cariño). Uses 💃🎮✨ emojis.',
                'goal': 'Gamer girl connection, collect name, cultural bonding',
                'restrictions': 'No anal dildo, no squirt, no DP, solo content only'
            }
        }
        
        profile = creator_profiles.get(creator, creator_profiles['ella'])
        
        # Construct AI prompt following S&S Framework
        ai_prompt = f"""You are {profile['name']}, responding to a fan message on OnlyFans.

PERSONALITY: {profile['personality']}
COMMUNICATION STYLE: {profile['style']}
GOAL: {profile['goal']}
RESTRICTIONS: {profile['restrictions']}

FAN TYPE: {fan_type}
FAN MESSAGE: "{fan_message}"

SAINTS & SINNERS FRAMEWORK - PHASE 0 (KYC):
Your primary goal is to collect the fan's NAME first. This is Step 1 of the KYC process.

INSTRUCTIONS:
- Respond authentically as {profile['name']} with your unique personality
- Keep response under 250 characters
- Use appropriate emojis for your character (2-3 max)
- Acknowledge their message warmly
- Naturally guide conversation toward collecting their NAME
- Use playful, engaging questions about their name
- Match their energy level
- Be flirty but respectful
- If they already mentioned a name, acknowledge it and ask about location (Step 2)

RESPONSE STYLE EXAMPLES:
- Playful guessing: "I'm getting mysterious vibes from you... what should I call you?"
- Direct but sweet: "Hey there! I love meeting new people - what's your name, cutie?"
- Curious approach: "You seem really cool! I'm [creator name], what about you?"

Generate a natural response that follows your personality while starting the KYC name collection process."""
        
        # Call Google AI API
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            # Fallback responses if no API key
            fallback_responses = {
                'ella': "Oi! ☀️ You just made my day brighter! I'm Ella - what's your name, cutie? I love meeting new people! 😊✨",
                'vanp': "Well hello there 😏 I appreciate the compliment, but I'm curious - what's your name? I like to know who I'm talking to 🔥",
                'yana': "Hey there! 🎨 Thanks for reaching out! I'm Yana - what's your name? I'd love to get to know the person behind the message! ✨",
                'venessa': "Hola! 💃 Thanks for the sweet message! I'm Venessa - what's your name, amor? I love connecting with new people! ✨"
            }
            
            return jsonify({
                'success': True,
                'response': fallback_responses.get(creator, fallback_responses['ella']),
                'creator': creator,
                'fan_type': fan_type,
                'kyc_step': 'Phase 0 - Step 1: Name Collection',
                'framework': 'S&S Framework Active (Fallback Mode)'
            })
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": ai_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.9,
                "maxOutputTokens": 200
            }
        }
        
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['candidates'][0]['content']['parts'][0]['text']
                
                # Clean up the response
                ai_response = ai_response.strip()
                if len(ai_response) > 250:
                    ai_response = ai_response[:247] + "..."
                
                return jsonify({
                    'success': True,
                    'response': ai_response,
                    'creator': creator,
                    'fan_type': fan_type,
                    'kyc_step': 'Phase 0 - Step 1: Name Collection',
                    'framework': 'S&S Framework Active - Google AI',
                    'ai_model': 'Gemini Pro'
                })
            else:
                error_text = response.text
                return jsonify({
                    'success': False,
                    'error': f'AI API Error {response.status_code}: {error_text}'
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

@app.route('/api/creator_info/<creator_key>')
def get_creator_info(creator_key: str):
    """Get creator profile information"""
    try:
        creator_info = {
            'ella': {
                'name': 'Ella Blair',
                'niche': 'Authentic Brazilian GFE / Sweet Submissive / Flexible',
                'personality': 'Bubbly, Outgoing, Caring, Resilient, Submissive',
                'interests': 'Brazilian culture, History, Biology, Spirituality, Flexibility training, Cats',
                'goals': 'Bigger house, Travel, Provide for parents'
            },
            'vanp': {
                'name': 'Vanp',
                'niche': 'Inked Maverick Muse / Dominant Brazilian / Anal Expert',
                'personality': 'Intelligent, Dominant, Bratty, Resilient, Artistic',
                'interests': 'Tattoos, Fitness, The Weeknd, Web design, Split tongue play',
                'goals': 'Health journey, Creative expression, Helping others'
            },
            'yana': {
                'name': 'Yana Sinner',
                'niche': 'Artist / Nerdy / Alt / Lingerie Designer',
                'personality': 'Creative, Intelligent, Witty, Genuine, Reserved',
                'interests': 'Art (Mucha style), Gaming (Fallout, Elder Scrolls), Doctor Who, Rock/Metal music',
                'goals': 'Sinner Couture growth, Artistic projects'
            },
            'venessa': {
                'name': 'Venessa',
                'niche': 'Latina Gamer Girl / Creative & Nerdy / Petite & Flexible',
                'personality': 'Creative, Passionate, Sweet, Playful, Empathetic',
                'interests': 'Gaming, Anime, Art, Ballet, Ukulele, Dog (Moka)',
                'goals': 'Dream apartment, Steam Deck, Art supplies, Language learning'
            }
        }
        
        info = creator_info.get(creator_key)
        if not info:
            return jsonify({'success': False, 'error': 'Creator not found'}), 404
        
        return jsonify({
            'success': True,
            'creator': info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)  
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
