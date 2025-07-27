"""
Interactive Graph ML Visualizations using PyVis
Full interactive network visualizations for cognitive benchmarking with physics simulation
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
import numpy as np
from pyvis.network import Network
import networkx as nx
from collections import Counter, defaultdict
from datetime import datetime
import colorsys


class PyVisGraphMLVisualizer:
    """Create fully interactive Graph ML visualizations using PyVis"""
    
    def __init__(self, results_path: str = "benchmarking/results"):
        self.results_path = Path(results_path)
        self.load_data()
        
        # Custom color scheme from thesis palette
        self.colors = {
            'proficiency': {
                'beginner': '#cd766d',      # Warm coral
                'intermediate': '#d99c66',   # Warm orange
                'advanced': '#784c80',       # Purple
                'expert': '#4f3a3e'          # Dark purple-brown
            },
            'cognitive': {
                'deep_thinking': '#4f3a3e',  # Dark purple-brown
                'reflection': '#5c4f73',     # Purple-blue
                'scaffolding': '#784c80',    # Purple
                'metacognition': '#b87189',  # Dusty rose
                'critical_analysis': '#cf436f', # Pink
                'synthesis': '#cda29a'       # Light dusty rose
            },
            'agents': {
                'SocraticTutor': '#cf436f',     # Pink (engaging)
                'AnalysisAgent': '#784c80',     # Purple (analytical)
                'CognitiveEnhancement': '#5c4f73', # Purple-blue (cognitive)
                'DomainExpert': '#4f3a3e',      # Dark (expertise)
                'ContextAgent': '#d99c66',      # Orange (contextual)
                'Orchestrator': '#b87189'       # Dusty rose (coordinator)
            },
            'architecture': {
                'spatial': '#5c4f73',        # Purple-blue
                'form': '#784c80',           # Purple
                'function': '#d99c66',       # Orange
                'context': '#cda29a',        # Light dusty rose
                'materiality': '#dcc188',    # Beige
                'sustainability': '#e0ceb5'  # Light beige
            },
            'default': '#cda29a',            # Light dusty rose as default
            'edge': '#e0ceb5',               # Light beige for edges
            'text': '#4f3a3e'                # Dark purple-brown for text
        }
        
    def load_data(self):
        """Load benchmarking data"""
        try:
            # Load evaluation reports
            eval_dir = self.results_path / "evaluation_reports"
            self.evaluation_reports = {}
            
            if eval_dir.exists():
                for file in eval_dir.glob("*_evaluation.json"):
                    with open(file, 'r') as f:
                        session_id = file.stem.replace("_evaluation", "")
                        self.evaluation_reports[session_id] = json.load(f)
            
            # Load benchmark report
            benchmark_file = self.results_path / "benchmark_report.json"
            if benchmark_file.exists():
                with open(benchmark_file, 'r') as f:
                    self.benchmark_data = json.load(f)
            else:
                self.benchmark_data = {}
                
        except Exception as e:
            print(f"Error loading data: {e}")
            self.evaluation_reports = {}
            self.benchmark_data = {}
    
    def _create_network(self, height="800px", width="100%", directed=False):
        """Create a properly configured network with white background and thesis styling"""
        net = Network(
            height=height,
            width=width,
            bgcolor="#ffffff",  # White background
            font_color=self.colors['text'],  # Dark text
            notebook=False,
            directed=directed,
            select_menu=False,  # Disable selection menu for cleaner view
            filter_menu=False,  # Disable filter menu for cleaner view
            cdn_resources='in_line'  # Include all resources inline
        )
        return net
    
    def _get_standard_options(self, physics_enabled=True, layout_type="force"):
        """Get standard options configuration for consistent styling"""
        base_options = {
            "nodes": {
                "font": {
                    "size": 14,
                    "face": "Arial",
                    "color": self.colors['text']
                },
                "shadow": {
                    "enabled": True,
                    "size": 10,
                    "x": 3,
                    "y": 3,
                    "color": "rgba(0,0,0,0.1)"
                },
                "borderWidth": 2,
                "borderWidthSelected": 3
            },
            "edges": {
                "smooth": {
                    "type": "continuous",
                    "roundness": 0.5
                },
                "width": 2,
                "color": {
                    "inherit": False
                },
                "font": {
                    "size": 12,
                    "color": self.colors['text'],
                    "strokeWidth": 3,
                    "strokeColor": "#ffffff"
                }
            },
            "interaction": {
                "hover": True,
                "tooltipDelay": 200,
                "hideEdgesOnDrag": False,
                "navigationButtons": True,
                "keyboard": True,
                "zoomView": True,
                "dragView": True
            },
            "manipulation": {
                "enabled": False
            }
        }
        
        # Add physics configuration
        if physics_enabled:
            if layout_type == "force":
                base_options["physics"] = {
                    "enabled": True,
                    "barnesHut": {
                        "gravitationalConstant": -30000,
                        "springConstant": 0.04,
                        "springLength": 100,
                        "centralGravity": 0.3,
                        "damping": 0.09
                    },
                    "stabilization": {
                        "enabled": True,
                        "iterations": 1000,
                        "updateInterval": 100
                    }
                }
            elif layout_type == "hierarchical":
                base_options["layout"] = {
                    "hierarchical": {
                        "enabled": True,
                        "direction": "UD",
                        "sortMethod": "directed",
                        "levelSeparation": 150,
                        "nodeSpacing": 100
                    }
                }
                base_options["physics"] = {"enabled": False}
        else:
            base_options["physics"] = {"enabled": False}
            
        return base_options
    
    def _add_legend_to_html(self, html: str, legend_items: list) -> str:
        """Add a custom legend to the HTML outside the main visualization"""
        legend_html = """
        <style>
            .legend-container {
                position: absolute;
                bottom: 10px;
                right: 10px;
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid #4f3a3e;
                border-radius: 6px;
                padding: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                font-family: Arial, sans-serif;
                z-index: 1000;
            }
            .legend-title {
                font-size: 13px;
                font-weight: bold;
                color: #4f3a3e;
                margin-bottom: 5px;
                text-align: center;
            }
            .legend-item {
                display: flex;
                align-items: center;
                margin: 4px 0;
            }
            .legend-color {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 6px;
                border: 1px solid #4f3a3e;
            }
            .legend-label {
                color: #4f3a3e;
                font-size: 11px;
            }
        </style>
        <div class="legend-container">
            <div class="legend-title">LEGEND</div>
        """
        
        for color, label in legend_items:
            legend_html += f"""
            <div class="legend-item">
                <div class="legend-color" style="background-color: {color};"></div>
                <div class="legend-label">{label}</div>
            </div>
            """
        
        legend_html += "</div>"
        
        # Insert legend HTML before closing body tag
        return html.replace('</body>', legend_html + '</body>')
    
    def create_knowledge_graph(self, output_file: str = "knowledge_graph.html"):
        """Create interactive knowledge graph showing architecture-cognition-AI relationships"""
        
        # Initialize PyVis network with white background
        net = self._create_network(directed=False)
        
        # Use repulsion physics like in the example for better spacing and centering
        net.repulsion(node_distance=120, spring_length=200)
        
        # Core concept nodes with more detailed categorization for color variety
        core_concepts = {
            # Spatial & Form concepts - Purple tones
            'Design Process': {'category': 'spatial_form', 'size': 40, 'level': 1},
            'Spatial Reasoning': {'category': 'spatial_form', 'size': 35, 'level': 1},
            'Form & Function': {'category': 'spatial_form', 'size': 30, 'level': 2},
            
            # Context & Environment - Orange/Beige tones
            'Context & Site': {'category': 'context_env', 'size': 30, 'level': 2},
            'Materiality': {'category': 'context_env', 'size': 25, 'level': 3},
            'Sustainability': {'category': 'context_env', 'size': 25, 'level': 3},
            
            # Critical Thinking - Dark purple-brown
            'Critical Thinking': {'category': 'critical', 'size': 40, 'level': 1},
            'Deep Analysis': {'category': 'critical', 'size': 25, 'level': 3},
            
            # Metacognitive - Dusty rose
            'Metacognition': {'category': 'metacognitive', 'size': 35, 'level': 1},
            'Reflection': {'category': 'metacognitive', 'size': 30, 'level': 2},
            
            # Synthesis & Integration - Light dusty rose
            'Synthesis': {'category': 'synthesis', 'size': 30, 'level': 2},
            'Pattern Recognition': {'category': 'synthesis', 'size': 25, 'level': 3},
            'Knowledge Integration': {'category': 'synthesis', 'size': 30, 'level': 2},
            
            # Teaching Methods - Pink
            'Socratic Method': {'category': 'teaching', 'size': 35, 'level': 1},
            'Cognitive Scaffolding': {'category': 'teaching', 'size': 35, 'level': 1},
            
            # System & Adaptation - Coral
            'Adaptive Learning': {'category': 'system', 'size': 30, 'level': 2},
            'Multi-Agent System': {'category': 'system', 'size': 25, 'level': 3},
            'Feedback Loops': {'category': 'system', 'size': 25, 'level': 3}
        }
        
        # Define category colors using the full palette
        category_colors = {
            'spatial_form': '#784c80',      # Purple
            'context_env': '#d99c66',       # Warm orange
            'critical': '#4f3a3e',          # Dark purple-brown
            'metacognitive': '#b87189',     # Dusty rose
            'synthesis': '#cda29a',         # Light dusty rose
            'teaching': '#cf436f',          # Pink
            'system': '#cd766d'             # Warm coral
        }
        
        # Add nodes with styling
        for concept, attrs in core_concepts.items():
            category = attrs['category']
            size = attrs['size']
            level = attrs['level']
            
            # Get color based on category
            color = category_colors.get(category, self.colors['default'])
            
            # Create hover text with details
            hover_text = f"""
            <b>{concept}</b><br>
            Category: {category.replace('_', ' ').title()}<br>
            Importance Level: {level}<br>
            <br>
            <i>Click and drag to explore connections</i>
            """
            
            net.add_node(
                concept,
                label=concept,
                title=hover_text.strip(),
                size=size,
                color={
                    'background': color,
                    'border': self.colors['text'],
                    'highlight': {
                        'background': color,
                        'border': self.colors['text']
                    }
                },
                level=level,
                font={'size': 12 + (4-level)*2, 'color': self.colors['text']},
                borderWidth=2,
                borderWidthSelected=4
            )
        
        # Define conceptual connections with weights
        connections = [
            # Architecture-Cognition bridges
            ('Design Process', 'Critical Thinking', 0.9),
            ('Design Process', 'Synthesis', 0.8),
            ('Spatial Reasoning', 'Pattern Recognition', 0.85),
            ('Form & Function', 'Deep Analysis', 0.7),
            ('Context & Site', 'Reflection', 0.75),
            ('Sustainability', 'Metacognition', 0.7),
            
            # Cognition-AI bridges
            ('Critical Thinking', 'Socratic Method', 0.9),
            ('Metacognition', 'Cognitive Scaffolding', 0.85),
            ('Reflection', 'Feedback Loops', 0.8),
            ('Deep Analysis', 'Knowledge Integration', 0.75),
            
            # Architecture-AI bridges
            ('Design Process', 'Adaptive Learning', 0.8),
            ('Spatial Reasoning', 'Multi-Agent System', 0.7),
            
            # Within-domain connections
            ('Form & Function', 'Materiality', 0.6),
            ('Context & Site', 'Sustainability', 0.7),
            ('Critical Thinking', 'Metacognition', 0.8),
            ('Socratic Method', 'Cognitive Scaffolding', 0.75)
        ]
        
        # Add edges with varying thickness based on weight
        for source, target, weight in connections:
            net.add_edge(
                source, 
                target,
                value=weight * 5,  # Edge thickness
                color={'color': self.colors['edge'], 'opacity': 0.3 + weight * 0.4},
                smooth={'type': 'curvedCW', 'roundness': 0.2}
            )
        
        # Add interaction data if available
        if self.evaluation_reports:
            # Analyze which concepts appear most in sessions
            concept_frequency = Counter()
            
            for session_id, report in self.evaluation_reports.items():
                if 'cognitive_patterns' in report:
                    patterns = report['cognitive_patterns']
                    for pattern in patterns.get('identified_patterns', []):
                        # Map patterns to concepts
                        if 'critical' in pattern.lower():
                            concept_frequency['Critical Thinking'] += 1
                        if 'spatial' in pattern.lower():
                            concept_frequency['Spatial Reasoning'] += 1
                        if 'reflect' in pattern.lower():
                            concept_frequency['Reflection'] += 1
            
            # Update node sizes based on actual usage
            for concept, freq in concept_frequency.items():
                if concept in net.get_nodes():
                    # Increase node size based on frequency
                    pass  # PyVis doesn't allow updating after creation
        
        # No legend nodes in the main graph - we'll add it in HTML later
        
        # Save the network with all resources inline and proper encoding
        output_path = str(self.results_path / "visualizations" / output_file)
        
        # Generate HTML and write with UTF-8 encoding to avoid issues
        html = net.generate_html(notebook=False)
        
        # Add legend for knowledge graph categories
        legend_items = [
            ('#784c80', 'Spatial & Form'),
            ('#d99c66', 'Context & Environment'),
            ('#4f3a3e', 'Critical Thinking'),
            ('#b87189', 'Metacognitive'),
            ('#cda29a', 'Synthesis & Integration'),
            ('#cf436f', 'Teaching Methods'),
            ('#cd766d', 'System & Adaptation')
        ]
        
        html = self._add_legend_to_html(html, legend_items)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return net
    
    def create_learning_trajectory_network(self, output_file: str = "learning_trajectories.html"):
        """Create interactive learning trajectory network showing skill progression paths"""
        
        # Initialize directed network for trajectories
        net = self._create_network(directed=True)
        
        # Use repulsion physics for better layout
        net.repulsion(node_distance=150, spring_length=250)
        
        # Skill progression hierarchy
        skills = ['Spatial Awareness', 'Design Principles', 'Critical Analysis', 
                 'System Thinking', 'Creative Synthesis']
        levels = ['Foundation', 'Developing', 'Proficient', 'Advanced', 'Expert']
        
        # Create skill nodes in hierarchical structure
        y_positions = {level: i * 150 for i, level in enumerate(levels[::-1])}
        x_positions = {skill: i * 200 - 400 for i, skill in enumerate(skills)}
        
        for skill in skills:
            for level in levels:
                node_id = f"{skill}_{level}"
                level_idx = levels.index(level)
                
                # Color gradient based on level
                color = self.colors['proficiency'].get(
                    ['beginner', 'intermediate', 'intermediate', 'advanced', 'expert'][level_idx],
                    self.colors['default']
                )
                
                # Size increases with level
                size = 15 + level_idx * 5
                
                hover_text = f"""
                <b>{skill}</b><br>
                Level: {level}<br>
                Proficiency: {level_idx + 1}/5<br>
                <br>
                Prerequisites: {level_idx} completed<br>
                Unlocks: {5 - level_idx - 1} levels
                """
                
                net.add_node(
                    node_id,
                    label=f"{skill}\n{level}",
                    title=hover_text.strip(),
                    size=size,
                    color={
                        'background': color,
                        'border': self.colors['text'],
                        'highlight': {
                            'background': color,
                            'border': self.colors['text']
                        }
                    },
                    level=level_idx,
                    x=x_positions[skill],
                    y=y_positions[level],
                    physics=False,  # Fixed positions for hierarchy
                    font={'size': 10 + level_idx, 'color': self.colors['text']},
                    borderWidth=2
                )
                
                # Add progression edges
                if level_idx > 0:
                    prev_node = f"{skill}_{levels[level_idx-1]}"
                    net.add_edge(
                        prev_node,
                        node_id,
                        arrows={'to': {'enabled': True, 'scaleFactor': 0.5}},
                        color={'color': self.colors['cognitive']['synthesis'], 'opacity': 0.6},
                        value=2
                    )
        
        # Add cross-skill dependencies
        dependencies = [
            ('Spatial Awareness_Proficient', 'Design Principles_Advanced', 'enables'),
            ('Design Principles_Proficient', 'Critical Analysis_Developing', 'supports'),
            ('Critical Analysis_Advanced', 'System Thinking_Developing', 'requires'),
            ('System Thinking_Proficient', 'Creative Synthesis_Foundation', 'unlocks')
        ]
        
        for source, target, relation in dependencies:
            net.add_edge(
                source,
                target,
                arrows={'to': {'enabled': True, 'scaleFactor': 0.5}},
                color={'color': '#FFA500', 'opacity': 0.4},
                value=1,
                title=relation,
                dashes=True
            )
        
        # Add learner nodes from actual data
        if self.evaluation_reports:
            learner_y = -200
            for i, (session_id, report) in enumerate(list(self.evaluation_reports.items())[:10]):
                if 'session_metrics' in report:
                    metrics = report['session_metrics']
                    skill_level = metrics.get('skill_progression', {}).get('final_level', 'beginner')
                    
                    learner_id = f"Learner_{i+1}"
                    color = self.colors['proficiency'].get(skill_level, self.colors['default'])
                    
                    # Calculate progress metrics
                    progress = metrics.get('skill_progression', {}).get('improvement_rate', 0)
                    interactions = len(report.get('interactions', []))
                    
                    hover_text = f"""
                    <b>{learner_id}</b><br>
                    Skill Level: {skill_level.title()}<br>
                    Progress Rate: {progress:.1%}<br>
                    Interactions: {interactions}<br>
                    Session: {session_id[:8]}...
                    """
                    
                    net.add_node(
                        learner_id,
                        label=learner_id,
                        title=hover_text.strip(),
                        size=20,
                        color=color,
                        shape='diamond',
                        x=i * 100 - 450,
                        y=learner_y,
                        physics=False
                    )
                    
                    # Connect to appropriate skill nodes
                    if skill_level == 'expert':
                        targets = ['Creative Synthesis_Advanced', 'System Thinking_Expert']
                    elif skill_level == 'advanced':
                        targets = ['System Thinking_Proficient', 'Critical Analysis_Advanced']
                    elif skill_level == 'intermediate':
                        targets = ['Critical Analysis_Developing', 'Design Principles_Proficient']
                    else:
                        targets = ['Spatial Awareness_Foundation', 'Design Principles_Foundation']
                    
                    for target in targets:
                        net.add_edge(
                            learner_id,
                            target,
                            arrows={'to': {'enabled': True, 'scaleFactor': 0.3}},
                            color={'color': '#3498DB', 'opacity': 0.3},
                            value=0.5
                        )
        
        # Disable physics for fixed layout
        net.toggle_physics(False)
        
        # Save the network with all resources inline and proper encoding
        output_path = str(self.results_path / "visualizations" / output_file)
        
        # Generate HTML and write with UTF-8 encoding to avoid issues
        html = net.generate_html(notebook=False)
        
        # Add legend for learning trajectories
        legend_items = [
            ('#cd766d', 'Beginner Level'),
            ('#d99c66', 'Intermediate Level'),
            ('#784c80', 'Advanced Level'),
            ('#4f3a3e', 'Expert Level'),
            ('#cda29a', 'Skill Node'),
            ('#3498DB', 'Learner Connection'),
            ('#FFA500', 'Cross-skill Dependency')
        ]
        
        html = self._add_legend_to_html(html, legend_items)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return net
    
    def create_agent_collaboration_network(self, output_file: str = "agent_collaboration.html"):
        """Create interactive agent collaboration network showing handoffs and interactions"""
        
        # Initialize network
        net = self._create_network(directed=True)
        
        # Use repulsion physics for agent network
        net.repulsion(node_distance=180, spring_length=200)
        
        # Agent nodes with roles
        agents = {
            'Orchestrator': {
                'role': 'Central coordinator',
                'size': 50,
                'interactions': 0,
                'central': True
            },
            'SocraticTutor': {
                'role': 'Guides through questions',
                'size': 40,
                'interactions': 0,
                'central': False
            },
            'AnalysisAgent': {
                'role': 'Analyzes visual artifacts',
                'size': 40,
                'interactions': 0,
                'central': False
            },
            'CognitiveEnhancement': {
                'role': 'Prevents cognitive offloading',
                'size': 40,
                'interactions': 0,
                'central': False
            },
            'DomainExpert': {
                'role': 'Provides architectural knowledge',
                'size': 35,
                'interactions': 0,
                'central': False
            },
            'ContextAgent': {
                'role': 'Maintains conversation continuity',
                'size': 35,
                'interactions': 0,
                'central': False
            }
        }
        
        # Analyze actual agent interactions from data
        agent_handoffs = defaultdict(lambda: defaultdict(int))
        agent_usage = Counter()
        
        if self.evaluation_reports:
            for session_id, report in self.evaluation_reports.items():
                if 'agent_metrics' in report:
                    metrics = report['agent_metrics']
                    
                    # Count agent usage
                    for agent, count in metrics.get('usage_count', {}).items():
                        agent_usage[agent] += count
                        if agent in agents:
                            agents[agent]['interactions'] += count
                    
                    # Track handoffs
                    handoffs = metrics.get('handoff_patterns', [])
                    for i in range(len(handoffs) - 1):
                        from_agent = handoffs[i]
                        to_agent = handoffs[i + 1]
                        agent_handoffs[from_agent][to_agent] += 1
        
        # Add agent nodes
        for agent_name, agent_info in agents.items():
            color = self.colors['agents'].get(agent_name, self.colors['default'])
            
            # Scale size based on usage
            base_size = agent_info['size']
            usage_boost = min(agent_usage.get(agent_name, 0) * 0.5, 20)
            size = base_size + usage_boost
            
            hover_text = f"""
            <b>{agent_name}</b><br>
            Role: {agent_info['role']}<br>
            Total Interactions: {agent_info['interactions']}<br>
            Usage Frequency: {agent_usage.get(agent_name, 0)}<br>
            <br>
            <i>{agent_info['role']}</i>
            """
            
            # Central node gets special treatment
            if agent_info['central']:
                shape = 'star'
                border_width = 3
            else:
                shape = 'dot'
                border_width = 2
            
            net.add_node(
                agent_name,
                label=agent_name,
                title=hover_text.strip(),
                size=size,
                color=color,
                shape=shape,
                borderWidth=border_width,
                borderWidthSelected=4,
                font={'size': 14 if agent_info['central'] else 12}
            )
        
        # Add edges for agent handoffs
        for from_agent, targets in agent_handoffs.items():
            for to_agent, count in targets.items():
                if from_agent in agents and to_agent in agents:
                    # Edge thickness based on frequency
                    value = min(1 + count * 0.5, 10)
                    
                    # Color intensity based on frequency
                    opacity = min(0.3 + count * 0.1, 0.8)
                    
                    net.add_edge(
                        from_agent,
                        to_agent,
                        value=value,
                        arrows={'to': {'enabled': True, 'scaleFactor': 0.5}},
                        color={'color': self.colors['cognitive']['synthesis'], 'opacity': opacity},
                        title=f"Handoffs: {count}",
                        smooth={'type': 'curvedCW', 'roundness': 0.2}
                    )
        
        # Add common interaction patterns as floating nodes
        patterns = [
            ('Question Analysis', 'Analyzes user questions for cognitive depth'),
            ('Knowledge Retrieval', 'Fetches relevant architectural knowledge'),
            ('Socratic Dialogue', 'Engages in questioning strategies'),
            ('Cognitive Monitoring', 'Tracks and prevents offloading')
        ]
        
        pattern_y = 300
        for i, (pattern_name, description) in enumerate(patterns):
            pattern_id = f"pattern_{i}"
            
            net.add_node(
                pattern_id,
                label=pattern_name,
                title=description,
                size=15,
                color='#95A5A6',
                shape='square',
                x=(i - 1.5) * 200,
                y=pattern_y,
                physics=False,
                font={'size': 10}
            )
            
            # Connect patterns to relevant agents
            if 'Question' in pattern_name:
                net.add_edge('AnalysisAgent', pattern_id, value=0.5, 
                           color={'color': self.colors['edge'], 'opacity': 0.3}, dashes=True)
            elif 'Knowledge' in pattern_name:
                net.add_edge('DomainExpert', pattern_id, value=0.5,
                           color={'color': self.colors['edge'], 'opacity': 0.3}, dashes=True)
            elif 'Socratic' in pattern_name:
                net.add_edge('SocraticTutor', pattern_id, value=0.5,
                           color={'color': self.colors['edge'], 'opacity': 0.3}, dashes=True)
            elif 'Cognitive' in pattern_name:
                net.add_edge('CognitiveEnhancement', pattern_id, value=0.5,
                           color={'color': self.colors['edge'], 'opacity': 0.3}, dashes=True)
        
        # Keep physics enabled for agent network
        
        # Save the network with all resources inline and proper encoding
        output_path = str(self.results_path / "visualizations" / output_file)
        
        # Generate HTML and write with UTF-8 encoding to avoid issues
        html = net.generate_html(notebook=False)
        
        # Add legend for agent collaboration
        legend_items = [
            ('#b87189', 'Orchestrator (Central)'),
            ('#cf436f', 'Socratic Tutor'),
            ('#784c80', 'Analysis Agent'),
            ('#5c4f73', 'Cognitive Enhancement'),
            ('#4f3a3e', 'Domain Expert'),
            ('#d99c66', 'Context Agent'),
            ('#cda29a', 'Agent Handoff'),
            ('#95A5A6', 'Interaction Pattern')
        ]
        
        html = self._add_legend_to_html(html, legend_items)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return net
    
    def create_cognitive_pattern_network(self, output_file: str = "cognitive_patterns.html"):
        """Create interactive cognitive pattern network showing thinking patterns and relationships"""
        
        # Initialize network
        net = self._create_network(directed=False)
        
        # Use repulsion physics for cognitive patterns
        net.repulsion(node_distance=200, spring_length=150)
        
        # Core cognitive patterns
        patterns = {
            'Deep Thinking': {
                'category': 'primary',
                'frequency': 0,
                'connections': ['Critical Analysis', 'Reflection', 'Synthesis']
            },
            'Critical Analysis': {
                'category': 'primary', 
                'frequency': 0,
                'connections': ['Pattern Recognition', 'Evaluation']
            },
            'Reflection': {
                'category': 'primary',
                'frequency': 0,
                'connections': ['Metacognition', 'Self-Assessment']
            },
            'Synthesis': {
                'category': 'secondary',
                'frequency': 0,
                'connections': ['Creative Thinking', 'Integration']
            },
            'Pattern Recognition': {
                'category': 'secondary',
                'frequency': 0,
                'connections': ['Spatial Reasoning', 'Abstract Thinking']
            },
            'Metacognition': {
                'category': 'secondary',
                'frequency': 0,
                'connections': ['Self-Regulation', 'Learning Awareness']
            },
            'Evaluation': {
                'category': 'supporting',
                'frequency': 0,
                'connections': ['Judgment', 'Criteria Application']
            },
            'Creative Thinking': {
                'category': 'supporting',
                'frequency': 0,
                'connections': ['Innovation', 'Divergent Thinking']
            }
        }
        
        # Analyze patterns from session data
        pattern_cooccurrence = defaultdict(lambda: defaultdict(int))
        
        if self.evaluation_reports:
            for session_id, report in self.evaluation_reports.items():
                if 'cognitive_patterns' in report:
                    identified = report['cognitive_patterns'].get('identified_patterns', [])
                    
                    # Count pattern frequencies
                    for pattern in identified:
                        pattern_name = pattern.split(':')[0].strip()
                        for key in patterns:
                            if key.lower() in pattern_name.lower():
                                patterns[key]['frequency'] += 1
                    
                    # Track co-occurrences
                    for i in range(len(identified)):
                        for j in range(i+1, len(identified)):
                            p1 = identified[i].split(':')[0].strip()
                            p2 = identified[j].split(':')[0].strip()
                            pattern_cooccurrence[p1][p2] += 1
        
        # Add pattern nodes
        for pattern_name, pattern_info in patterns.items():
            category = pattern_info['category']
            frequency = pattern_info['frequency']
            
            # Size based on frequency and category
            base_sizes = {'primary': 40, 'secondary': 30, 'supporting': 20}
            size = base_sizes.get(category, 20) + min(frequency * 2, 20)
            
            # Color based on category
            colors = {
                'primary': self.colors['cognitive']['deep_thinking'],
                'secondary': self.colors['cognitive']['reflection'],
                'supporting': self.colors['cognitive']['scaffolding']
            }
            color = colors.get(category, self.colors['default'])
            
            hover_text = f"""
            <b>{pattern_name}</b><br>
            Category: {category.title()}<br>
            Observed Frequency: {frequency}<br>
            <br>
            Cognitive pattern that indicates<br>
            {category} level thinking
            """
            
            net.add_node(
                pattern_name,
                label=pattern_name,
                title=hover_text.strip(),
                size=size,
                color=color,
                borderWidth=2,
                borderWidthSelected=4,
                font={'size': 12 if category == 'primary' else 10}
            )
        
        # Add connections between patterns
        added_edges = set()
        
        # Predefined connections
        for pattern_name, pattern_info in patterns.items():
            for connection in pattern_info['connections']:
                if connection in patterns:
                    edge_key = tuple(sorted([pattern_name, connection]))
                    if edge_key not in added_edges:
                        added_edges.add(edge_key)
                        
                        # Check co-occurrence frequency
                        cooccur = pattern_cooccurrence.get(pattern_name, {}).get(connection, 0)
                        value = 1 + min(cooccur * 0.5, 4)
                        opacity = 0.3 + min(cooccur * 0.1, 0.5)
                        
                        net.add_edge(
                            pattern_name,
                            connection,
                            value=value,
                            color={'color': self.colors['edge'], 'opacity': opacity},
                            title=f"Co-occurrences: {cooccur}"
                        )
        
        # Add observed co-occurrences not in predefined list
        for p1, connections in pattern_cooccurrence.items():
            for p2, count in connections.items():
                if count > 2:  # Only strong co-occurrences
                    edge_key = tuple(sorted([p1, p2]))
                    if edge_key not in added_edges:
                        added_edges.add(edge_key)
                        
                        # Find matching pattern nodes
                        p1_match = None
                        p2_match = None
                        for pattern in patterns:
                            if pattern.lower() in p1.lower():
                                p1_match = pattern
                            if pattern.lower() in p2.lower():
                                p2_match = pattern
                        
                        if p1_match and p2_match and p1_match != p2_match:
                            net.add_edge(
                                p1_match,
                                p2_match,
                                value=1 + count * 0.3,
                                color={'color': '#FFA500', 'opacity': 0.4},
                                title=f"Observed co-occurrences: {count}",
                                dashes=True
                            )
        
        # Add session clusters as background context
        if len(self.evaluation_reports) > 3:
            cluster_nodes = {
                'Novice Patterns': {'x': -400, 'y': 200},
                'Intermediate Patterns': {'x': 0, 'y': 200},
                'Advanced Patterns': {'x': 400, 'y': 200}
            }
            
            for cluster_name, position in cluster_nodes.items():
                net.add_node(
                    cluster_name,
                    label=cluster_name,
                    size=60,
                    color={'background': '#2C3E50', 'border': '#34495E'},
                    shape='ellipse',
                    x=position['x'],
                    y=position['y'],
                    physics=False,
                    font={'size': 14, 'color': '#7F8C8D'},
                    opacity=0.3
                )
        
        # Keep default repulsion physics
        
        # Save the network with all resources inline and proper encoding
        output_path = str(self.results_path / "visualizations" / output_file)
        
        # Generate HTML and write with UTF-8 encoding to avoid issues
        html = net.generate_html(notebook=False)
        
        # Add legend for cognitive patterns
        legend_items = [
            ('#4f3a3e', 'Primary Patterns'),
            ('#5c4f73', 'Secondary Patterns'),
            ('#784c80', 'Supporting Patterns'),
            ('#e0ceb5', 'Pattern Connection'),
            ('#FFA500', 'Observed Co-occurrence'),
            ('#2C3E50', 'Pattern Cluster')
        ]
        
        html = self._add_legend_to_html(html, legend_items)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return net
    
    def create_session_evolution_network(self, output_file: str = "session_evolution.html"):
        """Create interactive session evolution network showing learning progression over time"""
        
        # Initialize network
        net = self._create_network(directed=True)
        
        # Use repulsion physics for timeline
        net.repulsion(node_distance=150, spring_length=100)
        
        if not self.evaluation_reports:
            # Create demo data if no reports
            net.add_node("No Data", label="No session data available", size=30, color='#E74C3C')
            net.save_graph(str(self.results_path / "visualizations" / output_file))
            return net
        
        # Process sessions chronologically
        sessions = []
        for session_id, report in self.evaluation_reports.items():
            session_data = {
                'id': session_id,
                'metrics': report.get('session_metrics', {}),
                'timestamp': report.get('timestamp', ''),
                'interactions': len(report.get('interactions', [])),
                'cognitive_score': report.get('overall_scores', {}).get('total_score', 0)
            }
            sessions.append(session_data)
        
        # Sort by timestamp if available
        sessions.sort(key=lambda x: x['timestamp'])
        
        # Create timeline nodes
        timeline_y = 0
        x_spacing = 150
        
        for i, session in enumerate(sessions):
            session_id = session['id']
            node_id = f"Session_{i+1}"
            
            # Determine proficiency level
            skill_level = session['metrics'].get('skill_progression', {}).get('final_level', 'beginner')
            color = self.colors['proficiency'].get(skill_level, self.colors['default'])
            
            # Calculate metrics
            interactions = session['interactions']
            cog_score = session['cognitive_score']
            improvement = session['metrics'].get('skill_progression', {}).get('improvement_rate', 0)
            
            # Size based on interaction count
            size = 20 + min(interactions * 0.5, 30)
            
            hover_text = f"""
            <b>Session {i+1}</b><br>
            ID: {session_id[:8]}...<br>
            Skill Level: {skill_level.title()}<br>
            Interactions: {interactions}<br>
            Cognitive Score: {cog_score:.1f}<br>
            Improvement: {improvement:.1%}
            """
            
            net.add_node(
                node_id,
                label=f"S{i+1}\n{skill_level[:3].upper()}",
                title=hover_text.strip(),
                size=size,
                color=color,
                x=i * x_spacing,
                y=timeline_y,
                physics=False,
                borderWidth=2,
                borderWidthSelected=4
            )
            
            # Connect to previous session
            if i > 0:
                prev_node = f"Session_{i}"
                
                # Edge color based on improvement
                if improvement > 0.2:
                    edge_color = '#2ECC71'  # Green for good improvement
                elif improvement > 0:
                    edge_color = '#F39C12'  # Orange for some improvement  
                else:
                    edge_color = '#E74C3C'  # Red for no improvement
                
                net.add_edge(
                    prev_node,
                    node_id,
                    arrows={'to': {'enabled': True, 'scaleFactor': 0.5}},
                    color=edge_color,
                    value=2,
                    title=f"Progress: {improvement:.1%}"
                )
            
            # Add milestone indicators
            if skill_level in ['advanced', 'expert']:
                milestone_id = f"milestone_{i}"
                net.add_node(
                    milestone_id,
                    label="🏆",
                    size=15,
                    color='#F1C40F',
                    shape='star',
                    x=i * x_spacing,
                    y=timeline_y - 50,
                    physics=False,
                    title=f"Achieved {skill_level} level!"
                )
                
                net.add_edge(
                    node_id,
                    milestone_id,
                    color={'color': '#F1C40F', 'opacity': 0.3},
                    dashes=True
                )
        
        # Add cognitive pattern evolution
        pattern_timeline_y = 150
        
        # Track pattern emergence
        pattern_emergence = {}
        for i, session in enumerate(sessions):
            report = self.evaluation_reports.get(session['id'], {})
            patterns = report.get('cognitive_patterns', {}).get('identified_patterns', [])
            
            for pattern in patterns:
                pattern_type = pattern.split(':')[0].strip()
                if pattern_type not in pattern_emergence:
                    pattern_emergence[pattern_type] = i
        
        # Add pattern nodes
        for pattern_type, first_session in pattern_emergence.items():
            pattern_node_id = f"pattern_{pattern_type.replace(' ', '_')}"
            
            # Categorize pattern
            if 'deep' in pattern_type.lower() or 'critical' in pattern_type.lower():
                pattern_color = self.colors['cognitive']['deep_thinking']
            elif 'reflect' in pattern_type.lower():
                pattern_color = self.colors['cognitive']['reflection']
            else:
                pattern_color = self.colors['cognitive']['scaffolding']
            
            net.add_node(
                pattern_node_id,
                label=pattern_type,
                size=15,
                color=pattern_color,
                shape='square',
                x=first_session * x_spacing,
                y=pattern_timeline_y,
                physics=False,
                title=f"First emerged in Session {first_session + 1}",
                font={'size': 10}
            )
            
            # Connect to session where it emerged
            net.add_edge(
                f"Session_{first_session + 1}",
                pattern_node_id,
                color={'color': pattern_color, 'opacity': 0.3},
                dashes=True,
                arrows={'to': {'enabled': True, 'scaleFactor': 0.3}}
            )
        
        # Add legend
        legend_x = -200
        legend_y = -150
        
        legend_items = [
            ('Beginner', self.colors['proficiency']['beginner']),
            ('Intermediate', self.colors['proficiency']['intermediate']),
            ('Advanced', self.colors['proficiency']['advanced']),
            ('Expert', self.colors['proficiency']['expert'])
        ]
        
        for i, (label, color) in enumerate(legend_items):
            net.add_node(
                f"legend_{label}",
                label=label,
                size=10,
                color=color,
                x=legend_x + i * 100,
                y=legend_y,
                physics=False,
                shape='dot',
                font={'size': 10}
            )
        
        # Disable physics for timeline layout
        net.toggle_physics(False)
        
        # Save the network with all resources inline and proper encoding
        output_path = str(self.results_path / "visualizations" / output_file)
        
        # Generate HTML and write with UTF-8 encoding to avoid issues
        html = net.generate_html(notebook=False)
        
        # Add legend for session evolution
        legend_items = [
            ('#cd766d', 'Beginner Session'),
            ('#d99c66', 'Intermediate Session'),
            ('#784c80', 'Advanced Session'),
            ('#4f3a3e', 'Expert Session'),
            ('#F1C40F', 'Milestone Achievement'),
            ('#2ECC71', 'Good Progress'),
            ('#F39C12', 'Some Progress'),
            ('#E74C3C', 'No Progress')
        ]
        
        html = self._add_legend_to_html(html, legend_items)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return net
    
    def export_all_visualizations(self):
        """Export all interactive PyVis visualizations"""
        
        output_dir = self.results_path / "visualizations" / "pyvis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("\nGenerating Interactive PyVis Visualizations...")
        
        visualizations = [
            ("Knowledge Graph", self.create_knowledge_graph, "knowledge_graph_pyvis.html"),
            ("Learning Trajectories", self.create_learning_trajectory_network, "learning_trajectories_pyvis.html"),
            ("Agent Collaboration", self.create_agent_collaboration_network, "agent_collaboration_pyvis.html"),
            ("Cognitive Patterns", self.create_cognitive_pattern_network, "cognitive_patterns_pyvis.html"),
            ("Session Evolution", self.create_session_evolution_network, "session_evolution_pyvis.html")
        ]
        
        for name, method, filename in visualizations:
            try:
                print(f"  [*] Creating {name}...", end='')
                method(output_file=f"pyvis/{filename}")
                print(" Done!")
            except Exception as e:
                print(f" Error: {e}")
        
        # Create index page
        self._create_index_page(output_dir)
        
        print(f"\nAll PyVis visualizations exported to: {output_dir}")
        return output_dir
    
    def _create_index_page(self, output_dir):
        """Create an index page for all PyVis visualizations"""
        
        index_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MEGA - Interactive Graph ML Visualizations</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #ffffff;
                    color: {self.colors['text']};
                    margin: 0;
                    padding: 20px;
                }}
                h1 {{
                    text-align: center;
                    color: {self.colors['cognitive']['deep_thinking']};
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .viz-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                }}
                .viz-card {{
                    background: {self.colors['edge']};
                    border: 2px solid {self.colors['default']};
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    transition: transform 0.2s, box-shadow 0.2s;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .viz-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                    border-color: {self.colors['cognitive']['synthesis']};
                }}
                .viz-card h3 {{
                    color: {self.colors['cognitive']['reflection']};
                    margin-bottom: 10px;
                }}
                .viz-card p {{
                    color: {self.colors['text']};
                    font-size: 14px;
                    margin-bottom: 15px;
                }}
                .viz-card a {{
                    display: inline-block;
                    background: {self.colors['cognitive']['synthesis']};
                    color: #ffffff;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    transition: background 0.2s;
                }}
                .viz-card a:hover {{
                    background: {self.colors['cognitive']['metacognition']};
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>MEGA Architectural Mentor - Interactive Graph Visualizations</h1>
                <p style="text-align: center; color: #ccc;">
                    Fully interactive network visualizations powered by PyVis.<br>
                    Click and drag nodes, zoom, and explore the relationships.
                </p>
                
                <div class="viz-grid">
                    <div class="viz-card">
                        <h3>Knowledge Graph</h3>
                        <p>Explore the interconnected relationships between architectural concepts, 
                        cognitive processes, and AI components.</p>
                        <a href="knowledge_graph_pyvis.html" target="_blank">Open Visualization</a>
                    </div>
                    
                    <div class="viz-card">
                        <h3>Learning Trajectories</h3>
                        <p>Visualize skill progression paths and learner journeys through 
                        different proficiency levels.</p>
                        <a href="learning_trajectories_pyvis.html" target="_blank">Open Visualization</a>
                    </div>
                    
                    <div class="viz-card">
                        <h3>Agent Collaboration</h3>
                        <p>See how AI agents work together, their handoff patterns, 
                        and interaction frequencies.</p>
                        <a href="agent_collaboration_pyvis.html" target="_blank">Open Visualization</a>
                    </div>
                    
                    <div class="viz-card">
                        <h3>Cognitive Patterns</h3>
                        <p>Discover thinking patterns, their relationships, and how they 
                        emerge during learning sessions.</p>
                        <a href="cognitive_patterns_pyvis.html" target="_blank">Open Visualization</a>
                    </div>
                    
                    <div class="viz-card">
                        <h3>Session Evolution</h3>
                        <p>Track learning progression over time, skill development, 
                        and milestone achievements.</p>
                        <a href="session_evolution_pyvis.html" target="_blank">Open Visualization</a>
                    </div>
                </div>
                
                <div style="margin-top: 50px; text-align: center; color: #666;">
                    <p>MaCAD Thesis 2025 - Cognitive Benchmarking System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(output_dir / "index.html", 'w') as f:
            f.write(index_html)


# Main execution
if __name__ == "__main__":
    visualizer = PyVisGraphMLVisualizer()
    visualizer.export_all_visualizations()