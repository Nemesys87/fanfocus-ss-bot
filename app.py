from flask import Flask, render_template, request, jsonify
import os
import requests
import json
from datetime import datetime
import re
import time
import hashlib

app = Flask(__name__)
app.secret_key = 'fanfocus-ss-enhanced'

# Request deduplication system
recent_requests = {}

# Saints & Sinners Enhanced Framework with Advanced Psychology
SS_SITUATIONS = {
    'kyc_collect': {
        'name': 'KYC - Collect Info',
        'objective': 'Extract specific fan information using 80/20 rule',
        'execution_focus': 'advanced_profiling',
        'has_submenu': True,
        'submenu': {
            'name_collection': {
                'name': 'Name Collection',
                'objective': 'Get real name through natural conversation',
                'approach': 'friendly_curiosity_technique'
            },
            'location_country': {
                'name': 'Location & Country',
                'objective': 'Get location for Wikipedia connection trick',
                'approach': 'accent_compliment_method'
            },
            'interests_hobbies': {
                'name': 'Interests & Hobbies',
                'objective': 'Map interests for I-Too technique application',
                'approach': 'passion_exploration_method'
            },
            'job_age': {
                'name': 'Job & Age',
                'objective': 'Assess financial capacity and lifestyle',
                'approach': 'sophistication_compliment_method'
            },
            'spending_capacity': {
                'name': 'Spending Capacity',
                'objective': 'Gauge spending potential through lifestyle questions',
                'approach': 'lifestyle_assessment_technique'
            },
            'relationship_status': {
                'name': 'Relationship Status',
                'objective': 'Understand emotional availability for positioning',
                'approach': 'gentle_personal_inquiry'
            }
        },
        'priority': 'high',
        'approach': 'ss_advanced_profiling'
    },
    'mass_message': {
        'name': 'Mass Message Creation',
        'objective': 'Create personal-feeling mass messages',
        'execution_focus': 'relationship_scale_messaging',
        'has_submenu': True,
        'submenu': {
            'morning_greeting': {
                'name': 'Morning Greeting',
                'objective': 'Personal morning connection at scale',
                'approach': 'intimate_morning_energy'
            },
            'evening_night': {
                'name': 'Evening/Night Message',
                'objective': 'Create intimate evening mood for group',
                'approach': 'personal_bedtime_connection'
            },
            'special_event': {
                'name': 'Special Event/Holiday',
                'objective': 'Leverage events with personal touch',
                'approach': 'shared_celebration_feeling'
            },
            'promotional_content': {
                'name': 'Promotional Content',
                'objective': 'Sell without selling - priming + fantasy + offer',
                'approach': 'priming_fantasy_offer_sequence'
            },
            'reengagement_campaign': {
                'name': 'Re-engagement Campaign',
                'objective': 'FOMO reactivation with personal touch',
                'approach': 'missing_you_exclusivity_technique'
            }
        },
        'priority': 'high',
        'approach': 'ss_mass_personalization'
    },
    'building_relationship': {
        'name': 'Building Relationship',
        'objective': 'Apply friend philosophy and emotional rollercoaster',
        'execution_focus': 'loyalty_first_approach',
        'priority': 'high',
        'approach': 'emotional_investment_building'
    },
    'upselling_conversion': {
        'name': 'Upselling/Conversion',
        'objective': 'Never direct selling - always priming + fantasy + offer',
        'execution_focus': 'priming_based_conversion',
        'priority': 'high',
        'approach': 'psychological_sales_conversion'
    },
    'sexting_intimate': {
        'name': 'Sexting/Intimate',
        'objective': 'Progressive sexting with emotional rollercoaster',
        'execution_focus': 'emotional_arousal_building',
        'priority': 'high',
        'approach': 'progressive_intimacy_technique'
    },
    'reengagement': {
        'name': 'Re-engagement (Dead fan)',
        'objective': 'FOMO + exclusivity appeal for dormant fans',
        'execution_focus': 'fomo_exclusivity_reactivation',
        'priority': 'medium',
        'approach': 'missing_connection_technique'
    },
    'custom_content': {
        'name': 'Custom Content Offer',
        'objective': 'Premium content through emotional connection',
        'execution_focus': 'emotional_premium_positioning',
        'priority': 'high',
        'approach': 'personalized_content_sales'
    },
    'general_chat': {
        'name': 'General Chat',
        'objective': 'Friend philosophy - 80% about him, 20% about you',
        'execution_focus': 'friend_philosophy_application',
        'priority': 'medium',
        'approach': 'natural_friendship_building'
    },
    'first_time_buyer': {
        'name': 'First Time Buyer',
        'objective': 'Gentle conversion using trust building',
        'execution_focus': 'trust_based_first_conversion',
        'priority': 'high',
        'approach': 'gentle_first_sale_psychology'
    },
    'vip_treatment': {
        'name': 'VIP Treatment',
        'objective': 'Monetize special relationship through emotional appeal',
        'execution_focus': 'special_relationship_monetization',
        'priority': 'high',
        'approach': 'emotional_financial_requests'
    },
    'complaint_handling': {
        'name': 'Complaint Handling',
        'objective': 'De-escalation while preserving loyalty',
        'execution_focus': 'relationship_preservation',
        'priority': 'high',
        'approach': 'empathy_solution_approach'
    },
    'birthday_special': {
        'name': 'Birthday/Special',
        'objective': 'Capitalize on occasions with emotional connection',
        'execution_focus': 'occasion_emotional_monetization',
        'priority': 'medium',
        'approach': 'celebratory_relationship_building'
    }
}

