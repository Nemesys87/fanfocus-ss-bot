"""
FanFocusGPT Prompt Generation System
Integrates Saints & Sinners Framework with Creator Profiles
"""

class PromptGenerator:
    def __init__(self):
        self.fanfocus_system_prompt = """
You are FanFocusGPT, an AI assistant that helps chatters respond to OnlyFans messages.

MISSION: Generate ONE compliant reply (≤250 chars) that:
1. Collects KYC data in strict order
2. Updates fan profile  
3. Matches creator personality

KYC ORDER (Phase 0):
1. Name 2. Location 3. Age 4. Job 5. Relationship 6. Interests 7. Routine 8. Social 9. Purchase

REPLY FORMAT:
(YES|ALMOST|NOT YET)|<Personality>| <reply text>

Always be authentic, warm, and follow creator personality traits.
"""

    def generate_system_prompt(self, creator_profile, fan_profile):
        return f"""
{self.fanfocus_system_prompt}

CREATOR: {creator_profile.name}
Personality: {creator_profile.personality_traits}
Style: {creator_profile.communication_style}
Niche: {creator_profile.niche_positioning}
Restrictions: {creator_profile.restrictions}

FAN PROFILE:
Status: {fan_profile.fan_status}
Type: {fan_profile.fan_type}
Confidence: {fan_profile.confidence_level}
KYC Progress: {fan_profile.get_kyc_progress()}
"""

    def generate_user_prompt(self, fan_message, fan_profile, creator_profile):
        return f"""
Fan says: "{fan_message}"

Current KYC step: {fan_profile.current_kyc_step}
Generate appropriate response following creator personality.
"""

class SSFrameworkEngine:
    def classify_fan_type(self, fan_profile):
        # Implement S&S fan classification logic
        if fan_profile.purchase_indicators == "HIGH":
            return "BS"  # Big Spender
        elif fan_profile.purchase_indicators == "MEDIUM":
            return "BO"  # Occasional Buyer
        else:
            return "FT"  # Free Trial
    
    def get_upselling_suggestions(self, fan_type, creator_profile):
        suggestions = {
            "BS": f"VIP content for {creator_profile.name}",
            "BO": "Limited time offer",
            "FT": "First-time buyer discount"
        }
        return suggestions.get(fan_type, "General engagement")
