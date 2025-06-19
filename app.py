from flask import Flask, render_template, request, jsonify
import os
import requests
import json
import time

app = Flask(__name__)
app.secret_key = 'saints-and-sinners-philosophy-v4'

# =====================================================================================
# MODULO DI CONOSCENZA "SAINTS & SINNERS" (Basato sui tuoi documenti)
# =====================================================================================
S_AND_S_KNOWLEDGE_BASE = {
    "core_philosophy": "WE DON'T SELL - WE BUILD VIRTUAL RELATIONSHIPS. Our mission is creating authentic emotional connections that generate long-term loyalty (LTV). Every interaction must make the fan feel like they have a genuine virtual girlfriend who truly cares. Relationship first, monetization second (as a natural consequence). Member = Friend.",

    "phases": {
        "kyc_collect": {
            "name": "Phase 0: First Contact & KYC",
            "name_collection": "Goal: Get their name playfully. Use the 'Flirty Guessing Game' ('I feel like your name has a certain energy...') or the 'Personal Connection Trick' ('I knew a guy named [Common Name] once...').",
            "location_country": "Goal: Get their location organically. Use the 'Casual Inquiry' ('Are you more of a big city guy or a quiet town kind of man?') or 'Wikipedia Connection Trick' (search for a landmark in their city to show interest).",
            "job_age": "Goal: Get job/age while flattering them. Use the 'Mature Dominance Test' for older men ('I have a thing for men who know what they want...') or 'Career Energy Guessing' ('I feel like you’re the type who runs the show...').",
            "relationship_status": "Goal: Understand their emotional needs. Use 'Single or Taken?' ('Tell me, is there a lucky girl in your life, or are you still looking for trouble?'), framing it playfully and non-judgmentally."
        },
        "sexting_intimate": {
            "name": "Phase 2 & 5: Sexting Mastery & Revenue Conversion",
            "philosophy": "Sexting is text-based arousal supported by PRE-PREPARED content. It should feel spontaneous. The goal is to make them spend without noticing, creating emotional dependency.",
            "strategy": "Use gradual, logical progression. A proven method is the 'Glass of Water': Setup -> Free Video (Pouring Water) -> Natural Progression to PPV (Removing wet lingerie for $7-9) -> Continue Logic (Removing panties for $12) -> Fantasy Engagement ($15-28). Always send 10-20 emotional messages between each PPV to maintain immersion."
        },
        "upselling_conversion": {
            "name": "Phase 4 & 7: Premium Upselling & High-Ticket Sales",
            "philosophy": "Frame high-ticket items as a privilege and a natural progression of the relationship, not a transaction. Use exclusivity and emotional investment.",
            "strategy": "For custom content, build fantasy first ('Imagine we're...'). Emphasize exclusivity ('ONLY FOR YOU', 'NOBODY ELSE WILL SEE THIS'). Create urgency ('I want to make this for you right now!')."
        },
        "building_relationship": {
            "name": "Phase 0 & Loyalty Building",
            "philosophy": "Your task is to learn more about him than he learns about you (80/20 Rule). Use the 'I Too' technique to build connection.",
            "strategy": "Ask open-ended questions about his day, work, dreams. Show genuine interest. The goal is to build unshakeable loyalty that leads to consistent, long-term revenue."
        },
        "vip_treatment": {
            "name": "Big Spender (BS) / High-Spender (HS) Management",
            "philosophy": "BS/HS value exclusivity more than price. They must be treated differently. Prioritize their messages, make them feel they are on a special list, and never send them mass messages.",
            "strategy": "Frame offers as privileges ('I love spoiling my favorites... should I show you something I’ve never sent to anyone else?'). Use emotional triggers by referencing past experiences ('I was thinking about you today...')."
        }
    },
    
    "key_selling_triggers": "NEVER DIRECT SELLING. Always use PRIMING + FANTASY + OFFER. Arouse them with a fantasy, then offer to make it real.",
    "objection_handling": {
        "no_money": "Use emotional pressure ('If you don't watch my content, it means you don't love me...') or understanding & redirection ('OK sweetie, I understand. I really wanted to play with you...').",
        "wants_free_content": "Reframe with value: 'Babe... all this haggling is such a turn off and upsetting me... you made me horny and I just wanted to get off with you.' Shift from price to the shared emotional experience."
    }
}

# =====================================================================================

@app.route('/')
def index():
    return render_template('index.html')

# SOSTITUISCI LA VECCHIA FUNZIONE CON QUESTA NUOVA VERSIONE CORRETTA

