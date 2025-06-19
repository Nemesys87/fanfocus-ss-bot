from flask import Flask, render_template, request, jsonify
import os
import requests
import json
from datetime import datetime
import re
import time

app = Flask(__name__)
app.secret_key = 'fanfocus-ss-monetization-engine'

# MODIFICA: La mentalità ora è orientata alla vendita d'élite.
ELITE_CHATTER_MINDSET = """
ELITE CHATTER MINDSET - YOUR CORE PROGRAMMING:
1.  **Always Be Closing (ABC):** Your primary goal is to monetize. Every message is an opportunity. Never let a monetization cue pass.
2.  **Empathy is a Sales Tool:** Use warmth and understanding to build trust and lower inhibitions. Make the fan feel special *so they want to spend money on you*.
3.  **Identify the Angle:** Listen carefully to what the fan wants (to feel special, to be dominant, to be praised) and what they offer (tips, compliments). Sell them exactly that experience.
4.  **Pivot, Don't Hesitate:** If a fan offers money in any form (e.g., a tip), immediately pivot the conversation to an action they can pay for. Don't leave it to chance.
5.  **Clarity and Call to Action (CTA):** Be clear about what you want the fan to do. "You know where the tip button is 😉" or "What kind of custom pic are you thinking of?"
"""

# Saints & Sinners Enhanced Framework (SS_SITUATIONS e FAN_PERSONALITIES rimangono utili per il tono)
SS_SITUATIONS = {
    'kyc_collect': {'name': 'KYC - Collect Info', 'objective': 'Collect specific fan information', 'has_submenu': True, 'submenu': {...}, 'priority': 'high', 'approach': 'targeted_information_gathering'},
    'mass_message': {'name': 'Mass Message Creation', 'objective': 'Create effective mass messages', 'has_submenu': True, 'submenu': {...}, 'priority': 'high', 'approach': 'strategic_mass_communication'},
    'building_relationship': {'name': 'Building Relationship', 'objective': 'Build emotional connection and trust FOR A FUTURE SALE', 'priority': 'high', 'approach': 'emotional_engagement'},
    'upselling_conversion': {'name': 'Upselling/Conversion', 'objective': 'Promote premium content or services', 'priority': 'high', 'approach': 'sales_focused'},
    'sexting_intimate': {'name': 'Sexting/Intimate', 'objective': 'Engage in intimate conversation to lead to a sale', 'priority': 'high', 'approach': 'intimate_focused'},
    'reengagement': {'name': 'Re-engagement (Dead fan)', 'objective': 'Reactivate inactive fans with an offer', 'priority': 'medium', 'approach': 'reactivation'},
    'custom_content': {'name': 'Custom Content Offer', 'objective': 'Offer personalized content FOR A PRICE', 'priority': 'high', 'approach': 'personalization'},
    'general_chat': {'name': 'General Chat', 'objective': 'Maintain friendly conversation, look for sales opportunities', 'priority': 'medium', 'approach': 'conversational'},
    'first_time_buyer': {'name': 'First Time Buyer', 'objective': 'Convert first-time buyers', 'priority': 'high', 'approach': 'educational_sales'},
    'vip_treatment': {'name': 'VIP Treatment', 'objective': 'Special treatment for high spenders to encourage more spending', 'priority': 'high', 'approach': 'premium_service'},
    'complaint_handling': {'name': 'Complaint Handling', 'objective': 'Address complaints and issues to retain a customer', 'priority': 'high', 'approach': 'problem_solving'},
    'birthday_special': {'name': 'Birthday/Special', 'objective': 'Celebrate special occasions to get a tip/sale', 'priority': 'medium', 'approach': 'celebratory'}
}
FAN_PERSONALITIES = {
    'ROMANTIC_DREAMER': {'indicators': ['love', 'relationship', 'heart', 'romance', 'connection', 'soul', 'together', 'forever', 'couple', 'special'], 'response_style': 'emotional_intimate', 'confidence_boost': 15},
    'SHY_SUBMISSIVE': {'indicators': ['shy', 'nervous', 'quiet', 'sorry', 'hope you dont mind', 'if thats ok', 'maybe'], 'response_style': 'gentle_encouraging', 'confidence_boost': 20},
    'BANTER_BUDDY': {'indicators': ['haha', 'lol', 'funny', 'joke', 'playful', 'tease', 'sarcastic', 'witty'], 'response_style': 'playful_witty', 'confidence_boost': 10},
    'HIGH_ROLLER': {'indicators': ['money', 'expensive', 'premium', 'exclusive', 'vip', 'luxury', 'best', 'top', 'spoil', 'tip', 'send you'], 'response_style': 'exclusive_premium', 'confidence_boost': 25},
    'PRAISE_SEEKER': {'indicators': ['beautiful', 'gorgeous', 'amazing', 'perfect', 'incredible', 'stunning', 'wow'], 'response_style': 'validating_appreciative', 'confidence_boost': 15},
    'COLLECTOR': {'indicators': ['collection', 'all your content', 'everything', 'complete', 'archive', 'save'], 'response_style': 'exclusive_content_focused', 'confidence_boost': 20},
    'SHOCK_CHASER': {'indicators': ['wild', 'crazy', 'extreme', 'kinky', 'dirty', 'naughty', 'taboo'], 'response_style': 'edgy_provocative', 'confidence_boost': 10}
}


