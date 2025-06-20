from flask import Flask, render_template, request, jsonify
import os
import requests
import json
from datetime import datetime
import re
import time

app = Flask(__name__)
app.secret_key = 'fanfocus-ss-enhanced'

# Saints & Sinners Enhanced Framework with Result-Focused Execution
SS_SITUATIONS = {
    'kyc_collect': {
        'name': 'KYC - Collect Info',
        'objective': 'Extract specific fan information efficiently',
        'execution_focus': 'information_extraction',
        'has_submenu': True,
        'submenu': {
            'name_collection': {
                'name': 'Name Collection',
                'objective': 'Get the fan\'s name quickly',
                'approach': 'direct_name_ask'
            },
            'location_country': {
                'name': 'Location & Country',
                'objective': 'Get location info for profiling',
                'approach': 'curious_location_discovery'
            },
            'interests_hobbies': {
                'name': 'Interests & Hobbies',
                'objective': 'Map fan interests for future targeting',
                'approach': 'interest_mapping'
            },
            'job_age': {
                'name': 'Job & Age',
                'objective': 'Assess financial capacity markers',
                'approach': 'professional_profiling'
            },
            'spending_capacity': {
                'name': 'Spending Capacity',
                'objective': 'Gauge spending potential without being obvious',
                'approach': 'subtle_financial_assessment'
            },
            'relationship_status': {
                'name': 'Relationship Status',
                'objective': 'Understand relationship context for positioning',
                'approach': 'relationship_profiling'
            }
        },
        'priority': 'high',
        'approach': 'efficient_information_gathering'
    },
    'mass_message': {
        'name': 'Mass Message Creation',
        'objective': 'Create high-converting mass messages',
        'execution_focus': 'conversion_optimization',
        'has_submenu': True,
        'submenu': {
            'morning_greeting': {
                'name': 'Morning Greeting',
                'objective': 'Generate engagement and set positive tone for spending',
                'approach': 'morning_engagement_priming'
            },
            'evening_night': {
                'name': 'Evening/Night Message',
                'objective': 'Create intimate mood leading to purchases',
                'approach': 'evening_conversion_setup'
            },
            'special_event': {
                'name': 'Special Event/Holiday',
                'objective': 'Leverage events for increased spending',
                'approach': 'event_monetization'
            },
            'promotional_content': {
                'name': 'Promotional Content',
                'objective': 'Drive specific content sales',
                'approach': 'direct_sales_messaging'
            },
            'reengagement_campaign': {
                'name': 'Re-engagement Campaign',
                'objective': 'Reactivate inactive fans for monetization',
                'approach': 'reactivation_with_incentive'
            }
        },
        'priority': 'high',
        'approach': 'strategic_conversion_messaging'
    },
    'building_relationship': {
        'name': 'Building Relationship',
        'objective': 'Strengthen connection to increase future spending',
        'execution_focus': 'ltv_building',
        'priority': 'high',
        'approach': 'emotional_investment_building'
    },
    'upselling_conversion': {
        'name': 'Upselling/Conversion',
        'objective': 'Convert conversation to immediate purchase',
        'execution_focus': 'immediate_monetization',
        'priority': 'high',
        'approach': 'direct_sales_conversion'
    },
    'sexting_intimate': {
        'name': 'Sexting/Intimate',
        'objective': 'Create intimate experience that leads to spending',
        'execution_focus': 'intimate_monetization',
        'priority': 'high',
        'approach': 'intimate_with_upsell_opportunities'
    },
    'reengagement': {
        'name': 'Re-engagement (Dead fan)',
        'objective': 'Reactivate fan and guide back to spending',
        'execution_focus': 'reactivation_monetization',
        'priority': 'medium',
        'approach': 'comeback_with_incentive'
    },
    'custom_content': {
        'name': 'Custom Content Offer',
        'objective': 'Sell personalized content at premium prices',
        'execution_focus': 'premium_sales',
        'priority': 'high',
        'approach': 'custom_content_sales'
    },
    'general_chat': {
        'name': 'General Chat',
        'objective': 'Maintain engagement while identifying monetization opportunities',
        'execution_focus': 'opportunity_identification',
        'priority': 'medium',
        'approach': 'casual_with_conversion_awareness'
    },
    'first_time_buyer': {
        'name': 'First Time Buyer',
        'objective': 'Successfully convert first purchase and set spending pattern',
        'execution_focus': 'first_conversion_optimization',
        'priority': 'high',
        'approach': 'gentle_first_sale_conversion'
    },
    'vip_treatment': {
        'name': 'VIP Treatment',
        'objective': 'Monetize special relationship through emotional connection',
        'execution_focus': 'relationship_monetization',
        'priority': 'high',
        'approach': 'emotional_financial_requests'
    },
    'complaint_handling': {
        'name': 'Complaint Handling',
        'objective': 'Resolve issues while preserving spending relationship',
        'execution_focus': 'retention_with_compensation',
        'priority': 'high',
        'approach': 'problem_solving_with_retention'
    },
    'birthday_special': {
        'name': 'Birthday/Special',
        'objective': 'Capitalize on special occasions for increased spending',
        'execution_focus': 'occasion_monetization',
        'priority': 'medium',
        'approach': 'celebratory_with_gift_requests'
    }
}