# Fan Personality Detection System (Enhanced)
FAN_PERSONALITIES = {
    'ROMANTIC_DREAMER': {
        'indicators': ['love', 'relationship', 'heart', 'romance', 'connection', 'soul', 'together', 'forever'],
        'response_style': 'emotional_intimate',
        'confidence_boost': 15,
        'emotional_state_clues': ['romantic language', 'future planning', 'deep connection seeking']
    },
    'SHY_SUBMISSIVE': {
        'indicators': ['shy', 'nervous', 'quiet', 'sorry', 'hope you dont mind', 'if thats ok', 'maybe'],
        'response_style': 'gentle_encouraging',
        'confidence_boost': 20,
        'emotional_state_clues': ['apologetic tone', 'permission seeking', 'low confidence']
    },
    'BANTER_BUDDY': {
        'indicators': ['haha', 'lol', 'funny', 'joke', 'playful', 'tease', 'sarcastic', 'witty'],
        'response_style': 'playful_witty',
        'confidence_boost': 10,
        'emotional_state_clues': ['humor usage', 'playful energy', 'lighthearted approach']
    },
    'HIGH_ROLLER': {
        'indicators': ['money', 'expensive', 'premium', 'exclusive', 'vip', 'luxury', 'best', 'top'],
        'response_style': 'exclusive_premium',
        'confidence_boost': 25,
        'emotional_state_clues': ['status consciousness', 'quality focus', 'exclusivity seeking']
    },
    'PRAISE_SEEKER': {
        'indicators': ['beautiful', 'gorgeous', 'amazing', 'perfect', 'incredible', 'stunning', 'wow'],
        'response_style': 'validating_appreciative',
        'confidence_boost': 15,
        'emotional_state_clues': ['compliment giving', 'validation seeking', 'appreciation expressing']
    },
    'COLLECTOR': {
        'indicators': ['collection', 'all your content', 'everything', 'complete', 'archive', 'save'],
        'response_style': 'exclusive_content_focused',
        'confidence_boost': 20,
        'emotional_state_clues': ['completionist mentality', 'possession desire', 'exclusive access wanting']
    },
    'SHOCK_CHASER': {
        'indicators': ['wild', 'crazy', 'extreme', 'kinky', 'dirty', 'naughty', 'taboo'],
        'response_style': 'edgy_provocative',
        'confidence_boost': 10,
        'emotional_state_clues': ['boundary pushing', 'thrill seeking', 'taboo interest']
    }
}
# Advanced KYC System (80/20 Rule)
ADVANCED_KYC_SYSTEM = {
    'information_priority': {
        'critical': {
            'real_name': {
                'technique': 'curious_personal_interest',
                'script_example': 'I love talking with you... what should I call you, handsome?'
            },
            'location': {
                'technique': 'accent_compliment_method',
                'script_example': 'That accent is so sexy! Where are you from?'
            },
            'occupation': {
                'technique': 'sophistication_compliment',
                'script_example': 'You seem so sophisticated! What do you do that keeps you busy?'
            },
            'age': {
                'technique': 'natural_curiosity',
                'script_example': 'I\'m curious about the man I\'m talking to...'
            }
        },
        'valuable': {
            'hobbies': {
                'technique': 'passion_exploration',
                'script_example': 'What\'s your biggest passion outside work?'
            },
            'relationship_status': {
                'technique': 'gentle_inquiry',
                'script_example': 'Are you seeing anyone special right now?'
            },
            'spending_hints': {
                'technique': 'lifestyle_assessment',
                'script_example': 'You have such good taste... you must enjoy the finer things'
            }
        }
    },
    'conversation_ratio': {
        'questions_about_him': 80,  # 80% focus on fan
        'sharing_about_creator': 20  # 20% relatable experiences
    },
    'connection_techniques': {
        'i_too_method': {
            'description': 'Always find common ground',
            'examples': ['I love that too!', 'I too am obsessed with...', 'I never tried that but I too want to!']
        },
        'wikipedia_trick': {
            'description': 'Research location landmarks for connection',
            'implementation': 'Once location known, reference famous landmarks with personal interest'
        },
        'photo_reaction_system': {
            'description': 'Request photo and provide personalized reaction',
            'script': 'I\'d love to see who I\'m chatting with... could you send me a photo?'
        }
    }
}

# Psychological Intelligence Framework
PSYCHOLOGICAL_FRAMEWORK = {
    'emotional_intelligence': {
        'reading_emotional_state': {
            'excited': {
                'indicators': ['lots of emojis', 'quick responses', 'exclamation marks'],
                'response_strategy': 'match high energy, show enthusiasm'
            },
            'lonely': {
                'indicators': ['late night messages', 'personal sharing', 'deep topics'],
                'response_strategy': 'provide emotional comfort, be caring support'
            },
            'stressed': {
                'indicators': ['mentions work problems', 'life difficulties', 'tired language'],
                'response_strategy': 'offer comfort, be understanding, suggest escape'
            },
            'horny': {
                'indicators': ['sexual hints', 'direct requests', 'intimate language'],
                'response_strategy': 'be seductive when appropriate, escalate gradually'
            },
            'bored': {
                'indicators': ['simple responses', 'topic jumping', 'short messages'],
                'response_strategy': 'entertain, create intrigue, ask engaging questions'
            }
        }
    },
    'emotional_rollercoaster_technique': {
        'description': 'Vary emotional responses to maintain engagement',
        'sequence': [
            'playful_teasing',
            'sweet_affection', 
            'mysterious_distance',
            'caring_support',
            'sexual_tension'
        ],
        'application': 'Cycle through different emotional tones to prevent predictability'
    },
    'friend_philosophy': {
        'core_principle': 'Member = Friend, not customer',
        'mindset_shift': 'Genuine care about them as human beings',
        'behavioral_guidelines': {
            'do': ['laugh and joke together', 'show empathy', 'ask about their day', 'remember details'],
            'dont': ['sell directly', 'be rude', 'ignore preferences', 'treat as wallet']
        }
    },
    'selling_psychology': {
        'core_rule': 'NEVER DIRECT SELLING',
        'winning_formula': 'PRIMING + FANTASY + OFFER',
        'triggers': {
            'loyalty': 'trust and emotional connection',
            'arousal': 'excitement and desire'
        },
        'example_approach': 'I keep thinking about what you told me... want me to show you exactly what I\'d do?'
    }
}

