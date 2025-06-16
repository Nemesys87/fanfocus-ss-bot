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
    """Generate AI response for fan message"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        
        if not all([creator, fan_type, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Smart fallback responses that adapt to fan message
        def generate_smart_response(creator, fan_message, fan_type):
            # Analyze fan message for context
            fan_lower = fan_message.lower()
            
            greeting_words = ['hi', 'hey', 'hello', 'hola', 'oi', 'good morning', 'good evening']
            compliment_words = ['beautiful', 'gorgeous', 'sexy', 'hot', 'cute', 'stunning', 'amazing']
            question_words = ['how', 'what', 'where', 'when', 'why', 'are you', 'do you']
            time_words = ['day', 'morning', 'evening', 'night', 'today']
            
            is_greeting = any(word in fan_lower for word in greeting_words)
            is_compliment = any(word in fan_lower for word in compliment_words)
            is_question = any(word in fan_lower for word in question_words)
            mentions_time = any(word in fan_lower for word in time_words)
            
            if creator == 'ella':
                if is_greeting and is_compliment and mentions_time:
                    return "Oi! ☀️ You just made my day so much brighter with those sweet words! I'm Ella - what's your name, cutie? I love meeting kind people like you! 😊✨"
                elif is_greeting and is_compliment:
                    return "Oi! ☀️ Obrigada for the lovely compliment! You're so sweet! I'm Ella - what's your name? I'd love to get to know you better! 💖😊"
                elif is_greeting and mentions_time:
                    return "Hey there! ☀️ My day is going wonderfully, especially now that you're here! I'm Ella - what's your name? How's your day treating you? 😊✨"
                elif is_greeting:
                    return "Oi! ☀️ I'm Ella and I'm so happy you reached out! What's your name? I love meeting new people and making connections! 💖😊"
                elif is_compliment:
                    return "Aww, obrigada! 😊 You're making me blush! I'm Ella - what should I call you? I love connecting with sweet people like you! ☀️💖"
                elif is_question and mentions_time:
                    return "My day is absolutely amazing, especially with lovely messages like yours! ☀️ I'm Ella - what's your name? Tell me about your day too! 😊✨"
                else:
                    return "Oi! ✨ Thanks for reaching out to me! I'm Ella - what's your name? I'm always excited to meet new people and hear their stories! ☀️😊"
                    
            elif creator == 'vanp':
                if is_greeting and is_compliment:
                    return "Well hello there 😏 I appreciate the compliment, but I'm intrigued - what's your name? I like to know who I'm talking to before we go further 🔥💋"
                elif is_greeting and mentions_time:
                    return "Hey there 😏 My day's been good, but it just got more interesting. I'm Vanp - what's your name? I prefer knowing who I'm dealing with 🔥"
                elif is_greeting:
                    return "Hey 😏 I'm Vanp. You caught my attention - what's your name? I don't usually chat with mysterious strangers for long 🔥"
                elif is_compliment:
                    return "Mmm, I like the confidence 😏 But tell me - what's your name? I appreciate the words, but I need to know who's behind them 🔥💋"
                elif is_question and mentions_time:
                    return "My day? It's been productive, and now it's getting more entertaining 😏 I'm Vanp - what's your name? And more importantly, how's yours going? 🔥"
                else:
                    return "Interesting approach... 😏 I'm Vanp. What's your name? You've got my attention, but I like to know who I'm talking to 🔥"
                    
            elif creator == 'yana':
                if is_greeting and is_compliment:
                    return "Hey there! 🎨 Thanks for the sweet words! I'm Yana - what's your name? Are you into art or gaming at all? I love meeting people with good taste! ✨"
                elif is_greeting and mentions_time:
                    return "Hey! 🎨 My day's been creative and productive! I'm Yana - what's your name? Are you having a good day? What's keeping you busy? ✨"
                elif is_greeting:
                    return "Hey! 🎨 I'm Yana, nice to meet you! What's your name? I'm always curious about the people who reach out - any cool hobbies? ✨"
                elif is_compliment:
                    return "Aww thank you! 🎨 I appreciate that! I'm Yana - what should I call you? I love meeting people who notice the details! ✨😊"
                elif is_question and mentions_time:
                    return "My day's been great! Been working on some new designs 🎨 I'm Yana - what's your name? Tell me about your day! Are you creative too? ✨"
                else:
                    return "Hey there! 🎨 I'm Yana - what's your name? I'm always excited to connect with new people and learn about their interests! ✨"
                    
            elif creator == 'venessa':
                if is_greeting and is_compliment:
                    return "Hola! 💃 Gracias for the sweet message! You're making me smile! I'm Venessa - what's your name, amor? Where are you from? ✨🌎"
                elif is_greeting and mentions_time:
                    return "Hey there! 💃 My day's been amazing - been gaming and creating! I'm Venessa - what's your name? How's your day going? 🎮✨"
                elif is_greeting:
                    return "Hola! 💃 I'm Venessa - what's your name? I love meeting new people! Are you a gamer by any chance? 🎮✨"
                elif is_compliment:
                    return "Aww, that's so sweet! 💃 You're making me blush! I'm Venessa - what should I call you, amor? You seem really nice! ✨💖"
                elif is_question and mentions_time:
                    return "My day's been fantastic! Been playing some games and working on art 💃 I'm Venessa - what's your name? Tell me about your day! 🎮✨"
                else:
                    return "Hola! 💃 Thanks for reaching out! I'm Venessa - what's your name? I'm excited to get to know you better! ✨"
            
            # Default fallback
            return "Hey! What's your name? I'd love to get to know you! 💖"
        
        # Try Google AI API first, then fallback to smart responses
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        
        if api_key:
            try:
                # Creator personalities for AI prompting
                creator_profiles = {
                    'ella': {
                        'name': 'Ella Blair',
                        'personality': 'Bubbly, outgoing, sunny Brazilian GFE. Sweet, caring, submissive. Uses lots of emojis ☀️💖😊✨',
                        'style': 'Warm, enthusiastic, grateful. Light Portuguese phrases (Oi, Tudo bem, Beijo). Always positive.',
                        'restrictions': 'No negativity, focus on overcoming challenges positively'
                    },
                    'vanp': {
                        'name': 'Vanp',
                        'personality': 'Dominant Brazilian, heavily tattooed, intelligent, witty, confident. Split tongue. 37 looks 25.',
                        'style': 'Confident, teasing, commands respect. Uses 🔥😏💋 emojis. Bratty when challenged.',
                        'restrictions': 'No degrading language, maintain self-respect'
                    },
                    'yana': {
                        'name': 'Yana Sinner',
                        'personality': 'Artistic, nerdy, creative. SuicideGirls model, lingerie designer. Witty, intelligent, genuine.',
                        'style': 'Creative language, gaming/art references. Uses 🎨🎮✨ emojis. Always late but passionate.',
                        'restrictions': 'No custom videos or video calls offered'
                    },
                    'venessa': {
                        'name': 'Venessa',
                        'personality': 'Latina gamer girl, petite, flexible, sweet but spicy. Creative, empathetic, playful submissive.',
                        'style': 'Bright, energetic, occasional Spanish words (Hola, amor, cariño). Uses 💃🎮✨ emojis.',
                        'restrictions': 'No anal dildo, no squirt, no DP, solo content only'
                    }
                }
                
                profile = creator_profiles.get(creator, creator_profiles['ella'])
                
                ai_prompt = f"""You are {profile['name']}, responding to a fan message on OnlyFans.

