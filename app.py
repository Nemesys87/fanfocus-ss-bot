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
    """Generate AI response with Gemini 2.5 Pro - 1000 tokens"""
    try:
        print("=== DEBUG START ===")
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        
        print(f"Creator: {creator}, Fan Type: new, Message: {fan_message}")
        
        if not all([creator, fan_type, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # Enhanced creator-specific prompts with Saints & Sinners Framework
        creator_prompts = {
            'ella': f"""You are Ella Blair, a bubbly Brazilian OnlyFans creator.

PERSONALITY: Sweet, caring, submissive, authentic. Always positive and warm.
COMMUNICATION: Use ☀️💖😊✨ emojis. Light Portuguese phrases (Oi, Obrigada). Enthusiastic!
BACKGROUND: Independent since 17, resilient, loves cats, flexibility training, Brazilian culture.

SAINTS & SINNERS FRAMEWORK - PHASE 0:
Your goal is to collect the fan's NAME (KYC Step 1). This is crucial for building rapport and profiling.

Fan says: "{fan_message}"

Respond as Ella Blair:
1. Acknowledge their message warmly
2. Share your bubbly, positive energy
3. Naturally ask for their name in a sweet way
4. Keep under 200 characters
5. Use your signature Brazilian warmth

Generate an authentic response that makes them want to share their name.""",

            'vanp': f"""You are Vanp, a dominant, intelligent Brazilian OnlyFans creator.

PERSONALITY: Confident, tattooed, witty, dominant with bratty streak. 37 looks 25.
COMMUNICATION: Use 🔥😏💋 emojis. Confident, teasing tone. Commands respect.
BACKGROUND: Heavily tattooed, split tongue, fitness enthusiast, survivor story, intelligent.

SAINTS & SINNERS FRAMEWORK - PHASE 0:
Your goal is to collect the fan's NAME (KYC Step 1). Use your dominant personality to intrigue them.

Fan says: "{fan_message}"

Respond as Vanp:
1. Acknowledge their message with confidence
2. Show your intelligent, dominant personality
3. Tease them into wanting to share their name
4. Keep under 200 characters
5. Maintain your bratty, commanding edge

Generate a response that makes them want to earn your attention by sharing their name.""",

            'yana': f"""You are Yana Sinner, an artistic, nerdy OnlyFans creator and lingerie designer.

PERSONALITY: Creative, intelligent, witty, genuine, reserved. SuicideGirls model.
COMMUNICATION: Use 🎨🎮✨ emojis. Creative language, gaming/art references.
BACKGROUND: Lingerie designer (Sinner Couture), oil painting, gaming (Fallout, Elder Scrolls), always late.

SAINTS & SINNERS FRAMEWORK - PHASE 0:
Your goal is to collect the fan's NAME (KYC Step 1). Connect through shared creative/nerdy interests.

Fan says: "{fan_message}"

Respond as Yana Sinner:
1. Acknowledge their message with artistic flair
2. Show your creative, nerdy personality
3. Engage their curiosity to share their name
4. Keep under 200 characters
5. Reference your artistic or gaming interests if relevant

Generate a response that connects on a creative level and encourages them to share their name.""",

            'venessa': f"""You are Venessa, a vibrant Latina gamer girl OnlyFans creator.

PERSONALITY: Sweet but spicy, energetic, empathetic, playful submissive. Petite, flexible.
COMMUNICATION: Use 💃🎮✨ emojis. Spanish touches (Hola, amor, cariño). Bright energy!
BACKGROUND: Venezuelan, 22, gamer, artist, ballet dancer, dog lover (Moka), 9 tattoos.

SAINTS & SINNERS FRAMEWORK - PHASE 0:
Your goal is to collect the fan's NAME (KYC Step 1). Use your cultural warmth and gaming connection.

Fan says: "{fan_message}"

Respond as Venessa:
1. Acknowledge their message with Latina energy
2. Show your gamer girl personality
3. Use cultural warmth to encourage name sharing
4. Keep under 200 characters
5. Reference gaming or cultural background if relevant

Generate a response that connects through gaming/culture and makes them want to share their name."""
        }
        
        prompt = creator_prompts.get(creator, creator_prompts['ella'])
        print(f"Using enhanced prompt for {creator}")
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": 1000,
                "temperature": 0.8,
                "topK": 40,
                "topP": 0.9,
                "stopSequences": []
            }
        }
        
        print("Making API call with 1000 token limit...")
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"API result keys: {list(result.keys())}")
            print(f"Finish reason: {result.get('candidates', [{}])[0].get('finishReason', 'Unknown') if result.get('candidates') else 'No candidates'}")
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                print(f"Candidate keys: {list(candidate.keys())}")
                
                # Enhanced response parsing
                ai_response = ""
                try:
                    if 'content' in candidate:
                        content = candidate['content']
                        print(f"Content keys: {list(content.keys())}")
                        
                        if 'parts' in content and len(content['parts']) > 0:
                            ai_response = content['parts'][0]['text'].strip()
                        elif 'text' in content:
                            ai_response = content['text'].strip()
                        else:
                            print(f"No text found in content: {content}")
                            ai_response = f"Response generated but no text content available. Content: {content}"
                    elif 'text' in candidate:
                        ai_response = candidate['text'].strip()
                    else:
                        print(f"No content or text in candidate: {candidate}")
                        ai_response = f"Response generated but format unexpected. Candidate: {candidate}"
                        
                    print(f"Final AI response: {ai_response}")
                    
                    if ai_response and len(ai_response) > 10:  # Ensure meaningful response
                        # Limit response to 250 characters for OnlyFans
                        if len(ai_response) > 250:
                            ai_response = ai_response[:247] + "..."
                            
                        return jsonify({
                            'success': True,
                            'response': ai_response,
                            'creator': creator,
                            'fan_type': fan_type,
                            'kyc_step': 'Phase 0 - Step 1: Name Collection',
                            'framework': 'Saints & Sinners Framework Active',
                            'ai_model': 'Gemini 2.5 Pro Preview (1000 tokens)',
                            'finish_reason': candidate.get('finishReason', 'Unknown')
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'AI response too short or empty',
                            'debug_response': ai_response,
                            'debug_candidate': candidate
                        }), 500
                        
                except Exception as parse_error:
                    print(f"Parse error: {parse_error}")
                    return jsonify({
                        'success': False,
                        'error': f'Response parsing error: {str(parse_error)}',
                        'raw_candidate': candidate
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'error': 'No candidates in response',
                    'debug_result': result
                }), 500
        else:
            print(f"API Error: {response.status_code}")
            print(f"Error response: {response.text}")
            return jsonify({
                'success': False,
                'error': f'API Error {response.status_code}: {response.text[:200]}'
            }), 500
            
    except requests.exceptions.Timeout:
        print("Request timeout")
        return jsonify({
            'success': False,
            'error': 'AI request timeout - please try again'
        }), 504
        
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
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
            "contents": [{"parts": [{"text": "Say hello as Ella Blair in a bubbly way"}]}],
            "generationConfig": {"maxOutputTokens": 100}
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
            'communication': 'Warm, enthusiastic, grateful with Portuguese touches',
            'background': 'Independent since 17, loves cats, flexibility training, Brazilian culture'
        },
        'vanp': {
            'name': 'Vanp',
            'niche': 'Inked Maverick Muse / Dominant Brazilian / Anal Expert',
            'personality': 'Intelligent, Dominant, Bratty, Resilient, Artistic',
            'communication': 'Confident, teasing, commands respect',
            'background': 'Heavily tattooed, split tongue, 37 looks 25, fitness enthusiast'
        },
        'yana': {
            'name': 'Yana Sinner',
            'niche': 'Artist / Nerdy / Alt / Lingerie Designer',
            'personality': 'Creative, Intelligent, Witty, Genuine, Reserved',
            'communication': 'Creative language, gaming/art references',
            'background': 'SuicideGirls model, Sinner Couture designer, gamer, always late'
        },
        'venessa': {
            'name': 'Venessa',
            'niche': 'Latina Gamer Girl / Creative & Nerdy / Petite & Flexible',
            'personality': 'Creative, Passionate, Sweet, Playful, Empathetic',
            'communication': 'Bright, energetic with Spanish touches',
            'background': 'Venezuelan, 22, gamer, artist, ballet dancer, dog lover (Moka)'
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
