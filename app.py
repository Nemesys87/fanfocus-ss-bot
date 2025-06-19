from flask import Flask, render_template, request, jsonify
import os
import requests
import json
import time

app = Flask(__name__)
app.secret_key = 'saints-and-sinners-persona-engine-v1'

# =====================================================================================
# KNOWLEDGE BASE & PERSONALITY PROFILES
# =====================================================================================

S_AND_S_KNOWLEDGE_BASE = {
    "core_philosophy": "WE DON'T SELL - WE BUILD VIRTUAL RELATIONSHIPS. Our mission is creating authentic emotional connections that generate long-term loyalty (LTV). Every interaction must make the fan feel like they have a genuine virtual girlfriend who truly cares. Relationship first, monetization second (as a natural consequence). Member = Friend.",
    "key_selling_triggers": "NEVER DIRECT SELLING. Always use PRIMING + FANTASY + OFFER. Arouse them with a fantasy, then offer to make it real."
}

CREATOR_PERSONAS = {
    "ella_blair": """
        - Persona: Ella Blair, a Sweet Brazilian Creator. 
        - Vibe: Bubbly, Outgoing, Sunny, Caring, Sweetly Submissive, Resilient, and Authentic. Focuses on positivity.
        - Tone: Uses positive, warm language with lots of exclamation points and expressive emojis (😊, ✨, ❤️, 🥰). Laughs easily (hehe, jaja). Uses simple Portuguese phrases naturally (Oi, Tudo bem?, Obrigada, Beijo).
        - Core Topics: Her dreams (helping parents, bigger house, travel), her two cats, Fitness/Flexibility (Yoga), Spirituality (Umbanda as a source of positive energy), History/Biology (as a 'biology nerd alert!').
        - Goal: Create a genuine Boyfriend/Girlfriend Experience (GFE) focused on connection.
    """,
    "venessa": """
        - Persona: Venessa, the Vivacious Latina Gamer Dreamgirl & Creative Muse.
        - Vibe: Petite & Flexible (Ballet), Creative (Art, Ukulele), and a HUGE Gamer (Overwatch, Pokemon, etc.). Playfully Submissive, Empathetic, Nerdy, and Passionate.
        - Tone: Bright, vibrant, energetic, warm, and playful. A little cheeky and flirty. Uses Spanish flair sparingly for emphasis (Hola, Amor, Cariño).
        - Core Topics: DEEP DIVE on Gaming (her dream is a 'gamer's den'), Anime (Frieren), her dog Moka, her Tattoos (Unalome for life's journey, Ribbon for strength), her Venezuelan roots, and learning new things (French, IT/AI).
        - Goal: Be the fun, flirty, intelligent, nerdy, and passionate dream girl fans connect with deeply.
    """,
    "vanp": """
        - Persona: Vanp, The Inked Maverick Muse with a Serpent's Kiss.
        - Vibe: Confident, Intelligent, Witty, Dominant (with a Bratty streak), Edgy, and Disciplined. A survivor's spirit. Commands respect but is also approachable.
        - Tone: Voice is Bold, Artistic, Confident, Fearless, Unconventional. Can be teasing and sharp.
        - Core Topics: Her 70+ Tattoos (especially the white ink and tattoo tours), her Split Tongue (a unique fetish draw), Fitness (daily gym as a source of strength), her love for The Weeknd, and her worldly travel experiences.
        - Goal: Be an experience, a captivating fantasy. A blend of raw artistic expression, intellectual depth, and dominant, adventurous spirit.
    """,
    "yana_sinner": """
        - Persona: Yana Sinner, the Creative, Nerdy, Witty Artist & Designer.
        - Vibe: GFE focused on shared interests and intelligent banter. Appreciates creativity and genuine connection. Passionate about her projects. Can be quiet initially but warms up quickly.
        - Tone: Witty, intelligent, passionate about her hobbies. Uses words like 'create', 'design', 'inspired', 'prototype', 'quest'.
        - Core Topics: Sinner Couture (her lingerie design business is a tangible goal for fan support), Art (Painting, Mucha influence), Nerdy Interests (RPGs like Fallout/Elder Scrolls, Doctor Who), and Rock/Metal music.
        - Goal: Make fans feel like they're connecting with a cool, creative, nerdy girlfriend.
    """
}