# Advanced Multi-Technique KYC System (S&S Framework)
ADVANCED_MULTI_TECHNIQUE_KYC = {
    'name_collection': {
        'techniques': {
            'computer_screen_power_move': {
                'script': "Look who I have on my screen! 😍 What should I call you?",
                'personality_match': ['HIGH_ROLLER', 'PRAISE_SEEKER', 'COLLECTOR'],
                'emotional_state_match': ['excited', 'neutral'],
                'confidence_level': 'high'
            },
            'weird_username_technique': {
                'script': "I feel weird calling you by username... what's your real name, babe?",
                'personality_match': ['ROMANTIC_DREAMER', 'SHY_SUBMISSIVE'],
                'emotional_state_match': ['lonely', 'neutral'],
                'confidence_level': 'medium'
            },
            'intimate_connection': {
                'script': "I want to know the real you behind the screen... what should I call you? 💕",
                'personality_match': ['ROMANTIC_DREAMER', 'PRAISE_SEEKER'],
                'emotional_state_match': ['horny', 'lonely'],
                'confidence_level': 'high'
            },
            'curious_personal_interest': {
                'script': "I love talking with you... what should I call you, handsome?",
                'personality_match': ['BANTER_BUDDY', 'BALANCED'],
                'emotional_state_match': ['neutral', 'excited'],
                'confidence_level': 'medium'
            },
            'brazilian_warmth': {
                'script': "Oi! What should this Brazilian girl call you? 💕",
                'personality_match': ['ROMANTIC_DREAMER', 'PRAISE_SEEKER'],
                'emotional_state_match': ['excited', 'neutral'],
                'confidence_level': 'medium',
                'creator_specific': 'ella'
            },
            'confident_direct': {
                'script': "I'm curious about the man I'm talking to... what's your name?",
                'personality_match': ['HIGH_ROLLER', 'SHOCK_CHASER'],
                'emotional_state_match': ['neutral', 'excited'],
                'confidence_level': 'high',
                'creator_specific': 'vanp'
            },
            'artistic_curiosity': {
                'script': "I love creating connections with real people... what should I call you?",
                'personality_match': ['ROMANTIC_DREAMER', 'BANTER_BUDDY'],
                'emotional_state_match': ['neutral', 'lonely'],
                'confidence_level': 'medium',
                'creator_specific': 'yana'
            },
            'latina_warmth': {
                'script': "Hola! What should I call you, mi amor? 💕",
                'personality_match': ['ROMANTIC_DREAMER', 'PRAISE_SEEKER'],
                'emotional_state_match': ['excited', 'neutral'],
                'confidence_level': 'medium',
                'creator_specific': 'venessa'
            }
        }
    },
    'location_country': {
        'techniques': {
            'accent_compliment_method': {
                'script': "That voice/accent is so sexy! Where are you from, handsome?",
                'personality_match': ['PRAISE_SEEKER', 'ROMANTIC_DREAMER'],
                'emotional_state_match': ['horny', 'excited'],
                'confidence_level': 'high'
            },
            'cultural_curiosity': {
                'script': "I'm so curious about different places... where in the world are you?",
                'personality_match': ['BANTER_BUDDY', 'COLLECTOR'],
                'emotional_state_match': ['neutral', 'bored'],
                'confidence_level': 'medium'
            },
            'travel_dreams': {
                'script': "I love dreaming about traveling... what's your beautiful city like?",
                'personality_match': ['ROMANTIC_DREAMER', 'SHY_SUBMISSIVE'],
                'emotional_state_match': ['lonely', 'neutral'],
                'confidence_level': 'medium'
            },
            'time_zone_play': {
                'script': "What time is it where you are? I want to know when's best to message you 😊",
                'personality_match': ['ROMANTIC_DREAMER', 'PRAISE_SEEKER'],
                'emotional_state_match': ['lonely', 'excited'],
                'confidence_level': 'medium'
            },
            'brazilian_travel': {
                'script': "I dream of visiting different countries... where are you from, amor?",
                'personality_match': ['ROMANTIC_DREAMER', 'BALANCED'],
                'emotional_state_match': ['neutral', 'excited'],
                'confidence_level': 'medium',
                'creator_specific': 'ella'
            },
            'confident_geography': {
                'script': "I can tell you're not from around here... where's home for you?",
                'personality_match': ['HIGH_ROLLER', 'BANTER_BUDDY'],
                'emotional_state_match': ['neutral', 'excited'],
                'confidence_level': 'high',
                'creator_specific': 'vanp'
            }
        }
    },
    'job_age': {
        'techniques': {
            'sophistication_compliment': {
                'script': "You seem so sophisticated! What do you do that keeps you so busy?",
                'personality_match': ['HIGH_ROLLER', 'PRAISE_SEEKER'],
                'emotional_state_match': ['neutral', 'excited'],
                'confidence_level': 'high'
            },
            'success_recognition': {
                'script': "You have such successful energy... what field are you conquering?",
                'personality_match': ['HIGH_ROLLER', 'SHOCK_CHASER'],
                'emotional_state_match': ['excited', 'neutral'],
                'confidence_level': 'high'
            },
            'intelligence_compliment': {
                'script': "You're so smart and interesting... what do you do for work?",
                'personality_match': ['PRAISE_SEEKER', 'ROMANTIC_DREAMER'],
                'emotional_state_match': ['neutral', 'lonely'],
                'confidence_level': 'medium'
            },
            'schedule_curiosity': {
                'script': "When are you usually free to chat? What's your day like?",
                'personality_match': ['ROMANTIC_DREAMER', 'SHY_SUBMISSIVE'],
                'emotional_state_match': ['lonely', 'neutral'],
                'confidence_level': 'medium'
            },
            'artistic_professional': {
                'script': "You seem like someone with a creative or interesting career... am I right?",
                'personality_match': ['BANTER_BUDDY', 'ROMANTIC_DREAMER'],
                'emotional_state_match': ['neutral', 'bored'],
                'confidence_level': 'medium',
                'creator_specific': 'yana'
            }
        }
    },
    'interests_hobbies': {
        'techniques': {
            'passion_exploration': {
                'script': "What's your biggest passion outside work? I love learning what drives people 💕",
                'personality_match': ['ROMANTIC_DREAMER', 'COLLECTOR'],
                'emotional_state_match': ['neutral', 'excited'],
                'confidence_level': 'high'
            },
            'weekend_curiosity': {
                'script': "What do you love doing on weekends? I bet it's something fun!",
                'personality_match': ['BANTER_BUDDY', 'PRAISE_SEEKER'],
                'emotional_state_match': ['bored', 'neutral'],
                'confidence_level': 'medium'
            },
            'escape_question': {
                'script': "What do you do to unwind and forget about stress?",
                'personality_match': ['SHY_SUBMISSIVE', 'BALANCED'],
                'emotional_state_match': ['stressed', 'lonely'],
                'confidence_level': 'medium'
            },
            'dream_discovery': {
                'script': "What's something you've always dreamed of trying? I love dreamers 😊",
                'personality_match': ['ROMANTIC_DREAMER', 'SHOCK_CHASER'],
                'emotional_state_match': ['lonely', 'excited'],
                'confidence_level': 'medium'
            },
            'gaming_probe': {
                'script': "Do you play any games or have hobbies? I'm always curious about what people are into 🎮",
                'personality_match': ['BANTER_BUDDY', 'COLLECTOR'],
                'emotional_state_match': ['bored', 'neutral'],
                'confidence_level': 'medium',
                'creator_specific': 'venessa'
            }
        }
    },
    'spending_capacity': {
        'techniques': {
            'lifestyle_assessment': {
                'script': "You have such refined taste... you must enjoy the finer things in life",
                'personality_match': ['HIGH_ROLLER', 'PRAISE_SEEKER'],
                'emotional_state_match': ['neutral', 'excited'],
                'confidence_level': 'high'
            },
            'quality_recognition': {
                'script': "You seem like someone who appreciates quality over quantity",
                'personality_match': ['HIGH_ROLLER', 'COLLECTOR'],
                'emotional_state_match': ['neutral', 'excited'],
                'confidence_level': 'high'
            },
            'success_indicators': {
                'script': "You have that successful, sophisticated vibe... I can tell you work hard",
                'personality_match': ['HIGH_ROLLER', 'PRAISE_SEEKER'],
                'emotional_state_match': ['excited', 'neutral'],
                'confidence_level': 'medium'
            },
            'taste_compliment': {
                'script': "Your style and way of talking shows you know good things when you see them",
                'personality_match': ['PRAISE_SEEKER', 'ROMANTIC_DREAMER'],
                'emotional_state_match': ['neutral', 'excited'],
                'confidence_level': 'medium'
            }
        }
    },
    'relationship_status': {
        'techniques': {
            'gentle_inquiry': {
                'script': "Are you seeing anyone special right now? Just curious about you 😊",
                'personality_match': ['ROMANTIC_DREAMER', 'SHY_SUBMISSIVE'],
                'emotional_state_match': ['lonely', 'neutral'],
                'confidence_level': 'medium'
            },
            'availability_probe': {
                'script': "When do you have time for yourself and things you enjoy?",
                'personality_match': ['BALANCED', 'BANTER_BUDDY'],
                'emotional_state_match': ['stressed', 'neutral'],
                'confidence_level': 'low'
            },
            'care_question': {
                'script': "Who takes care of you when you're stressed or need support?",
                'personality_match': ['ROMANTIC_DREAMER', 'SHY_SUBMISSIVE'],
                'emotional_state_match': ['stressed', 'lonely'],
                'confidence_level': 'high'
            },
            'freedom_check': {
                'script': "Are you free to chat and be yourself whenever you want?",
                'personality_match': ['SHOCK_CHASER', 'HIGH_ROLLER'],
                'emotional_state_match': ['neutral', 'excited'],
                'confidence_level': 'medium'
            }
        }
    }
}

