"""
Storytelling Framework for Narrative-Driven Learning
Creates immersive story-based challenges with character development and scenarios.
"""

import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import random

class StorytellingFramework:
    """Framework for creating narrative-driven architectural learning experiences."""
    
    def __init__(self):
        self.story_archetypes = {
            "community_builder": {
                "name": "The Community Builder",
                "description": "You're designing spaces that bring people together",
                "icon": "🏘️",
                "color": "#e74c3c",
                "themes": ["social_connection", "inclusive_design", "cultural_sensitivity"]
            },
            "sustainability_champion": {
                "name": "The Sustainability Champion", 
                "description": "You're creating environmentally responsible architecture",
                "icon": "🌱",
                "color": "#27ae60",
                "themes": ["environmental_impact", "resource_efficiency", "future_generations"]
            },
            "innovation_pioneer": {
                "name": "The Innovation Pioneer",
                "description": "You're pushing the boundaries of architectural possibility",
                "icon": "🚀",
                "color": "#3498db",
                "themes": ["technological_integration", "creative_solutions", "future_thinking"]
            },
            "heritage_guardian": {
                "name": "The Heritage Guardian",
                "description": "You're preserving and adapting historical architecture",
                "icon": "🏛️",
                "color": "#f39c12",
                "themes": ["historical_preservation", "adaptive_reuse", "cultural_continuity"]
            },
            "wellness_advocate": {
                "name": "The Wellness Advocate",
                "description": "You're designing for human health and wellbeing",
                "icon": "💚",
                "color": "#9b59b6",
                "themes": ["human_comfort", "biophilic_design", "mental_health"]
            }
        }
        
        self.narrative_scenarios = {
            "community_center": {
                "setting": "A diverse urban neighborhood needs a new community center",
                "stakeholders": ["Local residents", "City council", "Community leaders", "Youth groups", "Seniors"],
                "challenges": ["Limited budget", "Diverse needs", "Site constraints", "Cultural sensitivity"],
                "success_metrics": ["Community engagement", "Functional efficiency", "Cultural appropriateness"]
            },
            "hospital": {
                "setting": "A growing city needs a new healing-focused hospital",
                "stakeholders": ["Patients", "Medical staff", "Administrators", "Families", "Community"],
                "challenges": ["Complex medical requirements", "Wayfinding", "Infection control", "Emotional support"],
                "success_metrics": ["Patient outcomes", "Staff efficiency", "Family comfort", "Operational effectiveness"]
            },
            "school": {
                "setting": "An innovative school district wants to reimagine learning spaces",
                "stakeholders": ["Students", "Teachers", "Parents", "Administrators", "Community"],
                "challenges": ["Diverse learning styles", "Technology integration", "Safety", "Flexibility"],
                "success_metrics": ["Learning outcomes", "Teacher satisfaction", "Student engagement", "Community pride"]
            }
        }
        
        self.character_archetypes = {
            "the_visionary": {
                "name": "The Visionary",
                "description": "Sees the big picture and future possibilities",
                "strengths": ["Strategic thinking", "Innovation", "Inspiration"],
                "challenges": ["Practical constraints", "Budget limitations", "Stakeholder buy-in"]
            },
            "the_pragmatist": {
                "name": "The Pragmatist", 
                "description": "Focuses on practical solutions and implementation",
                "strengths": ["Problem-solving", "Resource management", "Execution"],
                "challenges": ["Limited vision", "Risk aversion", "Innovation resistance"]
            },
            "the_collaborator": {
                "name": "The Collaborator",
                "description": "Brings people together and builds consensus",
                "strengths": ["Communication", "Empathy", "Conflict resolution"],
                "challenges": ["Decision paralysis", "Compromise quality", "Time management"]
            },
            "the_specialist": {
                "name": "The Specialist",
                "description": "Deep expertise in specific architectural domains",
                "strengths": ["Technical knowledge", "Quality standards", "Best practices"],
                "challenges": ["Narrow focus", "Integration difficulties", "Communication barriers"]
            }
        }
        
        self._initialize_story_state()
    
    def _initialize_story_state(self):
        """Initialize storytelling framework state."""
        if 'storytelling_state' not in st.session_state:
            st.session_state.storytelling_state = {
                'current_story': None,
                'character_profile': None,
                'story_progress': {},
                'narrative_choices': [],
                'character_development': {},
                'story_outcomes': [],
                'unlocked_scenarios': ['community_center'],  # Start with one unlocked
                'story_achievements': []
            }
    
    def render_story_selection(self):
        """Render story selection interface."""
        st.markdown("## 📚 Choose Your Architectural Journey")
        
        story_state = st.session_state.storytelling_state
        
        # Character archetype selection
        if not story_state['character_profile']:
            self._render_character_selection()
        else:
            # Story scenario selection
            self._render_scenario_selection()
    
    def _render_character_selection(self):
        """Render character archetype selection."""
        st.markdown("### 🎭 Choose Your Architect Persona")
        st.markdown("Your character will influence how you approach design challenges and interact with stakeholders.")
        
        cols = st.columns(2)
        
        for i, (archetype_id, archetype) in enumerate(self.story_archetypes.items()):
            col = cols[i % 2]
            
            with col:
                if st.button(
                    f"{archetype['icon']} {archetype['name']}", 
                    key=f"archetype_{archetype_id}",
                    help=archetype['description']
                ):
                    self._select_character_archetype(archetype_id)
                    st.rerun()
                
                st.markdown(f"*{archetype['description']}*")
                st.markdown(f"**Themes:** {', '.join(archetype['themes'])}")
    
    def _select_character_archetype(self, archetype_id: str):
        """Select character archetype and initialize profile."""
        story_state = st.session_state.storytelling_state
        archetype = self.story_archetypes[archetype_id]
        
        story_state['character_profile'] = {
            'archetype_id': archetype_id,
            'name': archetype['name'],
            'description': archetype['description'],
            'icon': archetype['icon'],
            'color': archetype['color'],
            'themes': archetype['themes'],
            'experience_level': 1,
            'reputation': 50,
            'specializations': [],
            'relationships': {}
        }
        
        st.success(f"Welcome, {archetype['name']}! Your architectural journey begins now.")
    
    def _render_scenario_selection(self):
        """Render story scenario selection."""
        st.markdown("### 🏗️ Choose Your Next Project")
        
        story_state = st.session_state.storytelling_state
        character = story_state['character_profile']
        unlocked_scenarios = story_state['unlocked_scenarios']
        
        # Display character info
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {character['color']}20, {character['color']}40);
            border: 2px solid {character['color']};
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
        ">
            <h4 style="color: {character['color']}; margin: 0;">
                {character['icon']} {character['name']}
            </h4>
            <p style="margin: 5px 0;">{character['description']}</p>
            <small>Experience Level: {character['experience_level']} | Reputation: {character['reputation']}/100</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Available scenarios
        for scenario_id, scenario in self.narrative_scenarios.items():
            is_unlocked = scenario_id in unlocked_scenarios
            
            with st.expander(
                f"{'🔓' if is_unlocked else '🔒'} {scenario_id.replace('_', ' ').title()}", 
                expanded=is_unlocked
            ):
                st.markdown(f"**Setting:** {scenario['setting']}")
                st.markdown(f"**Key Stakeholders:** {', '.join(scenario['stakeholders'])}")
                st.markdown(f"**Main Challenges:** {', '.join(scenario['challenges'])}")
                
                if is_unlocked:
                    if st.button(f"Start {scenario_id.replace('_', ' ').title()} Project", key=f"start_{scenario_id}"):
                        self._start_story_scenario(scenario_id)
                        st.rerun()
                else:
                    st.info("Complete other projects to unlock this scenario.")
    
    def _start_story_scenario(self, scenario_id: str):
        """Start a new story scenario."""
        story_state = st.session_state.storytelling_state
        
        story_state['current_story'] = {
            'scenario_id': scenario_id,
            'scenario_data': self.narrative_scenarios[scenario_id],
            'current_chapter': 1,
            'total_chapters': 5,
            'story_choices': [],
            'stakeholder_relationships': {stakeholder: 50 for stakeholder in self.narrative_scenarios[scenario_id]['stakeholders']},
            'project_constraints': {},
            'design_decisions': [],
            'story_timeline': []
        }
        
        st.success(f"Starting your {scenario_id.replace('_', ' ').title()} project!")
    
    def render_story_chapter(self):
        """Render the current story chapter."""
        story_state = st.session_state.storytelling_state
        current_story = story_state['current_story']
        
        if not current_story:
            self.render_story_selection()
            return
        
        scenario_id = current_story['scenario_id']
        chapter = current_story['current_chapter']
        
        st.markdown(f"## 📖 Chapter {chapter}: {scenario_id.replace('_', ' ').title()} Project")
        
        # Render chapter content based on scenario and chapter
        if chapter == 1:
            self._render_introduction_chapter(current_story)
        elif chapter == 2:
            self._render_stakeholder_chapter(current_story)
        elif chapter == 3:
            self._render_design_development_chapter(current_story)
        elif chapter == 4:
            self._render_challenge_resolution_chapter(current_story)
        elif chapter == 5:
            self._render_project_completion_chapter(current_story)
        
        # Chapter navigation
        self._render_chapter_navigation(current_story)
    
    def _render_introduction_chapter(self, story: Dict[str, Any]):
        """Render the introduction chapter."""
        scenario_data = story['scenario_data']
        
        st.markdown("### 🎬 Project Introduction")
        st.markdown(f"**Setting:** {scenario_data['setting']}")
        
        # Initial scenario presentation
        scenario_id = story['scenario_id']
        
        if scenario_id == "community_center":
            story_text = """
            You've been selected to design a new community center for the Riverside neighborhood. 
            This diverse area has been without a central gathering space for years, and residents 
            are excited but have very different ideas about what the center should be.
            
            The site is a former parking lot next to the river, with beautiful views but also 
            flooding concerns. The budget is tight, but the community's enthusiasm is high.
            """
        elif scenario_id == "hospital":
            story_text = """
            The Regional Health Authority has commissioned you to design a new healing-focused hospital. 
            This isn't just about medical efficiency - they want a space that supports patient recovery, 
            staff wellbeing, and family comfort.
            
            The site is in the growing suburbs, with good transportation access but limited urban context. 
            The medical staff are excited about innovative approaches, but administrators are concerned about costs.
            """
        else:
            story_text = f"Your new {scenario_id.replace('_', ' ')} project begins with exciting possibilities and complex challenges."
        
        st.markdown(story_text)
        
        # Initial choice
        st.markdown("### 🤔 Your First Decision")
        st.markdown("How do you want to approach this project?")
        
        approach_options = [
            "Start with extensive community engagement and listening sessions",
            "Begin with thorough site analysis and technical studies", 
            "Focus on innovative design concepts and precedent research",
            "Prioritize budget analysis and phasing strategies"
        ]
        
        selected_approach = st.radio("Choose your approach:", approach_options, key="intro_approach")
        
        if st.button("Proceed with This Approach", key="intro_proceed"):
            self._record_story_choice("introduction", "approach", selected_approach)
            self._advance_chapter(story)
    
    def _render_stakeholder_chapter(self, story: Dict[str, Any]):
        """Render the stakeholder engagement chapter."""
        st.markdown("### 👥 Stakeholder Engagement")
        
        scenario_data = story['scenario_data']
        stakeholders = scenario_data['stakeholders']
        relationships = story['stakeholder_relationships']
        
        st.markdown("You need to engage with various stakeholders. Each has different priorities and concerns.")
        
        # Display stakeholder relationships
        st.markdown("**Current Relationships:**")
        for stakeholder, relationship_level in relationships.items():
            if relationship_level >= 70:
                status = "😊 Strong"
                color = "success"
            elif relationship_level >= 40:
                status = "😐 Neutral"
                color = "info"
            else:
                status = "😟 Strained"
                color = "warning"
            
            st.markdown(f"- **{stakeholder}:** {status} ({relationship_level}/100)")
        
        # Stakeholder interaction
        st.markdown("### 💬 Stakeholder Meeting")
        
        selected_stakeholder = st.selectbox("Choose who to meet with:", stakeholders, key="stakeholder_select")
        
        # Generate stakeholder-specific scenario
        meeting_scenarios = self._generate_stakeholder_scenarios(story['scenario_id'], selected_stakeholder)
        
        st.markdown(f"**Meeting with {selected_stakeholder}:**")
        st.markdown(meeting_scenarios['scenario'])
        
        # Response options
        st.markdown("**How do you respond?**")
        response = st.radio("Choose your response:", meeting_scenarios['options'], key="stakeholder_response")
        
        if st.button("Respond", key="stakeholder_respond"):
            self._process_stakeholder_interaction(story, selected_stakeholder, response)
            st.rerun()
    
    def _generate_stakeholder_scenarios(self, scenario_id: str, stakeholder: str) -> Dict[str, Any]:
        """Generate stakeholder-specific interaction scenarios."""
        scenarios = {
            "community_center": {
                "Local residents": {
                    "scenario": "The residents are concerned about noise levels and parking. They want the center to serve families but worry about disruption to the neighborhood.",
                    "options": [
                        "Propose sound-dampening design and underground parking",
                        "Suggest community programming guidelines and shared parking agreements",
                        "Focus on the economic benefits the center will bring",
                        "Invite them to co-design the outdoor spaces"
                    ]
                },
                "City council": {
                    "scenario": "The city council is focused on budget constraints and long-term maintenance costs. They want to ensure the project is financially sustainable.",
                    "options": [
                        "Present a detailed cost-benefit analysis with revenue projections",
                        "Propose a phased construction approach to spread costs",
                        "Suggest partnerships with local businesses for funding",
                        "Focus on energy-efficient design to reduce operating costs"
                    ]
                }
            }
        }
        
        return scenarios.get(scenario_id, {}).get(stakeholder, {
            "scenario": f"{stakeholder} has specific concerns about the project that need to be addressed.",
            "options": [
                "Listen carefully and ask clarifying questions",
                "Present your design vision enthusiastically", 
                "Focus on practical solutions to their concerns",
                "Suggest a collaborative design process"
            ]
        })
    
    def _process_stakeholder_interaction(self, story: Dict[str, Any], stakeholder: str, response: str):
        """Process stakeholder interaction and update relationships."""
        # Simple relationship impact based on response type
        relationship_change = 0
        
        if "listen" in response.lower() or "collaborative" in response.lower():
            relationship_change = 10
        elif "practical" in response.lower() or "detailed" in response.lower():
            relationship_change = 5
        elif "enthusiastically" in response.lower():
            relationship_change = random.choice([-5, 15])  # Risk/reward
        
        # Update relationship
        current_level = story['stakeholder_relationships'][stakeholder]
        new_level = max(0, min(100, current_level + relationship_change))
        story['stakeholder_relationships'][stakeholder] = new_level
        
        # Record the interaction
        self._record_story_choice("stakeholder_engagement", stakeholder, response)
        
        # Provide feedback
        if relationship_change > 0:
            st.success(f"Your relationship with {stakeholder} improved! (+{relationship_change})")
        elif relationship_change < 0:
            st.warning(f"Your relationship with {stakeholder} was strained. ({relationship_change})")
        else:
            st.info(f"Your relationship with {stakeholder} remained stable.")
    
    def _render_design_development_chapter(self, story: Dict[str, Any]):
        """Render the design development chapter."""
        st.markdown("### 🎨 Design Development")
        st.markdown("Now it's time to develop your design concept based on what you've learned.")
        
        # Design challenge based on scenario
        scenario_id = story['scenario_id']
        
        if scenario_id == "community_center":
            design_challenge = """
            **Design Challenge:** Create a flexible community space that can accommodate:
            - Large community gatherings (200+ people)
            - Small group meetings and classes
            - Children's activities and senior programs
            - Cultural events and celebrations
            - Quiet study and work spaces
            
            **Site Constraints:** 
            - Riverside location with flood risk
            - Limited parking availability
            - Noise concerns from neighbors
            - Budget of $2.5M
            """
        else:
            design_challenge = f"Design challenge for {scenario_id.replace('_', ' ')} project."
        
        st.markdown(design_challenge)
        
        # Design decisions
        st.markdown("### 🏗️ Key Design Decisions")
        
        design_aspects = [
            "Building Layout and Organization",
            "Material Selection and Sustainability",
            "Accessibility and Universal Design",
            "Technology Integration",
            "Outdoor Space Integration"
        ]
        
        selected_aspect = st.selectbox("Focus on which design aspect?", design_aspects, key="design_aspect")
        
        # Generate aspect-specific options
        design_options = self._generate_design_options(scenario_id, selected_aspect)
        
        st.markdown(f"**{selected_aspect} Options:**")
        selected_option = st.radio("Choose your design approach:", design_options, key="design_option")
        
        if st.button("Implement This Design Decision", key="design_implement"):
            self._record_design_decision(story, selected_aspect, selected_option)
            st.success(f"Design decision recorded: {selected_aspect}")
    
    def _generate_design_options(self, scenario_id: str, aspect: str) -> List[str]:
        """Generate design options for specific aspects."""
        options_map = {
            "Building Layout and Organization": [
                "Central atrium with surrounding flexible spaces",
                "Linear organization with clear public-to-private gradient",
                "Clustered pavilions connected by covered walkways",
                "Multi-level design with different functions on each floor"
            ],
            "Material Selection and Sustainability": [
                "Local materials with high thermal mass for climate control",
                "Prefabricated modular construction for cost efficiency",
                "Recycled and upcycled materials for environmental impact",
                "High-performance envelope with renewable energy systems"
            ],
            "Accessibility and Universal Design": [
                "Single-level design with ramped access throughout",
                "Multi-sensory wayfinding and communication systems",
                "Flexible furniture and adaptable spaces",
                "Dedicated accessibility features integrated seamlessly"
            ]
        }
        
        return options_map.get(aspect, [
            "Option A: Conservative approach",
            "Option B: Innovative approach", 
            "Option C: Balanced approach",
            "Option D: Community-focused approach"
        ])
    
    def _record_design_decision(self, story: Dict[str, Any], aspect: str, decision: str):
        """Record a design decision in the story."""
        story['design_decisions'].append({
            'aspect': aspect,
            'decision': decision,
            'timestamp': datetime.now().isoformat()
        })
    
    def _render_challenge_resolution_chapter(self, story: Dict[str, Any]):
        """Render the challenge resolution chapter."""
        st.markdown("### ⚡ Challenge Resolution")
        st.markdown("Unexpected challenges have emerged that require immediate attention.")
        
        # Generate scenario-specific challenge
        scenario_id = story['scenario_id']
        challenge = self._generate_story_challenge(scenario_id, story)
        
        st.markdown(f"**Challenge:** {challenge['description']}")
        st.markdown(f"**Impact:** {challenge['impact']}")
        
        # Resolution options
        st.markdown("**How do you address this challenge?**")
        resolution = st.radio("Choose your approach:", challenge['options'], key="challenge_resolution")
        
        if st.button("Implement Resolution", key="resolve_challenge"):
            self._process_challenge_resolution(story, challenge, resolution)
            self._advance_chapter(story)
    
    def _generate_story_challenge(self, scenario_id: str, story: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a story-specific challenge."""
        challenges = {
            "community_center": {
                "description": "Heavy rains have revealed that the site floods more severely than expected. The community is concerned about safety and accessibility.",
                "impact": "This could delay construction and require significant design changes.",
                "options": [
                    "Raise the building on stilts and create flood-resilient design",
                    "Implement comprehensive stormwater management systems",
                    "Relocate critical functions to upper levels",
                    "Partner with the city on neighborhood-wide flood mitigation"
                ]
            }
        }
        
        return challenges.get(scenario_id, {
            "description": "An unexpected challenge has emerged that tests your design decisions.",
            "impact": "This requires creative problem-solving and stakeholder management.",
            "options": [
                "Address the challenge directly with technical solutions",
                "Engage stakeholders in collaborative problem-solving",
                "Seek additional resources and expertise",
                "Adapt the design to work with the constraint"
            ]
        })
    
    def _process_challenge_resolution(self, story: Dict[str, Any], challenge: Dict[str, Any], resolution: str):
        """Process challenge resolution and update story state."""
        # Record the resolution
        self._record_story_choice("challenge_resolution", "approach", resolution)
        
        # Update story outcomes based on resolution
        if "collaborative" in resolution.lower():
            # Improve stakeholder relationships
            for stakeholder in story['stakeholder_relationships']:
                story['stakeholder_relationships'][stakeholder] += 5
            st.success("Your collaborative approach strengthened stakeholder relationships!")
        
        elif "technical" in resolution.lower():
            # Add to character specializations
            character = st.session_state.storytelling_state['character_profile']
            if "technical_expertise" not in character['specializations']:
                character['specializations'].append("technical_expertise")
            st.success("You've developed stronger technical problem-solving skills!")
        
        st.success(f"Challenge resolved: {resolution}")
    
    def _render_project_completion_chapter(self, story: Dict[str, Any]):
        """Render the project completion chapter."""
        st.markdown("### 🎉 Project Completion")
        st.markdown("Your project is complete! Let's see how your decisions impacted the outcome.")
        
        # Calculate project success metrics
        success_metrics = self._calculate_project_success(story)
        
        # Display results
        st.markdown("### 📊 Project Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Stakeholder Satisfaction", f"{success_metrics['stakeholder_avg']:.0f}/100")
        
        with col2:
            st.metric("Design Innovation", f"{success_metrics['innovation_score']:.0f}/100")
        
        with col3:
            st.metric("Project Impact", f"{success_metrics['impact_score']:.0f}/100")
        
        # Story conclusion
        self._render_story_conclusion(story, success_metrics)
        
        # Character development
        self._update_character_development(success_metrics)
        
        # Unlock new scenarios
        self._unlock_new_scenarios(success_metrics)
    
    def _calculate_project_success(self, story: Dict[str, Any]) -> Dict[str, float]:
        """Calculate project success metrics."""
        relationships = story['stakeholder_relationships']
        stakeholder_avg = sum(relationships.values()) / len(relationships)
        
        # Innovation score based on design decisions
        design_decisions = story['design_decisions']
        innovation_score = len(design_decisions) * 15 + random.randint(10, 30)
        
        # Impact score based on story choices
        story_choices = story['story_choices']
        impact_score = len(story_choices) * 10 + stakeholder_avg * 0.5
        
        return {
            'stakeholder_avg': stakeholder_avg,
            'innovation_score': min(100, innovation_score),
            'impact_score': min(100, impact_score)
        }
    
    def _render_story_conclusion(self, story: Dict[str, Any], metrics: Dict[str, float]):
        """Render story conclusion based on outcomes."""
        avg_score = (metrics['stakeholder_avg'] + metrics['innovation_score'] + metrics['impact_score']) / 3
        
        if avg_score >= 80:
            conclusion = "🌟 **Outstanding Success!** Your project has become a model for community-centered design. The space is beloved by users and has won several design awards."
            color = "success"
        elif avg_score >= 60:
            conclusion = "✅ **Successful Project!** Your design successfully meets the community's needs and has been well-received. There are lessons learned for future projects."
            color = "success"
        elif avg_score >= 40:
            conclusion = "⚠️ **Mixed Results.** The project is functional but faced some challenges. Some stakeholders are satisfied while others have concerns."
            color = "warning"
        else:
            conclusion = "📚 **Learning Experience.** The project faced significant challenges, but you've gained valuable experience for future endeavors."
            color = "info"
        
        if color == "success":
            st.success(conclusion)
        elif color == "warning":
            st.warning(conclusion)
        else:
            st.info(conclusion)
    
    def _update_character_development(self, metrics: Dict[str, float]):
        """Update character development based on project outcomes."""
        character = st.session_state.storytelling_state['character_profile']
        
        # Increase experience level
        character['experience_level'] += 1
        
        # Update reputation
        avg_score = (metrics['stakeholder_avg'] + metrics['innovation_score'] + metrics['impact_score']) / 3
        reputation_change = int((avg_score - 50) / 5)  # -10 to +10 change
        character['reputation'] = max(0, min(100, character['reputation'] + reputation_change))
        
        st.success(f"Character Development: Level {character['experience_level']}, Reputation: {character['reputation']}/100")
    
    def _unlock_new_scenarios(self, metrics: Dict[str, float]):
        """Unlock new scenarios based on performance."""
        story_state = st.session_state.storytelling_state
        avg_score = (metrics['stakeholder_avg'] + metrics['innovation_score'] + metrics['impact_score']) / 3
        
        if avg_score >= 70 and 'hospital' not in story_state['unlocked_scenarios']:
            story_state['unlocked_scenarios'].append('hospital')
            st.success("🔓 New scenario unlocked: Hospital Design!")
        
        if avg_score >= 80 and 'school' not in story_state['unlocked_scenarios']:
            story_state['unlocked_scenarios'].append('school')
            st.success("🔓 New scenario unlocked: School Design!")
    
    def _render_chapter_navigation(self, story: Dict[str, Any]):
        """Render chapter navigation controls."""
        current_chapter = story['current_chapter']
        total_chapters = story['total_chapters']
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if current_chapter > 1:
                if st.button("← Previous Chapter", key="prev_chapter"):
                    story['current_chapter'] -= 1
                    st.rerun()
        
        with col2:
            st.markdown(f"**Chapter {current_chapter} of {total_chapters}**")
            progress = current_chapter / total_chapters
            st.progress(progress)
        
        with col3:
            if current_chapter < total_chapters:
                if st.button("Next Chapter →", key="next_chapter"):
                    self._advance_chapter(story)
    
    def _advance_chapter(self, story: Dict[str, Any]):
        """Advance to the next chapter."""
        if story['current_chapter'] < story['total_chapters']:
            story['current_chapter'] += 1
            st.rerun()
        else:
            # Story complete
            st.balloons()
            story['current_chapter'] = story['total_chapters']
    
    def _record_story_choice(self, chapter: str, choice_type: str, choice: str):
        """Record a story choice for tracking."""
        story_state = st.session_state.storytelling_state
        current_story = story_state['current_story']
        
        choice_record = {
            'chapter': chapter,
            'choice_type': choice_type,
            'choice': choice,
            'timestamp': datetime.now().isoformat()
        }
        
        current_story['story_choices'].append(choice_record)

# Global instance
storytelling_framework = StorytellingFramework()
