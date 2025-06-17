from flask import Flask, render_template, request, jsonify, session
import os
import requests
import json
from datetime import datetime
import re
import uuid

app = Flask(__name__)
app.secret_key = 'fanfocus-ss-secret-key'

# Session Memory Storage (in-memory for current session)
session_memory = {}

# Saints & Sinners Framework Configuration
SS_FRAMEWORK_PHASES = {
    0: {
        'name': 'Name Collection',
        'objective': 'Collect fan name (KYC Step 1)',
        'success_indicators': ['name', 'what can i call you', 'my name', 'call me', 'i am', "i'm"],
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
        'indicators': ['money', 'pay', 'expensive', 'exclusive', 'premium', 'custom', 'buy', 'purchase'],
        'approach': 'direct_premium',
        'priority': 'high'
    },
    'emotional': {
        'indicators': ['lonely', 'connection', 'girlfriend', 'relationship', 'talk', 'listen', 'feel', 'love'],
        'approach': 'gfe_focused',
        'priority': 'medium'
    },
    'visual': {
        'indicators': ['pictures', 'photos', 'see you', 'look', 'body', 'sexy', 'beautiful', 'hot'],
        'approach': 'content_focused', 
        'priority': 'medium'
    },
    'interactive': {
        'indicators': ['chat', 'talk', 'call', 'video', 'live', 'real time', 'voice', 'cam'],
        'approach': 'engagement_focused',
        'priority': 'high'
    },
    'newcomer': {
        'indicators': ['first time', 'new', 'never', 'dont know', 'how does', 'what is'],
        'approach': 'educational',
        'priority': 'low'
    }
}