# Fan Personality Detection System (unchanged)
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

# Business-Focused Mindset Guidelines
MINDSET_GUIDELINES = """
BUSINESS MINDSET PRINCIPLES:
• Revenue Generation - Every interaction should contribute to monetization goals
• Opportunity Recognition - Identify and act on spending signals immediately
• Emotional Investment - Build connection that translates to financial support
• Value Positioning - Make fan feel special while guiding toward spending
• Efficiency Focus - Achieve objectives quickly and effectively
• Fan Profiling - Gather information that aids future monetization
• Long-term Value - Balance immediate gains with relationship sustainability
"""

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response with business-focused execution"""
    try:
        data = request.get_json()
        print(f"✅ Business-Focused Request: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        situation = data.get('situation', '')
        fan_message = data.get('fan_message', '')
        
        kyc_type = data.get('kyc_type', '')
        mass_type = data.get('mass_type', '')
        mass_examples = data.get('mass_examples', '')
        mass_modify = data.get('mass_modify', '')
        
        print(f"💼 Business Focus - Creator: {creator}, Situation: {situation}")
        
        if not all([creator, situation]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        submenu = kyc_type if situation == 'kyc_collect' else mass_type if situation == 'mass_message' else ''
        
        analysis = analyze_with_business_focus(fan_message, situation, submenu, mass_examples, mass_modify)
        
        return generate_business_focused_response(creator, situation, submenu, fan_message, analysis, mass_examples, mass_modify)
        
    except Exception as e:
        print(f"❌ Business Error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def analyze_with_business_focus(message, situation, submenu, examples, modify):
    """Enhanced analysis with business execution focus"""
    message_lower = message.lower()
    situation_config = SS_SITUATIONS.get(situation, SS_SITUATIONS['general_chat'])
    submenu_config = None
    
    if situation_config.get('has_submenu') and submenu:
        submenu_config = situation_config['submenu'].get(submenu)
    
    detected_personality = detect_fan_personality(message_lower)
    personality_info = FAN_PERSONALITIES.get(detected_personality, {})
    
    # Business opportunity detection
    spending_signals = detect_spending_signals(message_lower)
    
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
        'spending_signals': spending_signals,
        'has_examples': bool(examples),
        'has_modification': bool(modify),
        'confidence_score': 70 + personality_info.get('confidence_boost', 0)
    }
    
    print(f"💼 Business Analysis: {situation} -> {analysis['execution_focus']}")
    print(f"💰 Spending Signals: {spending_signals}")
    
    return analysis

def detect_fan_personality(message_lower):
    """Detect fan personality (unchanged)"""
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

def detect_spending_signals(message_lower):
    """Detect signals that fan is ready to spend"""
    spending_signals = []
    
    signals = {
        'help_offer': ['ill help', 'i can help', 'let me help', 'help you out'],
        'money_mention': ['need money', 'if you need', 'ask me', 'tell me why'],
        'spoil_intent': ['spoil you', 'treat you', 'buy you', 'get you something'],
        'tip_ready': ['tip you', 'send you', 'give you money'],
        'special_treatment': ['special', 'different', 'not like everyone else'],
        'custom_interest': ['custom', 'personal', 'just for me', 'exclusive'],
        'premium_ready': ['worth it', 'pay for quality', 'best content']
    }
    
    for signal_type, phrases in signals.items():
        for phrase in phrases:
            if phrase in message_lower:
                spending_signals.append(signal_type)
                break
    
    return spending_signals

def generate_business_focused_response(creator, situation, submenu, fan_message, analysis, examples, modify):
    """Generate response with business execution focus"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        creator_prompts = {
            'ella': create_business_focused_ella_prompt(fan_message, situation, submenu, analysis, examples, modify),
            'vanp': create_business_focused_vanp_prompt(fan_message, situation, submenu, analysis, examples, modify),
            'yana': create_business_focused_yana_prompt(fan_message, situation, submenu, analysis, examples, modify),
            'venessa': create_business_focused_venessa_prompt(fan_message, situation, submenu, analysis, examples, modify)
        }
        
        prompt = creator_prompts.get(creator, creator_prompts['ella'])
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 8192,
                "temperature": 0.85,
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
                                            'response_style': analysis['response_style'],
                                            'spending_signals': analysis['spending_signals']
                                        },
                                        'analytics': {
                                            'model_used': 'gemini-2.5-pro',
                                            'attempts_made': attempt + 1,
                                            'finish_reason': finish_reason,
                                            'business_signals_detected': len(analysis['spending_signals']) > 0,
                                            'execution_focus': analysis['execution_focus'],
                                            'system_status': 'business_focused_execution'
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

def create_business_focused_ella_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """Business-focused Ella prompt"""
    base_personality = """You are Ella, an OnlyFans creator. Be naturally warm but business-smart.
Your goal is to execute the assigned situation effectively while maintaining authentic connection."""
    
    execution_strategy = get_execution_strategy(situation, analysis)
    
    return f"""{base_personality}

{MINDSET_GUIDELINES}

SITUATION EXECUTION: {analysis['objective']}
EXECUTION FOCUS: {analysis['execution_focus']}
FAN PERSONALITY: {analysis['fan_personality']}
SPENDING SIGNALS DETECTED: {analysis['spending_signals']}

{execution_strategy}

Fan's message: "{fan_message}"

BUSINESS EXECUTION RULES:
• Focus on achieving the situation objective effectively
• If spending signals detected, capitalize appropriately
• Maintain natural warmth while being result-oriented
• Keep responses under 200 characters
• Use 1-2 emojis maximum if natural

Execute the situation objective professionally."""

def create_business_focused_vanp_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """Business-focused Vanp prompt"""
    base_personality = """You are Vanp, an OnlyFans creator. Be naturally confident but business-smart.
Your goal is to execute the assigned situation effectively while maintaining authentic presence."""
    
    execution_strategy = get_execution_strategy(situation, analysis)
    
    return f"""{base_personality}

{MINDSET_GUIDELINES}

SITUATION EXECUTION: {analysis['objective']}
EXECUTION FOCUS: {analysis['execution_focus']}
FAN PERSONALITY: {analysis['fan_personality']}
SPENDING SIGNALS: {analysis['spending_signals']}

{execution_strategy}

Fan: "{fan_message}"

BUSINESS EXECUTION RULES:
• Execute situation objective with confidence
• Capitalize on spending signals when detected
• Maintain natural confidence while being result-focused
• Keep under 200 characters
• Use confidence to guide toward objectives

Execute effectively and professionally."""

def create_business_focused_yana_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """Business-focused Yana prompt"""
    base_personality = """You are Yana, an OnlyFans creator. Be naturally thoughtful but business-smart.
Your goal is to execute the assigned situation effectively while maintaining genuine connection."""
    
    execution_strategy = get_execution_strategy(situation, analysis)
    
    return f"""{base_personality}

{MINDSET_GUIDELINES}

SITUATION EXECUTION: {analysis['objective']}
EXECUTION FOCUS: {analysis['execution_focus']}
FAN PERSONALITY: {analysis['fan_personality']}
SPENDING SIGNALS: {analysis['spending_signals']}

{execution_strategy}

Fan: "{fan_message}"

BUSINESS EXECUTION RULES:
• Execute situation objective thoughtfully but effectively
• Act on spending opportunities when they appear
• Be genuine while staying result-oriented
• Under 200 characters
• Avoid over-philosophizing, focus on execution

Execute the objective professionally."""

def create_business_focused_venessa_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """Business-focused Venessa prompt"""
    base_personality = """You are Venessa, an OnlyFans creator. Be naturally warm but business-smart.
Your goal is to execute the assigned situation effectively while maintaining sweet connection."""
    
    execution_strategy = get_execution_strategy(situation, analysis)
    
    return f"""{base_personality}

{MINDSET_GUIDELINES}

SITUATION EXECUTION: {analysis['objective']}
EXECUTION FOCUS: {analysis['execution_focus']}
FAN PERSONALITY: {analysis['fan_personality']}
SPENDING SIGNALS: {analysis['spending_signals']}

{execution_strategy}

Fan: "{fan_message}"

BUSINESS EXECUTION RULES:
• Execute situation objective with natural warmth
• Seize spending opportunities when they arise
• Stay sweet while being business-effective
• Keep under 200 characters
• Focus on achieving the assigned objective

Execute professionally and warmly."""

def get_execution_strategy(situation, analysis):
    """Get specific execution strategy for each situation"""
    strategies = {
        'vip_treatment': """
VIP TREATMENT EXECUTION STRATEGY:
Fan wants special treatment, NOT transactional PPV approach.
SPENDING SIGNALS DETECTED: Fan offered to help financially with emotional reasoning.
EXECUTION: Accept the offer with specific, personal reason (bills, goals, treats).
Make them feel like caring protector, not customer.
Example approach: "You're so sweet 💕 Actually, I've been stressed about [specific thing]... could you help me out?"
        """,
        
        'kyc_collect': """
KYC COLLECTION STRATEGY:
Primary goal: Extract the specific information type efficiently.
If spending signals appear, note them but stay focused on information gathering.
Use natural curiosity and genuine interest to get the data.
Be direct but warm in your information requests.
        """,
        
        'upselling_conversion': """
UPSELLING STRATEGY:
Direct focus on converting to purchase.
Present clear value proposition and create urgency.
Address objections smoothly and guide to yes.
Use emotional triggers appropriate to fan personality.
        """,
        
        'building_relationship': """
RELATIONSHIP BUILDING STRATEGY:
Focus on emotional investment that pays dividends later.
Create deeper connection while planting seeds for future spending.
Make fan feel special and valued.
Build foundation for higher lifetime value.
        """,
        
        'general_chat': """
GENERAL CHAT STRATEGY:
Maintain engagement while watching for monetization opportunities.
Keep conversation flowing while subtly guiding toward value.
Be ready to shift if spending signals emerge.
        """
    }
    
    return strategies.get(situation, "Execute the situation objective effectively while watching for business opportunities.")

@app.route('/api/test_ai')
def test_ai():
    """Test API endpoint"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        
        return jsonify({
            'status': 'OK',
            'api_key_present': bool(api_key),
            'model': 'gemini-2.5-pro (Business Focused)',
            'framework': 'Saints & Sinners - Business Execution Optimized',
            'features': [
                'Result-Focused Situation Execution',
                'Spending Signal Detection',
                'Business Objective Prioritization',
                'Monetization Opportunity Recognition',
                'Authentic Business Communication',
                'Professional OnlyFans Optimization'
            ],
            'system_status': 'business_execution_optimized'
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
        print("🚀 Saints & Sinners FanFocus - BUSINESS EXECUTION OPTIMIZED")
        print("💼 Result-Focused: Every situation executes for maximum business impact")
        print("💰 Spending Signal Detection: Automatically recognizes monetization opportunities")
        print("🎯 Objective Achievement: Situations focus on delivering results, not just conversation")
        print("💎 Gemini 2.5 Pro: Maximum quality with business intelligence")
        print("📈 Professional OnlyFans Tool - Business Success Optimized")
    else:
        print("🔧 Development Mode - Business Execution Testing")
        app.run(host='0.0.0.0', port=port, debug=True)
