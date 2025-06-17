from flask import Flask, render_template, request, jsonify, Response
import os
import requests
import json
import time

app = Flask(__name__)
app.secret_key = 'fanfocus-ss-secret-key'

# --- FUNZIONI HELPER PER LA LOGICA DI GEMINI ---

def get_prompt_for_creator(creator, fan_message):
    """Restituisce il prompt specifico per il creator."""
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
    return creator_prompts.get(creator, creator_prompts['ella'])

def stream_generator(creator, fan_type, fan_message):
    """
    Generatore che chiama Gemini e produce eventi in formato Server-Sent Events (SSE).
    """
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            error_event = {"error": "API key not configured"}
            yield f"data: {json.dumps(error_event)}\n\n"
            return

        prompt = get_prompt_for_creator(creator, fan_message)
        
        # Invia stato iniziale
        yield f"data: {json.dumps({'status': 'starting', 'creator': creator})}\n\n"
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 2048,
                "temperature": 0.8,
                "topK": 40,
                "topP": 0.9
            }
        }
        
        # Invia stato di "thinking"
        yield f"data: {json.dumps({'status': 'thinking', 'message': f'{creator} is thinking...'})}\n\n"
        
        # Esegue la chiamata all'API di Google
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        # Analizza la risposta dell'API
        if response.status_code == 200:
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                candidate = result['candidates'][0]
                
                if candidate.get('finishReason') not in ['STOP', 'MAX_TOKENS']:
                    error_msg = f"API generation stopped for reason: {candidate.get('finishReason')}"
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
                    return

                if 'content' in candidate and 'parts' in candidate['content'] and candidate['content']['parts']:
                    full_response = candidate['content']['parts'][0].get('text', '').strip()
                    
                    if full_response:
                        yield f"data: {json.dumps({'status': 'generating'})}\n\n"
                        time.sleep(0.1) # Pausa prima di iniziare a "scrivere"

                        # Invia la risposta carattere per carattere per l'effetto streaming
                        for char in full_response:
                            yield f"data: {json.dumps({'chunk': char})}\n\n"
                            time.sleep(0.03) # Pausa per un effetto realistico
                        
                        # Invia il messaggio finale di completamento
                        yield f"data: {json.dumps({'status': 'complete', 'final_response': full_response})}\n\n"
                    else:
                        yield f"data: {json.dumps({'error': 'Empty response from AI'})}\n\n"
                else:
                    yield f"data: {json.dumps({'error': 'Invalid response structure from AI'})}\n\n"
            else:
                yield f"data: {json.dumps({'error': 'No response candidates from AI', 'details': response.text})}\n\n"
        else:
            yield f"data: {json.dumps({'error': f'API Error {response.status_code}', 'details': response.text})}\n\n"
            
    except Exception as e:
        yield f"data: {json.dumps({'error': f'Server stream error: {str(e)}'})}\n\n"


# --- ROTTE DELL'APPLICAZIONE FLASK ---

@app.route('/')
def index():
    """Pagina principale"""
    return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response_trigger():
    """
    Questa rotta riceve la richiesta POST iniziale e serve solo da "trigger".
    La risposta di questa rotta non viene usata dal frontend, che invece
    procede a chiamare l'endpoint GET per lo streaming.
    """
    return jsonify({'success': True, 'message': 'Stream request acknowledged. Connect to the GET stream endpoint.'})


@app.route('/api/stream/<creator>/<fan_type>/<fan_message>', methods=['GET'])
def handle_stream(creator, fan_type, fan_message):
    """
    Questo è l'endpoint che gestisce lo streaming vero e proprio.
    Viene chiamato dal frontend con una richiesta GET e i parametri nell'URL.
    """
    return Response(stream_generator(creator, fan_type, fan_message), mimetype='text/event-stream')


# --- GESTIONE ERRORI E AVVIO APPLICAZIONE ---

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found. Check your URL.'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method Not Allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': f'Internal server error: {error}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