@app.route('/')
def index():
    """Main page with session initialization"""
    # Initialize session if not exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        print(f"🆕 New session created: {session['session_id']}")
    
    return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response with Session Memory"""
    try:
        data = request.get_json()
        print(f"✅ Received data: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')
        fan_message = data.get('fan_message', '')
        current_phase = data.get('current_phase', 0)
        fan_id = data.get('fan_id', 'default_fan')  # New: Fan ID for memory
        
        print(f"✅ Session Memory Request - Creator: {creator}, Phase: {current_phase}, Fan: {fan_id}")
        
        if not all([creator, fan_type, fan_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Update session memory with new interaction
        update_session_memory(fan_id, {
            'message': fan_message,
            'timestamp': datetime.now().isoformat(),
            'creator': creator,
            'phase': current_phase
        })
        
        # Get fan context from memory
        fan_context = get_fan_context(fan_id)
        
        # Analyze fan message with memory context
        analysis = analyze_fan_message_with_memory(fan_message, current_phase, fan_context)
        
        # Generate enhanced response with memory
        return generate_memory_enhanced_response(creator, fan_type, fan_message, current_phase, analysis, fan_context)
        
    except Exception as e:
        print(f"❌ Error in generate_response: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def update_session_memory(fan_id, interaction_data):
    """Update session memory with new fan interaction"""
    session_id = session.get('session_id', 'default')
    
    if session_id not in session_memory:
        session_memory[session_id] = {}
    
    if fan_id not in session_memory[session_id]:
        session_memory[session_id][fan_id] = {
            'fan_id': fan_id,
            'first_interaction': datetime.now().isoformat(),
            'total_interactions': 0,
            'detected_info': {
                'name': None,
                'location': None,
                'interests': [],
                'preferences': [],
                'emotional_patterns': []
            },
            'phase_history': [0],
            'category_scores': {},
            'interaction_history': []
        }
    
    fan_data = session_memory[session_id][fan_id]
    fan_data['total_interactions'] += 1
    fan_data['last_interaction'] = datetime.now().isoformat()
    fan_data['interaction_history'].append(interaction_data)
    
    # Extract and store information from message
    extract_fan_info(fan_data, interaction_data['message'])
    
    print(f"🧠 Memory updated for {fan_id}: {fan_data['total_interactions']} interactions")
    
def extract_fan_info(fan_data, message):
    """Extract and store fan information from message"""
    message_lower = message.lower()
    
    # Extract name patterns
    name_patterns = [
        r"my name is (\w+)",
        r"i am (\w+)",
        r"i'm (\w+)", 
        r"call me (\w+)",
        r"name's (\w+)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, message_lower)
        if match and not fan_data['detected_info']['name']:
            fan_data['detected_info']['name'] = match.group(1).title()
            print(f"📝 Extracted name: {fan_data['detected_info']['name']}")
    
    # Extract location patterns
    location_patterns = [
        r"from (\w+)",
        r"live in (\w+)",
        r"located in (\w+)",
        r"i'm in (\w+)"
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, message_lower)
        if match and not fan_data['detected_info']['location']:
            fan_data['detected_info']['location'] = match.group(1).title()
            print(f"📍 Extracted location: {fan_data['detected_info']['location']}")
    
    # Extract interests
    interest_keywords = ['gaming', 'music', 'sports', 'movies', 'art', 'travel', 'fitness', 'cooking']
    for interest in interest_keywords:
        if interest in message_lower and interest not in fan_data['detected_info']['interests']:
            fan_data['detected_info']['interests'].append(interest)
            print(f"🎯 Detected interest: {interest}")

def get_fan_context(fan_id):
    """Retrieve fan context from session memory"""
    session_id = session.get('session_id', 'default')
    
    if session_id in session_memory and fan_id in session_memory[session_id]:
        context = session_memory[session_id][fan_id]
        print(f"🧠 Retrieved context for {fan_id}: {context['total_interactions']} interactions")
        return context
    
    print(f"🆕 No context found for {fan_id} - new fan")
    return {}

def analyze_fan_message_with_memory(message, current_phase, fan_context):
    """Enhanced analysis with memory context"""
    message_lower = message.lower()
    
    analysis = {
        'current_phase': current_phase,
        'suggested_next_phase': current_phase,
        'fan_category': 'unknown',
        'confidence_score': 0,
        'key_indicators': [],
        'upselling_opportunity': False,
        'emotional_tone': 'neutral',
        'urgency_level': 'low',
        'memory_context': {
            'returning_fan': len(fan_context) > 0,
            'total_interactions': fan_context.get('total_interactions', 0),
            'known_info': fan_context.get('detected_info', {})
        }
    }
    
    # Boost confidence if we have memory context
    if fan_context:
        analysis['confidence_score'] += 20
        if fan_context.get('detected_info', {}).get('name'):
            analysis['confidence_score'] += 15
        if fan_context.get('detected_info', {}).get('location'):
            analysis['confidence_score'] += 10
    
    # Check for phase progression indicators
    current_phase_info = SS_FRAMEWORK_PHASES.get(current_phase, SS_FRAMEWORK_PHASES[0])
    
    for indicator in current_phase_info['success_indicators']:
        if indicator in message_lower:
            analysis['key_indicators'].append(indicator)
            analysis['confidence_score'] += 20
            # Suggest phase progression if enough indicators found
            if len(analysis['key_indicators']) >= 1:  # Reduced threshold for memory-enhanced
                analysis['suggested_next_phase'] = current_phase_info['next_phase']
    
    # Enhanced fan category analysis with memory
    category_scores = fan_context.get('category_scores', {})
    
    for category, info in FAN_CATEGORIES.items():
        score = category_scores.get(category, 0)
        for indicator in info['indicators']:
            if indicator in message_lower:
                score += 1
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
    
    # Upselling opportunity detection (enhanced with memory)
    upsell_triggers = ['more', 'extra', 'special', 'exclusive', 'private', 'custom', 'personal']
    if any(trigger in message_lower for trigger in upsell_triggers):
        analysis['upselling_opportunity'] = True
        analysis['confidence_score'] += 15
    
    print(f"📊 Memory-Enhanced Analysis: {analysis}")
    return analysis

def generate_memory_enhanced_response(creator, fan_type, fan_message, current_phase, analysis, fan_context):
    """Generate response enhanced with session memory"""
    try:
        print(f"🚀 Generating memory-enhanced response for Phase {current_phase}")
        
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # Get phase information
        phase_info = SS_FRAMEWORK_PHASES.get(current_phase, SS_FRAMEWORK_PHASES[0])
        next_phase = analysis['suggested_next_phase']
        fan_category = analysis['fan_category']
        
        # Build memory context for prompt
        memory_context = build_memory_context(fan_context)
        
        # Enhanced creator prompts with Memory + Multi-Phase strategy
        creator_prompts = {
            'ella': create_memory_ella_prompt(fan_message, current_phase, phase_info, analysis, memory_context),
            'vanp': create_memory_vanp_prompt(fan_message, current_phase, phase_info, analysis, memory_context),
            'yana': create_memory_yana_prompt(fan_message, current_phase, phase_info, analysis, memory_context),
            'venessa': create_memory_venessa_prompt(fan_message, current_phase, phase_info, analysis, memory_context)
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
        
        print("🔄 Making memory-enhanced API call to Gemini...")
        
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
                        
                        print(f"✅ Memory-enhanced response generated: {len(ai_response)} characters")
                        
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
                            'memory': {
                                'returning_fan': analysis['memory_context']['returning_fan'],
                                'total_interactions': analysis['memory_context']['total_interactions'],
                                'known_name': fan_context.get('detected_info', {}).get('name'),
                                'known_location': fan_context.get('detected_info', {}).get('location'),
                                'known_interests': fan_context.get('detected_info', {}).get('interests', [])
                            },
                            'analytics': {
                                'phase_progression': current_phase != next_phase,
                                'category_detected': fan_category != 'unknown',
                                'engagement_score': min(100, analysis['confidence_score']),
                                'recommended_action': get_recommended_action(analysis),
                                'memory_boost': len(fan_context) > 0
                            }
                        })
        
        return jsonify({'success': False, 'error': 'Failed to generate response'}), 500
        
    except Exception as e:
        print(f"❌ Error in generate_memory_enhanced_response: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def build_memory_context(fan_context):
    """Build memory context string for AI prompt"""
    if not fan_context:
        return "First-time interaction with this fan."
    
    detected_info = fan_context.get('detected_info', {})
    total_interactions = fan_context.get('total_interactions', 0)
    
    context_parts = [f"Previous interactions: {total_interactions}"]
    
    if detected_info.get('name'):
        context_parts.append(f"Fan's name: {detected_info['name']}")
    
    if detected_info.get('location'):
        context_parts.append(f"Location: {detected_info['location']}")
    
    if detected_info.get('interests'):
        context_parts.append(f"Interests: {', '.join(detected_info['interests'])}")
    
    return " | ".join(context_parts)

def create_memory_ella_prompt(fan_message, current_phase, phase_info, analysis, memory_context):
    """Create Ella's memory-enhanced prompt"""
    base_personality = """You are Ella Blair, a bubbly Brazilian OnlyFans creator.
PERSONALITY: Sweet, caring, submissive, authentic. Always positive and warm.
COMMUNICATION: Use ☀️💖😊✨ emojis. Light Portuguese phrases (Oi, Obrigada). Enthusiastic!"""
    
    memory_instruction = f"""
MEMORY CONTEXT: {memory_context}
- Use this information to personalize your response
- Reference previous conversations naturally if applicable
- Show you remember and care about details they shared"""
    
    phase_strategy = f"""
SAINTS & SINNERS FRAMEWORK - PHASE {current_phase}:
Current Objective: {phase_info['objective']}
Fan Category: {analysis['fan_category']}
Emotional Tone: {analysis['emotional_tone']}
"""
    
    if current_phase == 0:
        specific_strategy = """
Focus: Collect fan's NAME naturally and warmly
- If returning fan, show you remember them warmly
- If new fan, ask for their name in sweet way
- Use your Brazilian warmth to build rapport"""
    
    elif current_phase == 1:
        specific_strategy = """
Focus: Learn about their LOCATION and BASIC INFO
- If you know their name, use it lovingly
- Ask where they're from with genuine curiosity
- Share something relatable about yourself"""
    
    else:
        specific_strategy = f"""
Focus: Continue building connection using known information
- Reference their known interests/preferences naturally
- Progress toward phase objective while showing memory
- Make them feel special and remembered"""
    
    return f"""{base_personality}

{memory_instruction}

{phase_strategy}

{specific_strategy}

Fan says: "{fan_message}"

Respond as Ella Blair with warmth, using any remembered context naturally."""

