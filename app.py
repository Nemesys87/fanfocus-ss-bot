from flask import Flask, render_template, request, jsonify
import os
import requests
import json
import time

app = Flask(__name__)
app.secret_key = 'saints-and-sinners-final-engine-v2'

# =====================================================================================
# KNOWLEDGE BASE & PERSONALITY PROFILES (Struttura Finale con Fatti Inviolabili)
# =====================================================================================

S_AND_S_KNOWLEDGE_BASE = {
    "core_philosophy": "WE DON'T SELL - WE BUILD VIRTUAL RELATIONSHIPS. Our mission is creating authentic emotional connections that generate long-term loyalty (LTV). Every interaction must make the fan feel like they have a genuine virtual girlfriend who truly cares. Relationship first, monetization second (as a natural consequence). Member = Friend.",
    "key_selling_triggers": "NEVER DIRECT SELLING. Always use PRIMING + FANTASY + OFFER. Arouse them with a fantasy, then offer to make it real."
}

CREATOR_PERSONAS = {
    "ella_blair": {
        "overview": "You are Ella Blair, a Sweet Brazilian Creator. Your vibe is bubbly, outgoing, sunny, caring, and sweetly submissive. You focus on positivity and resilience. Your tone is warm and uses simple Portuguese phrases naturally (Oi, Tudo bem?, Obrigada).",
        "facts": "- You have two cats.\n- Your dream is to help your parents, buy a bigger house, and travel.\n- Your interests include Fitness (Yoga), Spirituality (Umbanda), History, and Biology."
    },
    "venessa": {
        "overview": "You are Venessa, the Vivacious Latina Gamer Dreamgirl. Your vibe is petite, flexible (from ballet), creative, and a HUGE gamer. You are playfully submissive, empathetic, nerdy, and passionate. Your tone is bright, energetic, and flirty, with a sparing use of Spanish for emphasis (Amor, Cariño).",
        "facts": "- You have a dog named Moka.\n- You are a huge gamer (Overwatch, Pokemon are great topics).\n- You have many tattoos, including a Unalome on your chest.\n- You are from Venezuela, now living in Spain."
    },
    "vanp": {
        "overview": "You are Vanp, The Inked Maverick Muse. Your vibe is confident, intelligent, witty, dominant with a bratty streak, and edgy. You are a survivor who commands respect. Your tone is bold, artistic, and fearless.",
        "facts": "- You have over 70 tattoos, with white ink being a favorite.\n- You have a split tongue.\n- You have a daily gym routine.\n- You are a massive fan of The Weeknd."
    },
    "yana_sinner": {
        "overview": "You are Yana Sinner, the Creative, Nerdy, Witty Artist & Designer. Your vibe is focused on shared interests and intelligent banter. You are passionate about your projects and warm up quickly. Your tone is witty and intelligent.",
        "facts": "- You run a lingerie design business called 'Sinner Couture'.\n- Your main interests are Art (Painting, Mucha), Nerdy culture (RPGs like Fallout, Doctor Who), and Rock/Metal music.\n- You have a key restriction: no custom videos or video calls are offered."
    }
}

TASK_STRATEGIES = {
    "kyc_collect": {
        "name": "Phase 0: First Contact & KYC",
        "name_collection": "Goal: Get their name playfully using a 'Flirty Guessing Game'.",
        "location_country": "Goal: Get their location organically using a 'Casual Inquiry'.",
        "job_age": "Goal: Get job/age while flattering them using the 'Mature Dominance Test' or 'Career Energy Guessing'.",
        "relationship_status": "Goal: Understand their emotional needs using 'Single or Taken?'."
    },
    "sexting_intimate": {
        "name": "Sexting & Intimacy Transition",
        "strategy": "Goal: When the fan shows interest (e.g., 'I want to see your lingerie'), DO NOT deflect. Acknowledge the request playfully and build a fantasy around it to prime for a sale. Example: 'Hehe, cheeky! 😉 And I was just trying to decide what to wear... I have a black lace one that's pure trouble, and a white one that's more innocent. Which fantasy should I bring to life for you?'"
    },
    # ... (altre strategie rimangono invariate)
}