PERSONALITY: {profile['personality']}
COMMUNICATION STYLE: {profile['style']}
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
- Match their energy level
- Be flirty but respectful

Generate a natural response that follows your personality while starting the KYC name collection process."""
                
                headers = {'Content-Type': 'application/json'}
                payload = {
                    "contents": [{"parts": [{"text": ai_prompt}]}],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.9,
                        "maxOutputTokens": 200
                    }
                }
                
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    
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
                
            except Exception as e:
                print(f"Google AI API failed: {str(e)}")
                # Fall through to smart fallback
        
        # Use smart fallback system
        response_text = generate_smart_response(creator, fan_message, fan_type)
        
        return jsonify({
            'success': True,
            'response': response_text,
            'creator': creator,
            'fan_type': fan_type,
            'kyc_step': 'Phase 0 - Step 1: Name Collection',
            'framework': 'S&S Framework Active - Smart Engine',
            'ai_model': 'Smart Logic Engine'
        })
        
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
                'goals': 'Bigger house, Travel, Provide for parents',
                'communication': 'Warm, enthusiastic, grateful with Portuguese touches'
            },
            'vanp': {
                'name': 'Vanp',
                'niche': 'Inked Maverick Muse / Dominant Brazilian / Anal Expert',
                'personality': 'Intelligent, Dominant, Bratty, Resilient, Artistic',
                'interests': 'Tattoos, Fitness, The Weeknd, Web design, Split tongue play',
                'goals': 'Health journey, Creative expression, Helping others',
                'communication': 'Confident, teasing, commands respect'
            },
            'yana': {
                'name': 'Yana Sinner',
                'niche': 'Artist / Nerdy / Alt / Lingerie Designer',
                'personality': 'Creative, Intelligent, Witty, Genuine, Reserved',
                'interests': 'Art (Mucha style), Gaming (Fallout, Elder Scrolls), Doctor Who, Rock/Metal music',
                'goals': 'Sinner Couture growth, Artistic projects',
                'communication': 'Creative language, gaming/art references'
            },
            'venessa': {
                'name': 'Venessa',
                'niche': 'Latina Gamer Girl / Creative & Nerdy / Petite & Flexible',
                'personality': 'Creative, Passionate, Sweet, Playful, Empathetic',
                'interests': 'Gaming, Anime, Art, Ballet, Ukulele, Dog (Moka)',
                'goals': 'Dream apartment, Steam Deck, Art supplies, Language learning',
                'communication': 'Bright, energetic with Spanish touches'
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

@app.route('/dashboard')
def dashboard():
    """Dashboard view for monitoring"""
    return render_template('dashboard.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)  
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
