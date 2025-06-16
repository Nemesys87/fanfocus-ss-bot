from flask import Flask, render_template, request, jsonify
import os

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
            return jsonify({
                'success': False,
                'error': 'No data received'
            }), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        
        if not all([creator, fan_type, fan_message]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Creator-specific responses following S&S Framework Phase 0 (KYC - Name collection)
        responses = {
            'ella': "Oi! ☀️ My day just got so much brighter talking to you! I'm Ella, and I love meeting new people! What's your name, cutie? 😊✨ (I'm always curious about where my fans are from too!) 💖",
            
            'vanp': "Well hello there 😏 I appreciate the compliment, but I'm intrigued - what's your name? I like to know who I'm talking to before we dive deeper 🔥 Where are you writing me from? 💋",
            
            'yana': "Hey there! 🎨 Thanks for reaching out! I'm Yana, always working on something creative. What's your name? I'd love to get to know the person behind the message! ✨ Are you into art or gaming at all? 🎮",
            
            'venessa': "Hola there! 💃 Thanks for the sweet message! I'm Venessa - what's your name, amor? I love connecting with new people! Where are you from? I'm curious about my fans! 🌎✨"
        }
        
        # Get appropriate response
        response_text = responses.get(creator, "Hey! What's your name? I'd love to get to know you! 💖")
        
        return jsonify({
            'success': True,
            'response': response_text,
            'creator': creator,
            'fan_type': fan_type,
            'kyc_step': 'Phase 0 - Step 1: Name Collection',
            'framework_note': 'S&S Framework: Starting KYC process with name extraction'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)  
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
