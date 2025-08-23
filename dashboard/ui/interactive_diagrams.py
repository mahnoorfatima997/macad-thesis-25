"""
Interactive Diagram System for Spatial Challenges
Clickable architectural diagrams for spatial reasoning and design problem solving.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import json
import random

class InteractiveDiagramSystem:
    """Interactive architectural diagrams for spatial learning challenges."""
    
    def __init__(self):
        self.diagram_types = {
            "floor_plan": {
                "name": "Floor Plan",
                "icon": "🏗️",
                "description": "Interactive floor plan with clickable spaces"
            },
            "section": {
                "name": "Section View",
                "icon": "📐",
                "description": "Building section with vertical relationships"
            },
            "site_plan": {
                "name": "Site Plan",
                "icon": "🌍",
                "description": "Site layout with context and circulation"
            },
            "circulation": {
                "name": "Circulation Diagram",
                "icon": "🔄",
                "description": "Movement patterns and flow analysis"
            },
            "zoning": {
                "name": "Zoning Diagram",
                "icon": "📊",
                "description": "Functional zones and relationships"
            }
        }
        
        self.space_types = {
            "entrance": {"color": "#e74c3c", "name": "Entrance"},
            "lobby": {"color": "#3498db", "name": "Lobby"},
            "office": {"color": "#f39c12", "name": "Office"},
            "meeting": {"color": "#9b59b6", "name": "Meeting Room"},
            "circulation": {"color": "#95a5a6", "name": "Circulation"},
            "service": {"color": "#27ae60", "name": "Service"},
            "outdoor": {"color": "#2ecc71", "name": "Outdoor Space"},
            "storage": {"color": "#34495e", "name": "Storage"},
            "restroom": {"color": "#16a085", "name": "Restroom"},
            "kitchen": {"color": "#e67e22", "name": "Kitchen/Cafe"}
        }
        
        self._initialize_diagram_state()
    
    def _initialize_diagram_state(self):
        """Initialize diagram interaction state."""
        if 'diagram_state' not in st.session_state:
            st.session_state.diagram_state = {
                'selected_spaces': [],
                'user_annotations': {},
                'challenge_progress': {},
                'interaction_history': []
            }
    
    def render_spatial_challenge(self, challenge_type: str, building_type: str = "community_center"):
        """Render an interactive spatial challenge."""
        st.markdown(f"## 🏗️ Interactive Spatial Challenge")
        
        if challenge_type == "space_organization":
            self._render_space_organization_challenge(building_type)
        elif challenge_type == "circulation_flow":
            self._render_circulation_challenge(building_type)
        elif challenge_type == "zoning_analysis":
            self._render_zoning_challenge(building_type)
        elif challenge_type == "site_planning":
            self._render_site_planning_challenge(building_type)
        else:
            self._render_generic_spatial_challenge(building_type)
    
    def _render_space_organization_challenge(self, building_type: str):
        """Render space organization challenge with interactive floor plan."""
        st.markdown("### 🎯 Challenge: Organize the Spaces")
        st.markdown("Click on spaces to select them and analyze their relationships.")
        
        # Create interactive floor plan
        fig = self._create_floor_plan(building_type)
        
        # Add click event handling
        selected_points = st.plotly_chart(
            fig, 
            use_container_width=True,
            on_select="rerun",
            selection_mode="points"
        )
        
        # Challenge questions based on selections
        self._render_space_analysis_questions()
        
        # Feedback and scoring
        self._render_spatial_feedback()
    
    def _create_floor_plan(self, building_type: str) -> go.Figure:
        """Create an interactive floor plan diagram."""
        fig = go.Figure()
        
        # Define spaces based on building type
        if building_type == "community_center":
            spaces = self._get_community_center_spaces()
        elif building_type == "hospital":
            spaces = self._get_hospital_spaces()
        else:
            spaces = self._get_generic_spaces()
        
        # Add spaces as interactive shapes
        for space_id, space_data in spaces.items():
            # Add space as a filled rectangle
            fig.add_shape(
                type="rect",
                x0=space_data['x'], y0=space_data['y'],
                x1=space_data['x'] + space_data['width'],
                y1=space_data['y'] + space_data['height'],
                fillcolor=self.space_types[space_data['type']]['color'],
                opacity=0.7,
                line=dict(color="black", width=2),
                name=space_id
            )
            
            # Add space label
            fig.add_annotation(
                x=space_data['x'] + space_data['width']/2,
                y=space_data['y'] + space_data['height']/2,
                text=space_data['name'],
                showarrow=False,
                font=dict(size=10, color="white"),
                bgcolor="rgba(0,0,0,0.5)",
                bordercolor="white",
                borderwidth=1
            )
            
            # Add invisible scatter point for click detection
            fig.add_trace(go.Scatter(
                x=[space_data['x'] + space_data['width']/2],
                y=[space_data['y'] + space_data['height']/2],
                mode='markers',
                marker=dict(size=20, opacity=0),
                name=space_data['name'],
                customdata=[space_id],
                hovertemplate=f"<b>{space_data['name']}</b><br>" +
                            f"Type: {self.space_types[space_data['type']]['name']}<br>" +
                            f"Area: {space_data['width'] * space_data['height']} sq units<br>" +
                            "<extra></extra>"
            ))
        
        # Update layout
        fig.update_layout(
            title="Interactive Floor Plan - Click on spaces to analyze",
            xaxis=dict(showgrid=True, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=True, zeroline=False, showticklabels=False),
            showlegend=False,
            height=500,
            dragmode='select'
        )
        
        return fig
    
    def _get_community_center_spaces(self) -> Dict[str, Dict]:
        """Define spaces for a community center."""
        return {
            "entrance": {
                "name": "Main Entrance",
                "type": "entrance",
                "x": 5, "y": 8, "width": 3, "height": 2
            },
            "lobby": {
                "name": "Lobby",
                "type": "lobby", 
                "x": 2, "y": 5, "width": 6, "height": 3
            },
            "main_hall": {
                "name": "Main Hall",
                "type": "meeting",
                "x": 10, "y": 2, "width": 8, "height": 6
            },
            "kitchen": {
                "name": "Community Kitchen",
                "type": "kitchen",
                "x": 2, "y": 2, "width": 4, "height": 3
            },
            "office": {
                "name": "Admin Office",
                "type": "office",
                "x": 15, "y": 9, "width": 3, "height": 2
            },
            "storage": {
                "name": "Storage",
                "type": "storage",
                "x": 6, "y": 2, "width": 2, "height": 2
            },
            "restrooms": {
                "name": "Restrooms",
                "type": "restroom",
                "x": 8, "y": 5, "width": 2, "height": 3
            },
            "outdoor": {
                "name": "Outdoor Terrace",
                "type": "outdoor",
                "x": 10, "y": 9, "width": 5, "height": 3
            }
        }
    
    def _get_hospital_spaces(self) -> Dict[str, Dict]:
        """Define spaces for a hospital."""
        return {
            "entrance": {
                "name": "Main Entrance",
                "type": "entrance",
                "x": 8, "y": 1, "width": 4, "height": 2
            },
            "lobby": {
                "name": "Reception Lobby",
                "type": "lobby",
                "x": 5, "y": 3, "width": 10, "height": 4
            },
            "waiting": {
                "name": "Waiting Area",
                "type": "meeting",
                "x": 2, "y": 7, "width": 6, "height": 3
            },
            "consultation": {
                "name": "Consultation Rooms",
                "type": "office",
                "x": 15, "y": 3, "width": 5, "height": 7
            },
            "treatment": {
                "name": "Treatment Area",
                "type": "service",
                "x": 8, "y": 7, "width": 7, "height": 4
            },
            "pharmacy": {
                "name": "Pharmacy",
                "type": "service",
                "x": 2, "y": 3, "width": 3, "height": 4
            },
            "courtyard": {
                "name": "Healing Courtyard",
                "type": "outdoor",
                "x": 10, "y": 11, "width": 6, "height": 4
            }
        }
    
    def _get_generic_spaces(self) -> Dict[str, Dict]:
        """Define generic spaces."""
        return {
            "entrance": {
                "name": "Entrance",
                "type": "entrance",
                "x": 5, "y": 1, "width": 3, "height": 2
            },
            "main_space": {
                "name": "Main Space",
                "type": "meeting",
                "x": 3, "y": 3, "width": 8, "height": 6
            },
            "support": {
                "name": "Support Space",
                "type": "service",
                "x": 11, "y": 3, "width": 4, "height": 3
            },
            "outdoor": {
                "name": "Outdoor Area",
                "type": "outdoor",
                "x": 6, "y": 9, "width": 5, "height": 3
            }
        }
    
    def _render_space_analysis_questions(self):
        """Render analysis questions based on selected spaces."""
        st.markdown("### 🤔 Spatial Analysis")
        
        # Space relationship analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Adjacency Analysis**")
            if st.button("Analyze Space Relationships", key="analyze_adjacency"):
                self._show_adjacency_analysis()
        
        with col2:
            st.markdown("**Circulation Analysis**")
            if st.button("Analyze Movement Patterns", key="analyze_circulation"):
                self._show_circulation_analysis()
        
        # Interactive questions
        st.markdown("**Design Questions:**")
        
        questions = [
            "Which spaces should be closest to the entrance?",
            "How do people move between different areas?",
            "Which spaces need natural light?",
            "What spaces require privacy?",
            "How do service functions connect?"
        ]
        
        selected_question = st.selectbox("Choose a question to explore:", questions)
        
        if st.button("Explore This Question", key="explore_question"):
            self._provide_spatial_guidance(selected_question)
    
    def _show_adjacency_analysis(self):
        """Show adjacency matrix and relationships."""
        st.markdown("**Space Adjacency Matrix**")
        
        # Create a simple adjacency visualization
        spaces = ["Entrance", "Lobby", "Main Hall", "Kitchen", "Office", "Outdoor"]
        
        # Create adjacency matrix (simplified)
        adjacency_data = np.random.choice([0, 1, 2], size=(len(spaces), len(spaces)), p=[0.3, 0.5, 0.2])
        np.fill_diagonal(adjacency_data, 0)
        
        fig = px.imshow(
            adjacency_data,
            x=spaces,
            y=spaces,
            color_continuous_scale=['white', 'lightblue', 'darkblue'],
            title="Space Adjacency Relationships"
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Legend:**
        - White: No direct relationship
        - Light Blue: Adjacent/nearby
        - Dark Blue: Direct connection required
        """)
    
    def _show_circulation_analysis(self):
        """Show circulation flow analysis."""
        st.markdown("**Circulation Flow Analysis**")
        
        # Create circulation flow diagram
        fig = go.Figure()
        
        # Add flow arrows (simplified)
        flow_paths = [
            {"start": (6.5, 9), "end": (5, 6.5), "label": "Entry Flow"},
            {"start": (5, 6.5), "end": (14, 5), "label": "To Main Hall"},
            {"start": (5, 6.5), "end": (4, 3.5), "label": "To Kitchen"},
            {"start": (14, 5), "end": (12.5, 10.5), "label": "To Outdoor"}
        ]
        
        for path in flow_paths:
            fig.add_annotation(
                x=path["end"][0], y=path["end"][1],
                ax=path["start"][0], ay=path["start"][1],
                xref="x", yref="y",
                axref="x", ayref="y",
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=2,
                arrowcolor="red",
                text=path["label"],
                showarrow=True
            )
        
        fig.update_layout(
            title="Primary Circulation Flows",
            xaxis=dict(range=[0, 20], showgrid=True),
            yaxis=dict(range=[0, 15], showgrid=True),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _provide_spatial_guidance(self, question: str):
        """Provide guidance based on selected question."""
        guidance_map = {
            "Which spaces should be closest to the entrance?": {
                "answer": "Reception, lobby, and information areas should be immediately accessible from the entrance.",
                "principles": ["Wayfinding clarity", "First impressions", "Security control"],
                "examples": ["Hospital reception", "Hotel lobby", "Office reception"]
            },
            "How do people move between different areas?": {
                "answer": "Clear circulation paths with visual connections and logical flow patterns.",
                "principles": ["Intuitive navigation", "Minimal conflicts", "Universal accessibility"],
                "examples": ["Central corridor", "Atrium circulation", "Gallery spine"]
            },
            "Which spaces need natural light?": {
                "answer": "Occupied spaces, especially those for extended use, benefit most from natural light.",
                "principles": ["Human comfort", "Energy efficiency", "Circadian rhythms"],
                "examples": ["Offices", "Classrooms", "Patient rooms"]
            }
        }
        
        if question in guidance_map:
            guidance = guidance_map[question]
            
            st.success(f"**Answer:** {guidance['answer']}")
            
            st.markdown("**Key Principles:**")
            for principle in guidance['principles']:
                st.markdown(f"• {principle}")
            
            st.markdown("**Examples:**")
            for example in guidance['examples']:
                st.markdown(f"• {example}")
    
    def _render_spatial_feedback(self):
        """Render feedback on spatial analysis."""
        st.markdown("### 📊 Your Analysis")
        
        if st.button("Get Spatial Feedback", key="spatial_feedback"):
            feedback_items = [
                "✅ Good adjacency between entrance and lobby",
                "⚠️ Consider kitchen ventilation and service access",
                "✅ Outdoor space well-connected to main hall",
                "💡 Storage location could be more central for efficiency"
            ]
            
            for item in feedback_items:
                if item.startswith("✅"):
                    st.success(item)
                elif item.startswith("⚠️"):
                    st.warning(item)
                else:
                    st.info(item)
            
            # Award points for analysis
            st.balloons()
            st.success("🎉 Spatial analysis completed! +30 XP earned!")
    
    def _render_circulation_challenge(self, building_type: str):
        """Render circulation flow challenge."""
        st.markdown("### 🔄 Challenge: Design Circulation Flow")
        st.markdown("Analyze and optimize movement patterns through the space.")
        
        # Create circulation diagram
        fig = self._create_circulation_diagram(building_type)
        st.plotly_chart(fig, use_container_width=True)
        
        # Circulation analysis tools
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Flow Analysis**")
            flow_type = st.selectbox(
                "Select flow type:",
                ["Primary circulation", "Secondary paths", "Emergency egress", "Service access"]
            )
            
            if st.button("Analyze Flow", key="analyze_flow"):
                st.info(f"Analyzing {flow_type.lower()}...")
                # Add flow analysis logic here
        
        with col2:
            st.markdown("**Optimization**")
            if st.button("Suggest Improvements", key="suggest_improvements"):
                improvements = [
                    "Widen main corridor for better flow",
                    "Add secondary exit for emergency egress",
                    "Create visual connection between levels",
                    "Separate service and public circulation"
                ]
                
                for improvement in improvements:
                    st.markdown(f"💡 {improvement}")
    
    def _create_circulation_diagram(self, building_type: str) -> go.Figure:
        """Create circulation flow diagram."""
        fig = go.Figure()
        
        # Add base floor plan (simplified)
        spaces = self._get_community_center_spaces()
        
        for space_id, space_data in spaces.items():
            fig.add_shape(
                type="rect",
                x0=space_data['x'], y0=space_data['y'],
                x1=space_data['x'] + space_data['width'],
                y1=space_data['y'] + space_data['height'],
                fillcolor=self.space_types[space_data['type']]['color'],
                opacity=0.3,
                line=dict(color="gray", width=1)
            )
        
        # Add circulation paths
        circulation_paths = [
            {"points": [(6.5, 9), (5, 6.5), (14, 5)], "width": 3, "color": "red", "name": "Primary"},
            {"points": [(5, 6.5), (4, 3.5)], "width": 2, "color": "blue", "name": "Secondary"},
            {"points": [(14, 5), (12.5, 10.5)], "width": 2, "color": "green", "name": "To Outdoor"}
        ]
        
        for path in circulation_paths:
            points = path["points"]
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='lines+markers',
                line=dict(color=path["color"], width=path["width"]),
                name=path["name"],
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title="Circulation Flow Analysis",
            xaxis=dict(range=[0, 20], showgrid=True),
            yaxis=dict(range=[0, 15], showgrid=True),
            height=500
        )
        
        return fig
    
    def _render_zoning_challenge(self, building_type: str):
        """Render functional zoning challenge."""
        st.markdown("### 📊 Challenge: Functional Zoning")
        st.markdown("Organize spaces by function and analyze relationships.")
        
        # Zoning diagram
        fig = self._create_zoning_diagram(building_type)
        st.plotly_chart(fig, use_container_width=True)
        
        # Zoning analysis
        st.markdown("**Zoning Analysis Tools**")
        
        zone_types = ["Public", "Semi-Public", "Private", "Service", "Outdoor"]
        selected_zones = st.multiselect("Select zones to analyze:", zone_types)
        
        if selected_zones and st.button("Analyze Selected Zones", key="analyze_zones"):
            for zone in selected_zones:
                st.markdown(f"**{zone} Zone Analysis:**")
                # Add zone-specific analysis
                if zone == "Public":
                    st.info("High visibility, easy access, welcoming atmosphere")
                elif zone == "Private":
                    st.info("Controlled access, acoustic privacy, security")
                # Add more zone analyses...
    
    def _create_zoning_diagram(self, building_type: str) -> go.Figure:
        """Create functional zoning diagram."""
        fig = go.Figure()
        
        # Define zones with colors
        zones = {
            "public": {"color": "#e74c3c", "spaces": ["entrance", "lobby", "main_hall"]},
            "semi_public": {"color": "#f39c12", "spaces": ["kitchen", "outdoor"]},
            "private": {"color": "#3498db", "spaces": ["office"]},
            "service": {"color": "#27ae60", "spaces": ["storage", "restrooms"]}
        }
        
        spaces = self._get_community_center_spaces()
        
        for zone_name, zone_data in zones.items():
            for space_id in zone_data["spaces"]:
                if space_id in spaces:
                    space = spaces[space_id]
                    fig.add_shape(
                        type="rect",
                        x0=space['x'], y0=space['y'],
                        x1=space['x'] + space['width'],
                        y1=space['y'] + space['height'],
                        fillcolor=zone_data['color'],
                        opacity=0.6,
                        line=dict(color="black", width=2)
                    )
        
        fig.update_layout(
            title="Functional Zoning Diagram",
            xaxis=dict(range=[0, 20], showgrid=True),
            yaxis=dict(range=[0, 15], showgrid=True),
            height=500
        )
        
        return fig
    
    def _render_site_planning_challenge(self, building_type: str):
        """Render site planning challenge."""
        st.markdown("### 🌍 Challenge: Site Planning")
        st.markdown("Consider site context, orientation, and landscape integration.")
        
        # Site plan diagram
        fig = self._create_site_plan(building_type)
        st.plotly_chart(fig, use_container_width=True)
        
        # Site analysis tools
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Site Factors**")
            factors = st.multiselect(
                "Consider these factors:",
                ["Solar orientation", "Prevailing winds", "Views", "Noise", "Access", "Topography"]
            )
        
        with col2:
            st.markdown("**Design Response**")
            if factors and st.button("Generate Site Strategy", key="site_strategy"):
                strategies = {
                    "Solar orientation": "Orient main spaces south for natural light",
                    "Prevailing winds": "Use building form for natural ventilation",
                    "Views": "Frame important views with openings",
                    "Noise": "Buffer noisy areas with service spaces",
                    "Access": "Create clear arrival sequence",
                    "Topography": "Work with natural grade changes"
                }
                
                for factor in factors:
                    if factor in strategies:
                        st.success(f"**{factor}:** {strategies[factor]}")
    
    def _create_site_plan(self, building_type: str) -> go.Figure:
        """Create site plan diagram."""
        fig = go.Figure()
        
        # Add site boundary
        fig.add_shape(
            type="rect",
            x0=0, y0=0, x1=30, y1=20,
            line=dict(color="black", width=3),
            fillcolor="lightgreen",
            opacity=0.2
        )
        
        # Add building footprint
        fig.add_shape(
            type="rect",
            x0=8, y0=6, x1=22, y1=14,
            fillcolor="gray",
            opacity=0.8,
            line=dict(color="black", width=2)
        )
        
        # Add site features
        features = [
            {"type": "circle", "x": 5, "y": 5, "r": 2, "color": "green", "name": "Existing Tree"},
            {"type": "circle", "x": 25, "y": 15, "r": 1.5, "color": "green", "name": "New Planting"},
            {"type": "rect", "x": 0, "y": 18, "w": 30, "h": 2, "color": "blue", "name": "Street"}
        ]
        
        for feature in features:
            if feature["type"] == "circle":
                fig.add_shape(
                    type="circle",
                    x0=feature["x"]-feature["r"], y0=feature["y"]-feature["r"],
                    x1=feature["x"]+feature["r"], y1=feature["y"]+feature["r"],
                    fillcolor=feature["color"],
                    opacity=0.7
                )
            elif feature["type"] == "rect":
                fig.add_shape(
                    type="rect",
                    x0=feature["x"], y0=feature["y"],
                    x1=feature["x"]+feature["w"], y1=feature["y"]+feature["h"],
                    fillcolor=feature["color"],
                    opacity=0.7
                )
        
        # Add north arrow
        fig.add_annotation(
            x=28, y=18,
            text="N ↑",
            showarrow=False,
            font=dict(size=16, color="black"),
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )
        
        fig.update_layout(
            title="Site Plan Analysis",
            xaxis=dict(range=[0, 30], showgrid=True),
            yaxis=dict(range=[0, 20], showgrid=True),
            height=500
        )
        
        return fig
    
    def _render_generic_spatial_challenge(self, building_type: str):
        """Render a generic spatial challenge."""
        st.markdown("### 🏗️ Spatial Design Challenge")
        st.markdown("Explore spatial relationships and design principles.")
        
        # Generic interactive diagram
        fig = self._create_floor_plan(building_type)
        st.plotly_chart(fig, use_container_width=True)
        
        # Generic analysis tools
        st.markdown("**Analysis Tools**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Analyze Adjacencies", key="generic_adjacency"):
                st.info("Analyzing space relationships...")
        
        with col2:
            if st.button("Check Circulation", key="generic_circulation"):
                st.info("Evaluating movement patterns...")
        
        with col3:
            if st.button("Assess Lighting", key="generic_lighting"):
                st.info("Analyzing natural light access...")

# Global instance
interactive_diagrams = InteractiveDiagramSystem()
