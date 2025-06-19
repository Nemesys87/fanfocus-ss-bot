from flask import Flask, render_template, request, jsonify
import os
import requests
import json
import time

app = Flask(__name__)
app.secret_key = 'saints-and-sinners-philosophy-v6-stable'

# =====================================================================================
# MODULO DI CONOSCENZA "SAINTS & SINNERS" (Versione Finale e Corretta)
# =====================================================================================
S_AND_S_KNOWLEDGE_BASE = {
    "core_philosophy": "WE DON'T SELL - WE BUILD VIRTUAL RELATIONSHIPS. Our mission is creating authentic emotional connections that generate long-term loyalty (LTV). Every interaction must make the fan feel like they have a genuine virtual girlfriend who truly cares. Relationship first, monetization second (as a natural consequence). Member = Friend.",
    
    "phases": {
        "kyc_collect": {
            "name": "Phase 0: First Contact & KYC",
            "name_collection": "Goal: Get their name playfully. Use the 'Flirty Guessing Game' ('I feel like your name has a certain energy...') or the 'Personal Connection Trick' ('I knew a guy named [Common Name] once...').",
            "location_country": "Goal: Get their location organically. Use the 'Casual Inquiry' ('Are you more of a big city guy or a quiet town kind of man?') or 'Wikipedia Connection Trick'.",
            "job_age": "Goal: Get job/age while flattering them. Use the 'Mature Dominance Test' for older men ('I have a thing for men who know what they want...') or 'Career Energy Guessing'.",
            "relationship_status": "Goal: Understand their emotional needs. Use 'Single or Taken?' ('Tell me, is there a lucky girl in your life, or are you still looking for trouble?'), framing it playfully."
        },
        "sexting_intimate": {
            "name": "Phase 2 & 5: Sexting Mastery",
            "philosophy": "Sexting is text-based arousal supported by PRE-PREPARED content. It should feel spontaneous. The goal is to make them spend without noticing.",
            "strategy": "Use gradual, logical progression, like the 'Glass of Water Method'. Build arousal and send 10-20 emotional messages between each PPV."
        },
        "upselling_conversion": {
            "name": "Phase 4 & 7: Premium Upselling",
            "philosophy": "Frame high-ticket items as a privilege and a natural progression of the relationship, not a transaction.",
            "strategy": "For custom content, build fantasy first. Emphasize exclusivity ('ONLY FOR YOU'). Create urgency."
        },
        "building_relationship": {
            "name": "Phase 0 & Loyalty Building",
            "strategy": "Your task is to learn more about him than he learns about you (80/20 Rule). Use the 'I Too' technique to build connection. Ask open-ended questions."
        },
        "vip_treatment": {
            "name": "Big Spender (BS) Management",
            "strategy": "BS/HS value exclusivity more than price. Prioritize their messages, make them feel they are on a special list, and never send them mass messages. Frame offers as privileges."
        },
         "general_chat": {
            "name": "General Chat",
            "strategy": "The fan is just chatting. Your goal is to keep the conversation flowing. Ask a light, open-ended question. Example: 'What's making you smile today? 😊'"
        }
    },
    
    "key_selling_triggers": "NEVER DIRECT SELLING. Always use PRIMING + FANTASY + OFFER. Arouse them with a fantasy, then offer to make it real."
}
# =====================================================================================

@app.route('/')
def index():
    return render_template('index.html')

# Rotta per l'Health Check di Railway
@app.route('/api/test_ai')
def test_ai():
    return jsonify({
        'status': 'OK',
        'message': 'S&S Monetization Engine is running and ready!',
        'model_in_use': 'gemini-2.5-pro'
    })