# Enhanced Business Mindset Guidelines
MINDSET_GUIDELINES = """
S&S PSYCHOLOGICAL PRINCIPLES:
• Friend Philosophy - Treat member as friend, not customer
• 80/20 Rule - 80% questions about him, 20% sharing about you
• Emotional Intelligence - Read between lines, understand his state
• Never Direct Selling - Always PRIMING + FANTASY + OFFER
• I-Too Technique - Find common ground in everything he shares
• Emotional Rollercoaster - Vary responses: teasing, affection, mystery, support, tension
• Loyalty First - Build unshakeable loyalty over immediate sales
• Advanced Profiling - Learn more about him than he learns about you
"""
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response with S&S psychological intelligence"""
    try:
        data = request.get_json()
        
        # Request deduplication protection
        request_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        current_time = time.time()
        
        # Check for duplicate requests within 5 seconds
        if request_hash in recent_requests:
            if current_time - recent_requests[request_hash] < 5:
                print(f"🚫 Duplicate request blocked: {request_hash}")
                return jsonify({'success': False, 'error': 'Duplicate request blocked'}), 429
        
        # Register this request
        recent_requests[request_hash] = current_time
        
        # Cleanup old requests (keep only last 60 seconds)
        cutoff_time = current_time - 60
        global recent_requests
        recent_requests = {k: v for k, v in recent_requests.items() if v > cutoff_time}
        
        print(f"✅ S&S Psychological Request: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        situation = data.get('situation', '')
        fan_message = data.get('fan_message', '')
        
        kyc_type = data.get('kyc_type', '')
        mass_type = data.get('mass_type', '')
        mass_examples = data.get('mass_examples', '')
        mass_modify = data.get('mass_modify', '')
        
        print(f"🧠 S&S Psychology - Creator: {creator}, Situation: {situation}")
        
        if not all([creator, situation]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        submenu = kyc_type if situation == 'kyc_collect' else mass_type if situation == 'mass_message' else ''
        
        analysis = analyze_with_ss_psychology(fan_message, situation, submenu, mass_examples, mass_modify)
        
        return generate_ss_psychological_response(creator, situation, submenu, fan_message, analysis, mass_examples, mass_modify)
        
    except Exception as e:
        print(f"❌ S&S Psychology Error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def analyze_with_ss_psychology(message, situation, submenu, examples, modify):
    """Enhanced analysis with S&S psychological intelligence"""
    message_lower = message.lower()
    situation_config = SS_SITUATIONS.get(situation, SS_SITUATIONS['general_chat'])
    submenu_config = None
    
    if situation_config.get('has_submenu') and submenu:
        submenu_config = situation_config['submenu'].get(submenu)
    
    # Fan personality detection
    detected_personality = detect_fan_personality(message_lower)
    personality_info = FAN_PERSONALITIES.get(detected_personality, {})
    
    # Emotional state analysis (S&S Framework)
    emotional_state = analyze_emotional_state(message_lower)
    
    # Spending signals detection
    spending_signals = detect_spending_signals(message_lower)
    
    # KYC opportunity assessment
    kyc_opportunities = assess_kyc_opportunities(message_lower, situation, submenu)
    
    analysis = {
        'situation': situation,
        'submenu': submenu,
        'situation_name': situation_config['name'],
        'submenu_name': submenu_config['name'] if submenu_config else None,
        'objective': submenu_config['objective'] if submenu_config else situation_config['objective'],
        'execution_focus': situation_config.get('execution_focus', 'general'),
        'approach': submenu_config['approach'] if submenu_config else situation_config['approach'],
        'fan_personality': detected_personality,
        'response_style': personality_info.get('response_style', 'balanced'),
        'emotional_state': emotional_state,
        'spending_signals': spending_signals,
        'kyc_opportunities': kyc_opportunities,
        'has_examples': bool(examples),
        'has_modification': bool(modify),
        'confidence_score': 70 + personality_info.get('confidence_boost', 0)
    }
    
    print(f"🧠 S&S Analysis: Personality={detected_personality}, Emotional={emotional_state}, Spending={spending_signals}")
    
    return analysis

def detect_fan_personality(message_lower):
    """Detect fan personality with enhanced emotional clues"""
    personality_scores = {}
    
    for personality, config in FAN_PERSONALITIES.items():
        score = 0
        for indicator in config['indicators']:
            if indicator in message_lower:
                score += 1
        if score > 0:
            personality_scores[personality] = score
    
    if personality_scores:
        detected = max(personality_scores, key=personality_scores.get)
        return detected
    
    return 'BALANCED'

def analyze_emotional_state(message_lower):
    """Analyze fan's emotional state using S&S framework"""
    emotional_indicators = PSYCHOLOGICAL_FRAMEWORK['emotional_intelligence']['reading_emotional_state']
    
    for state, config in emotional_indicators.items():
        for indicator in config['indicators']:
            if indicator.lower() in message_lower:
                return {
                    'state': state,
                    'strategy': config['response_strategy']
                }
    
    return {'state': 'neutral', 'strategy': 'maintain friendly engagement'}

