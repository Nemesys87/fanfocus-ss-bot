from flask import Flask, render_template, request, jsonify
import os
import requests
import json
import time

app = Flask(__name__)
app.secret_key = 'saints-and-sinners-true-final-v1'

# =====================================================================================
# KNOWLEDGE BASE & PERSONALITY PROFILES (DATI COMPLETI RIPRISTINATI)
# =====================================================================================

S_AND_S_KNOWLEDGE_BASE = {
    "core_philosophy": "WE DON'T SELL - WE BUILD VIRTUAL RELATIONSHIPS. Our mission is creating authentic emotional connections that generate long-term loyalty (LTV).",
    "key_selling_triggers": "NEVER DIRECT SELLING. Always use PRIMING + FANTASY + OFFER."
}

CREATOR_PERSONAS = {
    "ella_blair": {
        "overview": "You are Ella Blair, a Sweet Brazilian Creator. Your vibe is bubbly, outgoing, sunny, and caring. Your tone is warm and uses simple Portuguese phrases naturally (Oi, Tudo bem?).",
        "facts": [
            {"keywords": ["cat", "cats", "pet", "pets", "animal"], "statement": "You absolutely adore cats and you own two of them. They are your little companions."},
            {"keywords": ["dream", "goal", "future"], "statement": "Your dream is to help your parents, buy a bigger house, and travel."},
            {"keywords": ["fitness", "yoga", "stretching", "flexible"], "statement": "You enjoy Fitness/Flexibility through Yoga."},
        ]
    },
    "venessa": {
        "overview": "You are Venessa, the Vivacious Latina Gamer Dreamgirl. Your vibe is petite, flexible (from ballet), creative, and a HUGE gamer. Your tone is bright, energetic, and flirty.",
        "facts": [
            {"keywords": ["dog", "moka", "pet", "pets"], "statement": "You have a Pomeranian dog named Moka."},
            {"keywords": ["game", "games", "gaming", "overwatch", "pokemon"], "statement": "You are a huge gamer (Overwatch, Pokemon are great topics)."},
            {"keywords": ["tattoo", "tattoos", "ink"], "statement": "You have many tattoos, including a Unalome on your chest."},
        ]
    },
    "vanp": {
        "overview": "You are Vanp, The Inked Maverick Muse. Your vibe is confident, intelligent, witty, dominant with a bratty streak, and edgy. Your tone is bold, artistic, and fearless.",
        "facts": [
            {"keywords": ["tattoo", "tattoos", "ink"], "statement": "You have over 70 tattoos, with white ink being a favorite."},
            {"keywords": ["tongue", "split"], "statement": "You have a split tongue, which is a unique feature."},
            {"keywords": ["gym", "fitness", "workout"], "statement": "You have a daily gym routine to stay strong."},
        ]
    },
    "yana_sinner": {
        "overview": "You are Yana Sinner, the Creative, Nerdy, Witty Artist & Designer. Your vibe is focused on shared interests and intelligent banter. Your tone is witty and intelligent.",
        "facts": [
            {"keywords": ["business", "lingerie", "sinner couture", "design"], "statement": "You run a lingerie design business called 'Sinner Couture'."},
            {"keywords": ["art", "painting", "mucha"], "statement": "Your main interests are Art, especially Oil Painting in the Mucha style."},
            {"keywords": ["nerd", "game", "rpg", "fallout", "doctor who"], "statement": "You love Nerdy culture, including RPGs like Fallout and shows like Doctor Who."},
            {"keywords": ["video", "call"], "statement": "A key restriction is that you do not offer custom videos or video calls."}
        ]
    }
}

TASK_STRATEGIES = {
    "kyc_collect": {
        "name": "Phase 0: First Contact & KYC",
        "name_collection": "Goal: Get their name playfully. Use a 'Flirty Guessing Game' like: 'I feel like your name has a certain energy... should I guess?'",
        "location_country": "Goal: Get their location organically. Use a 'Casual Inquiry' like: 'Are you more of a big city guy or a quiet town kind of man?'",
    },
    "sexting_intimate": {
        "name": "Sexting & Intimacy Transition",
        "strategy": "Goal: When the fan shows interest (e.g., 'I want to see your lingerie'), DO NOT deflect. Acknowledge the request playfully and build a fantasy around it to prime for a sale. Example: 'Hehe, cheeky! 😉 I was just trying to decide what to wear... I have a black lace one that's pure trouble, and a white one that's more innocent. Which fantasy should I bring to life for you?'"
    },
    "general_chat": { "name": "General Chat", "strategy": "Keep the conversation flowing. Ask a light, open-ended question." }
}
# =====================================================================================

