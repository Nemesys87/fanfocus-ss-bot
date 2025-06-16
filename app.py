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
    """Generate AI response with full debugging"""
    try:
        print("=== DEBUG START ===")
        
        # Check if we receive data
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            print("ERROR: No data received")
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        
        print(f"Creator: {creator}, Fan Type: {fan_type}, Message: {fan_message}")
        
        if not all([creator, fan_type, fan_message]):
            print("ERROR: Missing fields")
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Check API key
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        print(f"API Key present: {bool(api_key)}")
        print(f"API Key first 10 chars: {api_key[:10] if api_key else 'None'}")
        
        if not api_key:
            print("ERROR: No API key")
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # Simple test prompt
        simple_prompt = f"Respond as {creator} to this message: {fan_message}. Keep it under 100 characters."
        print(f"Using prompt: {simple_prompt}")
        
        # Minimal API call
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": simple_prompt}]}],
            "generationConfig": {"maxOutputTokens": 100}
        }
        
        print("Making API call...")
        
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}"
        print(f"API URL: {api_url[:100]}...")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Headers: {dict(response.headers)}")
        print(f"API Response Text: {response.text[:500]}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"JSON Result keys: {result.keys() if result else 'No result'}")
            
            if 'candidates' in result and len(result['candidates']) > 0:
                ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
                print(f"AI Response: {ai_response}")
                
                return jsonify({
                    'success': True,
                    'response': ai_response,
                    'creator': creator,
                    'fan_type': fan_type,
                    'debug': 'Success!',
                    'ai_model': 'Gemini 2.5 Pro Preview'
                })
            else:
                print("ERROR: No candidates in response")
                print(f"Full result: {result}")
                return jsonify({
                    'success': False,
                    'error': 'No AI response generated',
                    'debug_response': result
                }), 500
        else:
            print(f"ERROR: API returned {response.status_code}")
            print(f"Error response: {response.text}")
            return jsonify({
                'success': False,
                'error': f'API Error {response.status_code}',
                'api_response': response.text[:200]
            }), 500
            
    except requests.exceptions.Timeout:
        print("ERROR: Request timeout")
        return jsonify({
            'success': False,
            'error': 'AI request timeout - please try again'
        }), 504
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request exception: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Network error: {str(e)}'
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
            "contents": [{"parts": [{"text": "Say hello as Ella Blair in a bubbly way"}]}]
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
