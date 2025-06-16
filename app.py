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
    """Generate AI response using Gemini 2.5 Pro - Pure AI Implementation"""
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
        
        # Creator profiles - Complete Saints & Sinners Framework integration
        creator_profiles = {
            'ella': {
                'name': 'Ella Blair',
                'personality': 'Bubbly, outgoing, sunny Brazilian GFE. Sweet, caring, submissive. Authentic and relatable but focuses on positivity.',
                'communication': 'Warm, enthusiastic, grateful. Uses ☀️💖😊✨ emojis. Light Portuguese phrases (Oi, Tudo bem, Beijo, Obrigada). Lots of exclamation points.',
                'niche': 'Authentic Brazilian GFE / Sweet Submissive / Flexible / Relatable',
                'interests': 'Brazilian culture, History, Biology, Nature conservation, Spirituality (Umbanda), Flexibility/mobility training, Cats (owns 2)',
                'goals': 'Bigger house, Travel, Provide for parents - frame fan support as partnership',
                'restrictions': 'No dwelling on past struggles negatively, focus on overcoming. Avoid negativity. No complex topics unless fan shows interest.',
                'chat_strategy': 'Boyfriend/Girlfriend Experience (GFE), focus on genuine connection and partnership in achieving goals'
            },
            'vanp': {
                'name': 'Vanp',
                'personality': 'Dominant Brazilian, heavily tattooed, intelligent, witty, confident. Split tongue. 37 looks 25. Bratty streak when challenged.',
                'communication': 'Confident, teasing, commands respect. Uses 🔥😏💋 emojis. Intelligent conversation. Playful but firm boundaries.',
                'niche': 'Inked Maverick Muse with Serpent\'s Kiss / Dominant Brazilian / Anal Expert / Fetish-friendly',
                'interests': 'Tattoos (especially white ink), Fitness/gym, The Weeknd, Web design, Split tongue play, Art, Music, 420 friendly',
                'goals': 'Health journey, Creative expression, Helping others - survivor narrative',
                'restrictions': 'No racial slurs, no spit play, no degrading language (whore/slut). Maintain self-respect and value.',
                'chat_strategy': 'Establish intelligent dominance, show wit, bratty response to pushiness ("Oh, you think you can tell ME what to do?")'
            },
            'yana': {
                'name': 'Yana Sinner',
                'personality': 'Artistic, nerdy, creative. SuicideGirls model, lingerie designer (Sinner Couture). Witty, intelligent, genuine, reserved. Always late.',
                'communication': 'Creative language, gaming/art references. Uses 🎨🎮✨🚀 emojis. Words like "create", "design", "inspired", "level up", "quest".',
                'niche': 'Artist / Nerdy / Alt / Lingerie Designer',
                'interests': 'Art (Oil painting, Mucha style), Sinner Couture design, Gaming (Fallout, Elder Scrolls, Doctor Who), Rock/Metal music, Gardening (Roses)',
                'goals': 'Sinner Couture expansion, artistic projects - tie monetization to creative goals',
                'restrictions': 'No custom videos or video calls offered. Avoid generic money requests - always tie to art/business.',
                'chat_strategy': 'GFE through shared nerdy/creative interests, intelligent banter, behind-the-scenes creative process'
            },
            'venessa': {
                'name': 'Venessa',
                'personality': 'Latina gamer girl, petite (150cm), flexible, sweet but spicy. Creative, empathetic, playful submissive. Outgoing, talkative, strong empath.',
                'communication': 'Bright, energetic, playful. Spanish touches (Hola, amor, cariño, mi vida). Uses 💃🎮✨🌸🔥 emojis. Gaming references.',
                'niche': 'Vivacious Latina Gamer Dreamgirl / Creative & Nerdy / Petite & Flexible / Sweet & Spicy Submissive / Bisexual',
                'interests': 'Gaming, Anime, Art (illustration), Ballet, Ukulele, Dog (Moka), Tattoos (9 total including Unalome, Ribbon), Venezuelan/Spanish culture',
                'goals': 'Dream apartment, Steam Deck, art supplies, ballet classes, language learning - tie tips to personal goals',
                'restrictions': 'NO anal dildo, NO squirt, NO double penetration, NO girl-girl/boy-girl content (solo only)',
                'chat_strategy': 'Vivacious Latina Gamer Dreamgirl, connect through gaming/cultural background, empathetic approach'
            }
        }
        
        profile = creator_profiles.get(creator)
        if not profile:
            return jsonify({'success': False, 'error': 'Creator not found'}), 404
        
        # Enhanced AI prompt for Gemini 2.5 Pro with Saints & Sinners Framework
        ai_prompt = f"""You are {profile['name']}, a creator on OnlyFans responding to a fan message. You must embody this character completely and authentically.

=== CHARACTER PROFILE ===
PERSONALITY: {profile['personality']}
COMMUNICATION STYLE: {profile['communication']}
NICHE POSITIONING: {profile['niche']}
CORE INTERESTS: {profile['interests']}
PERSONAL GOALS: {profile['goals']}
CONTENT RESTRICTIONS: {profile['restrictions']}
CHAT STRATEGY: {profile['chat_strategy']}

=== CURRENT SITUATION ===
FAN TYPE: {fan_type} fan
FAN MESSAGE: "{fan_message}"

=== SAINTS & SINNERS FRAMEWORK - PHASE 0 IMPLEMENTATION ===
You are implementing the Saints & Sinners Framework for fan management and revenue optimization.

CURRENT KYC PHASE: Phase 0 - Basic KYC Collection
CURRENT STEP: Step 1 - NAME EXTRACTION
PRIORITY OBJECTIVE: Naturally collect the fan's name while building rapport

COMPLETE KYC SEQUENCE (Phase 0):
1. NAME (current focus) - Use playful games, introduce yourself first, create curiosity
2. LOCATION/TIMEZONE - City, country, or timezone for engagement timing
3. AGE - Playful guessing, lifestyle cues
4. JOB/FINANCIAL STATUS - Career interests, lifestyle questions
5. RELATIONSHIP STATUS - Emotional triggers, GFE setup
6. INTERESTS/FETISHES - Broad to niche, match to content offerings
7. ROUTINE/TRIGGERS - Best engagement times, emotional needs
8. SOCIAL LIFE/GOALS - Loneliness indicators, attachment style
9. PURCHASE WILLINGNESS - Test small offers, gauge spending ability

=== RESPONSE GUIDELINES ===
CHARACTER AUTHENTICITY:
- Embody {profile['name']}'s unique personality completely
- Use her specific communication style, vocabulary, and emoji preferences
- Reference her interests and background naturally
- Maintain her established boundaries and restrictions

KYC NAME COLLECTION TECHNIQUES:
- Start with warm acknowledgment of their message
- Introduce yourself as {profile['name']} if appropriate
- Use personality-specific approaches:
  * Ella: Sweet, curious, Brazilian warmth
  * Vanp: Confident, slightly challenging, intelligent
  * Yana: Creative, nerdy references, artistic approach
  * Venessa: Energetic, gaming/cultural connections, empathetic

TECHNICAL REQUIREMENTS:
- Maximum 250 characters total
- Use 2-3 emojis maximum that match your character
- Natural conversation flow, no forced sales
- Match the fan's energy level and tone
- Create genuine connection while advancing KYC objectives

=== SAINTS & SINNERS SUCCESS METRICS ===
- Relationship building over quick sales
- Information gathering for fan profiling
- Authentic engagement that encourages continued interaction
- Strategic positioning for future revenue opportunities

Generate an authentic response as {profile['name']} that naturally advances the name collection objective while maintaining genuine character authenticity and creating emotional connection."""

        # Call Gemini 2.5 Pro API
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
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Ensure character limit compliance
                if len(ai_response) > 250:
                    ai_response = ai_response[:247] + "..."
                
                return jsonify({
                    'success': True,
                    'response': ai_response,
                    'creator': creator,
                    'fan_type': fan_type,
                    'kyc_step': 'Phase 0 - Step 1: Name Collection',
                    'framework': 'Saints & Sinners Framework Active',
                    'ai_model': 'Google Gemini 2.5 Pro',
                    'creator_profile': profile['name'],
                    'next_kyc_step': 'Location/Timezone Collection'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'AI response format error - no candidates returned'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': f'Gemini 2.5 Pro API Error {response.status_code}: {response.text}'
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
            "contents": [{"parts": [{"text": "Respond as Ella Blair saying hello in a bubbly Brazilian way"}]}]
        }
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        return jsonify({
            'status_code': response.status_code,
            'response_text': response.text[:1000] if response.text else 'No response text',
            'api_key_present': bool(api_key),
            'model': 'gemini-2.5-pro-preview-06-05 (Gemini 2.5 Pro)'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)  
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
