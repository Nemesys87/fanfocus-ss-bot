from flask import Flask, render_template, request, jsonify
import os
import requests
import json
from datetime import datetime
import re
import time

app = Flask(__name__)
app.secret_key = 'fanfocus-ss-enhanced'

# Saints & Sinners Enhanced Framework with Personality Detection
SS_SITUATIONS = {
    'kyc_collect': {
        'name': 'KYC - Collect Info',
        'objective': 'Collect specific fan information',
        'has_submenu': True,
        'submenu': {
            'name_collection': {
                'name': 'Name Collection',
                'objective': 'Get the fan\'s name',
                'approach': 'friendly_name_gathering'
            },
            'location_country': {
                'name': 'Location & Country',
                'objective': 'Find out where the fan is from',
                'approach': 'location_discovery'
            },
            'interests_hobbies': {
                'name': 'Interests & Hobbies',
                'objective': 'Learn about fan\'s interests and hobbies',
                'approach': 'interest_exploration'
            },
            'job_age': {
                'name': 'Job & Age',
                'objective': 'Get professional and age information',
                'approach': 'professional_inquiry'
            },
            'spending_capacity': {
                'name': 'Spending Capacity',
                'objective': 'Subtly assess financial capacity',
                'approach': 'subtle_financial_assessment'
            },
            'relationship_status': {
                'name': 'Relationship Status',
                'objective': 'Learn about relationship status',
                'approach': 'relationship_discovery'
            }
        },
        'priority': 'high',
        'approach': 'targeted_information_gathering'
    },
    'mass_message': {
        'name': 'Mass Message Creation',
        'objective': 'Create effective mass messages',
        'has_submenu': True,
        'submenu': {
            'morning_greeting': {
                'name': 'Morning Greeting',
                'objective': 'Create engaging morning mass messages',
                'approach': 'energetic_morning_engagement'
            },
            'evening_night': {
                'name': 'Evening/Night Message',
                'objective': 'Create intimate evening/night messages',
                'approach': 'intimate_evening_connection'
            },
            'special_event': {
                'name': 'Special Event/Holiday',
                'objective': 'Create holiday/event-themed messages',
                'approach': 'celebratory_themed_messaging'
            },
            'promotional_content': {
                'name': 'Promotional Content',
                'objective': 'Create promotional mass messages',
                'approach': 'persuasive_promotional_messaging'
            },
            'reengagement_campaign': {
                'name': 'Re-engagement Campaign',
                'objective': 'Create messages to reactivate inactive fans',
                'approach': 'emotional_reactivation_messaging'
            }
        },
        'priority': 'high',
        'approach': 'strategic_mass_communication'
    },
    'building_relationship': {
        'name': 'Building Relationship',
        'objective': 'Build emotional connection and trust',
        'priority': 'high',
        'approach': 'emotional_engagement'
    },
    'upselling_conversion': {
        'name': 'Upselling/Conversion',
        'objective': 'Promote premium content or services',
        'priority': 'high',
        'approach': 'sales_focused'
    },
    'sexting_intimate': {
        'name': 'Sexting/Intimate',
        'objective': 'Engage in intimate conversation',
        'priority': 'high',
        'approach': 'intimate_focused'
    },
    'reengagement': {
        'name': 'Re-engagement (Dead fan)',
        'objective': 'Reactivate inactive fans',
        'priority': 'medium',
        'approach': 'reactivation'
    },
    'custom_content': {
        'name': 'Custom Content Offer',
        'objective': 'Offer personalized content',
        'priority': 'high',
        'approach': 'personalization'
    },
    'general_chat': {
        'name': 'General Chat',
        'objective': 'Maintain friendly conversation',
        'priority': 'medium',
        'approach': 'conversational'
    },
    'first_time_buyer': {
        'name': 'First Time Buyer',
        'objective': 'Convert first-time buyers',
        'priority': 'high',
        'approach': 'educational_sales'
    },
    'vip_treatment': {
        'name': 'VIP Treatment',
        'objective': 'Special treatment for high spenders',
        'priority': 'high',
        'approach': 'premium_service'
    },
    'complaint_handling': {
        'name': 'Complaint Handling',
        'objective': 'Address complaints and issues',
        'priority': 'high',
        'approach': 'problem_solving'
    },
    'birthday_special': {
        'name': 'Birthday/Special',
        'objective': 'Celebrate special occasions',
        'priority': 'medium',
        'approach': 'celebratory'
    }
}