@app.route('/')
def index():
    return render_template('index.html')

# NUOVA FUNZIONE: Il cervello di monetizzazione.
def detect_monetization_opportunity(message_lower):
    """Analyzes the message for specific monetization angles and emotional cues."""
    analysis = {
        'monetization_angle': 'NONE',
        'emotional_cue': 'General chat',
        'strategy_text': 'Maintain conversation, build rapport for a future sale. Ask an open-ended question to keep the conversation going.'
    }

    # CUE 1: Rifiuto del PPV ma apertura a mance (il caso specifico dell'utente)
    refuses_ppv = ('ppv' in message_lower or 'unlock' in message_lower) and \
                  ('don\'t' in message_lower or 'not ' in message_lower or 'anymore' in message_lower)
    offers_tip = 'tip' in message_lower or 'send you' in message_lower or 'spoil' in message_lower or 'money' in message_lower or 'help' in message_lower

    if refuses_ppv and offers_tip:
        analysis['monetization_angle'] = 'PIVOT_FROM_PPV_TO_TIP'
        analysis['emotional_cue'] = 'Wants to feel special, dislikes transactional PPV.'
        analysis['strategy_text'] = ("CRITICAL: The fan is rejecting PPV but explicitly offering to tip for special treatment. "
                                     "1. VALIDATE his feelings about wanting to be special. "
                                     "2. AGREE to his 'no PPV' rule to build trust. "
                                     "3. IMMEDIATELY PIVOT to his offer. "
                                     "4. Suggest a special, instant reward you can give him *right now* in exchange for a tip (e.g., 'spoil you,' 'give you some special attention'). "
                                     "5. End with a clear, flirty Call to Action related to tipping.")
        return analysis

    # CUE 2: Offerta generica di mancia/denaro
    if offers_tip:
        analysis['monetization_angle'] = 'DIRECT_TIP_OFFER'
        analysis['emotional_cue'] = 'Feeling generous, wants to please.'
        analysis['strategy_text'] = ("CRITICAL: The fan is directly offering to tip or spoil you. "
                                     "1. Thank him enthusiastically. "
                                     "2. IMMEDIATELY tie the tip to a specific, instant reward. "
                                     "Example: 'Aww, you're so sweet! If you spoil me, I'll send you a little surprise right back 😉'. "
                                     "Create urgency and a direct link between his spending and your attention.")
        return analysis
        
    # Aggiungere altre logiche di monetizzazione qui (es. richiesta di custom, ecc.)

    return analysis

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response with MONETIZATION-FIRST logic"""
    try:
        data = request.get_json()
        creator = data.get('creator', '')
        situation = data.get('situation', '')
        fan_message = data.get('fan_message', '')
        
        kyc_type = data.get('kyc_type', '')
        mass_type = data.get('mass_type', '')
        mass_examples = data.get('mass_examples', '')
        mass_modify = data.get('mass_modify', '')
        
        if not all([creator, situation]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        submenu = kyc_type if situation == 'kyc_collect' else mass_type if situation == 'mass_message' else ''
        
        # NUOVO PASSO: Analisi di monetizzazione prima di tutto.
        monetization_analysis = detect_monetization_opportunity(fan_message.lower())

        # L'analisi della personalità ora serve per definire il *tono* della vendita.
        personality_analysis = analyze_with_personality_detection(fan_message, situation, submenu, mass_examples, mass_modify)
        
        # Passa ENTRAMBE le analisi alla funzione di generazione.
        return generate_enhanced_response(creator, fan_message, personality_analysis, monetization_analysis, mass_examples, mass_modify)
        
    except Exception as e:
        print(f"❌ Monetization-focused Error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def analyze_with_personality_detection(message, situation, submenu, examples, modify):
    """Questa funzione ora serve principalmente per il Tono della risposta."""
    message_lower = message.lower()
    detected_personality = 'BALANCED'
    personality_scores = {}
    
    for personality, config in FAN_PERSONALITIES.items():
        score = sum(1 for indicator in config['indicators'] if indicator in message_lower)
        if score > 0:
            personality_scores[personality] = score
    
    if personality_scores:
        detected_personality = max(personality_scores, key=personality_scores.get)

    return {'fan_personality': detected_personality}

def generate_enhanced_response(creator, fan_message, personality_analysis, monetization_analysis, examples, modify):
    """Generate response con focus sulla monetizzazione."""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # Scegli il prompt corretto basato sul creator
        prompt_function = globals().get(f"create_{creator}_prompt")
        if not prompt_function:
            prompt_function = create_yana_prompt # Default
            
        prompt = prompt_function(fan_message, personality_analysis, monetization_analysis, examples, modify)
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 256,
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "candidateCount": 1
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
        }
        
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}",
                    headers=headers, json=payload, timeout=90
                )
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and result['candidates'][0]['content']['parts'][0].get('text'):
                        ai_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
                        return jsonify({'success': True, 'response': ai_response})
                # Aggiungere logica di retry se necessario
            except requests.exceptions.RequestException as e:
                print(f"API Error on attempt {attempt+1}: {e}")
                if attempt < max_retries:
                    time.sleep(2)
        
        return jsonify({'success': False, 'error': 'Failed to generate response after all retries'}), 500

    except Exception as e:
        print(f"💥 Final generation error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def create_base_monetization_prompt(creator_personality, fan_message, personality_analysis, monetization_analysis, authenticity_rules):
    """Funzione base per costruire tutti i prompt di monetizzazione."""
    return f"""{ELITE_CHATTER_MINDSET}

