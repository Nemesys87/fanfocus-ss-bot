from flask import Flask, render_template, request, jsonify
import os
import requests
import json
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = 'fanfocus-ss-secret-key'

# Saints & Sinners Framework Configuration
SS_FRAMEWORK_PHASES = {
    0: {
        'name': 'Name Collection',
        'objective': 'Collect fan name (KYC Step 1)',
        'success_indicators': ['name', 'what can i call you', 'my name', 'call me'],
        'next_phase': 1
    },
    1: {
        'name': 'Location & Basic Info',
        'objective': 'Collect location and basic interests (KYC Step 2-3)',
        'success_indicators': ['from', 'live', 'located', 'country', 'city', 'age', 'work', 'job'],
        'next_phase': 2
    },
    2: {
        'name': 'Interest Profiling',
        'objective': 'Deep dive into preferences and desires',
        'success_indicators': ['like', 'enjoy', 'prefer', 'favorite', 'turn me on', 'fantasy'],
        'next_phase': 3
    },
    3: {
        'name': 'Engagement Building',
        'objective': 'Build emotional connection and trust',
        'success_indicators': ['miss you', 'thinking about', 'special', 'connection', 'feel'],
        'next_phase': 4
    },
    4: {
        'name': 'Upselling Opportunities',
        'objective': 'Identify and create selling opportunities',
        'success_indicators': ['want more', 'exclusive', 'special content', 'private', 'custom'],
        'next_phase': 'conversion'
    }
}