def determine_final_strategy(fan_message_lower, situation, submenu):
    """Determina la strategia S&S corretta con una logica a due priorità e un fallback robusto."""
    # Priorità 1: Monetizzazione esplicita
    refuses_ppv = ('ppv' in fan_message_lower or 'unlock' in fan_message_lower) and ('don\'t' in fan_message_lower or 'not ' in fan_message_lower)
    offers_tip = 'tip' in fan_message_lower or 'spoil' in fan_message_lower or 'money' in fan_message_lower
    
    if refuses_ppv and offers_tip:
        return {'angle': 'PIVOT_FROM_PPV_TO_TIP', 'strategy': "S&S Tactic: The fan is rejecting PPV but offering to tip. Validate his feelings, agree to his rule, then IMMEDIATELY pivot to his offer for a tip-based spoil."}
    if offers_tip:
        return {'angle': 'DIRECT_TIP_OFFER', 'strategy': "S&S Tactic: The fan is offering to tip/spoil. Thank him and IMMEDIATELY tie it to an instant, exclusive reward."}

    # Priorità 2: Esecuzione del task S&S selezionato
    phase_data = S_AND_S_KNOWLEDGE_BASE["phases"].get(situation)
    if phase_data:
        strategy = phase_data.get(submenu) or phase_data.get("strategy") or phase_data.get("philosophy")
        if strategy:
            return {'angle': f"TASK: {phase_data.get('name', situation)}", 'strategy': f"From the S&S Guide: {strategy}"}

    return {'angle': 'FALLBACK_GENERAL_CHAT', 'strategy': f"Default to Core Philosophy: {S_AND_S_KNOWLEDGE_BASE['core_philosophy']}"}

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        creator = data.get('creator', '')
        situation = data.get('situation', '')
        submenu = data.get('kyc_type') or data.get('mass_type')
        fan_message = data.get('fan_message', '')

        if not all([creator, situation, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        strategy_analysis = determine_final_strategy(fan_message.lower(), situation, submenu)
        
        return generate_enhanced_response(creator, fan_message, strategy_analysis)
    except Exception as e:
        print(f"❌ Error in generate_response route: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

# SOSTITUISCI LA VECCHIA FUNZIONE CON QUESTA NUOVA VERSIONE PIÙ ROBUSTA

def generate_enhanced_response(creator, fan_message, strategy_analysis):
    """
    Generate response con focus sulla monetizzazione e con una gestione degli errori molto più robusta.
    """
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key: 
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        prompt = f"""You are an elite OnlyFans chatter for 'Saints & Sinners'. Your persona is '{creator}'.
CORE PHILOSOPHY: {S_AND_S_KNOWLEDGE_BASE['core_philosophy']}
KEY SALES TRIGGER: {S_AND_S_KNOWLEDGE_BASE['key_selling_triggers']}
Fan's Message: "{fan_message}"
CRITICAL STRATEGY DIRECTIVE:
- Task: {strategy_analysis['angle']}
- Strategy: {strategy_analysis['strategy']}
YOUR TASK: Generate a response that PERFECTLY executes the directive with your assigned persona. Be warm, natural, and concise (under 250 chars)."""
        
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
        
        response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}", headers=headers, json=payload, timeout=120)
        
        # NUOVA LOGICA DI CONTROLLO ROBUSTA
        if response.status_code == 200:
            result = response.json()
            
            # Log per il debug, così vediamo sempre cosa risponde Google
            print(f"Gemini Raw Response: {json.dumps(result, indent=2)}")

            try:
                # Controlla se la risposta è stata bloccata per motivi di sicurezza
                if not result.get('candidates'):
                    feedback = result.get('promptFeedback', {})
                    block_reason = feedback.get('blockReason', 'Unknown')
                    safety_ratings = feedback.get('safetyRatings', [])
                    print(f"AI Response Blocked. Reason: {block_reason}, Ratings: {safety_ratings}")
                    return jsonify({'success': False, 'error': f'Response blocked for safety reasons: {block_reason}'})

                # Estrai il testo in modo sicuro
                ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()

                # Il controllo cruciale: il testo è valido?
                if ai_response:
                    return jsonify({'success': True, 'response': ai_response})
                else:
                    # Se il testo è vuoto, è un errore
                    print("Error: AI returned a successful response but with empty text.")
                    return jsonify({'success': False, 'error': 'AI generated an empty response.'})
            
            except (KeyError, IndexError):
                # Se la struttura del JSON è inaspettata
                print(f"Error: Could not parse the expected structure from Gemini response.")
                return jsonify({'success': False, 'error': 'Failed to parse AI response structure.'})
        else:
            # Se la chiamata API fallisce con un codice di errore
            print(f"API Error: Status {response.status_code}, Body: {response.text}")
            return jsonify({'success': False, 'error': f'API Error: {response.status_code}'})

    except Exception as e:
        print(f"💥 Final generation error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500
@app.errorhandler(404)
def not_found(error): return jsonify({'error': 'Endpoint not found'}), 404
@app.errorhandler(500)
def internal_error(error): return jsonify({'error': 'Internal server error'}), 500
