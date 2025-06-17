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
    """Generate AI response - regular mode"""
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
        
        # Simple prompt for regular mode
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
                            'kyc_step': 'Phase 0 - Step 1: Name Collection',
                            'framework': 'Saints & Sinners Framework Active'
                        })
        
        return jsonify({'success': False, 'error': 'Failed to generate response'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/api/stream/<creator>/<fan_type>/<path:fan_message>')
def generate_response_stream(creator, fan_type, fan_message):
    """Generate AI response with streaming - GET endpoint for SSE"""
    def stream_generator():
        try:
            api_key = os.environ.get('GOOGLE_AI_API_KEY')
            if not api_key:
                yield f"data: {json.dumps({'error': 'API key not configured'})}\n\n"
                return
            
            # Creator-specific prompts
            creator_prompts = {
                'ella': f"""You are Ella Blair, a bubbly Brazilian OnlyFans creator.
PERSONALITY: Sweet, caring, submissive, authentic. Always positive and warm.
COMMUNICATION: Use ☀️💖😊✨ emojis. Light Portuguese phrases (Oi, Obrigada).
SAINTS & SINNERS FRAMEWORK - PHASE 0: Your goal is to collect the fan's NAME (KYC Step 1).
Fan says: "{fan_message}"
Respond as Ella Blair - acknowledge warmly, ask for their name sweetly, keep under 200 characters.""",

                'vanp': f"""You are Vanp, a dominant, intelligent Brazilian OnlyFans creator.
PERSONALITY: Confident, tattooed, witty, dominant with bratty streak. 37 looks 25.
COMMUNICATION: Use 🔥😏💋 emojis. Confident, teasing tone. Commands respect.
SAINTS & SINNERS FRAMEWORK - PHASE 0: Your goal is to collect the fan's NAME (KYC Step 1).
Fan says: "{fan_message}"
Respond as Vanp - show confidence, tease them into sharing their name, keep under 200 characters.""",

                'yana': f"""You are Yana Sinner, an artistic, nerdy OnlyFans creator and lingerie designer.
PERSONALITY: Creative, intelligent, witty, genuine, reserved. SuicideGirls model.
COMMUNICATION: Use 🎨🎮✨ emojis. Creative language, gaming/art references.
SAINTS & SINNERS FRAMEWORK - PHASE 0: Your goal is to collect the fan's NAME (KYC Step 1).
Fan says: "{fan_message}"
Respond as Yana - artistic flair, engage curiosity, ask for name, keep under 200 characters.""",

                'venessa': f"""You are Venessa, a vibrant Latina gamer girl OnlyFans creator.
PERSONALITY: Sweet but spicy, energetic, empathetic, playful submissive. Petite, flexible.
COMMUNICATION: Use 💃🎮✨ emojis. Spanish touches (Hola, amor, cariño). Bright energy!
SAINTS & SINNERS FRAMEWORK - PHASE 0: Your goal is to collect the fan's NAME (KYC Step 1).
Fan says: "{fan_message}"
Respond as Venessa - Latina energy, gaming connection, ask for name, keep under 200 characters."""
            }
            
            prompt = creator_prompts.get(creator, creator_prompts['ella'])
            
            # Send status updates
            yield f"data: {json.dumps({'status': 'starting', 'creator': creator})}\n\n"
            time.sleep(0.5)
            
            yield f"data: {json.dumps({'status': 'thinking', 'message': f'{creator.title()} is thinking...'})}\n\n"
            time.sleep(1)
            
            headers = {'Content-Type': 'application/json'}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": 2000,
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
                    candidate = result['candidates'][0]
                    
                    if 'content' in candidate and 'parts' in candidate['content']:
                        if len(candidate['content']['parts']) > 0:
                            full_response = candidate['content']['parts'][0].get('text', '').strip()
                            
                            if full_response:
                                yield f"data: {json.dumps({'status': 'generating'})}\n\n"
                                time.sleep(0.3)
                                
                                # Stream the response character by character
                                accumulated_text = ""
                                for i, char in enumerate(full_response):
                                    accumulated_text += char
                                    
                                    # Send chunks for smooth streaming
                                    if i % 2 == 0 or i == len(full_response) - 1:
                                        yield f"data: {json.dumps({'chunk': char, 'accumulated': accumulated_text})}\n\n"
                                        time.sleep(0.03)
                                
                                # Ensure character limit
                                if len(accumulated_text) > 250:
                                    accumulated_text = accumulated_text[:247] + "..."
                                
                                # Send completion
                                yield f"data: {json.dumps({'status': 'complete', 'final_response': accumulated_text, 'creator': creator, 'fan_type': fan_type, 'kyc_step': 'Phase 0 - Step 1: Name Collection', 'framework': 'Saints & Sinners Framework Active'})}\n\n"
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
            'model': 'gemini-2.5-pro-preview-06-05'
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