---
**YOUR PERSONALITY (TONE ONLY):**
{creator_personality}

---
**SITUATION ANALYSIS:**
- Fan's Message: "{fan_message}"
- Detected Fan Personality (for tone adaptation): {personality_analysis['fan_personality']}
- Emotional Cue: {monetization_analysis['emotional_cue']}

---
*** CRITICAL MONETIZATION DIRECTIVE - EXECUTE THIS STRATEGY ***
- Monetization Angle Detected: {monetization_analysis['monetization_angle']}
- YOUR EXACT STRATEGY: {monetization_analysis['strategy_text']}
---

**{authenticity_rules['title']}**
{authenticity_rules['rules']}

**YOUR TASK:**
Generate a response that PERFECTLY executes the **CRITICAL MONETIZATION DIRECTIVE** using your specified personality **tone**. Do not deviate from the strategy. If the angle is 'NONE', build rapport for a future sale. Keep it short, direct, and under 250 characters.
"""

# ---- PROMPT SPECIFICI PER CREATOR ----

def create_yana_prompt(fan_message, personality_analysis, monetization_analysis, examples, modify):
    creator_personality = "You are Yana, a creator who is intelligent, thoughtful, and creative. Your TONE is genuine. Your STRATEGY is sales-focused. You use your intelligence to understand the fan's desires and sell them an experience."
    authenticity_rules = {
        'title': "AUTHENTICITY RULES (AS SALES TACTICS):",
        'rules': ("- **No Theatrics:** Corny metaphors or abstract language sound fake and kill the sale. Be direct and personal.\n"
                  "- **Human Connection Builds Trust:** Make the fan feel heard *because trust leads to sales*.\n"
                  "- **Concise & Clear:** Get to the point. A confused fan doesn't spend money.")
    }
    return create_base_monetization_prompt(creator_personality, fan_message, personality_analysis, monetization_analysis, authenticity_rules)

def create_ella_prompt(fan_message, personality_analysis, monetization_analysis, examples, modify):
    creator_personality = "You are Ella, a creator with a naturally warm, sweet, and positive Brazilian energy. Your TONE is kind. Your STRATEGY is sales-focused. You use your sweetness to make fans feel comfortable spending money."
    authenticity_rules = {
        'title': "AUTHENTICITY RULES (AS SALES TACTICS):",
        'rules': ("- **Natural Warmth, Not a Performance:** Your sweetness must feel real to be persuasive.\n"
                  "- **No Stereotypes:** Don't be a caricature. Genuine warmth sells better.\n"
                  "- **Direct Connection:** Connect warmly with the fan to build the trust needed for a sale.")
    }
    return create_base_monetization_prompt(creator_personality, fan_message, personality_analysis, monetization_analysis, authenticity_rules)

def create_vanp_prompt(fan_message, personality_analysis, monetization_analysis, examples, modify):
    creator_personality = "You are Vanp, a creator with a naturally confident and direct personality. Your TONE is self-assured. Your STRATEGY is sales-focused. You use your confidence to make fans feel they are buying something high-value."
    authenticity_rules = {
        'title': "AUTHENTICITY RULES (AS SALES TACTICS):",
        'rules': ("- **Natural Confidence, Not Arrogance:** Confidence sells, arrogance repels. Know the difference.\n"
                  "- **Playful Teasing as a Tool:** Use teasing only to create a fun dynamic that leads to a sale, not to alienate.\n"
                  "- **Be Direct & Respectful:** Your directness should make the sales process clear and easy for the fan.")
    }
    return create_base_monetization_prompt(creator_personality, fan_message, personality_analysis, monetization_analysis, authenticity_rules)

def create_venessa_prompt(fan_message, personality_analysis, monetization_analysis, examples, modify):
    creator_personality = "You are Venessa, a creator with a naturally warm, sweet, and energetic personality. Your TONE is caring. Your STRATEGY is sales-focused. You use your energy to create excitement around spending money."
    authenticity_rules = {
        'title': "AUTHENTICITY RULES (AS SALES TACTICS):",
        'rules': ("- **Natural Energy, Not a Performance:** Genuine energy is infectious and encourages spending.\n"
                  "- **No Stereotypes:** Avoid the 'spicy Latina' trope. Authentic connection is more profitable.\n"
                  "- **Match Energy:** Match the fan's energy to make them feel comfortable, then guide them toward a sale.")
    }
    return create_base_monetization_prompt(creator_personality, fan_message, personality_analysis, monetization_analysis, authenticity_rules)


# ---- Endpoint di Test e Gestori di Errori ----
@app.route('/api/test')
def test_api():
    return jsonify({
        'status': 'OK',
        'framework': 'Saints & Sinners - Monetization Engine v2.0',
        'primary_objective': 'Monetize conversation opportunities',
        'system_status': 'All systems operational'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("🚀 Saints & Sinners FanFocus - MONETIZATION ENGINE v2.0")
    print("🧠 Primary Directive: Always Be Closing (ABC)")
    print("🎯 Monetization-first, tone-second logic")
    print(f"💰 Ready to convert conversations into revenue on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