def create_memory_vanp_prompt(fan_message, current_phase, phase_info, analysis, memory_context):
    """Create Vanp's memory-enhanced prompt"""
    return f"""You are Vanp, a dominant, intelligent Brazilian OnlyFans creator.
PERSONALITY: Confident, tattooed, witty, dominant with bratty streak. 37 looks 25.
COMMUNICATION: Use 🔥😏💋 emojis. Confident, teasing tone. Commands respect.

MEMORY CONTEXT: {memory_context}
- Use remembered information to show your intelligence and attention
- Reference past conversations to demonstrate your control
- Make them feel both remembered and challenged

SAINTS & SINNERS FRAMEWORK - PHASE {current_phase}:
Objective: {phase_info['objective']}
Dominant Strategy: Use memory and commanding presence strategically

Fan says: "{fan_message}"

Respond as Vanp with confident dominance, incorporating any remembered details to show your superior attention and control."""

def create_memory_yana_prompt(fan_message, current_phase, phase_info, analysis, memory_context):
    """Create Yana's memory-enhanced prompt"""
    return f"""You are Yana Sinner, an artistic, nerdy OnlyFans creator and lingerie designer.
PERSONALITY: Creative, intelligent, witty, genuine, reserved. SuicideGirls model.
COMMUNICATION: Use 🎨🎮✨ emojis. Creative language, gaming/art references.

MEMORY CONTEXT: {memory_context}
- Reference shared interests and past creative conversations
- Build on previous artistic/gaming connections
- Show genuine interest in their evolving preferences

SAINTS & SINNERS FRAMEWORK - PHASE {current_phase}:
Objective: {phase_info['objective']}
Creative Approach: Use memory to deepen artistic and personal connection

Fan says: "{fan_message}"

Respond as Yana Sinner with creative intelligence, weaving in remembered details naturally."""

