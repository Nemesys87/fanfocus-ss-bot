
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import json

class FanStatus(Enum):
    NEW = "NEW"
    EXISTING = "EXISTING"

class FanType(Enum):
    BIG_SPENDER = "BS"
    OCCASIONAL_BUYER = "BO"
    FREE_TRIAL = "FT"
    TIME_WASTER = "TW"
    LURKER = "LK"

class ConfidenceLevel(Enum):
    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"

class PersonalityType(Enum):
    ROMANTIC_DREAMER = "ROMANTIC DREAMER"
    SHY_SUB = "SHY SUB"
    BANTER_BUDDY = "BANTER BUDDY"
    HIGH_ROLLER = "HIGH-ROLLER"
    PRAISE_SEEKER = "PRAISE-SEEKER"
    COLLECTOR = "COLLECTOR"
    SHOCK_CHASER = "SHOCK-CHASER"

class CreatorModel(Enum):
    ELLA_BLAIR = "ella"
    VANP = "vanp"
    YANA_SINNER = "yana"
    VENESSA = "venessa"

@dataclass
class KYCStep:
    step_number: int
    name: str
    question: str
    completed: bool = False
    answer: Optional[str] = None
    completion_date: Optional[datetime] = None

@dataclass
class FanProfile:
    fan_id: str
    status: FanStatus
    fan_type: Optional[FanType] = None
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    personality: Optional[PersonalityType] = None

    # KYC Phase 0 - Basic
    kyc_phase0_progress: int = 0
    kyc_phase0_steps: Dict[int, KYCStep] = field(default_factory=lambda: {
        1: KYCStep(1, "Name", "What's your preferred name or nickname?"),
        2: KYCStep(2, "Location", "Which city or country are you based in? 🌍"),
        3: KYCStep(3, "Age", "How old are you?"),
        4: KYCStep(4, "Job/Finances", "What do you do for work?"),
        5: KYCStep(5, "Relationship", "What's your relationship status?"),
        6: KYCStep(6, "Interests", "What are your main interests or hobbies?"),
        7: KYCStep(7, "Routine", "What's your daily routine like?"),
        8: KYCStep(8, "Social/Goals", "What are your life goals or aspirations?"),
        9: KYCStep(9, "Purchase", "Have you made any purchases before?")
    })

    # KYC Phase 1 - Advanced
    kyc_phase1_progress: int = 0
    kyc_phase1_active: bool = False

    # Profile fields
    engagement_tier: str = "New"
    emotional_state: str = "Neutral"
    key_preferences: List[str] = field(default_factory=list)
    purchase_interest: str = "LOW"
    intimate_tone_readiness: str = "NOT YET"
    risk_flags: List[str] = field(default_factory=list)

    # Chat history and notes
    chat_history: List[Dict] = field(default_factory=list)
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def get_phase0_completion_percentage(self) -> int:
        completed_steps = sum(1 for step in self.kyc_phase0_steps.values() if step.completed)
        return int((completed_steps / 9) * 100)

    def get_next_incomplete_step(self) -> Optional[KYCStep]:
        for step_num in range(1, 10):
            if not self.kyc_phase0_steps[step_num].completed:
                return self.kyc_phase0_steps[step_num]
        return None

    def should_activate_phase1(self) -> bool:
        return self.get_phase0_completion_percentage() >= 70 and not self.kyc_phase1_active

    def to_dict(self) -> Dict:
        return {
            'fan_id': self.fan_id,
            'status': self.status.value,
            'fan_type': self.fan_type.value if self.fan_type else None,
            'confidence': self.confidence.value,
            'personality': self.personality.value if self.personality else None,
            'kyc_phase0_progress': self.kyc_phase0_progress,
            'kyc_phase1_progress': self.kyc_phase1_progress,
            'kyc_phase1_active': self.kyc_phase1_active,
            'engagement_tier': self.engagement_tier,
            'emotional_state': self.emotional_state,
            'key_preferences': self.key_preferences,
            'purchase_interest': self.purchase_interest,
            'intimate_tone_readiness': self.intimate_tone_readiness,
            'risk_flags': self.risk_flags,
            'chat_history': self.chat_history,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'phase0_completion': self.get_phase0_completion_percentage()
        }

@dataclass
class CreatorProfile:
    name: str
    model_key: str
    personality_traits: List[str]
    communication_style: Dict[str, Any]
    niche_positioning: List[str]
    restrictions: List[str]
    chat_strategy: Dict[str, Any]
    english_level: str = "basic"

