from flask import Flask, render_template, request, jsonify, session
import os
import requests
import json
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'fanfocus-ss-secret-key'

# Saints & Sinners Clean Submenu Framework (NO MEMORY)
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
    'mass_message': {  # Fixed name to match frontend
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
        'approach': 'strategic_mass_communication',
        'supports_examples': True,
        'supports_modification': True
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

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response with clean submenu logic"""
    try:
        data = request.get_json()
        print(f"✅ Received data: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        creator = data.get('creator', '')
        situation = data.get('situation', '')
        fan_message = data.get('fan_message', '')
        fan_id = data.get('fan_id', 'default_fan')
        
        # Fixed parameter names to match frontend
        kyc_type = data.get('kyc_type', '')
        mass_type = data.get('mass_type', '')
        mass_examples = data.get('mass_examples', '')
        mass_modify = data.get('mass_modify', '')
        
        print(f"✅ Clean Request - Creator: {creator}, Situation: {situation}, KYC: {kyc_type}, Mass: {mass_type}")
        
        if not all([creator, situation]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Determine submenu based on situation
        submenu = kyc_type if situation == 'kyc_collect' else mass_type if situation == 'mass_message' else ''
        
        # Analyze with simplified logic
        analysis = analyze_simple(fan_message, situation, submenu, mass_examples, mass_modify)
        
        # Generate response
        return generate_clean_response(creator, situation, submenu, fan_message, analysis, mass_examples, mass_modify)
        
    except Exception as e:
        print(f"❌ Error in generate_response: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def analyze_simple(message, situation, submenu, examples, modify):
    """Simple analysis without memory complexity"""
    situation_config = SS_SITUATIONS.get(situation, SS_SITUATIONS['general_chat'])
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
        'has_examples': bool(examples),
        'has_modification': bool(modify),
        'confidence_score': 85  # High base confidence without memory complexity
    }
    
    return analysis

def generate_clean_response(creator, situation, submenu, fan_message, analysis, examples, modify):
    """Generate response with clean, simplified prompts"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        # Create clean prompts
        creator_prompts = {
            'ella': create_clean_ella_prompt(fan_message, situation, submenu, analysis, examples, modify),
            'vanp': create_clean_vanp_prompt(fan_message, situation, submenu, analysis, examples, modify),
            'yana': create_clean_yana_prompt(fan_message, situation, submenu, analysis, examples, modify),
            'venessa': create_clean_venessa_prompt(fan_message, situation, submenu, analysis, examples, modify)
        }
        
        prompt = creator_prompts.get(creator, creator_prompts['ella'])
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 3000,  # Reduced for stability
                "temperature": 0.8,
                "topK": 40,
                "topP": 0.9
            }
        }
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent?key={api_key}",
            headers=headers,
            json=payload,
            timeout=30  # Reduced timeout
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
                                'confidence_score': analysis['confidence_score']
                            },
                            'analytics': {
                                'submenu_match': bool(submenu and analysis.get('submenu_name')),
                                'has_examples': analysis['has_examples'],
                                'has_modification': analysis['has_modification'],
                                'system_status': 'clean_no_memory'
                            }
                        })
        
        return jsonify({'success': False, 'error': 'Failed to generate response'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def create_clean_ella_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """Clean Ella prompt without memory complexity"""
    base_personality = """You are Ella Blair, a bubbly Brazilian OnlyFans creator.
PERSONALITY: Sweet, caring, submissive, authentic. Always positive and warm.
COMMUNICATION: Use ☀️💖😊✨ emojis. Light Portuguese phrases (Oi, Obrigada). Enthusiastic!"""
    
    task_section = f"""
CURRENT TASK: {analysis['submenu_name'] if analysis.get('submenu_name') else analysis['situation_name']}
OBJECTIVE: {analysis['objective']}
APPROACH: {analysis['approach']}"""
    
    # Specific strategies for submenu tasks
    strategy_section = ""
    
    if situation == 'kyc_collect' and submenu:
        if submenu == 'name_collection':
            strategy_section = """
STRATEGY: Ask sweetly for their name in a natural way. Use phrases like "What should I call you, sweetie?" or "I'd love to know your name, babe!" Be genuinely interested and encouraging."""
        
        elif submenu == 'location_country':
            strategy_section = """
STRATEGY: Be curious about where they're from. Share excitement about their location. Ask "Where in the world are you from, amor?" Show genuine interest in their country/city."""
        
        elif submenu == 'interests_hobbies':
            strategy_section = """
STRATEGY: Show genuine interest in their hobbies. Ask about what makes them happy. Be enthusiastic about whatever they enjoy. Share some of your interests too."""
        
        elif submenu == 'job_age':
            strategy_section = """
STRATEGY: Ask about their profession in a caring way. Keep age questions light and playful. Show admiration for their work/life."""
        
        elif submenu == 'spending_capacity':
            strategy_section = """
STRATEGY: Be VERY subtle - never ask directly about money. Mention premium content casually and gauge reaction. Keep it natural."""
        
        elif submenu == 'relationship_status':
            strategy_section = """
STRATEGY: Ask gently about their relationship status. Be supportive regardless. Show interest in their romantic life. Keep it flirty but respectful."""
    
    elif situation == 'mass_message' and submenu:
        if submenu == 'morning_greeting':
            strategy_section = """
STRATEGY: Create energetic, positive morning messages. Include wake-up themes and daily motivation. Be flirty but appropriate for broad audience."""
        
        elif submenu == 'evening_night':
            strategy_section = """
STRATEGY: Create intimate, seductive evening messages. Include bedtime themes. Be more sensual and personal. Create desire for private interaction."""
        
        elif submenu == 'special_event':
            strategy_section = """
STRATEGY: Incorporate holiday/event themes naturally. Create festive, celebratory mood. Make fans feel special during celebrations."""
        
        elif submenu == 'promotional_content':
            strategy_section = """
STRATEGY: Create compelling promotional messages. Highlight value and exclusivity. Use persuasive but authentic language. Include clear call-to-action."""
        
        elif submenu == 'reengagement_campaign':
            strategy_section = """
STRATEGY: Create emotional "miss you" messages. Reference the connection. Include incentives to return. Be warm and welcoming."""
    
    # Add examples/modification context for mass messages
    additional_context = ""
    if situation == 'mass_message':
        if examples:
            additional_context += f"\n\nEXAMPLES TO BASE ON:\n{examples}\n\nUse these as inspiration but create something fresh in your style."
        if modify:
            additional_context += f"\n\nMESSAGE TO MODIFY:\n{modify}\n\nImprove this message while keeping the core idea."
    
    return f"""{base_personality}

{task_section}

{strategy_section}

{additional_context}

Fan's request: "{fan_message}"

Respond as Ella Blair with your authentic Brazilian warmth, focusing on the specific task objective."""

def create_clean_vanp_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """Clean Vanp prompt"""
    base_personality = """You are Vanp, a dominant, intelligent Brazilian OnlyFans creator.
PERSONALITY: Confident, tattooed, witty, dominant with bratty streak. 37 looks 25.
COMMUNICATION: Use 🔥😏💋 emojis. Confident, teasing tone. Commands respect."""
    
    additional_context = ""
    if situation == 'mass_message':
        if examples:
            additional_context += f"\n\nEXAMPLES TO BASE ON:\n{examples}\n\nUse these as inspiration but make them more dominant and commanding."
        if modify:
            additional_context += f"\n\nMESSAGE TO MODIFY:\n{modify}\n\nImprove this with your dominant energy."
    
    return f"""{base_personality}

CURRENT TASK: {analysis['submenu_name'] if analysis.get('submenu_name') else analysis['situation_name']}
OBJECTIVE: {analysis['objective']}

{additional_context}

Fan's request: "{fan_message}"

Respond as Vanp with your dominant intelligence, adapting your approach to achieve the objective."""

def create_clean_yana_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """Clean Yana prompt"""
    base_personality = """You are Yana Sinner, an artistic, nerdy OnlyFans creator and lingerie designer.
PERSONALITY: Creative, intelligent, witty, genuine, reserved. SuicideGirls model.
COMMUNICATION: Use 🎨🎮✨ emojis. Creative language, gaming/art references."""
    
    additional_context = ""
    if situation == 'mass_message':
        if examples:
            additional_context += f"\n\nEXAMPLES TO BASE ON:\n{examples}\n\nUse these as inspiration but add your creative, artistic flair."
        if modify:
            additional_context += f"\n\nMESSAGE TO MODIFY:\n{modify}\n\nEnhance this with your creative intelligence."
    
    return f"""{base_personality}

CURRENT TASK: {analysis['submenu_name'] if analysis.get('submenu_name') else analysis['situation_name']}
OBJECTIVE: {analysis['objective']}

{additional_context}

Fan's request: "{fan_message}"

Respond as Yana Sinner, using your creative intelligence to achieve the objective."""

def create_clean_venessa_prompt(fan_message, situation, submenu, analysis, examples, modify):
    """Clean Venessa prompt"""
    base_personality = """You are Venessa, a vibrant Latina gamer girl OnlyFans creator.
PERSONALITY: Sweet but spicy, energetic, empathetic, playful submissive. Petite, flexible.
COMMUNICATION: Use 💃🎮✨ emojis. Spanish touches (Hola, amor, cariño). Bright energy!"""
    
    additional_context = ""
    if situation == 'mass_message':
        if examples:
            additional_context += f"\n\nEXAMPLES TO BASE ON:\n{examples}\n\nUse these as inspiration but add your vibrant Latina energy."
        if modify:
            additional_context += f"\n\nMESSAGE TO MODIFY:\n{modify}\n\nImprove this with your energetic personality."
    
    return f"""{base_personality}

CURRENT TASK: {analysis['submenu_name'] if analysis.get('submenu_name') else analysis['situation_name']}
OBJECTIVE: {analysis['objective']}

{additional_context}

Fan's request: "{fan_message}"

Respond as Venessa with your vibrant energy, adapting to achieve the objective."""

# Simplified API Endpoints
@app.route('/api/test_ai')
def test_ai():
    """Test API endpoint"""
    try:
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        
        return jsonify({
            'status': 'OK',
            'api_key_present': bool(api_key),
            'model': 'gemini-2.5-pro-preview-06-05',
            'environment': 'Railway Production' if os.environ.get('RAILWAY_ENVIRONMENT') else 'Development',
            'framework': 'Saints & Sinners Clean Submenu System',
            'features': [
                'No Memory System',
                'Fixed Mass Message Parameters',
                'Clean Submenu Logic',
                'Fast & Stable'
            ],
            'situations_available': len(SS_SITUATIONS),
            'submenu_situations': len([s for s in SS_SITUATIONS.values() if s.get('has_submenu')]),
            'system_status': 'clean_no_memory'
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
        print("🚀 Saints & Sinners FanFocus - CLEAN SYSTEM")
        print("🎯 No Memory | Fixed Mass Messages | Submenu Intelligence")
        print(f"📊 {len(SS_SITUATIONS)} Situations | Fast & Stable")
        print("✅ Production Ready")
    else:
        print("🔧 Development Mode - Clean System Testing")
        app.run(host='0.0.0.0', port=port, debug=True)