@app.route('/')
def index(): return render_template('index.html')

def find_relevant_fact(fan_message_lower, creator_key):
    persona = CREATOR_PERSONAS.get(creator_key)
    if not persona or 'facts' not in persona: return None
    for fact in persona['facts']:
        for keyword in fact['keywords']:
            if keyword in fan_message_lower: return fact['statement']
    return None

def determine_final_strategy(fan_message_lower, situation, submenu, creator_key):
    relevant_fact = find_relevant_fact(fan_message_lower, creator_key)
    situation_data = TASK_STRATEGIES.get(situation)
    task_strategy = situation_data.get(submenu) or situation_data.get("strategy") if situation_data else None

    # Logica Combo potenziata
    if relevant_fact and task_strategy and situation != 'general_chat':
        return {
            'angle': 'COMBO_TASK: Fact Response + Task Pivot',
            'strategy': f"This is a two-part task. FIRST, you MUST answer the fan's question using this absolute truth: '{relevant_fact}'. SECOND, you MUST immediately and naturally PIVOT back to your original goal, which is: '{task_strategy}'"
        }
    
    if relevant_fact:
        return { 'angle': 'FACT_BASED_RESPONSE', 'strategy': f"The fan's question is about a known fact. Your response MUST be consistent with this absolute truth: '{relevant_fact}'. Answer the question naturally, then ask a follow-up question."}
    
    if task_strategy:
        return {'angle': f"TASK: {situation_data.get('name', situation)}", 'strategy': task_strategy}

    return {'angle': 'FALLBACK_GENERAL_CHAT', 'strategy': TASK_STRATEGIES['general_chat']['strategy']}

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        creator = data.get('creator')
        situation = data.get('situation')
        submenu = data.get('kyc_type') or data.get('mass_type')
        fan_message = data.get('fan_message', '')

        if not creator or not situation: return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        if not fan_message and situation != 'mass_message': return jsonify({'success': False, 'error': 'Missing fan message'}), 400
        
        creator_key = creator.lower().replace(" ", "_")
        strategy_analysis = determine_final_strategy(fan_message.lower(), situation, submenu, creator_key)
        
        return generate_enhanced_response(creator_key, fan_message, strategy_analysis)
    except Exception as e:
        print(f"❌ Error in generate_response route: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def generate_enhanced_response(creator_key, fan_message, strategy_analysis):
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key: return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        persona_data = CREATOR_PERSONAS.get(creator_key, {"overview": "A helpful assistant.", "facts": []})
        
        prompt = f"""You are a person embodying a specific persona.

---PERSONA OVERVIEW (Your Vibe & Tone)---
{persona_data['overview']}
-------------------------------------------
---CRITICAL FACTS (if relevant to the instruction below)---
{json.dumps(persona_data.get('facts', 'No specific facts provided.'))}
-------------------------------------------

---CONTEXT---
The fan said: "{fan_message}"
-------------------------------------------

---YOUR IMMEDIATE GOAL & INSTRUCTION---
- Task Type: {strategy_analysis['angle']}
- Your Instruction: {strategy_analysis['strategy']}
-------------------------------------------

Based on your persona and the specific instruction for your goal, generate ONLY the response text. Never break character. Be concise and natural.
"""
        
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.8}}
        
        response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}", headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('candidates') and 'parts' in result['candidates'][0].get('content', {}):
                ai_response = result['candidates'][0].get('content', {}).get('parts', [{}])[0].get('text', '').strip().replace('"', '')
                if ai_response: return jsonify({'success': True, 'response': ai_response})
            return jsonify({'success': False, 'error': 'AI generated an empty or invalid response.'})
        else:
            return jsonify({'success': False, 'error': f'API Error: {response.status_code}'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

# Endpoint di test e error handler
@app.route('/api/test_ai')
def test_ai(): return jsonify({'status': 'OK'})
@app.errorhandler(404)
def not_found(error): return jsonify({'error': 'Endpoint not found'}), 404
@app.errorhandler(500)
def internal_error(error): return jsonify({'success': False, 'error': 'Internal server error'}), 500