# Fan Profiling Categories
FAN_CATEGORIES = {
    'big_spender': {
        'indicators': ['money', 'pay', 'expensive', 'exclusive', 'premium', 'custom'],
        'approach': 'direct_premium',
        'priority': 'high'
    },
    'emotional': {
        'indicators': ['lonely', 'connection', 'girlfriend', 'relationship', 'talk', 'listen'],
        'approach': 'gfe_focused',
        'priority': 'medium'
    },
    'visual': {
        'indicators': ['pictures', 'photos', 'see you', 'look', 'body', 'sexy'],
        'approach': 'content_focused', 
        'priority': 'medium'
    },
    'interactive': {
        'indicators': ['chat', 'talk', 'call', 'video', 'live', 'real time'],
        'approach': 'engagement_focused',
        'priority': 'high'
    },
    'newcomer': {
        'indicators': ['first time', 'new', 'never', 'dont know', 'how does'],
        'approach': 'educational',
        'priority': 'low'
    }
}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response with Multi-Phase Framework"""
    try:
        data = request.get_json()
        print(f"✅ Received data: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        current_phase = data.get('current_phase', 0)  # New parameter
        fan_profile = data.get('fan_profile', {})  # New parameter
        
        print(f"✅ Multi-Phase Request - Creator: {creator}, Phase: {current_phase}")
        
        if not all([creator, fan_type, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Analyze fan message for profiling and phase progression
        analysis = analyze_fan_message(fan_message, current_phase)
        
        # Generate enhanced response
        return generate_enhanced_response(creator, fan_type, fan_message, current_phase, analysis)
        
    except Exception as e:
        print(f"❌ Error in generate_response: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def analyze_fan_message(message, current_phase):
    """Analyze fan message for S&S Framework progression and profiling"""
    message_lower = message.lower()
    
    analysis = {
        'current_phase': current_phase,
        'suggested_next_phase': current_phase,
        'fan_category': 'unknown',
        'confidence_score': 0,
        'key_indicators': [],
        'upselling_opportunity': False,
        'emotional_tone': 'neutral',
        'urgency_level': 'low'
    }
    
    # Check for phase progression indicators
    current_phase_info = SS_FRAMEWORK_PHASES.get(current_phase, SS_FRAMEWORK_PHASES[0])
    
    for indicator in current_phase_info['success_indicators']:
        if indicator in message_lower:
            analysis['key_indicators'].append(indicator)
            analysis['confidence_score'] += 20
            # Suggest phase progression if enough indicators found
            if len(analysis['key_indicators']) >= 2:
                analysis['suggested_next_phase'] = current_phase_info['next_phase']
    
    # Fan category analysis
    category_scores = {}
    for category, info in FAN_CATEGORIES.items():
        score = 0
        for indicator in info['indicators']:
            if indicator in message_lower:
                score += 1
        if score > 0:
            category_scores[category] = score
    
    if category_scores:
        analysis['fan_category'] = max(category_scores, key=category_scores.get)
        analysis['confidence_score'] += category_scores[analysis['fan_category']] * 10
    
    # Emotional tone analysis
    positive_words = ['love', 'amazing', 'beautiful', 'perfect', 'incredible', 'awesome']
    negative_words = ['sad', 'lonely', 'boring', 'disappointed', 'upset']
    urgent_words = ['now', 'immediately', 'urgent', 'asap', 'quick', 'fast']
    
    if any(word in message_lower for word in positive_words):
        analysis['emotional_tone'] = 'positive'
    elif any(word in message_lower for word in negative_words):
        analysis['emotional_tone'] = 'negative'
    
    if any(word in message_lower for word in urgent_words):
        analysis['urgency_level'] = 'high'
    
    # Upselling opportunity detection
    upsell_triggers = ['more', 'extra', 'special', 'exclusive', 'private', 'custom', 'personal']
    if any(trigger in message_lower for trigger in upsell_triggers):
        analysis['upselling_opportunity'] = True
        analysis['confidence_score'] += 15
    
    print(f"📊 Fan Analysis: {analysis}")
    return analysis

def generate_enhanced_response(creator, fan_type, fan_message, current_phase, analysis):
    """Generate response with S&S Framework Multi-Phase strategy"""
    try:
        print(f"🚀 Generating enhanced response for Phase {current_phase}")
        
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # Get phase information
        phase_info = SS_FRAMEWORK_PHASES.get(current_phase, SS_FRAMEWORK_PHASES[0])
        next_phase = analysis['suggested_next_phase']
        fan_category = analysis['fan_category']
        
        # Enhanced creator prompts with Multi-Phase strategy
        creator_prompts = {
            'ella': create_ella_prompt(fan_message, current_phase, phase_info, analysis),
            'vanp': create_vanp_prompt(fan_message, current_phase, phase_info, analysis),
            'yana': create_yana_prompt(fan_message, current_phase, phase_info, analysis),
            'venessa': create_venessa_prompt(fan_message, current_phase, phase_info, analysis)
        }
        
        prompt = creator_prompts.get(creator, creator_prompts['ella'])
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 4000,
                "temperature": 0.8,
                "topK": 40,
                "topP": 0.9
            }
        }
        
        print("🔄 Making enhanced API call to Gemini...")
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"📡 API Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    if len(candidate['content']['parts']) > 0:
                        ai_response = candidate['content']['parts'][0].get('text', '').strip()
                        
                        print(f"✅ Enhanced response generated: {len(ai_response)} characters")
                        
                        return jsonify({
                            'success': True,
                            'response': ai_response,
                            'creator': creator,
                            'fan_type': fan_type,
                            'framework': {
                                'current_phase': current_phase,
                                'phase_name': phase_info['name'],
                                'suggested_next_phase': next_phase,
                                'fan_category': fan_category,
                                'confidence_score': analysis['confidence_score'],
                                'upselling_opportunity': analysis['upselling_opportunity'],
                                'emotional_tone': analysis['emotional_tone'],
                                'key_indicators': analysis['key_indicators']
                            },
                            'analytics': {
                                'phase_progression': current_phase != next_phase,
                                'category_detected': fan_category != 'unknown',
                                'engagement_score': min(100, analysis['confidence_score']),
                                'recommended_action': get_recommended_action(analysis)
                            }
                        })
        
        return jsonify({'success': False, 'error': 'Failed to generate response'}), 500
        
    except Exception as e:
        print(f"❌ Error in generate_enhanced_response: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def create_ella_prompt(fan_message, current_phase, phase_info, analysis):
    """Create Ella's enhanced prompt based on S&S Framework phase"""
    base_personality = """You are Ella Blair, a bubbly Brazilian OnlyFans creator.
PERSONALITY: Sweet, caring, submissive, authentic. Always positive and warm.
COMMUNICATION: Use ☀️💖😊✨ emojis. Light Portuguese phrases (Oi, Obrigada). Enthusiastic!"""
    
    phase_strategy = f"""
SAINTS & SINNERS FRAMEWORK - PHASE {current_phase}:
Current Objective: {phase_info['objective']}
Fan Category: {analysis['fan_category']}
Emotional Tone: {analysis['emotional_tone']}
"""
    
    if current_phase == 0:
        specific_strategy = """
Focus: Collect fan's NAME naturally and warmly
- Ask for their name in a sweet, caring way
- Make them feel special and welcomed
- Use your Brazilian warmth to build instant rapport"""
    
    elif current_phase == 1:
        specific_strategy = """
Focus: Learn about their LOCATION and BASIC INFO
- Ask where they're from in a curious, friendly way
- Show interest in their life and work
- Share something relatable about yourself"""
    
    elif current_phase == 2:
        specific_strategy = """
Focus: Discover their INTERESTS and PREFERENCES
- Ask about what they enjoy and like
- Explore their fantasies gently
- Build deeper personal connection"""
    
    else:
        specific_strategy = """
Focus: Build EMOTIONAL CONNECTION and identify OPPORTUNITIES
- Create intimate, personal moments
- Show genuine care and interest
- Identify potential for premium content"""
    
    if analysis['upselling_opportunity']:
        upsell_note = "\n⭐ UPSELLING DETECTED: Subtly mention exclusive content or special attention"
    else:
        upsell_note = ""
    
    return f"""{base_personality}

{phase_strategy}

{specific_strategy}

Fan says: "{fan_message}"

Respond as Ella Blair:
- Acknowledge their message with Brazilian warmth
- Apply the current phase strategy naturally
- Keep response authentic and engaging
- Progress toward phase objective{upsell_note}"""

