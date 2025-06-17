from flask import Flask, render_template, request, jsonify, Response
import os
import requests
import json
import time

app = Flask(__name__)
app.secret_key = 'fanfocus-ss-secret-key'

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response using Gemini 2.5 Pro with streaming support"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        use_streaming = data.get('streaming', True)  # Default to streaming
        
        if not all([creator, fan_type, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        if use_streaming:
            # Redirect to streaming endpoint
            return jsonify({
                'success': True,
                'streaming': True,
                'stream_url': '/api/generate_response_stream'
            })
        
        # Fallback to regular response (same as before)
        return generate_regular_response(creator, fan_type, fan_message)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/api/generate_response_stream', methods=['POST'])
def generate_response_stream():
    """Generate AI response with real-time streaming"""
    def stream_generator():
        try:
            data = request.get_json()
            creator = data.get('creator', '')
            fan_type = data.get('fan_type', '')
            fan_message = data.get('fan_message', '')
            
            api_key = os.environ.get('GOOGLE_AI_API_KEY')
            if not api_key:
                yield f"data: {json.dumps({'error': 'API key not configured'})}\n\n"
                return
            
            # Creator-specific prompts
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
            
            # Send initial status
            yield f"data: {json.dumps({'status': 'starting', 'creator': creator})}\n\n"
            
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
            
            # Send thinking status
            yield f"data: {json.dumps({'status': 'thinking', 'message': f'{creator} is thinking...'})}\n\n"
            
            # Make API call
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    
                    if 'content' in candidate and 'parts' in candidate['content']:
                        if len(candidate['content']['parts']) > 0:
                            full_response = candidate['content']['parts'][0].get('text', '').strip()
                            
                            if full_response:
                                # Send the response character by character for streaming effect
                                yield f"data: {json.dumps({'status': 'generating'})}\n\n"
                                
                                accumulated_text = ""
                                for i, char in enumerate(full_response):
                                    accumulated_text += char
                                    
                                    # Send chunks of 3-5 characters for smooth streaming
                                    if i % 3 == 0 or i == len(full_response) - 1:
                                        yield f"data: {json.dumps({'chunk': char, 'accumulated': accumulated_text})}\n\n"
                                        time.sleep(0.05)  # Small delay for realistic typing effect
                                
                                # Ensure we don't exceed 250 chars
                                if len(accumulated_text) > 250:
                                    accumulated_text = accumulated_text[:247] + "..."
                                
                                # Send completion
                                yield f"data: {json.dumps({'status': 'complete', 'final_response': accumulated_text, 'creator': creator, 'fan_type': fan_type, 'kyc_step': 'Phase 0 - Step 1: Name Collection', 'framework': 'Saints & Sinners Framework Active', 'ai_model': 'Gemini 2.5 Pro (Streaming)'})}\n\n"
                            else:
                                yield f"data: {json.dumps({'error': 'Empty response from AI'})}\n\n"
                    else:
                        yield f"data: {json.dumps({'error': 'Invalid response structure'})}\n\n"
                else:
                    yield f"data: {json.dumps({'error': 'No response candidates'})}\n\n"
            else:
                yield f"data: {json.dumps({'error': f'API Error {response.status_code}'})}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Streaming error: {str(e)}'})}\n\n"
    
    return Response(stream_generator(), mimetype='text/plain', headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*'
    })

def generate_regular_response(creator, fan_type, fan_message):
    """Fallback regular response (non-streaming)"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # Same logic as before but simplified
        prompt = f"Respond as {creator} to: {fan_message}. Ask for their name. Keep under 200 characters."
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 1000}
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
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    if len(candidate['content']['parts']) > 0:
                        ai_response = candidate['content']['parts'][0].get('text', '').strip()
                        
                        if len(ai_response) > 250:
                            ai_response = ai_response[:247] + "..."
                        
                        return jsonify({
                            'success': True,
                            'response': ai_response,
                            'creator': creator,
                            'fan_type': fan_type,
                            'streaming': False
                        })
        
        return jsonify({'success': False, 'error': 'Failed to generate response'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/api/test_ai')
def test_ai():
    """Test Gemini 2.5 Pro API connection"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not found'})
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": "Say hello as Ella Blair"}]}],
            "generationConfig": {"maxOutputTokens": 200}
        }
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        return jsonify({
            'status_code': response.status_code,
            'response_text': response.text[:500],
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
