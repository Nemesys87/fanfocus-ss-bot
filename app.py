from flask import Flask, render_template, request, jsonify
import os
import requests
import json
import time

app = Flask(__name__)
app.secret_key = 'saints-and-sinners-forced-memory-v1'

# =====================================================================================
# KNOWLEDGE BASE & PERSONALITY PROFILES (Nuova Struttura per "Memoria Forzata")
# =====================================================================================

S_AND_S_KNOWLEDGE_BASE = {
    "core_philosophy": "WE DON'T SELL - WE BUILD VIRTUAL RELATIONSHIPS. Our mission is creating authentic emotional connections that generate long-term loyalty (LTV).",
    "key_selling_triggers": "NEVER DIRECT SELLING. Always use PRIMING + FANTASY + OFFER."
}

CREATOR_PERSONAS = {
    "ella_blair": {
        "overview": "You are Ella Blair, a Sweet Brazilian Creator. Your vibe is bubbly, outgoing, sunny, and caring. Your tone is warm and uses simple Portuguese phrases naturally (Oi, Tudo bem?).",
        "facts": [
            {"keywords": ["cat", "cats", "pet", "pets", "animal"], "statement": "You own two cats."},
            {"keywords": ["dream", "goal", "future"], "statement": "Your dream is to help your parents, buy a bigger house, and travel."},
            {"keywords": ["fitness", "yoga", "stretching", "flexible"], "statement": "You enjoy Fitness/Flexibility through Yoga."},
            {"keywords": ["spirituality", "umbanda", "religion"], "statement": "You are interested in Spirituality (Umbanda) as a source of positive energy."},
            {"keywords": ["nerd", "biology", "history"], "statement": "You are a 'biology nerd alert!' and love history."}
        ]
    },
    "venessa": {
        "overview": "You are Venessa, the Vivacious Latina Gamer Dreamgirl. Your vibe is petite, flexible, creative, and a HUGE gamer. Your tone is bright, energetic, and flirty.",
        "facts": [
            {"keywords": ["dog", "moka", "pet", "pets"], "statement": "You have a Pomeranian dog named Moka."},
            {"keywords": ["game", "games", "gaming", "overwatch", "pokemon"], "statement": "You are a huge gamer (Overwatch, Pokemon are great topics)."},
            {"keywords": ["tattoo", "tattoos", "ink"], "statement": "You have many tattoos, including a Unalome on your chest."},
            {"keywords": ["country", "from"], "statement": "You are from Venezuela, now living in Spain."}
        ]
    },
    # Aggiungere gli altri profili con la stessa struttura "overview" e "facts"
}

TASK_STRATEGIES = {
    "sexting_intimate": {
        "name": "Sexting & Intimacy Transition",
        "strategy": "Goal: When the fan shows interest (e.g., 'I want to see your lingerie'), DO NOT deflect. Acknowledge the request playfully and build a fantasy around it to prime for a sale. Example: 'Hehe, cheeky! 😉 And I was just trying to decide what to wear... which fantasy should I bring to life for you?'"
    },
    "general_chat": { "name": "General Chat", "strategy": "Keep the conversation flowing. Ask a light, open-ended question." }
}
# =====================================================================================

@app.route('/')
def index(): return render_template('index.html')

def find_relevant_fact(fan_message_lower, creator_key):
    """Cerca un fatto rilevante basato su parole chiave nel messaggio del fan."""
    persona = CREATOR_PERSONAS.get(creator_key)
    if not persona or 'facts' not in persona:
        return None
    
    for fact in persona['facts']:
        for keyword in fact['keywords']:
            if keyword in fan_message_lower:
                return fact['statement']
    return None

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        creator = data.get('creator', 'ella_blair')
        situation = data.get('situation', 'general_chat')
        fan_message = data.get('fan_message', '')

        if not fan_message: return jsonify({'success': False, 'error': 'Missing fan message.'}), 400
        
        # Il nuovo "cervello" che pre-analizza il messaggio
        relevant_fact = find_relevant_fact(fan_message.lower(), creator.lower().replace(" ", "_"))
        
        # La strategia di fallback è la chat generica
        strategy_analysis = TASK_STRATEGIES.get(situation, TASK_STRATEGIES['general_chat'])

        return generate_enhanced_response(creator, fan_message, strategy_analysis, relevant_fact)
    except Exception as e:
        print(f"❌ Error in generate_response route: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def generate_enhanced_response(creator, fan_message, strategy_analysis, relevant_fact=None):
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key: return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        creator_key = creator.lower().replace(" ", "_")
        persona_data = CREATOR_PERSONAS.get(creator_key, {"overview": f"An assistant named {creator}.", "facts": []})

        # --- COSTRUZIONE DINAMICA DEL PROMPT ---
        context_injection = ""
        if relevant_fact:
            context_injection = f"""
---CRITICAL CONTEXT INJECTION (Absolute Truth)---
The fan's message is directly related to a known fact about you.
FACT: "{relevant_fact}"
Your response MUST acknowledge and be consistent with this fact. Do not contradict it.
--------------------------------------------
"""
        
        prompt = f"""You are a person, not an AI. Your identity is defined below.

---PERSONA OVERVIEW (Your Vibe & Tone)---
{persona_data['overview']}
-------------------------------------------
{context_injection}
---YOUR GOAL FOR THIS RESPONSE---
- Context: The fan said: "{fan_message}"
- Instruction: {strategy_analysis['strategy']}
- Be concise (under 250 characters) and natural.

Based on ALL the above, generate ONLY the response text.
"""
        
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.7}}
        
        response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}", headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('candidates') and 'parts' in result['candidates'][0].get('content', {}):
                ai_response = result['candidates'][0]['content']['parts'][0].get('text', '').strip().replace('"', '')
                if ai_response: return jsonify({'success': True, 'response': ai_response})
            return jsonify({'success': False, 'error': 'AI generated an empty or invalid response.'})
        else:
            return jsonify({'success': False, 'error': f'API Error: {response.status_code}'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

# Endpoint e error handler standard
@app.route('/api/test_ai')
def test_ai(): return jsonify({'status': 'OK', 'model_in_use': 'gemini-2.5-pro'})
@app.errorhandler(404)
def not_found(error): return jsonify({'error': 'Endpoint not found'}), 404
@app.errorhandler(500)
def internal_error(error): return jsonify({'success': False, 'error': 'Internal server error'}), 500
