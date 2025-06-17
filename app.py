from flask import Flask, render_template, request, jsonify, Response
import os
import requests
import json
import time
import urllib.parse

app = Flask(__name__)
app.secret_key = 'fanfocus-ss-secret-key'

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response - handles both streaming and regular requests"""
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # DEBUG
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        use_streaming = data.get('streaming', False)
        
        print(f"Creator: {creator}, Fan Type: {fan_type}, Streaming: {use_streaming}")  # DEBUG
        
        if not all([creator, fan_type, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        if use_streaming:
            # Railway-compatible streaming URL with query parameters
            encoded_message = urllib.parse.quote(fan_message)
            return jsonify({
                'success': True,
                'streaming': True,
                'stream_url': f'/api/stream/{creator}/{fan_type}?message={encoded_message}'
            })
        
        # Regular non-streaming response
        return generate_regular_response(creator, fan_type, fan_message)
        
    except Exception as e:
        print(f"Error in generate_response: {str(e)}")  # DEBUG
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def generate_regular_response(creator, fan_type, fan_message):
    """Regular non-streaming response"""
    try:
        print(f"Generating regular response for {creator}")  # DEBUG
        
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            print("No API key found")  # DEBUG
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
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
- Be authentic and engaging
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
- Be commanding yet engaging
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
- Be authentic and creative
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
- Be energetic and engaging
- Reference gaming or cultural background if relevant"""
        }
        
        prompt = creator_prompts.get(creator, creator_prompts['ella'])
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 4000,
                "temperature": 0.8,
                "topK": 40,
                "topP": 0.9
            }
        }
        
        print("Making API call to Gemini...")  # DEBUG
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"API Response status: {response.status_code}")  # DEBUG
        
        if response.status_code == 200:
            result = response.json()
            print(f"API Result keys: {result.keys()}")  # DEBUG
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    if len(candidate['content']['parts']) > 0:
                        ai_response = candidate['content']['parts'][0].get('text', '').strip()
                        
                        print(f"Generated response: {ai_response[:100]}...")  # DEBUG
                        
                        return jsonify({
                            'success': True,
                            'response': ai_response,
                            'creator': creator,
                            'fan_type': fan_type,
                            'kyc_step': 'Phase 0 - Step 1: Name Collection',
                            'framework': 'Saints & Sinners Framework Active'
                        })
        
        print("Failed to get valid response from API")  # DEBUG
        return jsonify({'success': False, 'error': 'Failed to generate response'}), 500
        
    except Exception as e:
        print(f"Error in generate_regular_response: {str(e)}")  # DEBUG
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/api/stream/<creator>/<fan_type>', methods=['GET'])
def generate_stream(creator, fan_type):
    """Streaming endpoint using Server-Sent Events - Railway Optimized"""
    
    # Get fan_message from query parameter instead of URL path
    fan_message = request.args.get('message', '')
    
    if not fan_message:
        return jsonify({'error': 'Missing fan message'}), 400
    
    print(f"Streaming request: {creator}, {fan_type}, {fan_message}")  # DEBUG
    
    def stream_generator():
        try:
            # Send immediate connection test
            yield f"data: {json.dumps({'status': 'connected', 'message': 'Connection established'})}\n\n"
            
            api_key = os.environ.get('GOOGLE_AI_API_KEY')
            if not api_key:
                yield f"data: {json.dumps({'error': 'API key not configured'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'starting', 'creator': creator})}\n\n"
            
            # Creator-specific prompts (simplified for streaming)
            creator_prompts = {
                'ella': f"You are Ella Blair, bubbly Brazilian OnlyFans creator. Respond warmly to: '{fan_message}' and ask for their name naturally. Use emojis and Portuguese touches.",
                'vanp': f"You are Vanp, dominant Brazilian creator. Respond confidently to: '{fan_message}' and tease them to share their name. Be commanding.",
                'yana': f"You are Yana Sinner, artistic nerdy creator. Respond creatively to: '{fan_message}' and engage them to share their name. Reference art/gaming.",
                'venessa': f"You are Venessa, energetic Latina gamer creator. Respond with energy to: '{fan_message}' and warmly ask for their name. Use Spanish touches."
            }
            
            prompt = creator_prompts.get(creator, creator_prompts['ella'])
            
            yield f"data: {json.dumps({'status': 'thinking', 'message': f'{creator.title()} is thinking...'})}\n\n"
            
            headers = {'Content-Type': 'application/json'}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": 8192,
                    "temperature": 0.8,
                    "topK": 40,
                    "topP": 0.9
                }
            }
            
            print("Making streaming API call...")  # DEBUG
            
            # Make API call with shorter timeout for streaming
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
                headers=headers,
                json=payload,
                timeout=60  # Reduced timeout for Railway
            )
            
            print(f"Streaming API Response status: {response.status_code}")  # DEBUG
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    
                    if 'content' in candidate and 'parts' in candidate['content']:
                        if len(candidate['content']['parts']) > 0:
                            full_response = candidate['content']['parts'][0].get('text', '').strip()
                            
                            print(f"Streaming response generated: {len(full_response)} chars")  # DEBUG
                            
                            if full_response:
                                yield f"data: {json.dumps({'status': 'generating'})}\n\n"
                                
                                # Stream response in chunks for Railway
                                accumulated_text = ""
                                chunk_size = 5  # Bigger chunks for Railway stability
                                
                                for i in range(0, len(full_response), chunk_size):
                                    chunk = full_response[i:i+chunk_size]
                                    accumulated_text += chunk
                                    
                                    yield f"data: {json.dumps({'chunk': chunk, 'accumulated': accumulated_text})}\n\n"
                                    time.sleep(0.1)  # Slower for Railway stability
                                
                                # Final completion
                                yield f"data: {json.dumps({'status': 'complete', 'final_response': accumulated_text, 'creator': creator, 'fan_type': fan_type, 'kyc_step': 'Phase 0 - Step 1: Name Collection', 'framework': 'Saints & Sinners Framework Active'})}\n\n"
                            else:
                                yield f"data: {json.dumps({'error': 'Empty response from AI'})}\n\n"
                    else:
                        yield f"data: {json.dumps({'error': 'Invalid response structure'})}\n\n"
                else:
                    yield f"data: {json.dumps({'error': 'No response candidates'})}\n\n"
            else:
                yield f"data: {json.dumps({'error': f'API Error {response.status_code}: {response.text}'})}\n\n"
                
        except Exception as e:
            print(f"Streaming error: {str(e)}")  # DEBUG
            yield f"data: {json.dumps({'error': f'Streaming error: {str(e)}'})}\n\n"
    
    # Railway-optimized headers
    return Response(
        stream_generator(), 
        mimetype='text/event-stream',  # Changed from text/plain
        headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control',
            'X-Accel-Buffering': 'no',
            'Content-Type': 'text/event-stream'  # Explicit content type
        }
    )

@app.route('/api/test_ai')
def test_ai():
    """Test Gemini 2.5 Pro API connection"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not found'})
        
        return jsonify({
            'status': 'OK',
            'api_key_present': bool(api_key),
            'model': 'gemini-2.5-pro-preview-06-05',
            'environment': 'Railway Production' if os.environ.get('RAILWAY_ENVIRONMENT') else 'Development',
            'streaming_optimized': True
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
    
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('FLASK_ENV') == 'production':
        print("🚀 Saints & Sinners FanFocus - RAILWAY PRODUCTION")
        print("⚡ Streaming AI optimized for Railway + unlimited tokens")
        print("🎯 Framework S&S Active")
    else:
        print("🔧 Development Mode - Local Testing")
        app.run(host='0.0.0.0', port=port, debug=True)
