# state_manager.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class DesignPhase(Enum):
    IDEATION = "ideation"
    DEVELOPMENT = "development"
    REFINEMENT = "refinement"
    EVALUATION = "evaluation"

@dataclass
class VisualArtifact:
    id: str
    type: str  # "sketch", "plan", "section", "detail"
    image_path: str
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    annotations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class StudentProfile:
    skill_level: str = "intermediate"  # "beginner", "intermediate", "advanced"
    learning_style: str = "visual"
    cognitive_load: float = 0.3  # 0-1 scale
    engagement_level: float = 0.7
    knowledge_gaps: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)

@dataclass
class ConversationContext:
    """Enhanced conversation context tracking for continuity"""
    current_topic: str = ""
    topic_history: List[str] = field(default_factory=list)
    ongoing_discussion: Dict[str, Any] = field(default_factory=dict)
    last_route_used: str = ""
    route_history: List[str] = field(default_factory=list)
    conversation_thread_id: str = ""
    thread_start_time: str = field(default_factory=lambda: datetime.now().isoformat())

    # Context persistence
    detected_building_type: str = ""
    building_type_confidence: float = 0.0
    design_phase_detected: str = ""
    phase_confidence: float = 0.0

    # Project-specific context
    project_type: str = ""  # e.g., "adaptive_reuse", "new_construction"
    existing_building_type: str = ""  # e.g., "warehouse", "factory" for adaptive reuse
    target_building_type: str = ""  # e.g., "community_center" for adaptive reuse
    project_details: List[str] = field(default_factory=list)  # e.g., ["elder_care", "accessibility_focused"]

    # Conversation flow tracking
    questions_asked: List[str] = field(default_factory=list)
    concepts_discussed: List[str] = field(default_factory=list)
    user_understanding_level: str = "unknown"
    engagement_patterns: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ArchMentorState:
    # Core conversation
    messages: List[Dict[str, str]] = field(default_factory=list)
    current_design_brief: str = ""
    design_phase: DesignPhase = DesignPhase.IDEATION

    # Enhanced conversation continuity
    conversation_context: ConversationContext = field(default_factory=ConversationContext)

    # Visual artifacts
    visual_artifacts: List[VisualArtifact] = field(default_factory=list)
    current_sketch: Optional[VisualArtifact] = None

    # Student modeling
    student_profile: StudentProfile = field(default_factory=StudentProfile)
    session_metrics: Dict[str, float] = field(default_factory=dict)

    # Agent coordination
    last_agent: str = ""
    next_agent: str = "analysis"
    agent_context: Dict[str, Any] = field(default_factory=dict)

    # Domain configuration
    domain: str = "architecture"
    domain_config: Dict[str, Any] = field(default_factory=dict)

    # Project context
    building_type: str = "unknown"  # No more mixed_use default - centrally managed

    # Phase progression context (from dashboard phase system)
    phase_info: Optional[Dict[str, Any]] = None

    # Debug and display settings
    show_response_summary: bool = True  # Toggle for response processing summary
    show_scientific_metrics: bool = False  # Toggle for scientific metrics in response


    # Conversation History Management
    def ensure_brief_in_messages(self) -> bool:
        """Enhanced to maintain conversation continuity"""
        if self.current_design_brief:
            # Check if brief exists as first message
            brief_exists = (self.messages and
                        self.messages[0].get("role") == "brief" and
                        self.messages[0].get("content") == self.current_design_brief)

            if not brief_exists:
                # Remove any existing brief messages
                self.messages = [msg for msg in self.messages if msg.get("role") != "brief"]
                # Insert current brief at the beginning
                self.messages.insert(0, {
                    "role": "brief",
                    "content": self.current_design_brief
                })
            return True
        return False

    # Enhanced Conversation Continuity Management
    def update_conversation_context(self, user_input: str, route_used: str, detected_topic: str = "") -> None:
        """Update conversation context for continuity tracking"""
        # Update current topic if provided
        if detected_topic and detected_topic != self.conversation_context.current_topic:
            if self.conversation_context.current_topic:
                self.conversation_context.topic_history.append(self.conversation_context.current_topic)
            self.conversation_context.current_topic = detected_topic

        # Track route usage
        if route_used != self.conversation_context.last_route_used:
            if self.conversation_context.last_route_used:
                self.conversation_context.route_history.append(self.conversation_context.last_route_used)
            self.conversation_context.last_route_used = route_used

        # Update ongoing discussion context
        self.conversation_context.ongoing_discussion["last_user_input"] = user_input
        self.conversation_context.ongoing_discussion["timestamp"] = datetime.now().isoformat()

    def update_building_type_context(self, building_type: str, confidence: float) -> None:
        """Update building type context with confidence tracking"""
        if confidence > self.conversation_context.building_type_confidence:
            self.conversation_context.detected_building_type = building_type
            self.conversation_context.building_type_confidence = confidence
            # Update the main building_type if confidence is high enough
            if confidence > 0.7:
                self.building_type = building_type

    def update_project_context(self, project_details: Dict[str, Any]) -> None:
        """Update project-specific context for better conversation continuity"""
        try:
            # Update project type (adaptive_reuse, new_construction, etc.)
            if 'project_type' in project_details:
                self.conversation_context.project_type = project_details['project_type']

            # Update existing building type for adaptive reuse projects
            if 'existing_building_type' in project_details:
                self.conversation_context.existing_building_type = project_details['existing_building_type']

            # Update target building type
            if 'target_building_type' in project_details:
                self.conversation_context.target_building_type = project_details['target_building_type']

            # Add project details (avoiding duplicates)
            if 'details' in project_details:
                for detail in project_details['details']:
                    if detail not in self.conversation_context.project_details:
                        self.conversation_context.project_details.append(detail)

            print(f"🏗️ Updated project context: {self.conversation_context.project_type}, {self.conversation_context.existing_building_type} → {self.conversation_context.target_building_type}")

        except Exception as e:
            print(f"⚠️ Error updating project context: {e}")

    def detect_and_update_project_context_from_conversation(self) -> None:
        """Detect project context from conversation history and update accordingly"""
        try:
            if not self.messages:
                return

            # Get all user messages for analysis
            user_messages = [msg['content'] for msg in self.messages if msg.get('role') == 'user']
            conversation_text = ' '.join(user_messages).lower()

            project_details = {}
            details_list = []

            # Detect project type
            if 'adaptive reuse' in conversation_text or 'conversion' in conversation_text or 'warehouse' in conversation_text:
                project_details['project_type'] = 'adaptive_reuse'

                # Detect existing building type for adaptive reuse
                if 'warehouse' in conversation_text:
                    project_details['existing_building_type'] = 'warehouse'
                elif 'factory' in conversation_text:
                    project_details['existing_building_type'] = 'factory'
                elif 'church' in conversation_text:
                    project_details['existing_building_type'] = 'church'

                # Detect target building type
                if 'community center' in conversation_text:
                    project_details['target_building_type'] = 'community_center'
                elif 'museum' in conversation_text:
                    project_details['target_building_type'] = 'museum'
                elif 'library' in conversation_text:
                    project_details['target_building_type'] = 'library'

            # Detect specific user groups or requirements
            if 'elder' in conversation_text or 'senior' in conversation_text:
                details_list.append('elder_care')
            if 'accessibility' in conversation_text:
                details_list.append('accessibility_focused')
            if 'construction' in conversation_text:
                details_list.append('construction_considerations')

            if details_list:
                project_details['details'] = details_list

            # Update project context if we found relevant details
            if project_details:
                self.update_project_context(project_details)

        except Exception as e:
            print(f"⚠️ Error detecting project context: {e}")

    def extract_building_type_from_brief_only(self) -> str:
        """
        Extract building type ONLY from design brief or first user message.
        This should be called once at the beginning of the conversation.
        """
        # Priority 1: Extract from design brief
        if self.current_design_brief:
            detected_type = self._detect_building_type_from_text(self.current_design_brief)
            if detected_type != "unknown":
                self.update_building_type_context(detected_type, 0.9)  # High confidence from brief
                return detected_type

        # Priority 2: Extract from first user message only
        user_messages = [msg['content'] for msg in self.messages if msg.get('role') == 'user']
        if user_messages:
            first_message = user_messages[0]
            detected_type = self._detect_building_type_from_text(first_message)
            if detected_type != "unknown":
                self.update_building_type_context(detected_type, 0.8)  # High confidence from first message
                return detected_type

        return "unknown"

    def _detect_building_type_from_text(self, text: str) -> str:
        """
        Detect building type using the comprehensive detection patterns.
        Uses the same detailed patterns as conversation_progression.py for consistency.
        """
        if not text:
            return "unknown"

        text_lower = text.lower()

        # COMPLETE building type detection patterns - EACH SPECIFIC TYPE SEPARATE
        detection_patterns = [
            # High Priority - Cultural & Arts (each type separate - keep specific names)
            ("museum", ["museum"], 11),  # Keep museum as museum, not cultural
            ("library", ["library"], 11),  # Keep library as library, not cultural
            ("gallery", ["gallery"], 10),
            ("theater", ["theater"], 10),
            ("theatre", ["theatre"], 10),
            ("art_gallery", ["art gallery"], 10),
            ("exhibition_gallery", ["exhibition gallery"], 10),
            ("performance_theater", ["performance theater"], 10),
            ("drama_theater", ["drama theater"], 10),
            ("performance_center", ["performance center"], 10),
            ("exhibition_center", ["exhibition center"], 10),
            ("cultural_hub", ["cultural hub"], 10),

            # High Priority - Education & Learning (kindergarten highest priority for children)
            ("kindergarten", ["kindergarten"], 12),  # Higher priority for children's education
            ("school", ["school"], 11),  # Keep school as school, not educational
            ("learning_center", ["learning center"], 10),
            ("education_center", ["education center"], 10),
            ("learning_hub", ["learning hub"], 10),
            ("training_center", ["training center"], 10),
            ("skill_center", ["skill center"], 10),
            ("study_center", ["study center"], 10),
            ("workshop_center", ["workshop center"], 10),
            ("library", ["library"], 10),
            ("reading_room", ["reading room"], 10),
            ("study_space", ["study space"], 10),
            ("information_center", ["information center"], 10),
            ("book_center", ["book center"], 10),

            # High Priority - Community & Recreation (each type separate)
            ("community_center", ["community center"], 10),
            ("community_facility", ["community facility"], 10),
            ("civic_center", ["civic center"], 10),
            ("public_center", ["public center"], 10),
            ("social_hub", ["social hub"], 10),
            ("gathering_place", ["gathering place"], 10),
            ("neighborhood_center", ["neighborhood center"], 10),
            ("town_hall", ["town hall"], 10),
            ("sports_center", ["sports center"], 10),
            ("fitness_center", ["fitness center"], 10),
            ("gym", ["gym"], 10),
            ("athletic_center", ["athletic center"], 10),
            ("sports_facility", ["sports facility"], 10),
            ("fitness_facility", ["fitness facility"], 10),
            ("athletic_facility", ["athletic facility"], 10),
            ("sports_complex", ["sports complex"], 10),
            ("recreation_center", ["recreation center"], 10),
            ("activity_center", ["activity center"], 10),

            # High Priority - Research & Innovation (each type separate)
            ("research_facility", ["research facility"], 10),
            ("laboratory", ["laboratory"], 10),
            ("lab", ["lab"], 10),
            ("research_center", ["research center"], 10),
            ("innovation_center", ["innovation center"], 10),
            ("development_center", ["development center"], 10),
            ("testing_facility", ["testing facility"], 10),

            # High Priority - Healthcare (each type separate - keep specific names)
            ("hospital", ["hospital"], 10),  # Keep hospital as hospital, not healthcare
            ("clinic", ["clinic"], 9),  # Keep clinic as clinic, not healthcare
            ("medical_center", ["medical center"], 9),
            ("health_center", ["health center"], 9),
            ("medical_facility", ["medical facility"], 9),
            ("healthcare_facility", ["healthcare facility"], 9),
            ("treatment_center", ["treatment center"], 9),
            ("specialized_clinic", ["specialized clinic"], 9),
            ("specialty_clinic", ["specialty clinic"], 9),
            ("medical_clinic", ["medical clinic"], 9),
            ("health_clinic", ["health clinic"], 9),
            ("outpatient_clinic", ["outpatient clinic"], 9),
            ("diagnostic_center", ["diagnostic center"], 9),
            ("wellness_center", ["wellness center"], 9),
            ("medical_spa", ["medical spa"], 9),
            ("holistic_center", ["holistic center"], 9),
            ("rehabilitation_center", ["rehabilitation center"], 9),
            ("rehab_center", ["rehab center"], 9),
            ("recovery_center", ["recovery center"], 9),
            ("therapy_center", ["therapy center"], 9),
            ("treatment_facility", ["treatment facility"], 9),

            # High Priority - Educational (each type separate)
            ("school", ["school"], 9),
            ("primary_school", ["primary school"], 9),
            ("elementary_school", ["elementary school"], 9),
            ("high_school", ["high school"], 9),
            ("secondary_school", ["secondary school"], 9),
            ("university", ["university"], 9),
            ("college", ["college"], 9),
            ("higher_education", ["higher education"], 9),
            ("campus", ["campus"], 9),
            ("classroom", ["classroom"], 9),
            ("educational", ["educational"], 9),
            ("academy", ["academy"], 9),
            ("institute", ["institute"], 9),

            # Medium Priority - Residential (each type separate, house lower priority)
            ("apartment", ["apartment"], 8),
            ("residential", ["residential"], 8),
            ("housing", ["housing"], 8),
            ("dwelling", ["dwelling"], 8),
            ("residence", ["residence"], 8),
            ("house", ["house"], 7),  # Lower priority to avoid "warehouse" conflict
            ("home", ["home"], 7),
            ("apartment_building", ["apartment building"], 8),
            ("condominium", ["condominium"], 8),
            ("townhouse", ["townhouse"], 8),
            ("duplex", ["duplex"], 8),
            ("triplex", ["triplex"], 8),
            ("residential_complex", ["residential complex"], 8),
            ("senior_housing", ["senior housing"], 8),
            ("elderly_housing", ["elderly housing"], 8),
            ("retirement_community", ["retirement community"], 8),
            ("assisted_living", ["assisted living"], 8),
            ("nursing_home", ["nursing home"], 8),
            ("care_facility", ["care facility"], 8),
            ("student_housing", ["student housing"], 8),
            ("dormitory", ["dormitory"], 8),
            ("student_residence", ["student residence"], 8),
            ("college_housing", ["college housing"], 8),
            ("university_housing", ["university housing"], 8),

            # Medium Priority - Commercial (each type separate, hotels and warehouses higher priority)
            ("hotel", ["hotel"], 8),  # Higher priority to avoid "business" conflict
            ("lodging", ["lodging"], 8),
            ("accommodation", ["accommodation"], 8),
            ("inn", ["inn"], 8),
            ("resort", ["resort"], 8),
            ("guesthouse", ["guesthouse"], 8),
            ("hostel", ["hostel"], 8),
            ("bed_and_breakfast", ["bed and breakfast"], 8),
            ("restaurant", ["restaurant"], 8),
            ("cafe", ["cafe"], 8),
            ("dining", ["dining"], 8),
            ("eatery", ["eatery"], 8),
            ("bistro", ["bistro"], 8),
            ("food_service", ["food service"], 8),
            ("culinary", ["culinary"], 8),
            ("dining_establishment", ["dining establishment"], 8),
            ("office", ["office"], 8),  # Keep office as office, not commercial
            ("workplace", ["workplace"], 7),
            ("corporate", ["corporate"], 7),
            ("workspace", ["workspace"], 7),
            ("professional", ["professional"], 7),
            ("executive", ["executive"], 7),
            ("store", ["store"], 7),
            ("shop", ["shop"], 7),
            ("retail", ["retail"], 7),
            ("market", ["market"], 7),
            ("shopping", ["shopping"], 7),
            ("merchant", ["merchant"], 7),
            ("boutique", ["boutique"], 7),
            ("business", ["business"], 6),  # Lower priority to avoid conflicts

            # Medium Priority - Community & Recreation (each type separate)
            ("leisure_center", ["leisure center"], 7),
            ("entertainment_center", ["entertainment center"], 7),
            ("senior_center", ["senior center"], 7),
            ("elderly_center", ["elderly center"], 7),
            ("aging_center", ["aging center"], 7),
            ("retirement_center", ["retirement center"], 7),
            ("adult_center", ["adult center"], 7),
            ("mature_center", ["mature center"], 7),
            ("youth_center", ["youth center"], 7),
            ("teen_center", ["teen center"], 7),
            ("adolescent_center", ["adolescent center"], 7),
            ("young_center", ["young center"], 7),
            ("teenager_center", ["teenager center"], 7),

            # Medium Priority - Industrial (each type separate, warehouse higher priority)
            ("warehouse", ["warehouse"], 8),  # Higher priority to avoid "house" conflict
            ("factory", ["factory"], 6),
            ("industrial", ["industrial"], 6),
            ("manufacturing", ["manufacturing"], 6),
            ("production", ["production"], 6),
            ("industrial_facility", ["industrial facility"], 6),
            ("manufacturing_plant", ["manufacturing plant"], 6),
            ("logistics_center", ["logistics center"], 6),
            ("distribution_center", ["distribution center"], 6),
            ("fulfillment_center", ["fulfillment center"], 6),
            ("storage_facility", ["storage facility"], 6),
            ("warehouse_facility", ["warehouse facility"], 6),
            ("research_and_development", ["research and development"], 6),
            ("r_and_d_facility", ["R&D facility"], 6),
            ("technology_center", ["technology center"], 6),
            ("development_facility", ["development facility"], 6),

            # Medium Priority - Transportation (each type separate)
            ("transportation_hub", ["transportation hub"], 6),
            ("transit_center", ["transit center"], 6),
            ("transport_hub", ["transport hub"], 6),
            ("mobility_center", ["mobility center"], 6),
            ("travel_center", ["travel center"], 6),
            ("parking_facility", ["parking facility"], 6),
            ("parking_garage", ["parking garage"], 6),
            ("parking_structure", ["parking structure"], 6),
            ("parking_center", ["parking center"], 6),
            ("car_park", ["car park"], 6),
            ("maintenance_facility", ["maintenance facility"], 6),
            ("service_center", ["service center"], 6),
            ("repair_facility", ["repair facility"], 6),
            ("maintenance_center", ["maintenance center"], 6),

            # Lower Priority - Religious & Spiritual (each type separate)
            ("church", ["church"], 5),
            ("temple", ["temple"], 5),
            ("mosque", ["mosque"], 5),
            ("synagogue", ["synagogue"], 5),
            ("religious", ["religious"], 5),
            ("worship", ["worship"], 5),
            ("spiritual", ["spiritual"], 5),
            ("sacred", ["sacred"], 5),
            ("faith_center", ["faith center"], 5),
            ("meditation_center", ["meditation center"], 5),
            ("spiritual_center", ["spiritual center"], 5),
            ("zen_center", ["zen center"], 5),
            ("mindfulness_center", ["mindfulness center"], 5),
            ("contemplation_center", ["contemplation center"], 5),

            # Lower Priority - Agricultural & Environmental (each type separate)
            ("farm", ["farm"], 4),
            ("agricultural", ["agricultural"], 4),
            ("greenhouse", ["greenhouse"], 4),
            ("nursery", ["nursery"], 4),
            ("agricultural_facility", ["agricultural facility"], 4),
            ("farming_center", ["farming center"], 4),
            ("environmental_center", ["environmental center"], 4),
            ("nature_center", ["nature center"], 4),
            ("conservation_center", ["conservation center"], 4),
            ("ecology_center", ["ecology center"], 4),
            ("sustainability_center", ["sustainability center"], 4),

            # Lower Priority - Specialized (each type separate)
            ("conference_center", ["conference center"], 4),
            ("convention_center", ["convention center"], 4),
            ("meeting_center", ["meeting center"], 4),
            ("event_center", ["event center"], 4),
            ("summit_center", ["summit center"], 4),
            ("innovation_hub", ["innovation hub"], 4),
            ("startup_center", ["startup center"], 4),
            ("entrepreneurial_center", ["entrepreneurial center"], 4),
            ("business_incubator", ["business incubator"], 4),
            ("tech_hub", ["tech hub"], 4),
            ("creative_workspace", ["creative workspace"], 4),
            ("artist_studio", ["artist studio"], 4),
            ("design_studio", ["design studio"], 4),
            ("creative_center", ["creative center"], 4),
            ("artistic_space", ["artistic space"], 4),

            # Lower Priority - Government & Public (each type separate)
            ("government_building", ["government building"], 3),
            ("civic_building", ["civic building"], 3),
            ("public_building", ["public building"], 3),
            ("administrative_center", ["administrative center"], 3),
            ("public_service", ["public service"], 3),
            ("fire_station", ["fire station"], 3),
            ("police_station", ["police station"], 3),
            ("emergency_center", ["emergency center"], 3),
            ("public_safety", ["public safety"], 3),
            ("emergency_facility", ["emergency facility"], 3),
            ("utility_facility", ["utility facility"], 3),
            ("power_plant", ["power plant"], 3),
            ("water_treatment", ["water treatment"], 3),
            ("energy_center", ["energy center"], 3),
            ("infrastructure_facility", ["infrastructure facility"], 3),

            # Lowest Priority - Mixed Use (each type separate)
            ("mixed_use", ["mixed use"], 2),
            ("multi_use", ["multi-use"], 2),
            ("combined_use", ["combined use"], 2),
            ("integrated", ["integrated"], 2),
            ("hybrid", ["hybrid"], 2),
            ("versatile", ["versatile"], 2),
            ("flexible", ["flexible"], 2)
        ]

        # Score each building type based on keyword matches
        building_scores = {}
        for building_type, keywords, base_priority in detection_patterns:
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += base_priority
                    # Bonus for exact matches
                    if keyword == text_lower.strip():
                        score += 5
                    # Bonus for longer, more specific keywords
                    if len(keyword.split()) > 1:
                        score += 2
                    # Bonus for multiple keyword matches
                    if text_lower.count(keyword) > 1:
                        score += 1

            if score > 0:
                building_scores[building_type] = score

        # Return the highest scoring building type, or unknown as fallback
        if building_scores:
            best_match = max(building_scores.keys(), key=lambda k: building_scores[k])
            # Only return specific types if score is high enough
            if building_scores[best_match] >= 5:
                return best_match

        return "unknown"

    def update_design_phase_context(self, phase: str, confidence: float) -> None:
        """Update design phase context with confidence tracking"""
        if confidence > self.conversation_context.phase_confidence:
            self.conversation_context.design_phase_detected = phase
            self.conversation_context.phase_confidence = confidence
            # Update the main design_phase if confidence is high enough
            if confidence > 0.7:
                try:
                    self.design_phase = DesignPhase(phase)
                except ValueError:
                    pass  # Keep current phase if invalid

    def get_conversation_continuity_context(self) -> Dict[str, Any]:
        """Get context for maintaining conversation continuity"""
        return {
            "current_topic": self.conversation_context.current_topic,
            "topic_history": self.conversation_context.topic_history[-3:],  # Last 3 topics
            "last_route_used": self.conversation_context.last_route_used,
            "route_history": self.conversation_context.route_history[-5:],  # Last 5 routes
            "ongoing_discussion": self.conversation_context.ongoing_discussion,
            "detected_building_type": self.conversation_context.detected_building_type,
            "building_type_confidence": self.conversation_context.building_type_confidence,
            "design_phase_detected": self.conversation_context.design_phase_detected,
            "phase_confidence": self.conversation_context.phase_confidence,
            "project_type": self.conversation_context.project_type,
            "existing_building_type": self.conversation_context.existing_building_type,
            "target_building_type": self.conversation_context.target_building_type,
            "project_details": self.conversation_context.project_details,
            "questions_asked": self.conversation_context.questions_asked[-5:],  # Last 5 questions
            "concepts_discussed": self.conversation_context.concepts_discussed[-10:],  # Last 10 concepts
            "user_understanding_level": self.conversation_context.user_understanding_level,
            "conversation_length": len(self.messages),
            "thread_duration": self._calculate_thread_duration()
        }

    def _calculate_thread_duration(self) -> str:
        """Calculate how long the current conversation thread has been active"""
        try:
            start_time = datetime.fromisoformat(self.conversation_context.thread_start_time)
            duration = datetime.now() - start_time
            return f"{duration.total_seconds():.0f}s"
        except:
            return "unknown"

    def is_continuing_conversation(self) -> bool:
        """Check if this is a continuing conversation rather than a new topic"""
        return (
            len(self.messages) > 2 and  # More than just initial exchange
            bool(self.conversation_context.current_topic) and  # Has an established topic
            bool(self.conversation_context.ongoing_discussion)  # Has ongoing context
        )