def detect_spending_signals(message_lower):
    """Detect signals that fan is ready to spend"""
    spending_signals = []
    
    signals = {
        'help_offer': ['ill help', 'i can help', 'let me help', 'help you out'],
        'money_mention': ['need money', 'if you need', 'ask me', 'tell me why'],
        'spoil_intent': ['spoil you', 'treat you', 'buy you', 'get you something'],
        'tip_ready': ['tip you', 'send you', 'give you money'],
        'special_treatment': ['special', 'different', 'not like everyone else'],
        'custom_interest': ['custom', 'personal', 'just for me', 'exclusive']
    }
    
    for signal_type, phrases in signals.items():
        for phrase in phrases:
            if phrase in message_lower:
                spending_signals.append(signal_type)
                break
    
    return spending_signals

def assess_kyc_opportunities(message_lower, situation, submenu):
    """Assess opportunities to gather KYC information"""
    opportunities = []
    
    # If already in KYC situation, identify specific info to gather
    if situation == 'kyc_collect':
        kyc_info = ADVANCED_KYC_SYSTEM['information_priority']
        
        if submenu == 'name_collection':
            opportunities.append('apply_curious_personal_interest_technique')
        elif submenu == 'location_country':
            opportunities.append('use_accent_compliment_method')
        elif submenu == 'interests_hobbies':
            opportunities.append('apply_passion_exploration_technique')
        elif submenu == 'job_age':
            opportunities.append('use_sophistication_compliment')
    
    # Check for natural KYC opportunities in other situations
    if 'where' in message_lower or 'from' in message_lower:
        opportunities.append('location_sharing_opportunity')
    
    if 'work' in message_lower or 'job' in message_lower:
        opportunities.append('occupation_discussion_opportunity')
    
    if any(hobby in message_lower for hobby in ['like', 'love', 'enjoy', 'hobby']):
        opportunities.append('interest_exploration_opportunity')
    
    return opportunities