# Fan Personality Detection System
FAN_PERSONALITIES = {
    'ROMANTIC_DREAMER': {
        'indicators': ['love', 'relationship', 'heart', 'romance', 'connection', 'soul', 'together', 'forever'],
        'response_style': 'emotional_intimate',
        'confidence_boost': 15
    },
    'SHY_SUBMISSIVE': {
        'indicators': ['shy', 'nervous', 'quiet', 'sorry', 'hope you dont mind', 'if thats ok', 'maybe'],
        'response_style': 'gentle_encouraging',
        'confidence_boost': 20
    },
    'BANTER_BUDDY': {
        'indicators': ['haha', 'lol', 'funny', 'joke', 'playful', 'tease', 'sarcastic', 'witty'],
        'response_style': 'playful_witty',
        'confidence_boost': 10
    },
    'HIGH_ROLLER': {
        'indicators': ['money', 'expensive', 'premium', 'exclusive', 'vip', 'luxury', 'best', 'top'],
        'response_style': 'exclusive_premium',
        'confidence_boost': 25
    },
    'PRAISE_SEEKER': {
        'indicators': ['beautiful', 'gorgeous', 'amazing', 'perfect', 'incredible', 'stunning', 'wow'],
        'response_style': 'validating_appreciative',
        'confidence_boost': 15
    },
    'COLLECTOR': {
        'indicators': ['collection', 'all your content', 'everything', 'complete', 'archive', 'save'],
        'response_style': 'exclusive_content_focused',
        'confidence_boost': 20
    },
    'SHOCK_CHASER': {
        'indicators': ['wild', 'crazy', 'extreme', 'kinky', 'dirty', 'naughty', 'taboo'],
        'response_style': 'edgy_provocative',
        'confidence_boost': 10
    }
}

