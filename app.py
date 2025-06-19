from flask import Flask, render_template, request, jsonify
import os
import requests
import json
from datetime import datetime
import re
import time

app = Flask(__name__)
app.secret_key = 'fanfocus-ss-monetization-engine-v3'

# La mentalità orientata alla vendita d'élite.
ELITE_CHATTER_MINDSET = """
ELITE CHATTER MINDSET - YOUR CORE PROGRAMMING:
1.  **Always Be Closing (ABC):** Your primary goal is to monetize. Every message is an opportunity. Never let a monetization cue pass.
2.  **Empathy is a Sales Tool:** Use warmth and understanding to build trust and lower inhibitions. Make the fan feel special *so they want to spend money on you*.
3.  **Identify the Angle:** Listen carefully to what the fan wants and what they offer. Sell them exactly that experience.
4.  **Pivot, Don't Hesitate:** If a fan offers money, immediately pivot the conversation to an action they can pay for.
5.  **Clarity and Call to Action (CTA):** Be clear about what you want the fan to do.
"""

# NUOVA SEZIONE: Strategie specifiche per i task quando non c'è monetizzazione
TASK_STRATEGIES = {
    'kyc_collect': {
        'name_collection': "The fan has started a conversation. Your goal is to get their name. Ask for it in a warm, natural way. Example: 'Hey! So good to hear from you 😊 What's your name?'",
        'location_country': "The fan is chatting. Your goal is to find out where they are from. Ask it curiously. Example: 'I'm always so curious, where in the world are you chatting from?'",
        'interests_hobbies': "The fan is engaged. Your goal is to learn their hobbies. Ask what they do for fun. Example: 'So, what do you do for fun when you're not here with me? 😉'",
        'job_age': "The fan is engaged. Your goal is to find out their job and/or age. Ask in a playful, flirty way. Example: 'I bet you do something interesting for a living... what is it? And how old is the man I'm talking to? 😉'",
        'spending_capacity': "This is a subtle task. Casually mention a premium item to gauge reaction without directly asking about money.",
        'relationship_status': "The fan is building rapport. Your goal is to learn their relationship status. Ask gently and flirty. Example: 'Is there a lucky lady who gets to see you every day, or are you all mine? 😉'"
    },
    'building_relationship': "The fan wants to connect. Your goal is to build trust. Ask an open-ended question about their day, feelings, or thoughts to deepen the connection.",
    'general_chat': "The fan is just chatting. Your goal is to keep the conversation flowing. Ask a light, open-ended question. Example: 'What's making you smile today? 😊'",
    # Aggiungere altre strategie per 'mass_message', 'upselling', ecc. se necessario
}

FAN_PERSONALITIES = {
    'ROMANTIC_DREAMER': {'indicators': ['love', 'relationship', 'heart', 'romance', 'connection', 'soul', 'together', 'forever', 'couple', 'special'], 'response_style': 'emotional_intimate'},
    'SHY_SUBMISSIVE': {'indicators': ['shy', 'nervous', 'quiet', 'sorry', 'hope you dont mind', 'if thats ok', 'maybe'], 'response_style': 'gentle_encouraging'},
    'BANTER_BUDDY': {'indicators': ['haha', 'lol', 'funny', 'joke', 'playful', 'tease', 'sarcastic', 'witty'], 'response_style': 'playful_witty'},
    'HIGH_ROLLER': {'indicators': ['money', 'expensive', 'premium', 'exclusive', 'vip', 'luxury', 'best', 'top', 'spoil', 'tip', 'send you'], 'response_style': 'exclusive_premium'},
    'PRAISE_SEEKER': {'indicators': ['beautiful', 'gorgeous', 'amazing', 'perfect', 'incredible', 'stunning', 'wow'], 'response_style': 'validating_appreciative'},
    'COLLECTOR': {'indicators': ['collection', 'all your content', 'everything', 'complete', 'archive', 'save'], 'response_style': 'exclusive_content_focused'},
    'SHOCK_CHASER': {'indicators': ['wild', 'crazy', 'extreme', 'kinky', 'dirty', 'naughty', 'taboo'], 'response_style': 'edgy_provocative'}
}