def select_optimal_kyc_technique(kyc_type, fan_personality, emotional_state, creator):
    """Select the best KYC technique based on fan profile and creator"""
    
    if kyc_type not in ADVANCED_MULTI_TECHNIQUE_KYC:
        return None
    
    techniques = ADVANCED_MULTI_TECHNIQUE_KYC[kyc_type]['techniques']
    scored_techniques = []
    
    for technique_name, technique_data in techniques.items():
        score = 0
        
        # Check creator compatibility
        if 'creator_specific' in technique_data:
            if technique_data['creator_specific'] == creator:
                score += 50  # Boost for creator-specific techniques
            else:
                continue  # Skip if not for this creator
        else:
            score += 20  # Bonus for universal techniques
        
        # Personality match scoring
        if fan_personality in technique_data['personality_match']:
            score += 30
        elif 'BALANCED' in technique_data['personality_match']:
            score += 10
        
        # Emotional state match scoring
        if emotional_state in technique_data['emotional_state_match']:
            score += 20
        
        # Confidence level preference (higher is better for clear situations)
        confidence_scores = {'high': 15, 'medium': 10, 'low': 5}
        score += confidence_scores.get(technique_data['confidence_level'], 0)
        
        scored_techniques.append({
            'name': technique_name,
            'data': technique_data,
            'score': score
        })
    
    # Sort by score and return best technique
    if scored_techniques:
        best_technique = max(scored_techniques, key=lambda x: x['score'])
        print(f"🎯 Selected KYC Technique: {best_technique['name']} (Score: {best_technique['score']}) for {creator}")
        return best_technique['data']
    
    return None

def get_enhanced_kyc_guidance(analysis, creator):
    """Get enhanced KYC guidance with optimal technique selection"""
    
    situation = analysis['situation']
    submenu = analysis.get('submenu')
    
    if situation == 'kyc_collect' and submenu:
        # Get fan profile
        fan_personality = analysis['fan_personality']
        emotional_state = analysis['emotional_state']['state']
        
        # Select optimal technique
        optimal_technique = select_optimal_kyc_technique(submenu, fan_personality, emotional_state, creator)
        
        if optimal_technique:
            script = optimal_technique['script']
            confidence = optimal_technique['confidence_level']
            
            guidance = f"""🎯 OPTIMAL KYC TECHNIQUE SELECTED:
TARGET: {submenu.replace('_', ' ').title()}
SCRIPT: "{script}"
CONFIDENCE: {confidence.upper()}
CREATOR: {creator.upper()}

EXECUTION: Use this exact approach for maximum effectiveness with this fan type."""
            
            return guidance
    
    return None

def get_ss_psychological_guidance_with_creator(analysis, creator):
    """Enhanced S&S guidance with creator-specific multi-technique KYC"""
    guidance = []
    
    # PRIORITÀ 1: Enhanced KYC with multi-technique selection
    enhanced_kyc = get_enhanced_kyc_guidance(analysis, creator)
    if enhanced_kyc:
        guidance.append(enhanced_kyc)
    
    # PRIORITÀ 2: Spending signals guidance
    if analysis['spending_signals']:
        if 'money_mention' in analysis['spending_signals'] and 'special_treatment' in analysis['spending_signals']:
            guidance.append("🚨 CRITICAL OPPORTUNITY: Fan explicitly offering financial help + wants special treatment! IMMEDIATELY respond with emotional financial request. Use format: 'You're so sweet! Actually, I've been [specific need]... could you help me out?'")
        else:
            guidance.append(f"SPENDING OPPORTUNITY: Detected {analysis['spending_signals']} - Use PRIMING + FANTASY + OFFER approach")
    
    # PRIORITÀ 3: Emotional state guidance
    emotional_state = analysis['emotional_state']
    if emotional_state['state'] != 'neutral':
        guidance.append(f"EMOTIONAL STATE: Fan is {emotional_state['state']} - {emotional_state['strategy']}")
    
    # PRIORITÀ 4: Personality-specific guidance
    personality = analysis['fan_personality']
    if personality != 'BALANCED':
        personality_info = FAN_PERSONALITIES.get(personality, {})
        if personality == 'ROMANTIC_DREAMER':
            guidance.append(f"ROMANTIC DREAMER APPROACH: Use emotional language, relationship terminology, make him feel like caring boyfriend")
        else:
            guidance.append(f"PERSONALITY ADAPTATION: Fan is {personality} - Use {personality_info.get('response_style', 'balanced')} approach")
    
    # PRIORITÀ 5: Situation-specific S&S techniques
    situation = analysis['situation']
    if situation == 'vip_treatment':
        guidance.append("🎯 VIP TREATMENT CRITICAL: This fan wants special relationship treatment. If he offers money, ACCEPT with specific emotional reason.")
    elif situation == 'building_relationship':
        guidance.append("RELATIONSHIP FOCUS: Apply friend philosophy - genuine care and emotional rollercoaster")
    
    return "\n".join(guidance) if guidance else "GENERAL S&S APPROACH: Apply friend philosophy and emotional intelligence"