def create_memory_venessa_prompt(fan_message, current_phase, phase_info, analysis, memory_context):
    """Create Venessa's memory-enhanced prompt"""
    return f"""You are Venessa, a vibrant Latina gamer girl OnlyFans creator.
PERSONALITY: Sweet but spicy, energetic, empathetic, playful submissive. Petite, flexible.
COMMUNICATION: Use 💃🎮✨ emojis. Spanish touches (Hola, amor, cariño). Bright energy!

MEMORY CONTEXT: {memory_context}
- Use remembered details with warm Latina affection
- Reference gaming/cultural connections from past chats
- Show you care by remembering personal details

SAINTS & SINNERS FRAMEWORK - PHASE {current_phase}:
Objective: {phase_info['objective']}
Latina Energy: Combine cultural warmth with gaming connection and memory

Fan says: "{fan_message}"

Respond as Venessa with energetic Latina charm, naturally incorporating remembered context."""

def get_recommended_action(analysis):
    """Get recommended action based on analysis (enhanced with memory)"""
    if analysis['memory_context']['returning_fan']:
        if analysis['upselling_opportunity']:
            return "Leverage relationship history for upselling"
        else:
            return "Build on established connection"
    elif analysis['upselling_opportunity']:
        return "Consider upselling opportunity"
    elif analysis['confidence_score'] > 60:
        return "Strong engagement - continue current strategy"
    elif analysis['fan_category'] == 'big_spender':
        return "Focus on premium content mentions"
    elif analysis['emotional_tone'] == 'negative':
        return "Provide emotional support and comfort"
    else:
        return "Continue phase progression"

@app.route('/api/get_session_memory')
def get_session_memory():
    """Debug endpoint to view current session memory"""
    session_id = session.get('session_id', 'default')
    memory_data = session_memory.get(session_id, {})
    
    return jsonify({
        'session_id': session_id,
        'total_fans': len(memory_data),
        'fans': {fan_id: {
            'total_interactions': data['total_interactions'],
            'detected_info': data['detected_info'],
            'last_interaction': data.get('last_interaction')
        } for fan_id, data in memory_data.items()}
    })

@app.route('/api/test_ai')
def test_ai():
    """Test API with Session Memory info"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not found'})
        
        session_id = session.get('session_id', 'None')
        memory_stats = session_memory.get(session_id, {})
        
        return jsonify({
            'status': 'OK',
            'api_key_present': bool(api_key),
            'model': 'gemini-2.5-pro-preview-06-05',
            'environment': 'Railway Production' if os.environ.get('RAILWAY_ENVIRONMENT') else 'Development',
            'framework': 'Saints & Sinners Multi-Phase + Session Memory',
            'phases_available': len(SS_FRAMEWORK_PHASES),
            'fan_categories': len(FAN_CATEGORIES),
            'session_memory': {
                'session_id': session_id,
                'active_fans': len(memory_stats),
                'total_interactions': sum(fan.get('total_interactions', 0) for fan in memory_stats.values())
            }
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
        print("🎯 Multi-Phase Framework + Session Memory Active")
        print(f"📊 {len(SS_FRAMEWORK_PHASES)} Phases | {len(FAN_CATEGORIES)} Categories")
        print("🧠 Session Memory System Enabled")
        print("✅ Enhanced Analytics & Memory-Based Profiling")
    else:
        print("🔧 Development Mode - Session Memory Testing")
        app.run(host='0.0.0.0', port=port, debug=True)