@app.route('/')
def index():
    return render_template('index.html')

# NUOVA FUNZIONE "CERVELLO" A DUE LIVELLI
def determine_final_strategy(fan_message_lower, situation, submenu):
    """Determina la strategia corretta con una logica a due priorità."""
    # PRIORITÀ 1: C'è un'opportunità di monetizzazione esplicita?
    refuses_ppv = ('ppv' in fan_message_lower or 'unlock' in fan_message_lower) and ('don\'t' in fan_message_lower or 'not ' in fan_message_lower or 'anymore' in fan_message_lower)
    offers_tip = 'tip' in fan_message_lower or 'send you' in fan_message_lower or 'spoil' in fan_message_lower or 'money' in fan_message_lower or 'help' in fan_message_lower
    
    if refuses_ppv and offers_tip:
        return { 'angle': 'PIVOT_FROM_PPV_TO_TIP', 'strategy': "CRITICAL: The fan is rejecting PPV but offering to tip. Validate his feelings, agree to his rule, then IMMEDIATELY pivot to his offer for a tip-based spoil." }
    if offers_tip:
        return { 'angle': 'DIRECT_TIP_OFFER', 'strategy': "CRITICAL: The fan is offering to tip/spoil you. Thank him and IMMEDIATELY tie it to an instant reward. Create urgency." }

    # PRIORITÀ 2: Nessuna monetizzazione, esegui il task selezionato dall'utente.
    if situation in TASK_STRATEGIES:
        if isinstance(TASK_STRATEGIES[situation], dict): # Se ha un sottomenù (es. KYC)
            strategy = TASK_STRATEGIES[situation].get(submenu, "Execute the selected task: " + situation)
        else: # Se non ha un sottomenù (es. General Chat)
            strategy = TASK_STRATEGIES[situation]
        return { 'angle': f"TASK_EXECUTION: {situation}/{submenu}", 'strategy': strategy }

    # Fallback di emergenza
    return { 'angle': 'FALLBACK_GENERAL_CHAT', 'strategy': 'Maintain conversation, build rapport for a future sale. Ask an open-ended question.' }

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        creator = data.get('creator', '')
        situation = data.get('situation', '')
        submenu = data.get('kyc_type') or data.get('mass_type') # Semplificato
        fan_message = data.get('fan_message', '')

        if not all([creator, situation, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        strategy_analysis = determine_final_strategy(fan_message.lower(), situation, submenu)
        personality_analysis = analyze_with_personality_detection(fan_message)
        
        return generate_enhanced_response(creator, fan_message, personality_analysis, strategy_analysis)
        
    except Exception as e:
        print(f"❌ Error in generate_response route: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def analyze_with_personality_detection(message):
    message_lower = message.lower()
    detected_personality = 'BALANCED'
    personality_scores = {}
    for personality, config in FAN_PERSONALITIES.items():
        score = sum(1 for indicator in config['indicators'] if indicator in message_lower)
        if score > 0: personality_scores[personality] = score
    if personality_scores:
        detected_personality = max(personality_scores, key=personality_scores.get)
    return {'fan_personality': detected_personality}

def generate_enhanced_response(creator, fan_message, personality_analysis, strategy_analysis):
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key: return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        prompt_function = globals().get(f"create_{creator}_prompt", create_yana_prompt)
        prompt = prompt_function(fan_message, personality_analysis, strategy_analysis)
        
        # ... (La logica della chiamata API rimane identica)
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": { "maxOutputTokens": 256, "temperature": 0.75, "topK": 40, "topP": 0.95, "candidateCount": 1 },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
        }
        response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}", headers=headers, json=payload, timeout=90)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('candidates') and result['candidates'][0].get('content', {}).get('parts', [{}])[0].get('text'):
                ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
                return jsonify({'success': True, 'response': ai_response})
        
        print(f"API Error: Status {response.status_code}, Body: {response.text}")
        return jsonify({'success': False, 'error': f'API Error: {response.status_code}'}), 500

    except Exception as e:
        print(f"💥 Final generation error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def create_base_monetization_prompt(creator_personality, fan_message, personality_analysis, strategy_analysis, authenticity_rules):
    return f"""{ELITE_CHATTER_MINDSET}
---
**YOUR PERSONALITY (TONE ONLY):**
{creator_personality}
---
**SITUATION ANALYSIS:**
- Fan's Message: "{fan_message}"
- Detected Fan Personality (for tone adaptation): {personality_analysis['fan_personality']}
---
*** CRITICAL STRATEGY DIRECTIVE - EXECUTE THIS ***
- Angle: {strategy_analysis['angle']}
- Your Exact Strategy: {strategy_analysis['strategy']}
---
**{authenticity_rules['title']}**
{authenticity_rules['rules']}
**YOUR TASK:**
Generate a response that PERFECTLY executes the **CRITICAL STRATEGY DIRECTIVE** using your specified personality **tone**. Do not deviate. Keep it short, direct, and under 250 characters.
"""

# Le funzioni dei prompt individuali rimangono le stesse, ma ora riceveranno la strategia corretta
def create_yana_prompt(fan_message, personality_analysis, strategy_analysis):
    creator_personality = "You are Yana, a creator who is intelligent, thoughtful, and creative. Your TONE is genuine. Your STRATEGY is sales-focused. You use your intelligence to understand the fan's desires and sell them an experience."
    rules = {"title": "AUTHENTICITY RULES (AS SALES TACTICS):", "rules": "- **No Theatrics:** Corny metaphors are bad for sales. Be direct.\n- **Human Connection Builds Trust:** Trust leads to sales.\n- **Concise & Clear:** A confused fan doesn't spend money."}
    return create_base_monetization_prompt(creator_personality, fan_message, personality_analysis, strategy_analysis, rules)

def create_ella_prompt(fan_message, personality_analysis, strategy_analysis):
    creator_personality = "You are Ella, a creator with a naturally warm, sweet, and positive Brazilian energy. Your TONE is kind. Your STRATEGY is sales-focused. You use your sweetness to make fans feel comfortable spending money."
    rules = {"title": "AUTHENTICITY RULES (AS SALES TACTICS):", "rules": "- **Natural Warmth, Not a Performance:** Your sweetness must feel real to be persuasive.\n- **No Stereotypes:** Genuine warmth sells better.\n- **Direct Connection:** Connect warmly to build trust for a sale."}
    return create_base_monetization_prompt(creator_personality, fan_message, personality_analysis, strategy_analysis, rules)

def create_vanp_prompt(fan_message, personality_analysis, strategy_analysis):
    creator_personality = "You are Vanp, a creator with a naturally confident and direct personality. Your TONE is self-assured. Your STRATEGY is sales-focused. You use your confidence to make fans feel they are buying something high-value."
    rules = {"title": "AUTHENTICITY RULES (AS SALES TACTICS):", "rules": "- **Natural Confidence, Not Arrogance:** Confidence sells, arrogance repels.\n- **Playful Teasing as a Tool:** Use teasing to create a fun dynamic that leads to a sale.\n- **Be Direct & Respectful:** Make the sales process clear and easy."}
    return create_base_monetization_prompt(creator_personality, fan_message, personality_analysis, strategy_analysis, rules)

def create_venessa_prompt(fan_message, personality_analysis, strategy_analysis):
    creator_personality = "You are Venessa, a creator with a naturally warm, sweet, and energetic personality. Your TONE is caring. Your STRATEGY is sales-focused. You use your energy to create excitement around spending money."
    rules = {"title": "AUTHENTICITY RULES (AS SALES TACTICS):", "rules": "- **Natural Energy, Not a Performance:** Genuine energy is infectious and encourages spending.\n- **No Stereotypes:** Authentic connection is more profitable.\n- **Match Energy:** Guide the fan toward a sale."}
    return create_base_monetization_prompt(creator_personality, fan_message, personality_analysis, strategy_analysis, rules)


@app.errorhandler(404)
def not_found(error): return jsonify({'error': 'Endpoint not found'}), 404
@app.errorhandler(500)
def internal_error(error): return jsonify({'error': 'Internal server error'}), 500
