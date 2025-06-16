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
    """Generate AI response with safe response parsing"""
    try:
        print("=== DEBUG START ===")
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        
        print(f"Creator: {creator}, Fan Type: {fan_type}, Message: {fan_message}")
        
        if not all([creator, fan_type, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # Creator-specific prompts
        creator_prompts = {
            'ella': f"You are Ella Blair, a bubbly Brazilian OnlyFans creator. Respond warmly to: '{fan_message}' and ask for their name. Use ☀️💖 emojis. Keep under 150 characters.",
            'vanp': f"You are Vanp, a confident tattooed Brazilian OnlyFans creator. Respond with intelligent dominance to: '{fan_message}' and ask for their name. Use 🔥😏 emojis. Keep under 150 characters.",
            'yana': f"You are Yana Sinner, an artistic nerdy OnlyFans creator. Respond creatively to: '{fan_message}' and ask for their name. Use 🎨✨ emojis. Keep under 150 characters.",
            'venessa': f"You are Venessa, a Latina gamer girl OnlyFans creator. Respond energetically to: '{fan_message}' and ask for their name. Use 💃🎮 emojis. Keep under 150 characters."
        }
        
        prompt = creator_prompts.get(creator, creator_prompts['ella'])
        print(f"Using prompt for {creator}")
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 150, "temperature": 0.8}
        }
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Full API result: {result}")
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                print(f"Candidate structure: {candidate}")
                
                # Safe response parsing
                ai_response = ""
                try:
                    if 'content' in candidate:
                        content = candidate['content']
                        if 'parts' in content and len(content['parts']) > 0:
                            ai_response = content['parts'][0]['text'].strip()
                        elif 'text' in content:
                            ai_response = content['text'].strip()
                        else:
                            ai_response = str(content)
                    elif 'text' in candidate:
                        ai_response = candidate['text'].strip()
                    else:
                        ai_response = str(candidate)
                        
                    print(f"Extracted AI response: {ai_response}")
                    
                    if ai_response:
                        return jsonify({
                            'success': True,
                            'response': ai_response,
                            'creator': creator,
                            'fan_type': fan_type,
                            'kyc_step': 'Phase 0 - Step 1: Name Collection',
                            'framework': 'Saints & Sinners Framework Active',
                            'ai_model': 'Gemini 2.5 Pro Preview'
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'Empty AI response',
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
            return jsonify({
                'success': False,
                'error': f'API Error {response.status_code}: {response.text[:200]}'
            }), 500
            
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
            "contents": [{"parts": [{"text": "Say hello"}]}]
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

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)  
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