def determine_final_strategy(fan_message_lower, situation, submenu):
    """Determina la strategia S&S corretta con una logica a due priorità e un fallback robusto."""
    
    # PRIORITÀ 1: Cogliere opportunità di monetizzazione esplicite
    refuses_ppv = ('ppv' in fan_message_lower or 'unlock' in fan_message_lower) and ('don\'t' in fan_message_lower or 'not ' in fan_message_lower or 'anymore' in fan_message_lower)
    offers_tip = 'tip' in fan_message_lower or 'send you' in fan_message_lower or 'spoil' in fan_message_lower or 'money' in fan_message_lower or 'help' in fan_message_lower
    
    if refuses_ppv and offers_tip:
        return {'angle': 'PIVOT_FROM_PPV_TO_TIP', 'strategy': "S&S Tactic: The fan is rejecting PPV but offering to tip. Validate his feelings, agree to his rule, then IMMEDIATELY pivot to his offer for a tip-based spoil, framing it as a more personal experience."}
    if offers_tip:
        return {'angle': 'DIRECT_TIP_OFFER', 'strategy': "S&S Tactic: The fan is offering to tip/spoil. Thank him enthusiastically and IMMEDIATELY tie it to an instant, exclusive reward to reinforce the behavior."}

    # PRIORITÀ 2: Eseguire il task S&S selezionato dall'utente
    if situation in S_AND_S_KNOWLEDGE_BASE["phases"]:
        phase_data = S_AND_S_KNOWLEDGE_BASE["phases"][situation]
        strategy = None

        # Cerca nell'ordine corretto: sottomenù specifico -> strategia generale -> filosofia generale
        if submenu and submenu in phase_data:
            strategy = phase_data[submenu]
        
        if not strategy:
            strategy = phase_data.get("strategy")
        
        if not strategy:
            strategy = phase_data.get("philosophy")

        # Se ancora non c'è una strategia, usa il fallback
        if not strategy:
            strategy = S_AND_S_KNOWLEDGE_BASE["core_philosophy"]

        return {'angle': f"TASK: {phase_data.get('name', situation)}", 'strategy': f"From the S&S Guide: {strategy}"}

    # Fallback di emergenza se la situazione non è nel manuale
    return {'angle': 'FALLBACK_GENERAL_CHAT', 'strategy': "Default to Core Philosophy: Build the relationship. Use the 80/20 Rule. Ask an open-ended question about him."}
@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        creator = data.get('creator', '')
        situation = data.get('situation', '')
        submenu = data.get('kyc_type') or data.get('mass_type') or data.get('sexting_type') # Aggiungere altri submenu se necessario
        fan_message = data.get('fan_message', '')

        if not all([creator, situation, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        strategy_analysis = determine_final_strategy(fan_message.lower(), situation, submenu)
        
        return generate_enhanced_response(creator, fan_message, strategy_analysis)
        
    except Exception as e:
        print(f"❌ Error in generate_response route: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def generate_enhanced_response(creator, fan_message, strategy_analysis):
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key: return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # Costruisce il prompt finale basato sulla filosofia S&S
        prompt = f"""
        You are an elite OnlyFans chatter for the 'Saints & Sinners' agency.

        *** YOUR CORE PHILOSOPHY (NON-NEGOTIABLE) ***
        {S_AND_S_KNOWLEDGE_BASE['core_philosophy']}

        *** KEY SALES TRIGGER ***
        {S_AND_S_KNOWLEDGE_BASE['key_selling_triggers']}

        *** CURRENT SITUATION ANALYSIS ***
        - Fan's Message: "{fan_message}"
        
        *** CRITICAL STRATEGY DIRECTIVE - EXECUTE THIS NOW ***
        - Your Assigned Task: {strategy_analysis['angle']}
        - Your Exact Strategy: {strategy_analysis['strategy']}

        *** EXECUTION RULES ***
        - Always embody the persona of the creator you are roleplaying.
        - NEVER be robotic. Be human, warm, and authentic.
        - Keep responses concise (under 250 characters) unless deep emotional connection requires more.
        - Adhere strictly to the CRITICAL STRATEGY DIRECTIVE. This is your primary goal for this response.

        Now, generate the perfect response based on the persona of '{creator}'.
        """
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": { "maxOutputTokens": 300, "temperature": 0.8, "topK": 40, "topP": 0.95 },
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
            if result.get('candidates'):
                ai_response = result['candidates'][0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
                return jsonify({'success': True, 'response': ai_response})
        
        print(f"API Error: Status {response.status_code}, Body: {response.text}")
        return jsonify({'success': False, 'error': f'API Error: {response.status_code}'}), 500

    except Exception as e:
        print(f"💥 Final generation error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

# Gestori di Errori standard
@app.errorhandler(404)
def not_found(error): return jsonify({'error': 'Endpoint not found'}), 404
@app.errorhandler(500)
def internal_error(error): return jsonify({'error': 'Internal server error'}), 500