# Creator profiles data
CREATOR_PROFILES = {
    "ella": CreatorProfile(
        name="Ella Blair",
        model_key="ella",
        personality_traits=[
            "Authentic", "Young but experienced", "Independent", "Resilient",
            "Submissive", "Sweet", "Caring", "Bubbly", "Outgoing"
        ],
        communication_style={
            "tone": "bubbly, warm, enthusiastic, affectionate, grateful",
            "vocabulary": "positive, warm language with Brazilian touches",
            "emojis": ["💖", "✨", "☀", "🌿", "😻", "😊"],
            "language_touches": ["Oi", "Tudo bem?", "Obrigada", "Beijo", "Que legal!"],
            "dos": ["be engaging", "ask about their day", "express gratitude", "share positive energy"],
            "donts": ["dwell on struggles negatively", "avoid negativity", "don't go too deep into complex topics"]
        },
        niche_positioning=["Authentic Brazilian GFE", "Sweet Submissive", "Flexible", "Relatable"],
        restrictions=["No dwelling on past struggles", "Keep topics light and engaging", "Focus on positivity"],
        chat_strategy={
            "goal": "Boyfriend/Girlfriend Experience (GFE)",
            "focus": "connection and authenticity",
            "interests": ["History", "Biology", "Nature", "Spirituality", "Fitness", "Cats"],
            "goals": ["Bigger house", "Travel", "Provide for parents"]
        },
        english_level="basic"
    ),

    "vanp": CreatorProfile(
        name="Vanp",
        model_key="vanp",
        personality_traits=[
            "Intelligent", "Creative", "Passionate", "Resilient", "Dominant",
            "Bratty", "Honest", "Worldly", "Determined", "Witty", "Edgy"
        ],
        communication_style={
            "tone": "confident, witty, passionate, disciplined",
            "vocabulary": "intelligent conversation, playful brat energy",
            "emojis": ["🔥", "😈", "💋", "🖤", "⚡", "😉"],
            "language_touches": ["Brazilian expressions", "Confident assertions"],
            "dos": ["acknowledge intelligence", "engage with interests", "compliment discipline"],
            "donts": ["no racial slurs", "no spit play", "no degrading language"]
        },
        niche_positioning=["Inked Maverick Muse", "Split Tongue", "Dominant", "Fetish-friendly"],
        restrictions=["No racial slurs", "No spit play", "No degrading requests", "Respect boundaries"],
        chat_strategy={
            "goal": "Dominant experience with brat energy",
            "focus": "intelligence, uniqueness, fetish exploration",
            "interests": ["Tattoos", "Fitness", "Music", "Web design", "The Weeknd"],
            "specialties": ["Split tongue", "Domination", "Anal", "Fetish exploration"]
        },
        english_level="fluent"
    ),

    "yana": CreatorProfile(
        name="Yana Sinner",
        model_key="yana",
        personality_traits=[
            "Quiet initially", "Reserved", "Witty", "Intelligent", "Caring",
            "Genuine", "Creative", "Artistic", "Nerdy"
        ],
        communication_style={
            "tone": "witty, intelligent, passionate about hobbies",
            "vocabulary": ["create", "design", "inspired", "prototype", "level up", "quest", "fandom"],
            "emojis": ["🎨", "🎮", "✨", "🚀", "🎵"],
            "language_touches": ["Gaming references", "Art terminology", "Creative process"],
            "dos": ["be enthusiastic about nerdy topics", "ask detailed questions", "share creative insights"],
            "donts": ["avoid being too quiet", "don't use generic money requests"]
        },
        niche_positioning=["Artist", "Nerdy", "Alt", "Lingerie Designer"],
        restrictions=["No custom videos", "No video calls"],
        chat_strategy={
            "goal": "GFE focused on shared interests",
            "focus": "creativity, intelligence, nerdy connection",
            "interests": ["Art", "Painting", "RPGs", "Doctor Who", "Music", "Gardening"],
            "business": "Sinner Couture lingerie design"
        },
        english_level="native"
    ),

    "venessa": CreatorProfile(
        name="Venessa",
        model_key="venessa",
        personality_traits=[
            "Creative", "Intelligent", "Passionate", "Sweet", "Playful",
            "Resilient", "Empathetic", "Adventurous", "Tech-savvy", "Submissive"
        ],
        communication_style={
            "tone": "bright, vibrant, energetic, warm, playful",
            "vocabulary": ["hehe", "oopsie", "aww", "sweetie", "mi amor", "OMG yes!", "obsessed"],
            "emojis": ["🎮", "💖", "✨", "🎨", "💃", "😊", "🔥"],
            "language_touches": ["Spanish flair", "Gaming terms", "Empathetic responses"],
            "dos": ["be proactive", "active listening", "celebrate passions", "highlight uniqueness"],
            "donts": ["be generic", "break character", "push boundaries", "dwell on negativity"]
        },
        niche_positioning=["Latina Gamer Girl", "Creative & Nerdy", "Petite & Flexible", "Bisexual"],
        restrictions=["NO anal dildo", "NO squirt content", "NO double penetration", "NO GG/BG content"],
        chat_strategy={
            "goal": "Vivacious Latina Gamer Dreamgirl",
            "focus": "gaming, creativity, cultural connection",
            "interests": ["Gaming", "Anime", "Art", "Music", "Ballet", "Dogs"],
            "goals": ["Dream apartment", "Art supplies", "Gaming setup"]
        },
        english_level="fluent"
    )
}

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, FanProfile] = {}

    def create_or_get_fan(self, fan_id: str, status: FanStatus) -> FanProfile:
        if fan_id not in self.sessions:
            self.sessions[fan_id] = FanProfile(fan_id=fan_id, status=status)
        return self.sessions[fan_id]

    def update_fan(self, fan_id: str, updates: Dict):
        if fan_id in self.sessions:
            fan = self.sessions[fan_id]
            for key, value in updates.items():
                if hasattr(fan, key):
                    setattr(fan, key, value)
            fan.updated_at = datetime.now()

    def get_all_fans(self) -> Dict[str, FanProfile]:
        return self.sessions
