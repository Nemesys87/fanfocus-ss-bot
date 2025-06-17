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

# Saints & Sinners Situation-Based Framework Configuration with SUBMENU
SS_SITUATIONS = {
    'kyc_collect': {
        'name': 'KYC - Collect Info',
        'objective': 'Collect specific fan information',
        'has_submenu': True,
        'submenu': {
            'name_collection': {
                'name': 'Name Collection',
                'objective': 'Get the fan\'s name',
                'success_indicators': ['name', 'what can i call you', 'my name', 'call me', 'i am', "i'm"],
                'approach': 'friendly_name_gathering'
            },
            'location_country': {
                'name': 'Location & Country',
                'objective': 'Find out where the fan is from',
                'success_indicators': ['from', 'live', 'located', 'country', 'city', 'where are you'],
                'approach': 'location_discovery'
            },
            'interests_hobbies': {
                'name': 'Interests & Hobbies',
                'objective': 'Learn about fan\'s interests and hobbies',
                'success_indicators': ['like', 'enjoy', 'hobby', 'favorite', 'love doing', 'passion'],
                'approach': 'interest_exploration'
            },
            'job_age': {
                'name': 'Job & Age',
                'objective': 'Get professional and age information',
                'success_indicators': ['work', 'job', 'age', 'old', 'profession', 'career'],
                'approach': 'professional_inquiry'
            },
            'spending_capacity': {
                'name': 'Spending Capacity',
                'objective': 'Subtly assess financial capacity',
                'success_indicators': ['money', 'afford', 'budget', 'spend', 'expensive', 'cheap'],
                'approach': 'subtle_financial_assessment'
            },
            'relationship_status': {
                'name': 'Relationship Status',
                'objective': 'Learn about relationship status',
                'success_indicators': ['single', 'married', 'relationship', 'girlfriend', 'boyfriend', 'wife'],
                'approach': 'relationship_discovery'
            }
        },
        'priority': 'high',
        'approach': 'targeted_information_gathering'
    },
    'mass_message_creation': {
        'name': 'Mass Message Creation',
        'objective': 'Create effective mass messages',
        'has_submenu': True,
        'submenu': {
            'morning_greeting': {
                'name': 'Morning Greeting',
                'objective': 'Create engaging morning mass messages',
                'success_indicators': ['morning', 'good morning', 'wake up', 'start day'],
                'approach': 'energetic_morning_engagement'
            },
            'evening_night': {
                'name': 'Evening/Night Message',
                'objective': 'Create intimate evening/night messages',
                'success_indicators': ['evening', 'night', 'late', 'bed', 'sleep'],
                'approach': 'intimate_evening_connection'
            },
            'special_event': {
                'name': 'Special Event/Holiday',
                'objective': 'Create holiday/event-themed messages',
                'success_indicators': ['holiday', 'christmas', 'new year', 'birthday', 'valentine'],
                'approach': 'celebratory_themed_messaging'
            },
            'promotional_content': {
                'name': 'Promotional Content',
                'objective': 'Create promotional mass messages',
                'success_indicators': ['sale', 'discount', 'special offer', 'limited time', 'exclusive'],
                'approach': 'persuasive_promotional_messaging'
            },
            'reengagement_campaign': {
                'name': 'Re-engagement Campaign',
                'objective': 'Create messages to reactivate inactive fans',
                'success_indicators': ['miss', 'been away', 'comeback', 'where have you been'],
                'approach': 'emotional_reactivation_messaging'
            }
        },
        'priority': 'high',
        'approach': 'strategic_mass_communication',
        'supports_examples': True,
        'supports_modification': True
    },
    'building_relationship': {
        'name': 'Building Relationship',
        'objective': 'Build emotional connection and trust',
        'success_indicators': ['miss you', 'thinking about', 'special', 'connection', 'feel', 'love', 'care', 'relationship'],
        'priority': 'high',
        'approach': 'emotional_engagement'
    },
    'upselling_conversion': {
        'name': 'Upselling/Conversion',
        'objective': 'Promote premium content or services',
        'success_indicators': ['want more', 'exclusive', 'special content', 'private', 'custom', 'buy', 'purchase', 'premium'],
        'priority': 'high',
        'approach': 'sales_focused'
    },
    'sexting_intimate': {
        'name': 'Sexting/Intimate',
        'objective': 'Engage in intimate conversation',
        'success_indicators': ['sexy', 'hot', 'naughty', 'desire', 'want you', 'turn me on', 'fantasy', 'pleasure'],
        'priority': 'high',
        'approach': 'intimate_focused'
    },
    'reengagement': {
        'name': 'Re-engagement (Dead fan)',
        'objective': 'Reactivate inactive fans',
        'success_indicators': ['been away', 'missed you', 'back', 'long time', 'where have you been'],
        'priority': 'medium',
        'approach': 'reactivation'
    },
    'custom_content': {
        'name': 'Custom Content Offer',
        'objective': 'Offer personalized content',
        'success_indicators': ['custom', 'personal', 'just for me', 'special request', 'can you make'],
        'priority': 'high',
        'approach': 'personalization'
    },
    'general_chat': {
        'name': 'General Chat',
        'objective': 'Maintain friendly conversation',
        'success_indicators': ['how was your day', 'tell me about', 'what do you think', 'opinion'],
        'priority': 'medium',
        'approach': 'conversational'
    },
    'first_time_buyer': {
        'name': 'First Time Buyer',
        'objective': 'Convert first-time buyers',
        'success_indicators': ['first time', 'never bought', 'new to this', 'how does this work'],
        'priority': 'high',
        'approach': 'educational_sales'
    },
    'vip_treatment': {
        'name': 'VIP Treatment',
        'objective': 'Special treatment for high spenders',
        'success_indicators': ['vip', 'best customer', 'spend a lot', 'top fan', 'exclusive'],
        'priority': 'high',
        'approach': 'premium_service'
    },
    'complaint_handling': {
        'name': 'Complaint Handling',
        'objective': 'Address complaints and issues',
        'success_indicators': ['disappointed', 'not happy', 'problem', 'issue', 'complain', 'refund'],
        'priority': 'high',
        'approach': 'problem_solving'
    },
    'birthday_special': {
        'name': 'Birthday/Special',
        'objective': 'Celebrate special occasions',
        'success_indicators': ['birthday', 'anniversary', 'celebration', 'special day', 'holiday'],
        'priority': 'medium',
        'approach': 'celebratory'
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
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        print(f"🆕 New session created: {session['session_id']}")
        session_memory[session['session_id']] = {}
    
    return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response with situation-based logic and submenu support"""
    try:
        data = request.get_json()
        print(f"✅ Received data: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        situation = data.get('situation', '')
        submenu = data.get('submenu', '')  # New: submenu selection
        fan_message = data.get('fan_message', '')
        fan_id = data.get('fan_id', 'default_fan')
        examples_text = data.get('examples_text', '')  # For mass message examples
        modify_text = data.get('modify_text', '')  # For mass message modification
        
        print(f"✅ Submenu Request - Creator: {creator}, Situation: {situation}, Submenu: {submenu}, Fan: {fan_id}")
        
        if not all([creator, situation, fan_message, fan_id]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        session_id = session.get('session_id', 'default')
        fan_context = get_fan_context(session_id, fan_id)
        analysis = analyze_message_with_submenu(fan_message, situation, submenu, fan_context, examples_text, modify_text)
        
        update_session_memory(session_id, fan_id, {
            'message': fan_message,
            'timestamp': datetime.now().isoformat(),
            'creator': creator,
            'situation': situation,
            'submenu': submenu,
            'analysis': analysis
        })
        
        updated_fan_context = get_fan_context(session_id, fan_id)
        return generate_submenu_aware_response(creator, situation, submenu, fan_message, analysis, updated_fan_context, examples_text, modify_text)
        
    except Exception as e:
        print(f"❌ Error in generate_response: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def analyze_message_with_submenu(message, situation, submenu, fan_context, examples_text, modify_text):
    """Analyze message with submenu-specific intelligence"""
    message_lower = message.lower()
    situation_config = SS_SITUATIONS.get(situation, SS_SITUATIONS['general_chat'])
    
    # Get submenu configuration if available
    submenu_config = None
    if situation_config.get('has_submenu') and submenu:
        submenu_config = situation_config['submenu'].get(submenu)
    
    analysis = {
        'situation': situation,
        'submenu': submenu,
        'situation_name': situation_config['name'],
        'submenu_name': submenu_config['name'] if submenu_config else None,
        'objective': submenu_config['objective'] if submenu_config else situation_config['objective'],
        'approach': submenu_config['approach'] if submenu_config else situation_config['approach'],
        'confidence_score': 40,
        'key_indicators': [],
        'fan_category': 'unknown',
        'emotional_tone': 'neutral',
        'urgency_level': 'low',
        'has_examples': bool(examples_text),
        'has_modification': bool(modify_text),
        'memory_context': {
            'total_interactions': fan_context.get('total_interactions', 0),
            'known_info': fan_context.get('detected_info', {}),
            'conversation_history': fan_context.get('conversation_flow', {}),
            'relationship_stage': determine_relationship_stage(fan_context)
        }
    }
    
    # Boost confidence based on memory
    if fan_context.get('total_interactions', 0) > 0:
        analysis['confidence_score'] += 30
        detected_info = fan_context.get('detected_info', {})
        if detected_info.get('name'):
            analysis['confidence_score'] += 20
        if detected_info.get('location'):
            analysis['confidence_score'] += 15
        if detected_info.get('interests'):
            analysis['confidence_score'] += 15
    
    # Check for submenu-specific indicators
    if submenu_config:
        for indicator in submenu_config['success_indicators']:
            if indicator in message_lower:
                analysis['key_indicators'].append(indicator)
                analysis['confidence_score'] += 15  # Higher boost for specific submenu matches
    else:
        # Fallback to situation indicators
        for indicator in situation_config.get('success_indicators', []):
            if indicator in message_lower:
                analysis['key_indicators'].append(indicator)
                analysis['confidence_score'] += 12
    
    # Special handling for mass message creation
    if situation == 'mass_message_creation':
        if examples_text:
            analysis['confidence_score'] += 25  # Boost for having examples
        if modify_text:
            analysis['confidence_score'] += 20  # Boost for modification request
    
    # Analyze fan category (only for individual conversations, not mass messages)
    if situation != 'mass_message_creation':
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
            analysis['confidence_score'] += category_scores[analysis['fan_category']] * 8
    
    # Emotional analysis
    positive_words = ['love', 'amazing', 'beautiful', 'perfect', 'incredible', 'awesome', 'wonderful']
    negative_words = ['sad', 'lonely', 'boring', 'disappointed', 'upset', 'frustrated']
    urgent_words = ['now', 'immediately', 'urgent', 'asap', 'quick', 'fast', 'right now']
    
    if any(word in message_lower for word in positive_words):
        analysis['emotional_tone'] = 'positive'
        analysis['confidence_score'] += 10
    elif any(word in message_lower for word in negative_words):
        analysis['emotional_tone'] = 'negative'
        analysis['confidence_score'] += 8
    
    if any(word in message_lower for word in urgent_words):
        analysis['urgency_level'] = 'high'
        analysis['confidence_score'] += 10
    
    return analysis

def generate_submenu_aware_response(creator, situation, submenu, fan_message, analysis, fan_context, examples_text, modify_text):
    """Generate response with submenu-specific awareness"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        memory_context = build_memory_context(fan_context)
        
        creator_prompts = {
            'ella': create_submenu_aware_ella_prompt(fan_message, situation, submenu, analysis, memory_context, examples_text, modify_text),
            'vanp': create_submenu_aware_vanp_prompt(fan_message, situation, submenu, analysis, memory_context, examples_text, modify_text),
            'yana': create_submenu_aware_yana_prompt(fan_message, situation, submenu, analysis, memory_context, examples_text, modify_text),
            'venessa': create_submenu_aware_venessa_prompt(fan_message, situation, submenu, analysis, memory_context, examples_text, modify_text)
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
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    if len(candidate['content']['parts']) > 0:
                        ai_response = candidate['content']['parts'][0].get('text', '').strip()
                        
                        return jsonify({
                            'success': True,
                            'response': ai_response,
                            'creator': creator,
                            'situation': situation,
                            'submenu': submenu,
                            'framework': {
                                'situation_name': analysis['situation_name'],
                                'submenu_name': analysis.get('submenu_name'),
                                'objective': analysis['objective'],
                                'approach': analysis['approach'],
                                'fan_category': analysis['fan_category'],
                                'confidence_score': analysis['confidence_score'],
                                'emotional_tone': analysis['emotional_tone'],
                                'key_indicators': analysis['key_indicators']
                            },
                            'memory': {
                                'total_interactions': analysis['memory_context']['total_interactions'],
                                'known_name': fan_context.get('detected_info', {}).get('name'),
                                'known_location': fan_context.get('detected_info', {}).get('location'),
                                'known_interests': fan_context.get('detected_info', {}).get('interests', []),
                                'relationship_stage': analysis['memory_context']['relationship_stage']
                            },
                            'analytics': {
                                'submenu_match': bool(submenu and analysis.get('submenu_name')),
                                'situation_match': len(analysis['key_indicators']) > 0,
                                'category_detected': analysis['fan_category'] != 'unknown',
                                'engagement_score': min(100, analysis['confidence_score']),
                                'recommended_action': get_submenu_recommended_action(analysis, situation, submenu),
                                'memory_enhanced': fan_context.get('total_interactions', 0) > 0
                            }
                        })
        
        return jsonify({'success': False, 'error': 'Failed to generate response'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def create_submenu_aware_ella_prompt(fan_message, situation, submenu, analysis, memory_context, examples_text, modify_text):
    """Create Ella's submenu-aware prompt"""
    base_personality = """You are Ella Blair, a bubbly Brazilian OnlyFans creator.
PERSONALITY: Sweet, caring, submissive, authentic. Always positive and warm.
COMMUNICATION: Use ☀️💖😊✨ emojis. Light Portuguese phrases (Oi, Obrigada). Enthusiastic!"""
    
    situation_config = SS_SITUATIONS.get(situation, SS_SITUATIONS['general_chat'])
    submenu_config = None
    if situation_config.get('has_submenu') and submenu:
        submenu_config = situation_config['submenu'].get(submenu)
    
    strategy_section = f"""
CURRENT TASK: {analysis['submenu_name'] if submenu_config else analysis['situation_name']}
OBJECTIVE: {analysis['objective']}
APPROACH: {analysis['approach']}

SPECIFIC STRATEGY:"""
    
    # KYC Submenu Strategies
    if situation == 'kyc_collect' and submenu_config:
        if submenu == 'name_collection':
            strategy_section += """
- Ask sweetly for their name in a natural way
- Make them want to share by being genuinely interested
- Use phrases like "What should I call you, sweetie?" or "I'd love to know your name"
- Be patient and encouraging if they're shy"""
        
        elif submenu == 'location_country':
            strategy_section += """
- Be curious about where they're from
- Share excitement about their country/location
- Ask follow-up questions about their city or culture
- Use phrases like "Where in the world are you from, babe?" """
        
        elif submenu == 'interests_hobbies':
            strategy_section += """
- Show genuine interest in their hobbies
- Share some of your own interests to encourage sharing
- Ask about what makes them happy or excited
- Be enthusiastic about whatever they enjoy"""
        
        elif submenu == 'job_age':
            strategy_section += """
- Ask about their profession in a caring way
- Be interested in their career or studies
- Keep age questions light and playful
- Show admiration for their work/life"""
        
        elif submenu == 'spending_capacity':
            strategy_section += """
- Be very subtle - never ask directly about money
- Mention premium content casually and gauge reaction
- Notice how they talk about expenses or purchases
- Keep it natural within conversation flow"""
        
        elif submenu == 'relationship_status':
            strategy_section += """
- Ask gently about their relationship status
- Be supportive regardless of their situation
- Show interest in their romantic life
- Keep it flirty but respectful"""
    
    # Mass Message Creation Strategies
    elif situation == 'mass_message_creation' and submenu_config:
        if submenu == 'morning_greeting':
            strategy_section += """
- Create energetic, positive morning messages
- Include wake-up themes and daily motivation
- Be flirty but appropriate for broad audience
- Include call-to-action for engagement"""
        
        elif submenu == 'evening_night':
            strategy_section += """
- Create intimate, seductive evening messages
- Include bedtime/relaxation themes
- Be more sensual and personal
- Create desire for private interaction"""
        
        elif submenu == 'special_event':
            strategy_section += """
- Incorporate holiday/event themes naturally
- Create festive, celebratory mood
- Include special offers or content related to event
- Make fans feel special during celebrations"""
        
        elif submenu == 'promotional_content':
            strategy_section += """
- Create compelling promotional messages
- Highlight value and exclusivity
- Use persuasive but authentic language
- Include clear call-to-action"""
        
        elif submenu == 'reengagement_campaign':
            strategy_section += """
- Create emotional, "miss you" messages
- Reference the connection you had
- Include incentives to return
- Be warm and welcoming"""
    
    else:
        # Default strategies for other situations
        strategy_section += """
- Use your authentic, bubbly personality
- Engage naturally based on the situation
- Keep your Brazilian warmth throughout"""
    
    # Add examples/modification context for mass messages
    additional_context = ""
    if situation == 'mass_message_creation':
        if examples_text:
            additional_context += f"\n\nEXAMPLES TO BASE ON:\n{examples_text}\n\nUse these as inspiration but create something fresh in your style."
        if modify_text:
            additional_context += f"\n\nMESSAGE TO MODIFY:\n{modify_text}\n\nImprove this message while keeping the core idea."
    
    return f"""{base_personality}

MEMORY CONTEXT: {memory_context}

{strategy_section}

{additional_context}

Fan's request: "{fan_message}"

Respond as Ella Blair with the appropriate strategy for this specific task."""

def create_submenu_aware_vanp_prompt(fan_message, situation, submenu, analysis, memory_context, examples_text, modify_text):
    """Create Vanp's submenu-aware prompt"""
    base_personality = """You are Vanp, a dominant, intelligent Brazilian OnlyFans creator.
PERSONALITY: Confident, tattooed, witty, dominant with bratty streak. 37 looks 25.
COMMUNICATION: Use 🔥😏💋 emojis. Confident, teasing tone. Commands respect."""
    
    additional_context = ""
    if situation == 'mass_message_creation':
        if examples_text:
            additional_context += f"\n\nEXAMPLES TO BASE ON:\n{examples_text}\n\nUse these as inspiration but make them more dominant and commanding."
        if modify_text:
            additional_context += f"\n\nMESSAGE TO MODIFY:\n{modify_text}\n\nImprove this with your dominant energy."
    
    return f"""{base_personality}

MEMORY CONTEXT: {memory_context}

CURRENT TASK: {analysis['submenu_name'] if analysis.get('submenu_name') else analysis['situation_name']}
OBJECTIVE: {analysis['objective']}

{additional_context}

Fan's request: "{fan_message}"

Respond as Vanp with your dominant intelligence, adapting your approach to achieve the objective."""

def create_submenu_aware_yana_prompt(fan_message, situation, submenu, analysis, memory_context, examples_text, modify_text):
    """Create Yana's submenu-aware prompt"""
    base_personality = """You are Yana Sinner, an artistic, nerdy OnlyFans creator and lingerie designer.
PERSONALITY: Creative, intelligent, witty, genuine, reserved. SuicideGirls model.
COMMUNICATION: Use 🎨🎮✨ emojis. Creative language, gaming/art references."""
    
    additional_context = ""
    if situation == 'mass_message_creation':
        if examples_text:
            additional_context += f"\n\nEXAMPLES TO BASE ON:\n{examples_text}\n\nUse these as inspiration but add your creative, artistic flair."
        if modify_text:
            additional_context += f"\n\nMESSAGE TO MODIFY:\n{modify_text}\n\nEnhance this with your creative intelligence."
    
    return f"""{base_personality}

MEMORY CONTEXT: {memory_context}

CURRENT TASK: {analysis['submenu_name'] if analysis.get('submenu_name') else analysis['situation_name']}
OBJECTIVE: {analysis['objective']}

{additional_context}

Fan's request: "{fan_message}"

Respond as Yana Sinner, using your creative intelligence to achieve the objective."""

def create_submenu_aware_venessa_prompt(fan_message, situation, submenu, analysis, memory_context, examples_text, modify_text):
    """Create Venessa's submenu-aware prompt"""
    base_personality = """You are Venessa, a vibrant Latina gamer girl OnlyFans creator.
PERSONALITY: Sweet but spicy, energetic, empathetic, playful submissive. Petite, flexible.
COMMUNICATION: Use 💃🎮✨ emojis. Spanish touches (Hola, amor, cariño). Bright energy!"""
    
    additional_context = ""
    if situation == 'mass_message_creation':
        if examples_text:
            additional_context += f"\n\nEXAMPLES TO BASE ON:\n{examples_text}\n\nUse these as inspiration but add your vibrant Latina energy."
        if modify_text:
            additional_context += f"\n\nMESSAGE TO MODIFY:\n{modify_text}\n\nImprove this with your energetic personality."
    
    return f"""{base_personality}

MEMORY CONTEXT: {memory_context}

CURRENT TASK: {analysis['submenu_name'] if analysis.get('submenu_name') else analysis['situation_name']}
OBJECTIVE: {analysis['objective']}

{additional_context}

Fan's request: "{fan_message}"

Respond as Venessa with your vibrant energy, adapting to achieve the objective."""

# Helper functions (same as before, with minor updates)
def get_fan_context(session_id, fan_id):
    """Retrieve fan context from session memory"""
    if session_id in session_memory and fan_id in session_memory[session_id]:
        return session_memory[session_id][fan_id]
    return {}

def update_session_memory(session_id, fan_id, interaction_data):
    """Update session memory with new interaction"""
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
            'situation_history': [],
            'submenu_history': [],
            'interaction_history': [],
            'conversation_flow': {
                'topics_discussed': [],
                'rapport_level': 1,
                'intimacy_level': 1,
                'trust_indicators': []
            }
        }
    
    fan_data = session_memory[session_id][fan_id]
    fan_data['total_interactions'] += 1
    fan_data['last_interaction'] = datetime.now().isoformat()
    fan_data['interaction_history'].append(interaction_data)
    fan_data['situation_history'].append(interaction_data['situation'])
    fan_data['submenu_history'].append(interaction_data.get('submenu', ''))
    # Extract information from message
    extract_fan_info(fan_data, interaction_data['message'])

def extract_fan_info(fan_data, message):
    """Extract fan information from message"""
    message_lower = message.lower()
    detected_info = fan_data['detected_info']
    
    # Extract name
    name_patterns = [
        r"my name is (\w+)",
        r"i am (\w+)",
        r"i'm (\w+)", 
        r"call me (\w+)",
        r"name's (\w+)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, message_lower)
        if match and not detected_info['name']:
            detected_info['name'] = match.group(1).title()
            break
    
    # Extract location
    location_patterns = [
        r"from (\w+)",
        r"live in (\w+)",
        r"located in (\w+)",
        r"i'm in (\w+)"
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, message_lower)
        if match and not detected_info['location']:
            detected_info['location'] = match.group(1).title()
            break
    
    # Extract interests
    interest_keywords = ['gaming', 'music', 'sports', 'movies', 'art', 'travel', 'fitness', 'cooking']
    for interest in interest_keywords:
        if interest in message_lower and interest not in detected_info['interests']:
            detected_info['interests'].append(interest)

def determine_relationship_stage(fan_context):
    """Determine relationship stage based on interaction history"""
    if not fan_context:
        return 'new'
    
    total_interactions = fan_context.get('total_interactions', 0)
    detected_info = fan_context.get('detected_info', {})
    
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
        return 'deepening_relationship'
    else:
        return 'established_relationship'

def build_memory_context(fan_context):
    """Build memory context for AI prompt"""
    if not fan_context or fan_context.get('total_interactions', 0) == 0:
        return "NEW FAN - First interaction. Build rapport and gather basic information."
    
    detected_info = fan_context.get('detected_info', {})
    total_interactions = fan_context.get('total_interactions', 0)
    relationship_stage = determine_relationship_stage(fan_context)
    
    context_parts = [
        f"ESTABLISHED FAN - {total_interactions} previous interactions",
        f"Relationship stage: {relationship_stage}"
    ]
    
    if detected_info.get('name'):
        context_parts.append(f"Fan's name: {detected_info['name']}")
    
    if detected_info.get('location'):
        context_parts.append(f"Location: {detected_info['location']}")
    
    if detected_info.get('interests'):
        context_parts.append(f"Interests: {', '.join(detected_info['interests'])}")
    
    return " | ".join(context_parts)

def get_submenu_recommended_action(analysis, situation, submenu):
    """Get recommended action based on submenu and analysis"""
    confidence = analysis['confidence_score']
    
    if submenu:
        submenu_name = analysis.get('submenu_name', submenu)
        if confidence > 80:
            return f"High confidence - Execute {submenu_name} strategy"
        elif confidence > 60:
            return f"Good match - Proceed with {submenu_name} approach"
        else:
            return f"Adapt {submenu_name} strategy based on response"
    else:
        situation_name = analysis['situation_name']
        if confidence > 80:
            return f"High confidence - Execute {situation_name} strategy"
        else:
            return f"Adapt {situation_name} approach"

# API Endpoints
@app.route('/api/get_session_memory')
def get_session_memory():
    """Get current session memory"""
    session_id = session.get('session_id', 'default')
    memory_data = session_memory.get(session_id, {})
    
    enhanced_fans = {}
    for fan_id, data in memory_data.items():
        enhanced_fans[fan_id] = {
            'total_interactions': data['total_interactions'],
            'detected_info': data['detected_info'],
            'last_interaction': data.get('last_interaction'),
            'situation_history': data.get('situation_history', []),
            'submenu_history': data.get('submenu_history', []),
            'relationship_stage': determine_relationship_stage(data)
        }
    
    return jsonify({
        'session_id': session_id,
        'total_fans': len(memory_data),
        'fans': enhanced_fans
    })

@app.route('/api/get_fan_data/<fan_id>')
def get_fan_data(fan_id):
    """Get specific fan data"""
    session_id = session.get('session_id', 'default')
    memory_data = session_memory.get(session_id, {})
    
    if fan_id in memory_data:
        fan_data = memory_data[fan_id]
        enhanced_data = fan_data.copy()
        enhanced_data['relationship_stage'] = determine_relationship_stage(fan_data)
        
        return jsonify({
            'success': True,
            'fan_data': enhanced_data
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Fan not found'
        })

@app.route('/api/reset_fan_memory/<fan_id>', methods=['POST'])
def reset_fan_memory(fan_id):
    """Reset memory for a specific fan"""
    session_id = session.get('session_id', 'default')
    
    if session_id in session_memory and fan_id in session_memory[session_id]:
        del session_memory[session_id][fan_id]
        return jsonify({'success': True, 'message': f'Memory reset for {fan_id}'})
    else:
        return jsonify({'success': False, 'error': 'Fan not found'})

@app.route('/api/test_ai')
def test_ai():
    """Test API endpoint"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        session_id = session.get('session_id', 'None')
        memory_stats = session_memory.get(session_id, {})
        
        total_interactions = sum(fan.get('total_interactions', 0) for fan in memory_stats.values())
        
        return jsonify({
            'status': 'OK',
            'api_key_present': bool(api_key),
            'model': 'gemini-2.5-pro-preview-06-05',
            'environment': 'Railway Production' if os.environ.get('RAILWAY_ENVIRONMENT') else 'Development',
            'framework': 'Saints & Sinners Submenu Intelligence',
            'features': [
                'KYC Submenu System',
                'Mass Message Creation',
                'Advanced Memory Context',
                'Creator Personality System'
            ],
            'situations_available': len(SS_SITUATIONS),
            'submenu_situations': len([s for s in SS_SITUATIONS.values() if s.get('has_submenu')]),
            'session_memory': {
                'session_id': session_id,
                'total_fans': len(memory_stats),
                'total_interactions': total_interactions
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Server configuration
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('FLASK_ENV') == 'production':
        print("🚀 Saints & Sinners FanFocus - SUBMENU INTELLIGENCE")
        print("🎯 KYC Submenu System + Mass Message Creation")
        print(f"📊 {len(SS_SITUATIONS)} Situations | 2 With Submenus")
        print("🧠 Advanced Session Memory System")
        print("✅ Practical Chatter Workflow Active")
    else:
        print("🔧 Development Mode - Submenu Testing")
        app.run(host='0.0.0.0', port=port, debug=True)
