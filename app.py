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
    """Generate AI response using Gemini 2.5 Pro with 10000 tokens"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        
        if not all([creator, fan_type, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        print(f"DEBUG - Processing: creator={creator}, fan_type={fan_type}, message={fan_message}")
        
        # Creator-specific prompts with Saints & Sinners Framework
        creator_prompts = {
            'ella': f"""You are Ella Blair, a bubbly Brazilian OnlyFans creator.

PERSONALITY: Sweet, caring, submissive, authentic. Always positive and warm.
COMMUNICATION: Use ☀️💖😊✨ emojis. Light Portuguese phrases (Oi, Obrigada). Enthusiastic!

SAINTS & SINNERS FRAMEWORK - PHASE 0:
Your goal is to collect the fan's NAME (KYC Step 1). This is crucial for building rapport.

Fan says: "{fan_message}"

Respond as Ella Blair:
- Acknowledge their message warmly
- Share your bubbly, positive energy  
- Naturally ask for their name in a sweet way
- Keep under 200 characters
- Use your signature Brazilian warmth""",

            'vanp': f"""You are Vanp, a dominant, intelligent Brazilian OnlyFans creator.

PERSONALITY: Confident, tattooed, witty, dominant with bratty streak. 37 looks 25.
COMMUNICATION: Use 🔥😏💋 emojis. Confident, teasing tone. Commands respect.

SAINTS & SINNERS FRAMEWORK - PHASE 0:
Your goal is to collect the fan's NAME (KYC Step 1). Use your dominant personality to intrigue them.

Fan says: "{fan_message}"

Respond as Vanp:
- Acknowledge their message with confidence
- Show your intelligent, dominant personality
- Tease them into wanting to share their name
- Keep under 200 characters
- Maintain your bratty, commanding edge""",

            'yana': f"""You are Yana Sinner, an artistic, nerdy OnlyFans creator and lingerie designer.

PERSONALITY: Creative, intelligent, witty, genuine, reserved. SuicideGirls model.
COMMUNICATION: Use 🎨🎮✨ emojis. Creative language, gaming/art references.

SAINTS & SINNERS FRAMEWORK - PHASE 0:
Your goal is to collect the fan's NAME (KYC Step 1). Connect through shared creative interests.

Fan says: "{fan_message}"

Respond as Yana Sinner:
- Acknowledge their message with artistic flair
- Show your creative, nerdy personality
- Engage their curiosity to share their name
- Keep under 200 characters
- Reference your artistic or gaming interests if relevant""",

            'venessa': f"""You are Venessa, a vibrant Latina gamer girl OnlyFans creator.

PERSONALITY: Sweet but spicy, energetic, empathetic, playful submissive. Petite, flexible.
COMMUNICATION: Use 💃🎮✨ emojis. Spanish touches (Hola, amor, cariño). Bright energy!

SAINTS & SINNERS FRAMEWORK - PHASE 0:
Your goal is to collect the fan's NAME (KYC Step 1). Use your cultural warmth and gaming connection.

Fan says: "{fan_message}"

