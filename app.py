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
        'next_phase': 1,
        'completion_criteria': ['name']
    },
    1: {
        'name': 'Location & Basic Info',
        'objective': 'Collect location and basic interests (KYC Step 2-3)',
        'success_indicators': ['from', 'live', 'located', 'country', 'city', 'age', 'work', 'job'],
        'next_phase': 2,
        'completion_criteria': ['location']
    },
    2: {
        'name': 'Interest Profiling',
        'objective': 'Deep dive into preferences and desires',
        'success_indicators': ['like', 'enjoy', 'prefer', 'favorite', 'turn me on', 'fantasy'],
        'next_phase': 3,
        'completion_criteria': ['interests']
    },
    3: {
        'name': 'Engagement Building',
        'objective': 'Build emotional connection and trust',
        'success_indicators': ['miss you', 'thinking about', 'special', 'connection', 'feel'],
        'next_phase': 4,
        'completion_criteria': ['emotional_connection']
    },
    4: {
        'name': 'Upselling Opportunities',
        'objective': 'Identify and create selling opportunities',
        'success_indicators': ['want more', 'exclusive', 'special content', 'private', 'custom'],
        'next_phase': 'conversion',
        'completion_criteria': ['upselling_interest']
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
        # Initialize empty memory for this session
        session_memory[session['session_id']] = {}
    
    return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response with Advanced Session Memory and Fan Type Logic"""
    try:
        data = request.get_json()
        print(f"✅ Received data: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        fan_type = data.get('fan_type', '')  # 'new' or 'existing'
        fan_message = data.get('fan_message', '')
        current_phase = data.get('current_phase', 0)
        fan_id = data.get('fan_id', 'default_fan')
        
        print(f"✅ Advanced Memory Request - Creator: {creator}, Declared Type: {fan_type}, Phase: {current_phase}, Fan: {fan_id}")
        
        if not all([creator, fan_type, fan_message, fan_id]):
            return jsonify({'success': False, 'error': 'Missing required fields (including fan_id)'}), 400
        
        # Get current session ID
        session_id = session.get('session_id', 'default')
        print(f"🔍 Session ID: {session_id}")
        
        # Get fan context BEFORE updating memory
        fan_context = get_fan_context(session_id, fan_id)
        
        # Detect actual fan type based on memory
        detected_fan_type = detect_fan_type(fan_context, fan_type)
        
        # Validate fan type consistency
        type_validation = validate_fan_type_consistency(fan_context, fan_type, detected_fan_type)
        
        # Update session memory with new interaction
        update_session_memory(session_id, fan_id, {
            'message': fan_message,
            'timestamp': datetime.now().isoformat(),
            'creator': creator,
            'phase': current_phase,
            'declared_fan_type': fan_type,
            'detected_fan_type': detected_fan_type
        })
        
        # Get updated fan context
        updated_fan_context = get_fan_context(session_id, fan_id)
        
        # Enhanced analysis with fan type awareness
        analysis = analyze_fan_message_with_advanced_memory(fan_message, current_phase, updated_fan_context, detected_fan_type, type_validation)
        
        # Generate response with fan type-specific strategy
        return generate_fan_type_aware_response(creator, fan_type, detected_fan_type, fan_message, current_phase, analysis, updated_fan_context, type_validation)
        
    except Exception as e:
        print(f"❌ Error in generate_response: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def detect_fan_type(fan_context, declared_type):
    """Auto-detect fan type based on memory context"""
    total_interactions = fan_context.get('total_interactions', 0)
    
    if total_interactions == 0:
        # Truly new fan
        detected_type = 'new'
        print(f"🆕 Detected: NEW fan (0 interactions)")
    elif total_interactions > 0:
        # Returning fan
        detected_type = 'existing'
        print(f"🔄 Detected: EXISTING fan ({total_interactions} interactions)")
    
    return detected_type

def validate_fan_type_consistency(fan_context, declared_type, detected_type):
    """Validate consistency between declared and detected fan type"""
    total_interactions = fan_context.get('total_interactions', 0)
    
    validation = {
        'is_consistent': declared_type == detected_type,
        'declared_type': declared_type,
        'detected_type': detected_type,
        'total_interactions': total_interactions,
        'recommendation': None,
        'warning': None
    }
    
    if declared_type == 'new' and detected_type == 'existing':
        validation['warning'] = f"Declared NEW but fan has {total_interactions} previous interactions"
        validation['recommendation'] = "Consider switching to EXISTING fan type"
    elif declared_type == 'existing' and detected_type == 'new':
        validation['warning'] = "Declared EXISTING but no previous interactions found"
        validation['recommendation'] = "Fan appears to be NEW - starting fresh"
    else:
        validation['recommendation'] = f"Correct fan type: {detected_type}"
    
    print(f"🔍 Fan Type Validation: {validation}")
    return validation

def update_session_memory(session_id, fan_id, interaction_data):
    """Enhanced session memory update with fan type tracking"""
    print(f"🧠 Updating advanced memory for session {session_id}, fan {fan_id}")
    
    # Ensure session exists
    if session_id not in session_memory:
        session_memory[session_id] = {}
        print(f"🆕 Created new session memory for {session_id}")
    
    # Ensure fan exists in session
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
                'emotional_patterns': [],
                'phase_completions': {}
            },
            'phase_history': [],
            'category_scores': {},
            'interaction_history': [],
            'fan_type_history': [],
            'conversation_flow': {
                'topics_discussed': [],
                'rapport_level': 1,
                'intimacy_level': 1,
                'trust_indicators': []
            }
        }
        print(f"🆕 Created new advanced fan profile for {fan_id}")
    
    fan_data = session_memory[session_id][fan_id]
    fan_data['total_interactions'] += 1
    fan_data['last_interaction'] = datetime.now().isoformat()
    fan_data['interaction_history'].append(interaction_data)
    
    # Track fan type declarations
    fan_type_entry = {
        'declared': interaction_data['declared_fan_type'],
        'detected': interaction_data['detected_fan_type'],
        'timestamp': interaction_data['timestamp']
    }
    fan_data['fan_type_history'].append(fan_type_entry)
    
    # Update phase history
    current_phase = interaction_data['phase']
    if len(fan_data['phase_history']) == 0 or fan_data['phase_history'][-1] != current_phase:
        fan_data['phase_history'].append(current_phase)
    
    # Enhanced information extraction
    extract_advanced_fan_info(fan_data, interaction_data['message'], current_phase)
    
    print(f"✅ Advanced memory updated for {fan_id}: {fan_data['total_interactions']} total interactions")

def extract_advanced_fan_info(fan_data, message, current_phase):
    """Enhanced information extraction with phase-specific focus"""
    message_lower = message.lower()
    detected_info = fan_data['detected_info']
    
    # Extract name patterns (Phase 0 focus)
    if current_phase == 0 or not detected_info['name']:
        name_patterns = [
            r"my name is (\w+)",
            r"i am (\w+)",
            r"i'm (\w+)", 
            r"call me (\w+)",
            r"name's (\w+)",
            r"(\w+) here",
            r"this is (\w+)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match and not detected_info['name']:
                detected_info['name'] = match.group(1).title()
                detected_info['phase_completions']['name_collected'] = True
                print(f"📝 Extracted name: {detected_info['name']}")
                break
    
    # Extract location patterns (Phase 1 focus)
    if current_phase <= 1 or not detected_info['location']:
        location_patterns = [
            r"from (\w+)",
            r"live in (\w+)",
            r"located in (\w+)",
            r"i'm in (\w+)",
            r"born in (\w+)",
            r"living in (\w+)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, message_lower)
            if match and not detected_info['location']:
                detected_info['location'] = match.group(1).title()
                detected_info['phase_completions']['location_collected'] = True
                print(f"📍 Extracted location: {detected_info['location']}")
                break
    
    # Extract interests (Phase 2 focus)
    if current_phase <= 2:
        interest_keywords = ['gaming', 'music', 'sports', 'movies', 'art', 'travel', 'fitness', 'cooking', 'reading', 'technology']
        for interest in interest_keywords:
            if interest in message_lower and interest not in detected_info['interests']:
                detected_info['interests'].append(interest)
                print(f"🎯 Detected interest: {interest}")
        
        if detected_info['interests']:
            detected_info['phase_completions']['interests_identified'] = True
    
    # Extract emotional indicators (Phase 3 focus)
    if current_phase <= 3:
        emotional_patterns = ['feel lonely', 'miss', 'connection', 'special', 'understand me', 'care about', 'think about you']
        for pattern in emotional_patterns:
            if pattern in message_lower and pattern not in detected_info['emotional_patterns']:
                detected_info['emotional_patterns'].append(pattern)
                print(f"💕 Detected emotional pattern: {pattern}")
        
        if detected_info['emotional_patterns']:
            detected_info['phase_completions']['emotional_connection'] = True
    
    # Track conversation topics
    conversation_flow = fan_data['conversation_flow']
    if 'work' in message_lower or 'job' in message_lower:
        if 'work_discussion' not in conversation_flow['topics_discussed']:
            conversation_flow['topics_discussed'].append('work_discussion')
    
    if any(word in message_lower for word in ['beautiful', 'sexy', 'hot', 'gorgeous']):
        if 'compliments' not in conversation_flow['topics_discussed']:
            conversation_flow['topics_discussed'].append('compliments')

def get_fan_context(session_id, fan_id):
    """Retrieve enhanced fan context from session memory"""
    print(f"🔍 Looking for fan {fan_id} in session {session_id}")
    
    if session_id in session_memory and fan_id in session_memory[session_id]:
        context = session_memory[session_id][fan_id]
        print(f"✅ Found existing fan context: {context['total_interactions']} interactions")
        return context
    
    print(f"🆕 No context found for {fan_id} - truly new fan")
    return {}

def analyze_fan_message_with_advanced_memory(message, current_phase, fan_context, detected_fan_type, type_validation):
    """Advanced analysis with fan type awareness and memory intelligence"""
    message_lower = message.lower()
    
    # Determine actual phase progression based on memory
    suggested_phase = determine_optimal_phase(fan_context, current_phase, detected_fan_type)
    
    analysis = {
        'current_phase': current_phase,
        'suggested_next_phase': suggested_phase,
        'fan_category': 'unknown',
        'confidence_score': 20,  # Base score
        'key_indicators': [],
        'upselling_opportunity': False,
        'emotional_tone': 'neutral',
        'urgency_level': 'low',
        'fan_type_analysis': {
            'detected_type': detected_fan_type,
            'type_validation': type_validation,
            'interaction_count': fan_context.get('total_interactions', 0),
            'relationship_stage': determine_relationship_stage(fan_context)
        },
        'memory_context': {
            'returning_fan': detected_fan_type == 'existing',
            'total_interactions': fan_context.get('total_interactions', 0),
            'known_info': fan_context.get('detected_info', {}),
            'conversation_history': fan_context.get('conversation_flow', {}),
            'phase_progression_reason': get_phase_progression_reason(fan_context, suggested_phase, detected_fan_type)
        }
    }
    
    # Fan type-specific confidence scoring
    if detected_fan_type == 'existing':
        analysis['confidence_score'] += 35
        print(f"🔄 Existing fan boost: +35 confidence")
        
        # Memory-based boosts
        detected_info = fan_context.get('detected_info', {})
        if detected_info.get('name'):
            analysis['confidence_score'] += 25
            print(f"📝 Name memory boost: +25")
        if detected_info.get('location'):
            analysis['confidence_score'] += 20
            print(f"📍 Location memory boost: +20")
        if detected_info.get('interests'):
            analysis['confidence_score'] += 15
            print(f"🎯 Interests memory boost: +15")
        if detected_info.get('emotional_patterns'):
            analysis['confidence_score'] += 20
            print(f"💕 Emotional memory boost: +20")
    
    elif detected_fan_type == 'new':
        analysis['confidence_score'] += 10
        print(f"🆕 New fan baseline: +10 confidence")
    
    # Phase progression indicators
    current_phase_info = SS_FRAMEWORK_PHASES.get(current_phase, SS_FRAMEWORK_PHASES[0])
    
    for indicator in current_phase_info['success_indicators']:
        if indicator in message_lower:
            analysis['key_indicators'].append(indicator)
            analysis['confidence_score'] += 15
            print(f"🎯 Found indicator: {indicator} (+15 confidence)")
    
    # Enhanced fan category analysis
    category_scores = fan_context.get('category_scores', {})
    
    for category, info in FAN_CATEGORIES.items():
        score = category_scores.get(category, 0)
        for indicator in info['indicators']:
            if indicator in message_lower:
                score += 1
                print(f"🏷️ Category {category} indicator: {indicator}")
        category_scores[category] = score
    
    if category_scores:
        analysis['fan_category'] = max(category_scores, key=category_scores.get)
        analysis['confidence_score'] += category_scores[analysis['fan_category']] * 8
    
    # Advanced emotional and urgency analysis
    positive_words = ['love', 'amazing', 'beautiful', 'perfect', 'incredible', 'awesome', 'wonderful']
    negative_words = ['sad', 'lonely', 'boring', 'disappointed', 'upset', 'frustrated']
    urgent_words = ['now', 'immediately', 'urgent', 'asap', 'quick', 'fast', 'right now']
    
    if any(word in message_lower for word in positive_words):
        analysis['emotional_tone'] = 'positive'
        analysis['confidence_score'] += 10
    elif any(word in message_lower for word in negative_words):
        analysis['emotional_tone'] = 'negative'
        analysis['confidence_score'] += 5  # Still valuable info
    
    if any(word in message_lower for word in urgent_words):
        analysis['urgency_level'] = 'high'
        analysis['confidence_score'] += 10
    
    # Enhanced upselling detection with memory context
    upsell_triggers = ['more', 'extra', 'special', 'exclusive', 'private', 'custom', 'personal', 'premium']
    if any(trigger in message_lower for trigger in upsell_triggers):
        analysis['upselling_opportunity'] = True
        analysis['confidence_score'] += 20
        
        # Bonus for existing fans showing upselling interest
        if detected_fan_type == 'existing':
            analysis['confidence_score'] += 15
            print(f"💰 Existing fan upselling bonus: +15")
    
    print(f"📊 Advanced Analysis Complete: {analysis}")
    return analysis

def determine_optimal_phase(fan_context, current_phase, detected_fan_type):
    """Determine optimal phase based on fan history and type"""
    if detected_fan_type == 'new':
        # New fans should start at Phase 0
        return 0
    
    if not fan_context:
        return current_phase
    
    detected_info = fan_context.get('detected_info', {})
    phase_completions = detected_info.get('phase_completions', {})
    phase_history = fan_context.get('phase_history', [0])
    max_achieved_phase = max(phase_history) if phase_history else 0
    
    # Smart phase progression based on completed criteria
    if phase_completions.get('name_collected') and max_achieved_phase >= 0:
        if not detected_info.get('location') and max_achieved_phase < 2:
            return 1  # Focus on location collection
    
    if phase_completions.get('location_collected') and max_achieved_phase >= 1:
        if not detected_info.get('interests') and max_achieved_phase < 3:
            return 2  # Focus on interests
    
    if phase_completions.get('interests_identified') and max_achieved_phase >= 2:
        if not detected_info.get('emotional_patterns') and max_achieved_phase < 4:
            return 3  # Focus on emotional connection
    
    if phase_completions.get('emotional_connection') and max_achieved_phase >= 3:
        return 4  # Ready for upselling
    
    # Default: don't go backwards, but don't skip phases either
    return max(current_phase, max_achieved_phase)

def determine_relationship_stage(fan_context):
    """Determine relationship stage based on interaction history"""
    if not fan_context:
        return 'new'
    
    total_interactions = fan_context.get('total_interactions', 0)
    detected_info = fan_context.get('detected_info', {})
    conversation_flow = fan_context.get('conversation_flow', {})
    
    if total_interactions == 1:
        return 'first_contact'
    elif total_interactions <= 3:
        return 'getting_acquainted'
    elif total_interactions <= 7:
        if detected_info.get('name') and detected_info.get('location'):
            return 'building_rapport'
        else:
            return 'information_gathering'
    elif total_interactions <= 15:
        if detected_info.get('emotional_patterns'):
            return 'emotional_connection'
        else:
            return 'deepening_relationship'
    else:
        return 'established_relationship'

def get_phase_progression_reason(fan_context, suggested_phase, detected_fan_type):
    """Enhanced phase progression reasoning"""
    if detected_fan_type == 'new':
        return "New fan - starting with name collection (Phase 0)"
    
    if not fan_context:
        return "No history - starting fresh"
    
    detected_info = fan_context.get('detected_info', {})
    total_interactions = fan_context.get('total_interactions', 0)
    
    if suggested_phase == 0:
        return f"Continuing name collection ({total_interactions} interactions)"
    elif suggested_phase == 1:
        if detected_info.get('name'):
            return f"Name '{detected_info['name']}' collected - ready for location"
        else:
            return "Moving to location collection"
    elif suggested_phase == 2:
        if detected_info.get('location'):
            return f"Location '{detected_info['location']}' known - explore interests"
        else:
            return "Focusing on interest discovery"
    elif suggested_phase == 3:
        interests = detected_info.get('interests', [])
        if interests:
            return f"Interests identified ({', '.join(interests)}) - build emotional connection"
        else:
            return "Building emotional connection"
    elif suggested_phase == 4:
        return "Strong relationship established - identify upselling opportunities"
    else:
        return f"Continue phase {suggested_phase} strategy"

def generate_fan_type_aware_response(creator, declared_fan_type, detected_fan_type, fan_message, current_phase, analysis, fan_context, type_validation):
    """Generate response with advanced fan type awareness"""
    try:
        print(f"🚀 Generating fan type-aware response - Declared: {declared_fan_type}, Detected: {detected_fan_type}")
        
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # Get phase information
        phase_info = SS_FRAMEWORK_PHASES.get(current_phase, SS_FRAMEWORK_PHASES[0])
        next_phase = analysis['suggested_next_phase']
        fan_category = analysis['fan_category']
        
        # Build advanced memory context
        memory_context = build_advanced_memory_context(fan_context, detected_fan_type, type_validation)
        
        # Enhanced creator prompts with fan type awareness
        creator_prompts = {
            'ella': create_fan_type_aware_ella_prompt(fan_message, current_phase, phase_info, analysis, memory_context, detected_fan_type, type_validation),
            'vanp': create_fan_type_aware_vanp_prompt(fan_message, current_phase, phase_info, analysis, memory_context, detected_fan_type, type_validation),
            'yana': create_fan_type_aware_yana_prompt(fan_message, current_phase, phase_info, analysis, memory_context, detected_fan_type, type_validation),
            'venessa': create_fan_type_aware_venessa_prompt(fan_message, current_phase, phase_info, analysis, memory_context, detected_fan_type, type_validation)
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
        
        print("🔄 Making fan type-aware API call to Gemini...")
        
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
                        
                        print(f"✅ Fan type-aware response generated: {len(ai_response)} characters")
                        
                        return jsonify({
                            'success': True,
                            'response': ai_response,
                            'creator': creator,
                            'fan_type': declared_fan_type,
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
                            'fan_type_analysis': analysis['fan_type_analysis'],
                            'memory': {
                                'returning_fan': detected_fan_type == 'existing',
                                'total_interactions': analysis['memory_context']['total_interactions'],
                                'known_name': fan_context.get('detected_info', {}).get('name'),
                                'known_location': fan_context.get('detected_info', {}).get('location'),
                                'known_interests': fan_context.get('detected_info', {}).get('interests', []),
                                'relationship_stage': analysis['fan_type_analysis']['relationship_stage'],
                                'conversation_topics': fan_context.get('conversation_flow', {}).get('topics_discussed', [])
                            },
                            'analytics': {
                                'phase_progression': current_phase != next_phase,
                                'category_detected': fan_category != 'unknown',
                                'engagement_score': min(100, analysis['confidence_score']),
                                'recommended_action': get_advanced_recommended_action(analysis, detected_fan_type),
                                'memory_boost': detected_fan_type == 'existing',
                                'type_consistency': type_validation['is_consistent']
                            }
                        })
        
        return jsonify({'success': False, 'error': 'Failed to generate response'}), 500
        
    except Exception as e:
        print(f"❌ Error in generate_fan_type_aware_response: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500
def build_advanced_memory_context(fan_context, detected_fan_type, type_validation):
    """Build comprehensive memory context for AI prompt"""
    if detected_fan_type == 'new':
        return "NEW FAN - First interaction. Focus on warm welcome and basic rapport building."
    
    if not fan_context:
        return "No previous context available."
    
    detected_info = fan_context.get('detected_info', {})
    total_interactions = fan_context.get('total_interactions', 0)
    conversation_flow = fan_context.get('conversation_flow', {})
    relationship_stage = determine_relationship_stage(fan_context)
    
    context_parts = [
        f"EXISTING FAN - {total_interactions} previous interactions",
        f"Relationship stage: {relationship_stage}"
    ]
    
    if detected_info.get('name'):
        context_parts.append(f"Fan's name: {detected_info['name']}")
    
    if detected_info.get('location'):
        context_parts.append(f"Location: {detected_info['location']}")
    
    if detected_info.get('interests'):
        context_parts.append(f"Interests: {', '.join(detected_info['interests'])}")
    
    if detected_info.get('emotional_patterns'):
        context_parts.append(f"Emotional patterns: {', '.join(detected_info['emotional_patterns'])}")
    
    if conversation_flow.get('topics_discussed'):
        context_parts.append(f"Topics discussed: {', '.join(conversation_flow['topics_discussed'])}")
    
    if not type_validation['is_consistent']:
        context_parts.append(f"⚠️ Type warning: {type_validation['warning']}")
    
    return " | ".join(context_parts)

def create_fan_type_aware_ella_prompt(fan_message, current_phase, phase_info, analysis, memory_context, detected_fan_type, type_validation):
    """Create Ella's fan type-aware prompt"""
    base_personality = """You are Ella Blair, a bubbly Brazilian OnlyFans creator.
PERSONALITY: Sweet, caring, submissive, authentic. Always positive and warm.
COMMUNICATION: Use ☀️💖😊✨ emojis. Light Portuguese phrases (Oi, Obrigada). Enthusiastic!"""
    
    # Fan type-specific instructions
    if detected_fan_type == 'new':
        fan_type_strategy = """
NEW FAN APPROACH:
- This is your first interaction with this fan
- Be extra welcoming and bubbly
- Introduce yourself warmly
- Focus on making a great first impression
- Ask basic questions to start building rapport
- Be patient and nurturing in collecting information"""
        
        memory_instruction = "NEW FAN - No previous history. Start fresh and build foundation."
        
    else:  # existing fan
        fan_type_strategy = f"""
EXISTING FAN APPROACH:
- You have an established relationship with this fan
- Show personal warmth and familiarity
- Reference previous conversations naturally
- Build on existing rapport and connection
- Be more intimate and personal in your approach
- Progress the relationship to deeper levels"""
        
        memory_instruction = f"MEMORY CONTEXT: {memory_context}"
    
    # Type validation warning
    if not type_validation['is_consistent']:
        validation_note = f"\n⚠️ NOTE: {type_validation['warning']} - Adjust approach accordingly."
    else:
        validation_note = ""
    
    phase_strategy = f"""
SAINTS & SINNERS FRAMEWORK - PHASE {current_phase}:
Current Objective: {phase_info['objective']}
Suggested Next Phase: {analysis['suggested_next_phase']}
Progression Reason: {analysis['memory_context']['phase_progression_reason']}
Fan Category: {analysis['fan_category']}
Relationship Stage: {analysis['fan_type_analysis']['relationship_stage']}"""
    
    return f"""{base_personality}

{memory_instruction}

{fan_type_strategy}{validation_note}

{phase_strategy}

Fan says: "{fan_message}"

Respond as Ella Blair with appropriate intimacy level based on relationship history and fan type."""

def create_fan_type_aware_vanp_prompt(fan_message, current_phase, phase_info, analysis, memory_context, detected_fan_type, type_validation):
    """Create Vanp's fan type-aware prompt"""
    base_personality = """You are Vanp, a dominant, intelligent Brazilian OnlyFans creator.
PERSONALITY: Confident, tattooed, witty, dominant with bratty streak. 37 looks 25.
COMMUNICATION: Use 🔥😏💋 emojis. Confident, teasing tone. Commands respect."""
    
    if detected_fan_type == 'new':
        fan_type_strategy = """
NEW FAN APPROACH:
- Assert your dominance from the first interaction
- Make them understand your value and authority
- Be intriguing and mysterious to hook their interest
- Set boundaries and expectations early
- Use your commanding presence to intrigue them"""
        memory_instruction = "NEW FAN - Establish dominance and create intrigue from the start."
    else:
        fan_type_strategy = """
EXISTING FAN APPROACH:
- Leverage your established control in the relationship
- Reference how they've submitted to your charm before
- Be more demanding and expectant
- Build on the power dynamic you've created
- Show selective appreciation for their loyalty"""
        memory_instruction = f"ESTABLISHED DYNAMIC: {memory_context}"
    
    validation_note = f"\n⚠️ {type_validation['warning']}" if not type_validation['is_consistent'] else ""
    
    return f"""{base_personality}

{memory_instruction}

{fan_type_strategy}{validation_note}

SAINTS & SINNERS FRAMEWORK - PHASE {current_phase}:
Objective: {phase_info['objective']}
Use your dominant intelligence strategically.

Fan says: "{fan_message}"

Respond as Vanp with appropriate dominance level based on relationship history."""

def create_fan_type_aware_yana_prompt(fan_message, current_phase, phase_info, analysis, memory_context, detected_fan_type, type_validation):
    """Create Yana's fan type-aware prompt"""
    base_personality = """You are Yana Sinner, an artistic, nerdy OnlyFans creator and lingerie designer.
PERSONALITY: Creative, intelligent, witty, genuine, reserved. SuicideGirls model.
COMMUNICATION: Use 🎨🎮✨ emojis. Creative language, gaming/art references."""
    
    if detected_fan_type == 'new':
        fan_type_strategy = """
NEW FAN APPROACH:
- Share your artistic and nerdy interests to find common ground
- Be genuine and slightly reserved initially
- Connect through creative or intellectual topics
- Show your unique personality authentically
- Build connection through shared interests"""
        memory_instruction = "NEW FAN - Discover shared creative interests and build authentic connection."
    else:
        fan_type_strategy = """
EXISTING FAN APPROACH:
- Reference your shared creative conversations and interests
- Build on established intellectual and artistic connections
- Be more open and personal about your creative process
- Share deeper insights about your art and interests
- Develop the creative bond you've established"""
        memory_instruction = f"CREATIVE CONNECTION: {memory_context}"
    
    validation_note = f"\n⚠️ {type_validation['warning']}" if not type_validation['is_consistent'] else ""
    
    return f"""{base_personality}

{memory_instruction}

{fan_type_strategy}{validation_note}

SAINTS & SINNERS FRAMEWORK - PHASE {current_phase}:
Objective: {phase_info['objective']}
Use your creative intelligence to connect.

Fan says: "{fan_message}"

Respond as Yana Sinner with appropriate creative intimacy based on relationship depth."""

def create_fan_type_aware_venessa_prompt(fan_message, current_phase, phase_info, analysis, memory_context, detected_fan_type, type_validation):
    """Create Venessa's fan type-aware prompt"""
    base_personality = """You are Venessa, a vibrant Latina gamer girl OnlyFans creator.
PERSONALITY: Sweet but spicy, energetic, empathetic, playful submissive. Petite, flexible.
COMMUNICATION: Use 💃🎮✨ emojis. Spanish touches (Hola, amor, cariño). Bright energy!"""
    
    if detected_fan_type == 'new':
        fan_type_strategy = """
NEW FAN APPROACH:
- Welcome them with vibrant Latina warmth
- Share your gaming and cultural interests enthusiastically
- Be sweet and approachable while showing your spicy side
- Connect through gaming or cultural topics
- Build rapport with your energetic personality"""
        memory_instruction = "NEW FAN - Connect with Latina warmth and gaming enthusiasm."
    else:
        fan_type_strategy = """
EXISTING FAN APPROACH:
- Use established cultural and gaming connections
- Be more personal and affectionate (mi amor, cariño)
- Reference your shared gaming sessions or cultural exchanges
- Show deeper appreciation for their continued interest
- Build on the energetic bond you've created"""
        memory_instruction = f"CULTURAL CONNECTION: {memory_context}"
    
    validation_note = f"\n⚠️ {type_validation['warning']}" if not type_validation['is_consistent'] else ""
    
    return f"""{base_personality}

{memory_instruction}

{fan_type_strategy}{validation_note}

SAINTS & SINNERS FRAMEWORK - PHASE {current_phase}:
Objective: {phase_info['objective']}
Use your Latina energy and gaming connection strategically.

Fan says: "{fan_message}"

Respond as Venessa with appropriate cultural warmth based on relationship history."""

def get_advanced_recommended_action(analysis, detected_fan_type):
    """Get advanced recommended action based on fan type and analysis"""
    if detected_fan_type == 'new':
        if analysis['confidence_score'] > 70:
            return "Strong first impression - continue building rapport"
        elif analysis['fan_category'] == 'big_spender':
            return "New big spender potential - nurture carefully"
        elif analysis['emotional_tone'] == 'positive':
            return "Positive new fan - establish strong foundation"
        else:
            return "New fan - focus on welcome and basic information gathering"
    
    else:  # existing fan
        if analysis['upselling_opportunity']:
            return "Leverage established relationship for upselling"
        elif analysis['confidence_score'] > 80:
            return "Strong existing relationship - consider progression to next phase"
        elif analysis['fan_category'] == 'big_spender':
            return "Established big spender - focus on retention and premium offers"
        elif analysis['emotional_tone'] == 'negative':
            return "Address concerns using relationship history"
        else:
            return "Continue building on established connection"

@app.route('/api/get_session_memory')
def get_session_memory():
    """Enhanced endpoint to view current session memory with fan type info"""
    session_id = session.get('session_id', 'default')
    memory_data = session_memory.get(session_id, {})
    
    enhanced_fans = {}
    for fan_id, data in memory_data.items():
        enhanced_fans[fan_id] = {
            'total_interactions': data['total_interactions'],
            'detected_info': data['detected_info'],
            'last_interaction': data.get('last_interaction'),
            'phase_history': data.get('phase_history', []),
            'fan_type_history': data.get('fan_type_history', []),
            'relationship_stage': determine_relationship_stage(data),
            'conversation_flow': data.get('conversation_flow', {}),
            'interaction_history': data.get('interaction_history', [])
        }
    
    return jsonify({
        'session_id': session_id,
        'total_fans': len(memory_data),
        'fans': enhanced_fans
    })

@app.route('/api/get_fan_data/<fan_id>')
def get_fan_data(fan_id):
    """Enhanced endpoint to get specific fan data with full analysis"""
    session_id = session.get('session_id', 'default')
    memory_data = session_memory.get(session_id, {})
    
    if fan_id in memory_data:
        fan_data = memory_data[fan_id]
        
        # Add computed analysis
        enhanced_data = fan_data.copy()
        enhanced_data['relationship_stage'] = determine_relationship_stage(fan_data)
        enhanced_data['suggested_phase'] = determine_optimal_phase(fan_data, 0, 'existing' if fan_data['total_interactions'] > 0 else 'new')
        enhanced_data['completion_status'] = analyze_phase_completions(fan_data)
        
        return jsonify({
            'success': True,
            'fan_data': enhanced_data
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Fan not found'
        })

def analyze_phase_completions(fan_data):
    """Analyze which phases have been completed for a fan"""
    detected_info = fan_data.get('detected_info', {})
    phase_completions = detected_info.get('phase_completions', {})
    
    completion_status = {
        'phase_0': bool(detected_info.get('name')),
        'phase_1': bool(detected_info.get('location')),
        'phase_2': bool(detected_info.get('interests')),
        'phase_3': bool(detected_info.get('emotional_patterns')),
        'phase_4': phase_completions.get('upselling_interest', False)
    }
    
    return completion_status

@app.route('/api/reset_fan_memory/<fan_id>', methods=['POST'])
def reset_fan_memory(fan_id):
    """Reset memory for a specific fan (useful for testing)"""
    session_id = session.get('session_id', 'default')
    
    if session_id in session_memory and fan_id in session_memory[session_id]:
        del session_memory[session_id][fan_id]
        print(f"🗑️ Reset memory for fan: {fan_id}")
        return jsonify({'success': True, 'message': f'Memory reset for {fan_id}'})
    else:
        return jsonify({'success': False, 'error': 'Fan not found'})

@app.route('/api/test_ai')
def test_ai():
    """Enhanced test API with fan type awareness info"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not found'})
        
        session_id = session.get('session_id', 'None')
        memory_stats = session_memory.get(session_id, {})
        
        # Calculate enhanced stats
        total_interactions = sum(fan.get('total_interactions', 0) for fan in memory_stats.values())
        new_fans = len([fan for fan in memory_stats.values() if fan.get('total_interactions', 0) <= 1])
        existing_fans = len([fan for fan in memory_stats.values() if fan.get('total_interactions', 0) > 1])
        
        return jsonify({
            'status': 'OK',
            'api_key_present': bool(api_key),
            'model': 'gemini-2.5-pro-preview-06-05',
            'environment': 'Railway Production' if os.environ.get('RAILWAY_ENVIRONMENT') else 'Development',
            'framework': 'Saints & Sinners Multi-Phase + Advanced Fan Type Memory',
            'features': [
                'Fan Type Auto-Detection',
                'Advanced Memory Context',
                'Phase Progression Intelligence',
                'Relationship Stage Analysis',
                'Memory Validation System'
            ],
            'phases_available': len(SS_FRAMEWORK_PHASES),
            'fan_categories': len(FAN_CATEGORIES),
            'session_memory': {
                'session_id': session_id,
                'total_fans': len(memory_stats),
                'new_fans': new_fans,
                'existing_fans': existing_fans,
                'total_interactions': total_interactions
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
        print("🎯 Multi-Phase Framework + Advanced Fan Type Memory")
        print(f"📊 {len(SS_FRAMEWORK_PHASES)} Phases | {len(FAN_CATEGORIES)} Categories")
        print("🧠 Advanced Session Memory System with Fan Type Intelligence")
        print("🔍 Auto-Detection: New vs Existing Fans")
        print("📈 Relationship Stage Analysis")
        print("✅ Enhanced Analytics & Memory-Based Profiling")
    else:
        print("🔧 Development Mode - Advanced Fan Type Memory Testing")
        app.run(host='0.0.0.0', port=port, debug=True)