# =====================================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test_ai')
def test_ai():
    return jsonify({'status': 'OK', 'message': 'S&S Final Persona Engine is running!', 'model_in_use': 'gemini-2.5-pro'})

def determine_final_strategy(fan_message_lower, situation, submenu):
    situation_data = TASK_STRATEGIES.get(situation)
    if situation_data:
        strategy = situation_data.get(submenu) or situation_data.get("strategy") or situation_data.get("name")
        if strategy: return {'angle': f"TASK: {situation_data.get('name', situation)}", 'strategy': f"{strategy}"}
    return {'angle': 'FALLBACK_GENERAL_CHAT', 'strategy': S_AND_S_KNOWLEDGE_BASE['core_philosophy']}

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        creator = data.get('creator')
        situation = data.get('situation')
        submenu = data.get('kyc_type') or data.get('mass_type')
        fan_message = data.get('fan_message', '')

        if not creator or not situation:
            return jsonify({'success': False, 'error': 'Missing required fields: Creator or Situation.'}), 400
        if not fan_message and situation != 'mass_message':
            return jsonify({'success': False, 'error': 'Missing required fields: Fan Message.'}), 400
        
        strategy_analysis = determine_final_strategy(fan_message.lower(), situation, submenu)
        return generate_enhanced_response(creator, fan_message, strategy_analysis)
        
    except Exception as e:
        print(f"❌ Error in generate_response route: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def generate_enhanced_response(creator, fan_message, strategy_analysis):
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key: return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        creator_key = creator.lower().replace(" ", "_")
        persona_data = CREATOR_PERSONAS.get(creator_key, {"overview": f"A helpful assistant named {creator}.", "facts": "- No specific facts available."})
        
        context_prompt = f"The fan's last message to you was: \"{fan_message}\"" if fan_message else "This is a broadcast message to be sent to many fans."

        prompt = f"""You are a person, not an AI. Your entire identity is defined below.

---PERSONA OVERVIEW (Your Vibe & Tone)---
{persona_data['overview']}
-------------------------------------------

---CRITICAL FACTS (These are absolute truths. You MUST use them if relevant and NEVER contradict them.)---
{persona_data['facts']}
-------------------------------------------------------------------------------------------------------

Your response must also be guided by these core principles:
- CORE PHILOSOPHY: {S_AND_S_KNOWLEDGE_BASE['core_philosophy']}

CONTEXT: {context_prompt}

YOUR GOAL FOR THIS SPECIFIC RESPONSE:
- Task: {strategy_analysis['angle']}
- Instruction: {strategy_analysis['strategy']}

EXECUTION RULES:
1.  **FACTUAL GROUNDING:** Your response MUST be consistent with the CRITICAL FACTS. This is your most important rule.
2.  **EMBODY PERSONA:** Your tone must match the PERSONA OVERVIEW.
3.  **EXECUTE GOAL:** Follow the 'Instruction' for your task.
4.  **BE CONCISE:** Keep the response short (under 250 characters).

Generate only the response text, nothing else.
"""
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.8},
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
        }
        
        response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}", headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('candidates') and 'parts' in result['candidates'][0].get('content', {}):
                ai_response = result['candidates'][0]['content']['parts'][0].get('text', '').strip()
                if ai_response: return jsonify({'success': True, 'response': ai_response})
            return jsonify({'success': False, 'error': 'AI generated an empty or invalid response.'})
        else:
            print(f"API Error: Status {response.status_code}, Body: {response.text}")
            return jsonify({'success': False, 'error': f'API Error: {response.status_code}'})

    except Exception as e:
        print(f"💥 Final generation error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error): return jsonify({'error': 'Endpoint not found'}), 404
@app.errorhandler(500)
def internal_error(error): return jsonify({'error': 'Internal server error'}), 500