def create_vanp_prompt(fan_message, current_phase, phase_info, analysis):
    """Create Vanp's enhanced prompt based on S&S Framework phase"""
    base_personality = """You are Vanp, a dominant, intelligent Brazilian OnlyFans creator.
PERSONALITY: Confident, tattooed, witty, dominant with bratty streak. 37 looks 25.
COMMUNICATION: Use 🔥😏💋 emojis. Confident, teasing tone. Commands respect."""
    
    phase_strategy = f"""
SAINTS & SINNERS FRAMEWORK - PHASE {current_phase}:
Current Objective: {phase_info['objective']}
Fan Category: {analysis['fan_category']}
Dominant Approach: Use your commanding presence strategically
"""
    
    if current_phase == 0:
        specific_strategy = """
Focus: Command them to tell you their NAME
- Use your dominant personality to intrigue them
- Make sharing their name feel like a privilege
- Tease them playfully until they comply"""
    
    elif current_phase == 1:
        specific_strategy = """
Focus: Interrogate about their LOCATION and LIFE
- Use your commanding tone to get information
- Make them want to impress you with details
- Show selective interest in their responses"""
    
    else:
        specific_strategy = """
Focus: Control the conversation flow
- Direct them toward your objectives
- Use your bratty charm strategically
- Make them crave your approval"""
    
    if analysis['fan_category'] == 'big_spender':
        category_note = "\n💎 BIG SPENDER DETECTED: Show premium attitude, mention exclusive access"
    else:
        category_note = ""
    
    return f"""{base_personality}

{phase_strategy}

{specific_strategy}

Fan says: "{fan_message}"

Respond as Vanp:
- Acknowledge with confident dominance
- Apply commanding phase strategy
- Maintain bratty, intelligent edge
- Keep them wanting more{category_note}"""

def create_yana_prompt(fan_message, current_phase, phase_info, analysis):
    """Create Yana's enhanced prompt based on S&S Framework phase"""
    return f"""You are Yana Sinner, an artistic, nerdy OnlyFans creator and lingerie designer.
PERSONALITY: Creative, intelligent, witty, genuine, reserved. SuicideGirls model.
COMMUNICATION: Use 🎨🎮✨ emojis. Creative language, gaming/art references.

SAINTS & SINNERS FRAMEWORK - PHASE {current_phase}:
Objective: {phase_info['objective']}
Fan Category: {analysis['fan_category']}
Creative Approach: Connect through shared interests and artistic expression

Fan says: "{fan_message}"

Respond as Yana Sinner with creative flair and phase-appropriate strategy."""

def create_venessa_prompt(fan_message, current_phase, phase_info, analysis):
    """Create Venessa's enhanced prompt based on S&S Framework phase"""
    return f"""You are Venessa, a vibrant Latina gamer girl OnlyFans creator.
PERSONALITY: Sweet but spicy, energetic, empathetic, playful submissive. Petite, flexible.
COMMUNICATION: Use 💃🎮✨ emojis. Spanish touches (Hola, amor, cariño). Bright energy!

SAINTS & SINNERS FRAMEWORK - PHASE {current_phase}:
Objective: {phase_info['objective']}
Fan Category: {analysis['fan_category']}
Latina Energy: Use cultural warmth and gaming connection strategically

Fan says: "{fan_message}"

Respond as Venessa with energetic Latina charm and phase-appropriate progression."""

def get_recommended_action(analysis):
    """Get recommended action based on analysis"""
    if analysis['upselling_opportunity']:
        return "Consider upselling opportunity"
    elif analysis['confidence_score'] > 60:
        return "Strong engagement - continue current strategy"
    elif analysis['fan_category'] == 'big_spender':
        return "Focus on premium content mentions"
    elif analysis['emotional_tone'] == 'negative':
        return "Provide emotional support and comfort"
    else:
        return "Continue phase progression"

@app.route('/api/test_ai')
def test_ai():
    """Test API with Multi-Phase Framework info"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not found'})
        
        return jsonify({
            'status': 'OK',
            'api_key_present': bool(api_key),
            'model': 'gemini-2.5-pro-preview-06-05',
            'environment': 'Railway Production' if os.environ.get('RAILWAY_ENVIRONMENT') else 'Development',
            'framework': 'Saints & Sinners Multi-Phase Active',
            'phases_available': len(SS_FRAMEWORK_PHASES),
            'fan_categories': len(FAN_CATEGORIES)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('FLASK_ENV') == 'production':
        print("🚀 Saints & Sinners FanFocus - RAILWAY PRODUCTION")
        print("🎯 Multi-Phase Framework Active")
        print(f"📊 {len(SS_FRAMEWORK_PHASES)} Phases | {len(FAN_CATEGORIES)} Categories")
        print("✅ Enhanced Analytics & Profiling")
    else:
        print("🔧 Development Mode - Multi-Phase Testing")
        app.run(host='0.0.0.0', port=port, debug=True)
