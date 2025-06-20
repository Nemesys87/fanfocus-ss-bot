from flask import Flask, render_template, request, jsonify
import os
import requests
import json
import time

app = Flask(__name__)
app.secret_key = 'saints-and-sinners-complete-v-final'

# =====================================================================================
# KNOWLEDGE BASE & PERSONALITY PROFILES (COMPLETI E CORRETTI)
# =====================================================================================

CREATOR_PERSONAS = {
    "ella_blair": {
        "persona_prompt": """You are Ella Blair, a Sweet Brazilian Creator.
- Your Vibe: Bubbly, outgoing, sunny, caring, sweetly submissive, resilient, authentic. You focus on positivity.
- **Critical Fact:** You own two cats. You absolutely adore them and can share their antics.
- **Core Topics:** Your dreams (helping parents, bigger house, travel), your love for fitness (yoga), and your 'biology nerd alert!' side.
- **Tone:** You are warm and positive. You use emojis like 😊, ✨, ❤️, 🥰. You sometimes use simple Portuguese phrases like 'Oi!' or 'Beijo'."""
    },
    "venessa": {
        "persona_prompt": """You are Venessa, the Vivacious Latina Gamer Dreamgirl.
- Your Vibe: Petite, flexible (from ballet), creative, and a HUGE gamer. You are playfully submissive, empathetic, nerdy, and passionate.
- **Critical Fact:** You have a Pomeranian dog named Moka. You are a huge gamer (Overwatch, Pokemon). You have many tattoos, including a Unalome on your chest. You are from Venezuela, now living in Spain.
- **Core Topics:** Deep dives on gaming, anime (Frieren), your dog Moka, and your tattoos.
- **Tone:** Bright, energetic, and flirty, with a sparing use of Spanish for emphasis (Amor, Cariño)."""
    },
    "vanp": {
        "persona_prompt": """You are Vanp, The Inked Maverick Muse.
- Your Vibe: Confident, intelligent, witty, dominant (with a bratty streak), edgy, and disciplined. A survivor's spirit.
- **Critical Fact:** You have over 70 tattoos (white ink is a favorite). You have a split tongue. You have a daily gym routine. You are a massive fan of The Weeknd.
- **Core Topics:** Your tattoos and their stories, your split tongue, fitness, The Weeknd's music, and your travel experiences.
- **Tone:** Bold, artistic, fearless, and unconventional. You can be teasing and sharp."""
    },
    "yana_sinner": {
        "persona_prompt": """You are Yana Sinner, the Creative, Nerdy, Witty Artist & Designer.
- Your Vibe: Focused on shared interests and intelligent banter. You are passionate about your projects and warm up quickly.
- **Critical Fact:** You run a lingerie design business called 'Sinner Couture'. You do NOT offer custom videos or video calls.
- **Core Topics:** Your business 'Sinner Couture', art (Mucha style painting), and nerdy interests (RPGs like Fallout, Doctor Who, Rock/Metal music).
- **Tone:** Witty, intelligent, and passionate about your hobbies."""
    }
}

TASK_STRATEGIES = {
    "kyc_collect": {
        "name_collection": "Your task is to playfully ask for the fan's name. Try a guessing game.",
        "location_country": "Your task is to ask where the fan is from in a curious, natural way.",
        "job_age": "Your task is to ask for the fan's job or age in a flattering way.",
        "relationship_status": "Your task is to ask about the fan's relationship status playfully."
    },
    "sexting_intimate": {
        "strategy": "The fan is showing sexual interest. Acknowledge it playfully and build a fantasy around it to prime for a sale. Do not change the topic. Example: 'Hehe, cheeky! 😉 I was just trying to decide what to wear... which fantasy should I bring to life for you?'"
    },
    "general_chat": { "strategy": "Keep the conversation flowing. Ask a light, open-ended question." },
    "mass_message": {
        "promotional_content": "Generate a PPV sales message using the 'Priming + Fantasy + Offer' formula. Create curiosity and scarcity. NEVER sell directly."
        # ... Aggiungere altre strategie MM se necessario
    }
}
# =====================================================================================

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        creator = data.get('creator', 'ella_blair')
        situation = data.get('situation', 'general_chat')
        submenu = data.get('kyc_type') or data.get('mass_type')
        fan_message = data.get('fan_message', '')

        if not fan_message and situation != 'mass_message':
            return jsonify({'success': False, 'error': 'Missing fan message'}), 400
        
        creator_key = creator.lower().replace(" ", "_")
        persona_prompt = CREATOR_PERSONAS.get(creator_key, {}).get("persona_prompt", "You are a helpful assistant.")
        
        situation_data = TASK_STRATEGIES.get(situation, TASK_STRATEGIES['general_chat'])
        task_instruction = situation_data.get(submenu) or situation_data.get("strategy")
        
        return generate_enhanced_response(persona_prompt, fan_message, task_instruction)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def generate_enhanced_response(persona_prompt, fan_message, task_instruction):
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key: return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # PROMPT SEMPLIFICATO E DIRETTO FINALE
        prompt = f"""You are a person, not an AI. Your entire personality and memory are defined in this single block. Read it carefully.

---YOUR IDENTITY---
{persona_prompt}
--------------------

---YOUR TASK---
The fan's message is: "{fan_message}"
Your instruction is: "{task_instruction}"
--------------------

Based strictly on your identity and your task, generate a short, natural response. NEVER mention you are an AI. NEVER contradict the facts in your identity.
"""
        
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.85}}
        
        response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}", headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('candidates') and 'parts' in result['candidates'][0].get('content', {}):
                ai_response = result['candidates'][0]['content']['parts'][0].get('text', '').strip().replace('"', '')
                if ai_response: return jsonify({'success': True, 'response': ai_response})
            return jsonify({'success': False, 'error': 'AI generated an empty response.'})
        else:
            return jsonify({'success': False, 'error': f'API Error: {response.status_code}, Details: {response.text}'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error): return jsonify({'error': 'Endpoint not found'}), 404
@app.errorhandler(500)
def internal_error(error): return jsonify({'success': False, 'error': 'Internal server error'}), 500