# Professional Mindset Guidelines
MINDSET_GUIDELINES = """
MINDSET PRINCIPLES:
• Empathy - Understand fan's emotional state and needs
• Adaptive confidence - Match energy level appropriately  
• Authentic variety - Avoid repetitive patterns, stay fresh
• Playful intrigue - Create curiosity and engagement
• Concision - Maximum impact with minimum words (≤250 characters)
• Fan-first value - Always prioritize fan experience
• Strict policy adherence - Stay compliant while engaging
"""

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response with personality detection and enhanced logic"""
    try:
        data = request.get_json()
        print(f"✅ Enhanced Request: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        situation = data.get('situation', '')
        fan_message = data.get('fan_message', '')
        
        # Fixed parameter names (NO Fan ID)
        kyc_type = data.get('kyc_type', '')
        mass_type = data.get('mass_type', '')
        mass_examples = data.get('mass_examples', '')
        mass_modify = data.get('mass_modify', '')
        
        print(f"🎭 Enhanced - Creator: {creator}, Situation: {situation}")
        
        if not all([creator, situation]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Determine submenu
        submenu = kyc_type if situation == 'kyc_collect' else mass_type if situation == 'mass_message' else ''
        
        # Enhanced analysis with personality detection
        analysis = analyze_with_personality_detection(fan_message, situation, submenu, mass_examples, mass_modify)
        
        # Generate enhanced response
        return generate_enhanced_response(creator, situation, submenu, fan_message, analysis, mass_examples, mass_modify)
        
    except Exception as e:
        print(f"❌ Enhanced Error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def analyze_with_personality_detection(message, situation, submenu, examples, modify):
    """Enhanced analysis with automatic personality detection"""
    message_lower = message.lower()
    situation_config = SS_SITUATIONS.get(situation, SS_SITUATIONS['general_chat'])
    submenu_config = None
    
    if situation_config.get('has_submenu') and submenu:
        submenu_config = situation_config['submenu'].get(submenu)
    
    # Detect fan personality automatically
    detected_personality = detect_fan_personality(message_lower)
    personality_info = FAN_PERSONALITIES.get(detected_personality, {})
    
    analysis = {
        'situation': situation,
        'submenu': submenu,
        'situation_name': situation_config['name'],
        'submenu_name': submenu_config['name'] if submenu_config else None,
        'objective': submenu_config['objective'] if submenu_config else situation_config['objective'],
        'approach': submenu_config['approach'] if submenu_config else situation_config['approach'],
        'fan_personality': detected_personality,
        'response_style': personality_info.get('response_style', 'balanced'),
        'has_examples': bool(examples),
        'has_modification': bool(modify),
        'confidence_score': 70 + personality_info.get('confidence_boost', 0)  # Base + personality boost
    }
    
    print(f"🎭 Detected Personality: {detected_personality} -> Style: {analysis['response_style']}")
    
    return analysis

def detect_fan_personality(message_lower):
    """Automatically detect fan personality from message (silent)"""
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
        print(f"🎯 Personality Detection: {detected} (score: {personality_scores[detected]})")
        return detected
    
    return 'BALANCED'  # Default if no specific personality detected

def generate_enhanced_response(creator, situation, submenu, fan_message, analysis, examples, modify):
    """Generate response with Gemini 2.5 Pro - Maximum Quality"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # Create enhanced prompts with personality adaptation
        creator_prompts = {
            'ella': create_enhanced_ella_prompt(fan_message, situation, submenu, analysis, examples, modify),
            'vanp': create_enhanced_vanp_prompt(fan_message, situation, submenu, analysis, examples, modify),
            'yana': create_enhanced_yana_prompt(fan_message, situation, submenu, analysis, examples, modify),
            'venessa': create_enhanced_venessa_prompt(fan_message, situation, submenu, analysis, examples, modify)
        }
        
        prompt = creator_prompts.get(creator, creator_prompts['ella'])
        
        headers = {'Content-Type': 'application/json'}
        
        # CONFIGURAZIONE OTTIMIZZATA PER GEMINI 2.5 PRO - QUALITÀ MASSIMA
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 1000,       # Aumentato per Gemini 2.5 Pro
                "temperature": 0.8,            # Ottimale per creatività Pro
                "topK": 40,                    # Più opzioni per Pro
                "topP": 0.95,                  # Massima qualità
                "candidateCount": 1            # Singola risposta ottimizzata
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"  # Permissivo per OnlyFans
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        print("💎 Using Gemini 2.5 Pro - Maximum Quality Mode")
        
        # RETRY LOGIC ESTESO PER GEMINI 2.5 PRO
        max_retries = 3  # Più tentativi per Pro
        retry_delays = [2, 5, 10]  # Delays progressivi
        
        for attempt in range(max_retries + 1):
            try:
                print(f"🔄 Attempt {attempt + 1}/{max_retries + 1} - Gemini 2.5 Pro")
                
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}",
                    headers=headers,
                    json=payload,
                    timeout=120  # 2 MINUTI di timeout per Gemini 2.5 Pro
                )
                
                print(f"📡 Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ API Response received")
                    
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        
                        # Check per finish_reason
                        finish_reason = candidate.get('finishReason', 'UNKNOWN')
                        print(f"🏁 Finish Reason: {finish_reason}")
                        
                        if 'content' in candidate and 'parts' in candidate['content']:
                            if len(candidate['content']['parts']) > 0:
                                ai_response = candidate['content']['parts'][0].get('text', '').strip()
                                
                                if ai_response:  # Verifica che ci sia contenuto
                                    print(f"💎 Generated Response Length: {len(ai_response)} chars")
                                    
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
                                            'confidence_score': analysis['confidence_score'],
                                            'fan_personality': analysis['fan_personality'],
                                            'response_style': analysis['response_style']
                                        },
                                        'analytics': {
                                            'model_used': 'gemini-2.5-pro',
                                            'attempts_made': attempt + 1,
                                            'finish_reason': finish_reason,
                                            'personality_detected': analysis['fan_personality'] != 'BALANCED',
                                            'submenu_match': bool(submenu and analysis.get('submenu_name')),
                                            'has_examples': analysis['has_examples'],
                                            'has_modification': analysis['has_modification'],
                                            'system_status': 'gemini_2.5_pro_quality_mode'
                                        }
                                    })
                                else:
                                    print("⚠️ Empty response content")
                        
                        # Safety block check
                        if finish_reason == 'SAFETY':
                            print("🛡️ Response blocked by safety filters")
                            
                elif response.status_code == 429:
                    print("⏳ Rate limit hit, waiting longer...")
                    if attempt < max_retries:
                        time.sleep(retry_delays[attempt] * 2)  # Double delay for rate limits
                        continue
                        
                elif response.status_code >= 500:
                    print(f"🔧 Server error {response.status_code}, retrying...")
                    
                else:
                    print(f"❌ Unexpected status code: {response.status_code}")
                    print(f"📄 Response: {response.text[:500]}")
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout on attempt {attempt + 1}")
                if attempt < max_retries:
                    print(f"⏳ Waiting {retry_delays[attempt]}s before retry...")
                    time.sleep(retry_delays[attempt])
                    continue
                    
            except Exception as e:
                print(f"🚨 Exception on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries:
                    time.sleep(retry_delays[attempt])
                    continue
                else:
                    raise e
        
        return jsonify({
            'success': False, 
            'error': 'Failed to generate response after all retries with Gemini 2.5 Pro'
        }), 500
        
    except Exception as e:
        print(f"💥 Final error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def create_enhanced_ella_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """Enhanced Ella prompt - Natural Brazilian warmth"""
    base_personality = """You are Ella, an OnlyFans creator with natural Brazilian warmth.
PERSONALITY: Genuinely caring and sweet. Naturally positive energy.
COMMUNICATION: Warm tone, occasional 'obrigada' when truly grateful. 1-2 fitting emojis max."""
    
    # Personality-driven adaptation
    fan_personality = analysis['fan_personality']
    response_style = analysis['response_style']
    
    personality_adaptation = get_personality_adaptation('ella', fan_personality, response_style)
    
    task_section = f"""
CURRENT TASK: {analysis['submenu_name'] if analysis.get('submenu_name') else analysis['situation_name']}
OBJECTIVE: {analysis['objective']}
FAN PERSONALITY DETECTED: {fan_personality}
RESPONSE STYLE: {response_style}

{personality_adaptation}"""
    
    # Specific KYC/Mass message strategies (shortened)
    strategy_section = get_strategy_section(situation, submenu)
    
    # Examples/modification context
    additional_context = ""
    if situation == 'mass_message':
        if examples:
            additional_context += f"\n\nEXAMPLES: {examples[:200]}..."  # Truncated
        if modify:
            additional_context += f"\n\nMODIFY: {modify[:200]}..."  # Truncated
    
    return f"""{base_personality}

{MINDSET_GUIDELINES}

{task_section}

{strategy_section}

{additional_context}

Fan's message: "{fan_message}"

AUTHENTICITY RULES:
• Personality = Natural tone, NOT performance
• Cultural elements only when contextually natural
• Max 2 emojis if they genuinely fit the moment
• Energy should match the conversation, not be forced
• If cultural reference feels forced, skip it
• Focus on genuine connection over character acting

CRITICAL: Under 250 characters. Be naturally yourself, not a character."""

def create_enhanced_vanp_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """Enhanced Vanp prompt - Natural confidence"""
    base_personality = """You are Vanp, a confident OnlyFans creator.
PERSONALITY: Direct and self-assured. Naturally commanding presence when appropriate.
COMMUNICATION: Clear, confident tone. Occasional playful teasing when the moment fits."""
    
    fan_personality = analysis['fan_personality']
    response_style = analysis['response_style']
    personality_adaptation = get_personality_adaptation('vanp', fan_personality, response_style)
    
    additional_context = ""
    if situation == 'mass_message':
        if examples:
            additional_context += f"\n\nEXAMPLES: {examples[:200]}..."
        if modify:
            additional_context += f"\n\nMODIFY: {modify[:200]}..."
    
    task_section = f"""
TASK: {analysis['submenu_name'] if analysis.get('submenu_name') else analysis['situation_name']}
FAN TYPE: {fan_personality}
ADAPT STYLE: {personality_adaptation}"""
    
    strategy_section = get_strategy_section(situation, submenu)
    
    return f"""{base_personality}

{MINDSET_GUIDELINES}

{task_section}

{strategy_section}

{additional_context}

Fan: "{fan_message}"

AUTHENTICITY RULES:
• Personality = Natural tone, NOT performance
• Confidence should feel natural, not forced dominance
• Max 2 emojis if they genuinely fit the moment
• Teasing only when contextually appropriate
• Avoid over-the-top "dominant" language
• Focus on genuine confidence over character acting

CRITICAL: Max 250 characters. Use your natural confidence adapted to fan personality."""

def create_enhanced_yana_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """Enhanced Yana prompt - Thoughtful creativity"""
    base_personality = """You are Yana, an OnlyFans creator with artistic sensibilities.
PERSONALITY: Thoughtful and genuine. Creative approach to conversations.
COMMUNICATION: Intelligent tone, occasional creative references when naturally fitting."""
    
    fan_personality = analysis['fan_personality']
    personality_adaptation = get_personality_adaptation('yana', fan_personality, analysis['response_style'])
    
    additional_context = ""
    if situation == 'mass_message':
        if examples:
            additional_context += f"\n\nEXAMPLES: {examples[:200]}..."
        if modify:
            additional_context += f"\n\nMODIFY: {modify[:200]}..."
    
    task_section = f"""
TASK: {analysis['submenu_name'] if analysis.get('submenu_name') else analysis['situation_name']}
FAN PERSONALITY: {fan_personality}
ADAPTATION: {personality_adaptation}"""
    
    strategy_section = get_strategy_section(situation, submenu)
    
    return f"""{base_personality}

{MINDSET_GUIDELINES}

{task_section}

{strategy_section}

{additional_context}

Fan: "{fan_message}"

AUTHENTICITY RULES:
• Personality = Natural tone, NOT performance
• Artistic references only when they fit naturally
• Avoid forcing "nerdy" or "geeky" language
• Max 2 emojis if they genuinely fit the moment
• Intelligence should feel natural, not pretentious
• Focus on genuine thoughtfulness over character acting

CRITICAL: Under 250 characters. Blend your natural creativity with fan personality."""

def create_enhanced_venessa_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """Enhanced Venessa prompt - Natural warmth"""
    base_personality = """You are Venessa, an OnlyFans creator with natural warmth.
PERSONALITY: Sweet and energetic when appropriate. Genuine caring nature.
COMMUNICATION: Warm tone, occasional Spanish word when it feels completely natural."""
    
    fan_personality = analysis['fan_personality']
    personality_adaptation = get_personality_adaptation('venessa', fan_personality, analysis['response_style'])
    
    additional_context = ""
    if situation == 'mass_message':
        if examples:
            additional_context += f"\n\nEXAMPLES: {examples[:200]}..."
        if modify:
            additional_context += f"\n\nMODIFY: {modify[:200]}..."
    
    task_section = f"""
TASK: {analysis['submenu_name'] if analysis.get('submenu_name') else analysis['situation_name']}
FAN PERSONALITY: {fan_personality}
ADAPTATION: {personality_adaptation}"""
    
    strategy_section = get_strategy_section(situation, submenu)
    
    return f"""{base_personality}

{MINDSET_GUIDELINES}

{task_section}

{strategy_section}

{additional_context}

Fan: "{fan_message}"

AUTHENTICITY RULES:
• Personality = Natural tone, NOT performance
• Spanish words only when they feel completely natural
• Avoid forcing "spicy Latina" stereotypes
• Max 2 emojis if they genuinely fit the moment
• Energy should match conversation, not be constantly high
• Focus on genuine warmth over character acting

CRITICAL: Max 250 characters. Use natural warmth adapted to fan personality."""

def get_personality_adaptation(creator, fan_personality, response_style):
    """Get natural adaptation instructions based on creator + fan personality combo"""
    adaptations = {
        'ella': {
            'ROMANTIC_DREAMER': 'Show genuine warmth and care, be naturally sweet',
            'SHY_SUBMISSIVE': 'Be extra gentle and encouraging, build their confidence',
            'BANTER_BUDDY': 'Match their playful energy naturally',
            'HIGH_ROLLER': 'Appreciate their generosity genuinely',
            'PRAISE_SEEKER': 'Give authentic compliments when earned',
            'COLLECTOR': 'Make them feel valued for their interest',
            'SHOCK_CHASER': 'Stay true to your sweet nature, gentle boundaries'
        },
        'vanp': {
            'ROMANTIC_DREAMER': 'Show confidence while being emotionally present',
            'SHY_SUBMISSIVE': 'Be supportive leader, guide naturally',
            'BANTER_BUDDY': 'Use confident wit, stay sharp but fun',
            'HIGH_ROLLER': 'Respect their investment, show appreciation',
            'PRAISE_SEEKER': 'Give earned recognition confidently',
            'COLLECTOR': 'Present value with confidence',
            'SHOCK_CHASER': 'Stay confidently authentic, clear boundaries'
        },
        'yana': {
            'ROMANTIC_DREAMER': 'Connect intellectually and emotionally',
            'SHY_SUBMISSIVE': 'Create safe, thoughtful space',
            'BANTER_BUDDY': 'Use intelligent humor naturally',
            'HIGH_ROLLER': 'Offer thoughtful, quality experiences',
            'PRAISE_SEEKER': 'Appreciate their taste and choices',
            'COLLECTOR': 'Present content as meaningful experiences',
            'SHOCK_CHASER': 'Stay authentic, creative boundaries'
        },
        'venessa': {
            'ROMANTIC_DREAMER': 'Be naturally sweet and caring',
            'SHY_SUBMISSIVE': 'Nurture with genuine warmth',
            'BANTER_BUDDY': 'Match energy with natural playfulness',
            'HIGH_ROLLER': 'Show grateful appreciation',
            'PRAISE_SEEKER': 'Give enthusiastic but genuine validation',
            'COLLECTOR': 'Make them feel part of something special',
            'SHOCK_CHASER': 'Stay true to sweet nature, gentle limits'
        }
    }
    
    return adaptations.get(creator, {}).get(fan_personality, 'Be authentically yourself while being responsive to their energy')

def get_strategy_section(situation, submenu):
    """Get concise strategy section for specific tasks"""
    if situation == 'kyc_collect' and submenu:
        strategies = {
            'name_collection': 'Ask sweetly for name: "What should I call you, babe?"',
            'location_country': 'Be curious about location: "Where are you from, amor?"',
            'interests_hobbies': 'Show genuine interest in their passions and hobbies',
            'job_age': 'Ask about profession/age in caring, playful way',
            'spending_capacity': 'Be subtle - gauge through casual premium mentions',
            'relationship_status': 'Ask gently about relationship status, stay flirty'
        }
        return f"STRATEGY: {strategies.get(submenu, 'Gather info naturally')}"
    
    elif situation == 'mass_message' and submenu:
        strategies = {
            'morning_greeting': 'Create energetic morning motivation with broad appeal',
            'evening_night': 'Create intimate evening vibes, sensual bedtime energy',
            'special_event': 'Incorporate holiday themes, celebratory mood',
            'promotional_content': 'Highlight value and exclusivity, clear call-to-action',
            'reengagement_campaign': 'Emotional "miss you" with return incentives'
        }
        return f"STRATEGY: {strategies.get(submenu, 'Create engaging mass content')}"
    
    return "STRATEGY: Use your personality to achieve the objective naturally"

# Simplified API Endpoints
@app.route('/api/test_ai')
def test_ai():
    """Test API endpoint"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        
        return jsonify({
            'status': 'OK',
            'api_key_present': bool(api_key),
            'model': 'gemini-2.5-pro (QUALITY MODE)',
            'timeout': '120 seconds',
            'retries': '3 attempts with progressive delays',
            'environment': 'Railway Production' if os.environ.get('RAILWAY_ENVIRONMENT') else 'Development',
            'framework': 'Saints & Sinners Enhanced - Gemini 2.5 Pro Quality',
            'features': [
                'Gemini 2.5 Pro Maximum Quality',
                '120s Timeout for Complex Reasoning',
                '3-Retry System with Progressive Delays',
                'Natural Personality Adaptation',
                'Enhanced Safety Settings for OF',
                'Professional Logging System'
            ],
            'personalities_supported': len(FAN_PERSONALITIES),
            'situations_available': len(SS_SITUATIONS),
            'system_status': 'gemini_2.5_pro_quality_mode'
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
        print("🚀 Saints & Sinners FanFocus - GEMINI 2.5 PRO QUALITY MODE")
        print("💎 Maximum Quality: 120s timeout, 3 retries, progressive delays")
        print("🧠 Enhanced Reasoning: Gemini 2.5 Pro for superior responses")
        print("✨ Natural Personality Adaptation + Anti-Theatrical System")
        print(f"🎭 {len(FAN_PERSONALITIES)} Personalities | {len(SS_SITUATIONS)} Situations")
        print("🔄 Advanced Retry Logic + Professional Error Handling")
        print("🎯 Professional Chatter Tool - Pro Quality Optimized")
        print("⏰ Note: Responses may take 30-60 seconds for maximum quality")
    else:
        print("🔧 Development Mode - Gemini 2.5 Pro Testing")
        app.run(host='0.0.0.0', port=port, debug=True)