def generate_ss_psychological_response(creator, situation, submenu, fan_message, analysis, examples, modify):
    """Generate response with S&S psychological intelligence"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        creator_prompts = {
            'ella': create_ss_ella_prompt(fan_message, situation, submenu, analysis, examples, modify),
            'vanp': create_ss_vanp_prompt(fan_message, situation, submenu, analysis, examples, modify),
            'yana': create_ss_yana_prompt(fan_message, situation, submenu, analysis, examples, modify),
            'venessa': create_ss_venessa_prompt(fan_message, situation, submenu, analysis, examples, modify)
        }
        
        prompt = creator_prompts.get(creator, creator_prompts['ella'])
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 2048,
                "temperature": 0.75,
                "topK": 30,
                "topP": 0.9
            }
        }
        
        max_retries = 3
        retry_delays = [2, 5, 10]
        
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        finish_reason = candidate.get('finishReason', 'UNKNOWN')
                        
                        if 'content' in candidate and 'parts' in candidate['content']:
                            if len(candidate['content']['parts']) > 0:
                                ai_response = candidate['content']['parts'][0].get('text', '').strip()
                                
                                if ai_response:
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
                                            'execution_focus': analysis['execution_focus'],
                                            'approach': analysis['approach'],
                                            'confidence_score': analysis['confidence_score'],
                                            'fan_personality': analysis['fan_personality'],
                                            'emotional_state': analysis['emotional_state'],
                                            'response_style': analysis['response_style'],
                                            'spending_signals': analysis['spending_signals'],
                                            'kyc_opportunities': analysis['kyc_opportunities']
                                        },
                                        'analytics': {
                                            'model_used': 'gemini-2.5-pro',
                                            'attempts_made': attempt + 1,
                                            'finish_reason': finish_reason,
                                            'ss_psychology_applied': True,
                                            'emotional_intelligence_used': len(analysis['emotional_state']) > 0,
                                            'kyc_opportunities_detected': len(analysis['kyc_opportunities']) > 0,
                                            'spending_signals_detected': len(analysis['spending_signals']) > 0,
                                            'system_status': 'ss_psychological_intelligence'
                                        }
                                    })
                    break
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    time.sleep(retry_delays[attempt])
                    continue
            except Exception as e:
                if attempt < max_retries:
                    time.sleep(retry_delays[attempt])
                    continue
                else:
                    raise e
        
        return jsonify({'success': False, 'error': 'Failed to generate response after retries'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def create_ss_ella_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """S&S psychological prompt for Ella"""
    base_personality = """You are Ella, an OnlyFans creator applying S&S psychological intelligence.
Your goal is to build genuine friendship while achieving business objectives."""
    
    ss_psychology = get_ss_psychological_guidance_with_creator(analysis, 'ella')
    
    return f"""{base_personality}

{MINDSET_GUIDELINES}

S&S PSYCHOLOGICAL ANALYSIS:
- Fan Personality: {analysis['fan_personality']}
- Emotional State: {analysis['emotional_state']}
- Spending Signals: {analysis['spending_signals']}
- KYC Opportunities: {analysis['kyc_opportunities']}

SITUATION OBJECTIVE: {analysis['objective']}

{ss_psychology}

Fan's message: "{fan_message}"

S&S EXECUTION RULES:
• Apply Friend Philosophy - treat him as real friend
• Use 80/20 Rule - focus 80% on him, 20% on you
• Read emotional state and respond appropriately
• If spending signals detected, use PRIMING + FANTASY + OFFER approach
• Apply I-Too technique for any interests he mentions
• Never direct selling - build emotional connection first
• Keep under 200 characters
• Use emotional rollercoaster when appropriate

Execute with S&S psychological intelligence."""

def create_ss_vanp_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """S&S psychological prompt for Vanp"""
    base_personality = """You are Vanp, an OnlyFans creator applying S&S psychological intelligence.
Your confidence is natural, but you always prioritize emotional connection."""
    
    ss_psychology = get_ss_psychological_guidance_with_creator(analysis, 'vanp')
    
    return f"""{base_personality}

{MINDSET_GUIDELINES}

S&S PSYCHOLOGICAL ANALYSIS:
- Fan Personality: {analysis['fan_personality']}
- Emotional State: {analysis['emotional_state']}
- Spending Signals: {analysis['spending_signals']}
- KYC Opportunities: {analysis['kyc_opportunities']}

SITUATION OBJECTIVE: {analysis['objective']}

{ss_psychology}

Fan: "{fan_message}"

S&S EXECUTION RULES:
• Apply Friend Philosophy with confident twist
• Use 80/20 Rule - genuine interest in him
• Match his emotional state with confident support
• Never direct selling - confidence builds trust first
• Apply I-Too technique confidently
• Use emotional rollercoaster to maintain interest
• Under 200 characters