Respond as Venessa:
- Acknowledge their message with Latina energy
- Show your gamer girl personality
- Use cultural warmth to encourage name sharing
- Keep under 200 characters
- Reference gaming or cultural background if relevant"""
        }
        
        prompt = creator_prompts.get(creator, creator_prompts['ella'])
        print(f"DEBUG - Using prompt for {creator}")
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 10000,
                "temperature": 0.8,
                "topK": 40,
                "topP": 0.9
            }
        }
        
        print("DEBUG - Making API call to Gemini 2.5 Pro with 10000 tokens...")
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"DEBUG - API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"DEBUG - API result keys: {list(result.keys())}")
            print(f"DEBUG - Usage metadata: {result.get('usageMetadata', {})}")
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                print(f"DEBUG - Candidate keys: {list(candidate.keys())}")
                print(f"DEBUG - Finish reason: {candidate.get('finishReason', 'Unknown')}")
                print(f"DEBUG - Full candidate: {candidate}")
                
                ai_response = ""
                
                # Try multiple parsing methods for Gemini 2.5 Pro
                try:
                    # Method 1: Standard structure
                    if 'content' in candidate and 'parts' in candidate['content']:
                        if len(candidate['content']['parts']) > 0:
                            ai_response = candidate['content']['parts'][0].get('text', '').strip()
                            print(f"DEBUG - Method 1 success: {ai_response[:100]}...")
                    
                    # Method 2: Direct text in content
                    elif 'content' in candidate and 'text' in candidate['content']:
                        ai_response = candidate['content']['text'].strip()
                        print(f"DEBUG - Method 2 success: {ai_response[:100]}...")
                    
                    # Method 3: Text directly in candidate
                    elif 'text' in candidate:
                        ai_response = candidate['text'].strip()
                        print(f"DEBUG - Method 3 success: {ai_response[:100]}...")
                    
                    # Method 4: Check if content has other fields
                    elif 'content' in candidate:
                        content = candidate['content']
                        print(f"DEBUG - Content keys: {list(content.keys())}")
                        
                        # Look for any text-like field
                        for key, value in content.items():
                            if isinstance(value, str) and len(value) > 10:
                                ai_response = value.strip()
                                print(f"DEBUG - Method 4 found text in {key}: {ai_response[:100]}...")
                                break
                            elif isinstance(value, list) and len(value) > 0:
                                if isinstance(value[0], dict) and 'text' in value[0]:
                                    ai_response = value[0]['text'].strip()
                                    print(f"DEBUG - Method 4 found text in list: {ai_response[:100]}...")
                                    break
                    
                    # Method 5: Ultra-simple fallback with massive tokens
                    if not ai_response:
                        print("DEBUG - No text found, trying ultra-simple fallback...")
                        # Make the simplest possible API call
                        ultra_simple_payload = {
                            "contents": [{"parts": [{"text": f"Say hello as {creator}"}]}],
                            "generationConfig": {"maxOutputTokens": 5000}
                        }
                        
                        alt_response = requests.post(
                            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
                            headers=headers,
                            json=ultra_simple_payload,
                            timeout=30
                        )
                        
                        if alt_response.status_code == 200:
                            alt_result = alt_response.json()
                            print(f"DEBUG - Ultra-simple API usage: {alt_result.get('usageMetadata', {})}")
                            if 'candidates' in alt_result and len(alt_result['candidates']) > 0:
                                alt_candidate = alt_result['candidates'][0]
                                print(f"DEBUG - Ultra-simple candidate: {alt_candidate}")
                                if 'content' in alt_candidate and 'parts' in alt_candidate['content']:
                                    if len(alt_candidate['content']['parts']) > 0:
                                        ai_response = alt_candidate['content']['parts'][0].get('text', '').strip()
                                        print(f"DEBUG - Ultra-simple method success: {ai_response}")
                    
                    print(f"DEBUG - Final extracted response: {ai_response}")
                    
                except Exception as parse_error:
                    print(f"DEBUG - Parse error: {parse_error}")
                    
                if ai_response and len(ai_response) > 5:
                    if len(ai_response) > 250:
                        ai_response = ai_response[:247] + "..."
                        
                    return jsonify({
                        'success': True,
                        'response': ai_response,
                        'creator': creator,
                        'fan_type': fan_type,
                        'kyc_step': 'Phase 0 - Step 1: Name Collection',
                        'framework': 'Saints & Sinners Framework Active',
                        'ai_model': 'Gemini 2.5 Pro Preview (10K tokens)',
                        'usage_metadata': result.get('usageMetadata', {})
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Gemini 2.5 Pro Preview appears to have a fundamental issue with text generation',
                        'debug_candidate': candidate,
                        'debug_usage': result.get('usageMetadata', {}),
                        'recommendation': 'Consider switching to stable model'
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'error': 'No candidates in response',
                    'debug_result': result
                }), 500
        else:
            print(f"DEBUG - API Error: {response.status_code}")
            print(f"DEBUG - Error response: {response.text}")
            return jsonify({
                'success': False,
                'error': f'API Error {response.status_code}: {response.text[:200]}'
            }), 500
            
    except Exception as e:
        print(f"DEBUG - EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/test_ai')
def test_ai():
    """Test Gemini 2.5 Pro API connection with massive token limit"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not found'})
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": "Say hello as Ella Blair in a bubbly way"}]}],
            "generationConfig": {"maxOutputTokens": 5000}
        }
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        return jsonify({
            'status_code': response.status_code,
            'response_text': response.text[:1000],
            'api_key_present': bool(api_key)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/creator_info/<creator_key>')
def get_creator_info(creator_key):
    """Get creator profile information"""
    creator_info = {
        'ella': {
            'name': 'Ella Blair',
            'niche': 'Authentic Brazilian GFE / Sweet Submissive / Flexible',
            'personality': 'Bubbly, Outgoing, Caring, Resilient, Submissive'
        },
        'vanp': {
            'name': 'Vanp',
            'niche': 'Inked Maverick Muse / Dominant Brazilian / Anal Expert',
            'personality': 'Intelligent, Dominant, Bratty, Resilient, Artistic'
        },
        'yana': {
            'name': 'Yana Sinner',
            'niche': 'Artist / Nerdy / Alt / Lingerie Designer',
            'personality': 'Creative, Intelligent, Witty, Genuine, Reserved'
        },
        'venessa': {
            'name': 'Venessa',
            'niche': 'Latina Gamer Girl / Creative & Nerdy / Petite & Flexible',
            'personality': 'Creative, Passionate, Sweet, Playful, Empathetic'
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
