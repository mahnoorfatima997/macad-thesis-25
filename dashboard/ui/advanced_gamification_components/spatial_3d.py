"""
3D Visualization Components for Spatial Reasoning
Interactive 3D space representations for architectural learning challenges.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import random
import math

class Spatial3DSystem:
    """3D visualization system for spatial reasoning challenges."""
    
    def __init__(self):
        self.visualization_types = {
            "massing": {
                "name": "Massing Study",
                "icon": "🏗️",
                "description": "3D building volumes and relationships"
            },
            "interior": {
                "name": "Interior Space",
                "icon": "🏠",
                "description": "3D interior spatial experience"
            },
            "site": {
                "name": "Site Context",
                "icon": "🌍",
                "description": "Building in 3D site context"
            },
            "section": {
                "name": "Section Study",
                "icon": "📐",
                "description": "3D sectional relationships"
            },
            "light": {
                "name": "Light Study",
                "icon": "☀️",
                "description": "3D daylighting analysis"
            }
        }
        
        self.material_library = {
            "concrete": {"color": "#95a5a6", "opacity": 0.8, "name": "Concrete"},
            "glass": {"color": "#3498db", "opacity": 0.3, "name": "Glass"},
            "wood": {"color": "#d35400", "opacity": 0.9, "name": "Wood"},
            "steel": {"color": "#34495e", "opacity": 0.9, "name": "Steel"},
            "brick": {"color": "#e74c3c", "opacity": 0.9, "name": "Brick"},
            "vegetation": {"color": "#27ae60", "opacity": 0.7, "name": "Vegetation"}
        }
        
        self._initialize_3d_state()
    
    def _initialize_3d_state(self):
        """Initialize 3D visualization state."""
        if 'spatial_3d_state' not in st.session_state:
            st.session_state.spatial_3d_state = {
                'current_view': 'perspective',
                'selected_elements': [],
                'material_assignments': {},
                'lighting_conditions': 'daylight',
                'analysis_mode': 'design'
            }
    
    def render_3d_challenge(self, challenge_type: str, building_type: str = "community_center"):
        """Render a 3D spatial reasoning challenge."""
        st.markdown("## 🎯 3D Spatial Challenge")
        
        if challenge_type == "massing_study":
            self._render_massing_challenge(building_type)
        elif challenge_type == "interior_experience":
            self._render_interior_challenge(building_type)
        elif challenge_type == "daylighting":
            self._render_lighting_challenge(building_type)
        elif challenge_type == "site_integration":
            self._render_site_challenge(building_type)
        else:
            self._render_generic_3d_challenge(building_type)
    
    def _render_massing_challenge(self, building_type: str):
        """Render 3D massing study challenge."""
        st.markdown("### 🏗️ Challenge: 3D Massing Study")
        st.markdown("Explore building volumes and their relationships in 3D space.")
        
        # Control panel
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("**Controls**")
            
            # View controls
            view_type = st.selectbox(
                "View Type:",
                ["Perspective", "Axonometric", "Bird's Eye", "Street Level"]
            )
            
            # Massing options
            show_context = st.checkbox("Show Context", value=True)
            show_materials = st.checkbox("Show Materials", value=False)
            
            # Analysis tools
            st.markdown("**Analysis**")
            if st.button("Analyze Proportions", key="analyze_proportions"):
                self._show_proportion_analysis()
            
            if st.button("Study Shadows", key="study_shadows"):
                self._show_shadow_analysis()
        
        with col2:
            # Create 3D massing model
            fig = self._create_3d_massing(building_type, show_context, show_materials)
            st.plotly_chart(fig, use_container_width=True)
        
        # Interactive questions
        self._render_massing_questions()
    
    def _create_3d_massing(self, building_type: str, show_context: bool = True, show_materials: bool = False) -> go.Figure:
        """Create 3D massing visualization."""
        fig = go.Figure()
        
        # Define building masses based on type
        if building_type == "community_center":
            masses = self._get_community_center_masses()
        elif building_type == "hospital":
            masses = self._get_hospital_masses()
        else:
            masses = self._get_generic_masses()
        
        # Add building masses
        for mass_id, mass_data in masses.items():
            material = mass_data.get('material', 'concrete')
            material_props = self.material_library[material]
            
            # Create 3D box for each mass
            x, y, z = mass_data['position']
            w, d, h = mass_data['dimensions']
            
            # Define vertices of the box
            vertices = [
                [x, y, z], [x+w, y, z], [x+w, y+d, z], [x, y+d, z],  # bottom
                [x, y, z+h], [x+w, y, z+h], [x+w, y+d, z+h], [x, y+d, z+h]  # top
            ]
            
            # Define faces (using vertex indices)
            faces = [
                [0, 1, 2, 3],  # bottom
                [4, 7, 6, 5],  # top
                [0, 4, 5, 1],  # front
                [2, 6, 7, 3],  # back
                [0, 3, 7, 4],  # left
                [1, 5, 6, 2]   # right
            ]
            
            # Add mesh3d for the building mass
            x_coords = [v[0] for v in vertices]
            y_coords = [v[1] for v in vertices]
            z_coords = [v[2] for v in vertices]
            
            fig.add_trace(go.Mesh3d(
                x=x_coords,
                y=y_coords,
                z=z_coords,
                color=material_props['color'] if show_materials else '#3498db',
                opacity=material_props['opacity'] if show_materials else 0.7,
                name=mass_data['name'],
                hovertemplate=f"<b>{mass_data['name']}</b><br>" +
                            f"Material: {material_props['name']}<br>" +
                            f"Dimensions: {w}×{d}×{h}<br>" +
                            "<extra></extra>"
            ))
        
        # Add context if requested
        if show_context:
            self._add_site_context(fig)
        
        # Update layout for 3D
        fig.update_layout(
            title="3D Massing Study",
            scene=dict(
                xaxis_title="X (meters)",
                yaxis_title="Y (meters)",
                zaxis_title="Z (meters)",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                aspectmode='cube'
            ),
            height=600
        )
        
        return fig
    
    def _get_community_center_masses(self) -> Dict[str, Dict]:
        """Define 3D masses for community center."""
        return {
            "main_hall": {
                "name": "Main Hall",
                "position": [10, 5, 0],
                "dimensions": [15, 12, 8],
                "material": "concrete"
            },
            "entrance": {
                "name": "Entrance Pavilion",
                "position": [5, 8, 0],
                "dimensions": [8, 6, 4],
                "material": "glass"
            },
            "admin": {
                "name": "Administration",
                "position": [25, 5, 0],
                "dimensions": [8, 8, 6],
                "material": "brick"
            },
            "kitchen": {
                "name": "Kitchen Block",
                "position": [10, 17, 0],
                "dimensions": [10, 6, 4],
                "material": "concrete"
            }
        }
    
    def _get_hospital_masses(self) -> Dict[str, Dict]:
        """Define 3D masses for hospital."""
        return {
            "main_building": {
                "name": "Main Hospital",
                "position": [15, 10, 0],
                "dimensions": [20, 15, 12],
                "material": "concrete"
            },
            "entrance": {
                "name": "Entrance Atrium",
                "position": [10, 12, 0],
                "dimensions": [8, 8, 15],
                "material": "glass"
            },
            "emergency": {
                "name": "Emergency Wing",
                "position": [35, 10, 0],
                "dimensions": [12, 10, 8],
                "material": "brick"
            },
            "parking": {
                "name": "Parking Structure",
                "position": [5, 25, 0],
                "dimensions": [25, 12, 6],
                "material": "concrete"
            }
        }
    
    def _get_generic_masses(self) -> Dict[str, Dict]:
        """Define generic 3D masses."""
        return {
            "main_volume": {
                "name": "Main Volume",
                "position": [10, 10, 0],
                "dimensions": [12, 10, 8],
                "material": "concrete"
            },
            "secondary": {
                "name": "Secondary Volume",
                "position": [22, 12, 0],
                "dimensions": [8, 6, 6],
                "material": "wood"
            }
        }
    
    def _add_site_context(self, fig: go.Figure):
        """Add site context elements to 3D visualization."""
        # Ground plane
        fig.add_trace(go.Mesh3d(
            x=[0, 50, 50, 0],
            y=[0, 0, 30, 30],
            z=[0, 0, 0, 0],
            color='lightgreen',
            opacity=0.3,
            name="Site Ground",
            showlegend=False
        ))
        
        # Context buildings (simplified)
        context_buildings = [
            {"pos": [0, 0, 0], "dim": [8, 8, 6], "name": "Context Building 1"},
            {"pos": [40, 20, 0], "dim": [6, 10, 8], "name": "Context Building 2"}
        ]
        
        for building in context_buildings:
            x, y, z = building['pos']
            w, d, h = building['dim']
            
            fig.add_trace(go.Mesh3d(
                x=[x, x+w, x+w, x, x, x+w, x+w, x],
                y=[y, y, y+d, y+d, y, y, y+d, y+d],
                z=[z, z, z, z, z+h, z+h, z+h, z+h],
                color='lightgray',
                opacity=0.4,
                name=building['name'],
                showlegend=False
            ))
        
        # Trees (simplified as cylinders)
        tree_positions = [(5, 5), (45, 25), (15, 25), (35, 5)]
        for i, (tx, ty) in enumerate(tree_positions):
            fig.add_trace(go.Scatter3d(
                x=[tx], y=[ty], z=[4],
                mode='markers',
                marker=dict(size=8, color='green', symbol='circle'),
                name=f"Tree {i+1}",
                showlegend=False
            ))
    
    def _show_proportion_analysis(self):
        """Show proportion analysis results."""
        st.markdown("**Proportion Analysis Results:**")
        
        analyses = [
            "✅ Main hall follows golden ratio proportions (1:1.618)",
            "⚠️ Entrance pavilion height could be increased for better proportion",
            "✅ Good relationship between building masses",
            "💡 Consider adding vertical element for visual balance"
        ]
        
        for analysis in analyses:
            if analysis.startswith("✅"):
                st.success(analysis)
            elif analysis.startswith("⚠️"):
                st.warning(analysis)
            else:
                st.info(analysis)
    
    def _show_shadow_analysis(self):
        """Show shadow analysis visualization."""
        st.markdown("**Shadow Study Analysis:**")
        
        # Create shadow study visualization
        fig = go.Figure()
        
        # Simplified shadow representation
        times = ["9 AM", "12 PM", "3 PM", "6 PM"]
        shadow_data = []
        
        for i, time in enumerate(times):
            # Simulate shadow positions (simplified)
            shadow_length = 10 - i * 2
            shadow_angle = i * 30
            
            x_shadow = shadow_length * math.cos(math.radians(shadow_angle))
            y_shadow = shadow_length * math.sin(math.radians(shadow_angle))
            
            fig.add_trace(go.Scatter(
                x=[15, 15 + x_shadow],
                y=[10, 10 + y_shadow],
                mode='lines+markers',
                name=f"Shadow at {time}",
                line=dict(width=3)
            ))
        
        fig.update_layout(
            title="Shadow Study Throughout the Day",
            xaxis_title="X (meters)",
            yaxis_title="Y (meters)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_massing_questions(self):
        """Render interactive questions for massing study."""
        st.markdown("### 🤔 Design Analysis")
        
        questions = [
            {
                "question": "How do the building masses relate to each other?",
                "options": ["Harmonious composition", "Needs better integration", "Too fragmented", "Well balanced"],
                "feedback": {
                    "Harmonious composition": "Good eye! The masses create a cohesive architectural composition.",
                    "Needs better integration": "Consider how connecting elements could unify the masses.",
                    "Too fragmented": "Think about ways to create visual connections between volumes.",
                    "Well balanced": "The proportional relationships work well together."
                }
            },
            {
                "question": "What is the primary organizing principle?",
                "options": ["Central courtyard", "Linear arrangement", "Clustered volumes", "Hierarchical composition"],
                "feedback": {
                    "Central courtyard": "A courtyard can create strong spatial organization.",
                    "Linear arrangement": "Linear organization can create clear circulation.",
                    "Clustered volumes": "Clustering allows for flexible relationships.",
                    "Hierarchical composition": "Hierarchy helps establish primary and secondary spaces."
                }
            }
        ]
        
        for i, q in enumerate(questions):
            st.markdown(f"**Question {i+1}:** {q['question']}")
            
            answer = st.radio(
                "Select your answer:",
                q['options'],
                key=f"massing_q_{i}"
            )
            
            if st.button(f"Get Feedback", key=f"feedback_{i}"):
                feedback = q['feedback'].get(answer, "Interesting perspective!")
                st.info(f"💭 **Feedback:** {feedback}")
    
    def _render_interior_challenge(self, building_type: str):
        """Render 3D interior experience challenge."""
        st.markdown("### 🏠 Challenge: Interior Spatial Experience")
        st.markdown("Explore how spaces feel and connect in three dimensions.")
        
        # Create 3D interior visualization
        fig = self._create_3d_interior(building_type)
        st.plotly_chart(fig, use_container_width=True)
        
        # Interior analysis tools
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Spatial Qualities**")
            qualities = st.multiselect(
                "Analyze these qualities:",
                ["Scale", "Proportion", "Light", "Views", "Circulation", "Acoustics"]
            )
            
            if qualities and st.button("Analyze Qualities", key="analyze_interior"):
                for quality in qualities:
                    self._provide_interior_analysis(quality)
        
        with col2:
            st.markdown("**User Experience**")
            user_type = st.selectbox(
                "Experience from perspective of:",
                ["First-time visitor", "Regular user", "Staff member", "Child", "Elderly person"]
            )
            
            if st.button("Simulate Experience", key="simulate_experience"):
                self._simulate_user_experience(user_type)
    
    def _create_3d_interior(self, building_type: str) -> go.Figure:
        """Create 3D interior space visualization."""
        fig = go.Figure()
        
        # Create interior space (simplified room)
        room_width, room_depth, room_height = 12, 10, 4
        
        # Floor
        fig.add_trace(go.Mesh3d(
            x=[0, room_width, room_width, 0],
            y=[0, 0, room_depth, room_depth],
            z=[0, 0, 0, 0],
            color='lightgray',
            opacity=0.8,
            name="Floor"
        ))
        
        # Walls
        walls = [
            # Front wall
            {"x": [0, room_width, room_width, 0], "y": [0, 0, 0, 0], "z": [0, 0, room_height, room_height]},
            # Back wall  
            {"x": [0, room_width, room_width, 0], "y": [room_depth, room_depth, room_depth, room_depth], "z": [0, 0, room_height, room_height]},
            # Left wall
            {"x": [0, 0, 0, 0], "y": [0, room_depth, room_depth, 0], "z": [0, 0, room_height, room_height]},
            # Right wall
            {"x": [room_width, room_width, room_width, room_width], "y": [0, room_depth, room_depth, 0], "z": [0, 0, room_height, room_height]}
        ]
        
        for i, wall in enumerate(walls):
            fig.add_trace(go.Mesh3d(
                x=wall["x"],
                y=wall["y"], 
                z=wall["z"],
                color='white',
                opacity=0.6,
                name=f"Wall {i+1}",
                showlegend=False
            ))
        
        # Add windows (as openings)
        window_positions = [
            {"x": 3, "y": 0, "w": 2, "h": 2, "wall": "front"},
            {"x": 7, "y": 0, "w": 2, "h": 2, "wall": "front"}
        ]
        
        for window in window_positions:
            fig.add_trace(go.Mesh3d(
                x=[window["x"], window["x"]+window["w"], window["x"]+window["w"], window["x"]],
                y=[0, 0, 0, 0],
                z=[1, 1, 1+window["h"], 1+window["h"]],
                color='lightblue',
                opacity=0.3,
                name="Window",
                showlegend=False
            ))
        
        # Add furniture (simplified)
        furniture = [
            {"name": "Table", "pos": [6, 5, 0], "dim": [2, 1, 0.8], "color": "brown"},
            {"name": "Chairs", "pos": [4, 4, 0], "dim": [0.5, 0.5, 1], "color": "blue"},
            {"name": "Chairs", "pos": [8, 4, 0], "dim": [0.5, 0.5, 1], "color": "blue"}
        ]
        
        for item in furniture:
            x, y, z = item["pos"]
            w, d, h = item["dim"]
            
            fig.add_trace(go.Mesh3d(
                x=[x, x+w, x+w, x, x, x+w, x+w, x],
                y=[y, y, y+d, y+d, y, y, y+d, y+d],
                z=[z, z, z, z, z+h, z+h, z+h, z+h],
                color=item["color"],
                opacity=0.8,
                name=item["name"],
                showlegend=False
            ))
        
        fig.update_layout(
            title="3D Interior Experience",
            scene=dict(
                xaxis_title="X (meters)",
                yaxis_title="Y (meters)", 
                zaxis_title="Z (meters)",
                camera=dict(
                    eye=dict(x=0.5, y=-1.5, z=0.8)
                ),
                aspectmode='cube'
            ),
            height=600
        )
        
        return fig
    
    def _provide_interior_analysis(self, quality: str):
        """Provide analysis for interior spatial qualities."""
        analyses = {
            "Scale": "The room scale feels appropriate for 10-15 people. Ceiling height creates comfortable intimacy.",
            "Proportion": "Room proportions follow classical ratios. Length-to-width ratio creates good spatial balance.",
            "Light": "Natural light from windows creates dynamic lighting throughout the day. Consider light quality.",
            "Views": "Windows frame exterior views and connect interior to landscape. Visual connections are important.",
            "Circulation": "Clear circulation paths around furniture. Consider how people move through the space.",
            "Acoustics": "Hard surfaces may create echo. Consider acoustic treatments for better sound quality."
        }
        
        analysis = analyses.get(quality, "This quality affects spatial experience significantly.")
        st.info(f"**{quality} Analysis:** {analysis}")
    
    def _simulate_user_experience(self, user_type: str):
        """Simulate user experience from different perspectives."""
        experiences = {
            "First-time visitor": "Entering the space, they look for orientation cues and feel the scale. Clear sightlines help navigation.",
            "Regular user": "Familiar with the layout, they move efficiently to their preferred areas. Comfort and functionality matter most.",
            "Staff member": "Focused on operational efficiency. They need clear access to controls and service areas.",
            "Child": "Experiences the space from a lower eye level. Safety, play opportunities, and visual interest are key.",
            "Elderly person": "Values comfort, accessibility, and clear wayfinding. Seating and support are important considerations."
        }
        
        experience = experiences.get(user_type, "Each user brings unique needs and perspectives to the space.")
        st.success(f"**{user_type} Experience:** {experience}")
    
    def _render_lighting_challenge(self, building_type: str):
        """Render 3D daylighting analysis challenge."""
        st.markdown("### ☀️ Challenge: Daylighting Analysis")
        st.markdown("Study how natural light affects spatial quality and user experience.")
        
        # Lighting controls
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("**Lighting Controls**")
            
            time_of_day = st.slider("Time of Day", 6, 18, 12, key="time_slider")
            season = st.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"])
            weather = st.selectbox("Weather", ["Clear", "Partly Cloudy", "Overcast"])
            
            if st.button("Update Lighting", key="update_lighting"):
                st.success(f"Updated lighting for {time_of_day}:00, {season}, {weather}")
        
        with col2:
            # Create lighting visualization
            fig = self._create_lighting_study(building_type, time_of_day, season, weather)
            st.plotly_chart(fig, use_container_width=True)
        
        # Lighting analysis
        self._render_lighting_analysis(time_of_day, season, weather)
    
    def _create_lighting_study(self, building_type: str, time: int, season: str, weather: str) -> go.Figure:
        """Create 3D lighting study visualization."""
        fig = go.Figure()
        
        # Create basic room structure
        fig = self._create_3d_interior(building_type)
        
        # Add light rays (simplified)
        sun_angle = self._calculate_sun_angle(time, season)
        light_intensity = self._calculate_light_intensity(weather)
        
        # Add light rays as lines
        for i in range(5):
            start_x = 3 + i * 1.5
            start_y = -2
            start_z = 6
            
            end_x = start_x + 2 * math.cos(math.radians(sun_angle))
            end_y = 8
            end_z = 1
            
            fig.add_trace(go.Scatter3d(
                x=[start_x, end_x],
                y=[start_y, end_y],
                z=[start_z, end_z],
                mode='lines',
                line=dict(color='yellow', width=3),
                opacity=light_intensity,
                name="Light Ray",
                showlegend=False
            ))
        
        fig.update_layout(title=f"Daylighting Study - {time}:00, {season}, {weather}")
        
        return fig
    
    def _calculate_sun_angle(self, time: int, season: str) -> float:
        """Calculate sun angle based on time and season."""
        base_angle = (time - 6) * 15  # 15 degrees per hour from 6 AM
        
        season_adjustment = {
            "Spring": 0,
            "Summer": 15,
            "Fall": 0,
            "Winter": -15
        }
        
        return base_angle + season_adjustment.get(season, 0)
    
    def _calculate_light_intensity(self, weather: str) -> float:
        """Calculate light intensity based on weather."""
        intensities = {
            "Clear": 0.9,
            "Partly Cloudy": 0.6,
            "Overcast": 0.3
        }
        
        return intensities.get(weather, 0.6)
    
    def _render_lighting_analysis(self, time: int, season: str, weather: str):
        """Render lighting analysis results."""
        st.markdown("### 📊 Lighting Analysis")
        
        # Calculate lighting metrics
        light_level = self._calculate_light_intensity(weather) * (1 - abs(12 - time) / 12)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Light Level", f"{light_level:.1%}", "Good" if light_level > 0.5 else "Low")
        
        with col2:
            glare_risk = "High" if time in [10, 11, 12, 13, 14] and weather == "Clear" else "Low"
            st.metric("Glare Risk", glare_risk)
        
        with col3:
            energy_savings = f"{light_level * 100:.0f}%"
            st.metric("Potential Energy Savings", energy_savings)
        
        # Recommendations
        st.markdown("**Recommendations:**")
        recommendations = []
        
        if light_level < 0.3:
            recommendations.append("💡 Consider additional artificial lighting")
        if light_level > 0.8 and weather == "Clear":
            recommendations.append("🌞 Consider shading devices to control glare")
        if season == "Winter":
            recommendations.append("❄️ Maximize south-facing windows for winter heat gain")
        
        for rec in recommendations:
            st.info(rec)
    
    def _render_site_challenge(self, building_type: str):
        """Render 3D site integration challenge."""
        st.markdown("### 🌍 Challenge: Site Integration")
        st.markdown("Study how the building relates to its 3D site context.")
        
        # Create 3D site visualization
        fig = self._create_3d_site(building_type)
        st.plotly_chart(fig, use_container_width=True)
        
        # Site analysis tools
        st.markdown("**Site Analysis Tools**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Analyze Topography", key="analyze_topo"):
                st.info("The site slopes gently from north to south. Consider how this affects drainage and views.")
        
        with col2:
            if st.button("Study Context", key="study_context"):
                st.info("Surrounding buildings create urban context. Consider scale relationships and privacy.")
        
        with col3:
            if st.button("Evaluate Access", key="evaluate_access"):
                st.info("Primary access from the south provides good visibility. Consider service access separately.")
    
    def _create_3d_site(self, building_type: str) -> go.Figure:
        """Create 3D site context visualization."""
        fig = go.Figure()
        
        # Create topographic ground
        x = np.linspace(0, 50, 20)
        y = np.linspace(0, 30, 15)
        X, Y = np.meshgrid(x, y)
        
        # Simple topography (slope from north to south)
        Z = 2 - (Y / 30) * 2 + np.sin(X/5) * 0.5
        
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale='Greens',
            opacity=0.7,
            name="Site Topography",
            showscale=False
        ))
        
        # Add building (elevated above ground)
        building_x, building_y = 20, 15
        ground_height = 2 - (building_y / 30) * 2
        
        fig.add_trace(go.Mesh3d(
            x=[building_x, building_x+12, building_x+12, building_x, 
               building_x, building_x+12, building_x+12, building_x],
            y=[building_y, building_y, building_y+10, building_y+10,
               building_y, building_y, building_y+10, building_y+10],
            z=[ground_height, ground_height, ground_height, ground_height,
               ground_height+8, ground_height+8, ground_height+8, ground_height+8],
            color='lightblue',
            opacity=0.8,
            name="Building"
        ))
        
        # Add context elements
        self._add_site_context(fig)
        
        fig.update_layout(
            title="3D Site Integration Study",
            scene=dict(
                xaxis_title="X (meters)",
                yaxis_title="Y (meters)",
                zaxis_title="Z (meters)",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                )
            ),
            height=600
        )
        
        return fig
    
    def _render_generic_3d_challenge(self, building_type: str):
        """Render generic 3D spatial challenge."""
        st.markdown("### 🏗️ 3D Spatial Exploration")
        st.markdown("Explore architectural space in three dimensions.")
        
        # Create generic 3D visualization
        fig = self._create_3d_massing(building_type)
        st.plotly_chart(fig, use_container_width=True)
        
        # Generic analysis tools
        st.markdown("**3D Analysis Tools**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Volume Analysis", key="volume_analysis"):
                st.info("Building volumes create interesting spatial relationships. Consider how they connect.")
        
        with col2:
            if st.button("Scale Study", key="scale_study"):
                st.info("The scale feels appropriate for human use. Consider proportional relationships.")
        
        with col3:
            if st.button("Material Study", key="material_study"):
                st.info("Material choices affect both appearance and performance. Consider context and function.")

# Global instance
spatial_3d = Spatial3DSystem()