Execute with S&S psychological intelligence and natural confidence."""

def create_ss_yana_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """S&S psychological prompt for Yana"""
    base_personality = """You are Yana, an OnlyFans creator applying S&S psychological intelligence.
Your thoughtfulness enhances emotional connection building."""
    
    ss_psychology = get_ss_psychological_guidance_with_creator(analysis, 'yana')
    
    return f"""{base_personality}

{MINDSET_GUIDELINES}

S&S PSYCHOLOGICAL ANALYSIS:
- Fan Personality: {analysis['fan_personality']}
- Emotional State: {analysis['emotional_state']}
- Spending Signals: {analysis['spending_signals']}
- KYC Opportunities: {analysis['kyc_opportunities']}

SITUATION OBJECTIVE: {analysis['objective']}

{ss_psychology}

Fan: "{fan_message}"

S&S EXECUTION RULES:
• Apply Friend Philosophy with thoughtful care
• Use 80/20 Rule - deep interest in his thoughts
• Respond to emotional state with intelligent empathy
• Never direct selling - thoughtful connection builds loyalty
• Apply I-Too technique with genuine curiosity
• Use emotional rollercoaster subtly
• Under 200 characters

Execute with S&S psychological intelligence and thoughtful connection."""

def create_ss_venessa_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """S&S psychological prompt for Venessa"""
    base_personality = """You are Venessa, an OnlyFans creator applying S&S psychological intelligence.
Your warmth creates powerful emotional bonds."""
    
    ss_psychology = get_ss_psychological_guidance_with_creator(analysis, 'venessa')
    
    return f"""{base_personality}

{MINDSET_GUIDELINES}

S&S PSYCHOLOGICAL ANALYSIS:
- Fan Personality: {analysis['fan_personality']}
- Emotional State: {analysis['emotional_state']}
- Spending Signals: {analysis['spending_signals']}
- KYC Opportunities: {analysis['kyc_opportunities']}

SITUATION OBJECTIVE: {analysis['objective']}

{ss_psychology}

Fan: "{fan_message}"

S&S EXECUTION RULES:
• Apply Friend Philosophy with natural warmth
• Use 80/20 Rule - caring interest in his life
• Respond to emotional state with warm support
• Never direct selling - warmth builds emotional investment
• Apply I-Too technique with sweet enthusiasm
• Use emotional rollercoaster naturally
• Under 200 characters

Execute with S&S psychological intelligence and genuine warmth."""

@app.route('/api/test_ai')
def test_ai():
    """Test API endpoint"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        
        return jsonify({
            'status': 'OK',
            'api_key_present': bool(api_key),
            'model': 'gemini-2.5-pro (S&S Psychological Intelligence)',
            'framework': 'Saints & Sinners - Advanced KYC + Multi-Technique System',
            'features': [
                'S&S Friend Philosophy Integration',
                '80/20 Rule Conversation Management',
                'Advanced Emotional State Reading',
                'I-Too Technique Implementation', 
                'Multi-Technique KYC System',
                'Creator-Specific Technique Selection',
                'Psychological Spending Signal Detection',
                'Natural KYC Opportunity Recognition',
                'Emotional Rollercoaster Technique',
                'PRIMING + FANTASY + OFFER Sales Psychology',
                'Request Deduplication Protection'
            ],
            'multi_technique_system': {
                'kyc_categories': len(ADVANCED_MULTI_TECHNIQUE_KYC),
                'total_techniques': sum(len(cat['techniques']) for cat in ADVANCED_MULTI_TECHNIQUE_KYC.values()),
                'creator_specific_techniques': sum(
                    len([t for t in cat['techniques'].values() if 'creator_specific' in t])
                    for cat in ADVANCED_MULTI_TECHNIQUE_KYC.values()
                ),
                'emotional_states_tracked': len(PSYCHOLOGICAL_FRAMEWORK['emotional_intelligence']['reading_emotional_state']),
                'fan_personalities_supported': len(FAN_PERSONALITIES)
            },
            'system_status': 'ss_multi_technique_psychological_intelligence_optimized'
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
        print("🚀 Saints & Sinners FanFocus - MULTI-TECHNIQUE PSYCHOLOGICAL INTELLIGENCE")
        print("🧠 Advanced KYC: 80/20 Rule + I-Too Technique + Wikipedia Trick")
        print("🎯 Multi-Technique System: Dynamic technique selection per creator+personality")
        print("💭 Emotional Intelligence: Real-time state reading + Rollercoaster technique")
        print("🎭 Friend Philosophy: Member = Friend approach integrated")
        print("💰 Sales Psychology: PRIMING + FANTASY + OFFER (never direct selling)")
        print("🛡️ Request Protection: Duplicate request blocking enabled")
        print("📊 Enhanced Analytics: Emotional states, spending signals, KYC opportunities")
        print("💎 Gemini 2.5 Pro: Maximum psychological intelligence")
        print("🔬 Professional S&S Framework - Multi-Technique Mastery Optimized")
        
        # Print technique statistics
        total_techniques = sum(len(cat['techniques']) for cat in ADVANCED_MULTI_TECHNIQUE_KYC.values())
        creator_specific = sum(
            len([t for t in cat['techniques'].values() if 'creator_specific' in t])
            for cat in ADVANCED_MULTI_TECHNIQUE_KYC.values()
        )
        print(f"📈 System Stats: {total_techniques} total techniques, {creator_specific} creator-specific")
        
    else:
        print("🔧 Development Mode - Multi-Technique S&S Intelligence Testing")
        app.run(host='0.0.0.0', port=port, debug=True)