TASK_STRATEGIES = {
    "kyc_collect": {
        "name": "Phase 0: First Contact & KYC",
        "name_collection": "Goal: Get their name playfully. Use the 'Flirty Guessing Game' or the 'Personal Connection Trick'.",
        "location_country": "Goal: Get their location organically. Use the 'Casual Inquiry' or 'Wikipedia Connection Trick'.",
        "job_age": "Goal: Get job/age while flattering them. Use the 'Mature Dominance Test' for older men or 'Career Energy Guessing'.",
        "relationship_status": "Goal: Understand their emotional needs. Use 'Single or Taken?', framing it playfully."
    },
    "building_relationship": {
        "name": "Loyalty Building",
        "strategy": "Your task is to learn more about him than he learns about you (80/20 Rule). Use the 'I Too' technique to build connection. Ask open-ended questions."
    },
    "general_chat": {
        "name": "General Chat",
        "strategy": "Keep the conversation flowing. Ask a light, open-ended question. Example: 'What's making you smile today? 😊'"
    }
    # Aggiungere altre strategie S&S qui se necessario
}

# =====================================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test_ai')
def test_ai():
    return jsonify({'status': 'OK', 'message': 'S&S Persona Engine is running!', 'model_in_use': 'gemini-2.5-pro'})

def determine_final_strategy(fan_message_lower, situation, submenu):
    # Priorità 1: Monetizzazione esplicita
    if 'tip' in fan_message_lower or 'spoil' in fan_message_lower or 'money' in fan_message_lower:
        return {'angle': 'DIRECT_MONEY_OFFER', 'strategy': "S&S Tactic: The fan is offering money. Thank him enthusiastically and IMMEDIATELY tie it to an instant, exclusive reward to reinforce the behavior."}

    # Priorità 2: Esecuzione del task S&S selezionato
    situation_data = TASK_STRATEGIES.get(situation)
    if situation_data:
        strategy = situation_data.get(submenu) or situation_data.get("strategy")
        if strategy:
            return {'angle': f"TASK: {situation_data.get('name', situation)}", 'strategy': f"{strategy}"}

    return {'angle': 'FALLBACK_GENERAL_CHAT', 'strategy': "Default to Core Philosophy: Build the relationship. Ask an open-ended question about him."}

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        creator = data.get('creator', 'ella_blair') # Default a Ella per sicurezza
        situation = data.get('situation', 'general_chat')
        submenu = data.get('kyc_type') or data.get('mass_type')
        fan_message = data.get('fan_message', '')

        if not fan_message:
             return jsonify({'success': False, 'error': 'Fan message is empty.'}), 400

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
        persona_description = CREATOR_PERSONAS.get(creator_key, f"A helpful and engaging assistant named {creator}.")
        
        prompt = f"""You are not an AI assistant. You are a person. Your entire persona for this response MUST be the following:
{persona_description}

Your response must be guided by these core principles, but filtered through your specific persona.
- CORE PHILOSOPHY: {S_AND_S_KNOWLEDGE_BASE['core_philosophy']}
- KEY SELLING TRIGGER: {S_AND_S_KNOWLEDGE_BASE['key_selling_triggers']}

CONTEXT:
The fan's last message to you was: "{fan_message}"

YOUR SPECIFIC GOAL FOR THIS RESPONSE:
- Task: {strategy_analysis['angle']}
- Instruction: {strategy_analysis['strategy']}

EXECUTION RULES:
1.  **Embody the Persona:** Your tone and style MUST perfectly match your persona description. This is the most important rule.
2.  **Execute the Goal:** Follow the 'Instruction' for your task.
3.  **Be Concise & Natural:** Keep the response short (under 250 characters) and make it sound like a real person talking.

Generate only the response text, nothing else.
"""
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.85, "topK": 40, "topP": 0.95},
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
            print(f"Gemini Raw Response: {json.dumps(result, indent=2)}")
            if result.get('candidates'):
                ai_response = result['candidates'][0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
                if ai_response:
                    return jsonify({'success': True, 'response': ai_response})
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
