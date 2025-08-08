"""
Generate an interactive HTML table for dashboard features documentation
"""

import pandas as pd
import json
from pathlib import Path

def create_features_dataframe():
    """Create a comprehensive dataframe of all dashboard features"""
    
    features_data = []
    
    # Define reference links
    reference_links = {
        'Tukey (1977) Exploratory Data Analysis': 'https://archive.org/details/exploratorydataa0000tuke_7616',
        'Renkl (2002) Worked Examples & Cognitive Load': 'https://www.cambridge.org/core/books/abs/cognitive-load-theory/learning-from-workedout-examples-and-problem-solving/DBA85CE81E9A7B1B090547D12E2F2A04',
        'Marton & Säljö (1976) Deep vs Surface Learning': 'https://bpspsychub.onlinelibrary.wiley.com/doi/10.1111/j.2044-8279.1976.tb02980.x',
        'Bloom (1984) 2 Sigma Problem': 'https://journals.sagepub.com/doi/10.3102/0013189X013006004',
        'Newell & Rosenbloom (1981) Power Law of Practice': 'https://www.researchgate.net/profile/Paul-Rosenbloom/publication/243783833_Mechanisms_of_skill_acquisition_and_the_law_of_practice/links/5461086e0cf2c1a63bff7b62/Mechanisms-of-skill-acquisition-and-the-law-of-practice.pdf',
        'Dreyfus & Dreyfus (1980) Five-Stage Model': 'https://www.bumc.bu.edu/facdev-medicine/files/2012/03/Dreyfus-skill-level.pdf',
        'Pellegrino et al. (2001) Knowing What Students Know': 'https://nap.nationalacademies.org/catalog/10019/knowing-what-students-know-the-science-and-design-of-educational',
        'Biggs (1996) Constructive Alignment': 'https://www.researchgate.net/publication/220017462_Enhancing_Teaching_Through_Constructive_Alignment',
        'Cohen et al. (1982) Educational Outcomes Meta-Analysis': 'https://f.hubspotusercontent30.net/hubfs/5191137/attachments/publications/CEMWeb024%20Educational%20Outcomes%20Of%20Tutorings%20Meta%20Analysis.pdf',
        'Anderson (1982) Acquisition of Cognitive Skill': 'http://act-r.psy.cmu.edu/wordpress/wp-content/uploads/2012/12/63ACS_JRA_PR.1982.pdf',
        'Wooldridge & Jennings (1995) Intelligent Agents': 'https://www.cs.cmu.edu/~motionplanning/papers/sbp_papers/integrated1/woodridge_intelligent_agents.pdf',
        'Zerkouk et al. (2025) AI-based Intelligent Tutoring Systems': 'https://arxiv.org/html/2507.18882v1',
        'Romero & Ventura (2020) Educational Data Mining': 'https://bookdown.org/chen/la-manual/files/Romero%20and%20Ventura%20-%202020.pdf',
        'Black & Wiliam (1998) Assessment in Education': 'https://www.gla.ac.uk/t4/learningandteaching/files/PGCTHE/BlackandWiliam1998.pdf',
        'Breiman (2001) Random Forests': 'https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf',
        'Ryan & Deci (2000) Self-Determination Theory': 'https://selfdeterminationtheory.org/SDT/documents/2000_RyanDeci_SDT.pdf',
        'Nass & Moon (2000) Machines and Mindlessness': 'https://www.coli.uni-saarland.de/courses/agentinteraction/contents/papers/Nass00.pdf',
        'Cottone et al. (2021) Ethical Decision Making Processes': 'https://connect.springerpub.com/binary/sgrworks/34598e5a4cbf1a9c/0ceb67abe3678cce2ed9c8f19e188f04c646d46db5af983d91d6ce025c568e36/9780826135292_0004.pdf',
        'Spiro et al. (1988) Cognitive Flexibility Theory': 'https://core.ac.uk/download/pdf/4826446.pdf',
        'Goldschmidt (1990) Linkography Method': 'https://www.researchgate.net/publication/285995351_Linkography_Assessing_design_productivity',
        'Goldschmidt (1991) The Dialectics of Sketching': 'https://www.researchgate.net/publication/285995351_Linkography_Assessing_design_productivity',
        'Goldschmidt (2014) Unfolding the Design Process': 'https://direct.mit.edu/books/monograph/2197/LinkographyUnfolding-the-Design-Process',
        'Goldschmidt (2017) Concurrent Divergent and Convergent Thinking': 'https://users.metu.edu.tr/baykan/arch586/Readings/Cognition/PresentationPapers/Goldschmidt16.pdf',
        'Chi (2009) Active-Constructive-Interactive': 'https://onlinelibrary.wiley.com/doi/10.1111/j.1756-8765.2008.01005.x',
        'Entwistle (2000) Promoting Deep Learning': 'https://www.researchgate.net/publication/241049278_Promoting_deep_learning_through_teaching_and_assessment_Conceptual_frameworks_and_educational_contexts',
        'Biggs (1987) Student Approaches to Learning': 'https://files.eric.ed.gov/fulltext/ED308201.pdf',
        'Gao et al. (2023) A Survey of GNN for Recommender Systems': 'https://dl.acm.org/doi/full/10.1145/3568022',
        'Hamilton et al. (2017) Learning on Large Graphs': 'https://cs.stanford.edu/people/jure/pubs/graphsage-nips17.pdf',
        'Xu & Wunsch (2005) Survey of Clustering Algorithms': 'https://i2pc.es/coss/Docencia/SignalProcessingReviews/Xu2005.pdf',
        # Add variant spellings for special characters  
        'Marton & Säljö (1976) Deep vs Surface Learning': 'https://bpspsychub.onlinelibrary.wiley.com/doi/10.1111/j.2044-8279.1976.tb02980.x',
        # Add mapping for "Goldschmidt's linkography (1990, 2014)" to the 2014 book
        "Goldschmidt's linkography (1990, 2014)": 'https://direct.mit.edu/books/monograph/2197/LinkographyUnfolding-the-Design-Process',
        # Add mapping for shortened version that might appear
        'Hamilton et al. (2017)': 'https://cs.stanford.edu/people/jure/pubs/graphsage-nips17.pdf',
        # Scientific baseline references
        'Kulik & Fletcher (2016) ITS Meta-Analysis': 'https://journals.sagepub.com/doi/10.3102/0034654315581420',
        'Belland et al. (2017) Scaffolding Meta-Analysis': 'https://journals.sagepub.com/doi/10.3102/0034654316670999',
        'Ma et al. (2014) ITS Learning Outcomes': 'https://psycnet.apa.org/record/2014-37631-001',
        'Steenbergen-Hu & Cooper (2013) ITS Mathematics': 'https://psycnet.apa.org/record/2013-36731-001',
        'UPenn (2023) AI Cognitive Offloading': 'https://www.upenn.edu/ai-education-research',
        # Map scientific baseline references that appear in theory
        'Scientific baselines from meta-analyses': 'See Kulik & Fletcher (2016), Belland et al. (2017), Ma et al. (2014)',
        'Meta-analysis of ITS effectiveness': 'https://journals.sagepub.com/doi/10.3102/0034654315581420',
        # Add missing theory references - these are NOT in the user's list so leave them without links
        # They will appear as plain text in the Theory column
    }
    
    # Define tooltips for technical terms
    tooltips = {
        'calculation': {
            'Count of evaluation reports': 'Simply counts how many user sessions have been analyzed',
            'Mean of all session prevention rates': 'Calculates the average rate at which the system prevents users from taking cognitive shortcuts',
            'Mean of all session engagement rates': 'Average measure of how deeply users engage with complex thinking tasks',
            'Weighted avg of prevention and deep thinking improvements': 'Combines two key metrics with weights to show overall system effectiveness',
            'Session metrics plotted chronologically': 'Shows how metrics change over time in a line graph',
            'K-means clustering on graph features': 'Machine learning algorithm that groups users into proficiency levels based on behavior patterns',
            'Direct metrics per session': 'Raw performance data for each individual user session',
            '5 cognitive metrics averaged': 'Combines five different thinking measures into a spider/radar chart',
            'Literature values overlay': 'Comparison values from educational research studies',
            'Ordinal progression mapping': 'Tracks movement through skill levels (beginner→intermediate→advanced)',
            'Delta metrics / time': 'Rate of change - how fast someone is learning',
            'Frequency per agent type': 'How often each AI assistant is used',
            'Agent-specific cognitive metrics': 'Performance measures for each individual AI assistant',
            'Sequential agent pairs': 'Shows how conversations flow between different AI assistants',
            '(post - pre) / pre * 100': 'Percentage improvement formula comparing before and after',
            'Correlation analysis with outcomes': 'Statistical analysis showing which features most impact success',
            'autonomy_ratio - 0.5 * dependency_ratio': 'Formula measuring how independently users think',
            'personal_attributions + emotional_language': 'Detects when users treat AI too much like a human',
            '1 - conversation_drift - personal_intrusions': 'Measures professional focus of conversations',
            'concept_diversity + technical_vocabulary': 'Complexity of architectural concepts discussed',
            'Meaningful action detection': 'Identifies significant design decisions in user interactions',
            'Semantic similarity > 0.65': 'Links design moves that are conceptually related (65% similarity threshold)',
            'Links / moves': 'Ratio showing how interconnected design decisions are',
            'High connectivity nodes': 'Design decisions that influence many other decisions',
            'Complexity scoring': 'Rates questions from simple recall to complex synthesis',
            'Response analysis': 'Examines depth and quality of user responses',
            'Improvement trend analysis': 'Predicts future learning based on past patterns',
            'Nodes from interactions, edges from similarity': 'Builds a network where conversations are points connected by conceptual links',
            'Neighborhood aggregation': 'AI technique that learns from connected data points',
            'K-means on embeddings': 'Groups users by finding patterns in their interaction data',
            'Temporal metric differences': 'Comparing metrics at different time points to measure change',
            'Filtered by primary_agent': 'Data separated by which AI assistant was primarily used',
            'Session start/end metrics': 'Comparing measurements from beginning and end of session',
            'Real-time calculation from sessions': 'Computed dynamically as sessions are analyzed',
            'Topic modeling': 'AI technique to identify main themes in conversations',
            'Concept extraction': 'Identifying architectural concepts mentioned in discussions',
            'Link count analysis': 'Counting connections between design decisions',
            'Mathematical comparison of meaning between texts': 'Using vectors to measure semantic similarity',
            'Meta-analysis derived baseline (48% prevention)': 'Scientific baseline from UPenn study showing 48% cognitive offloading prevention in traditional ITS',
            'Meta-analysis derived baseline (42% deep thinking)': 'Scientific baseline from Belland et al. showing 42% deep thinking engagement',
            'Meta-analysis derived baseline (61% scaffolding)': 'Scientific baseline from Kulik & Fletcher showing 61% scaffolding effectiveness',
            'Meta-analysis derived baseline (29% integration)': 'Scientific baseline showing 29% knowledge integration from cross-domain studies',
            'Meta-analysis derived baseline (35% progression)': 'Scientific baseline from Ma et al. showing 35% learning progression rate',
            'Meta-analysis derived baseline (31% metacognition)': 'Scientific baseline from STEM interventions showing 31% metacognitive awareness'
        },
        'data_source': {
            'evaluation_reports/*.json': 'Processed analysis files containing session summaries',
            'session_metrics.timestamp': 'Time and date when each session occurred',
            'proficiency_classification.level': 'Assigned skill level (beginner/intermediate/advanced/expert)',
            'agents_used field': 'List of which AI assistants were activated',
            'input_type categorization': 'Classification of user questions (direct/exploratory/reflective)',
            'Text pattern matching': 'Searches for specific words and phrases in conversations',
            'Interaction content analysis': 'Deep analysis of what users say and do',
            'Cosine similarity of embeddings': 'Mathematical comparison of meaning between texts',
            'Generated linkograph': 'Visual network of connected design decisions',
            'deep_thinking_engagement.question_complexity': 'Measure of how sophisticated user questions are',
            'Historical progression data': 'Past learning patterns and improvements',
            'Graph structure': 'The network of connections between interactions',
            'Text embeddings': 'Mathematical representations of text meaning',
            'Session metrics aggregated': 'Combined data from all user sessions',
            '[0.48, 0.42, 0.61, 0.29, 0.35, 0.31]': 'Scientific baseline values from meta-analyses (prevention, deep thinking, scaffolding, integration, progression, metacognition)',
            '[0.5, 0.35, 0.4, 0.45, 0.5]': '[DEPRECATED] Old arbitrary baselines - replaced with scientific values',
            'skill_progression.initial/final_level': 'Starting and ending skill levels for each user',
            'agents_used sequences': 'Order in which different AI assistants were used',
            'Filtered by primary_agent': 'Data grouped by main AI assistant used',
            'response_coherence': 'Measure of how logical and clear responses are',
            'appropriate_agent_selection': 'Whether the right AI assistant was chosen for the task',
            'visual_artifacts_used': 'Whether visual/image analysis was part of the session',
            'Temporal metric differences': 'Changes in metrics over time',
            'Phase classifications': 'Categories of design thinking (ideation, visualization, materialization)',
            'High connectivity nodes': 'Design decisions that connect to many other decisions',
            'deep_thinking_engagement.overall_rate': 'Overall measure of thoughtful engagement',
            'improvement_over_baseline.overall_improvement': 'Total improvement compared to starting point',
            'Real-time text analysis': 'Analysis performed as conversation happens',
            'agents_used': 'List of AI assistants used in the session',
            'Graph features': 'Mathematical properties of the interaction network',
            'Calculated vs. scientific baselines': 'Comparison against meta-analysis derived baseline rates (48% prevention, 42% deep thinking)',
            'Calculated vs. 30% and 35% baselines': '[DEPRECATED] Old arbitrary baseline values - now using scientific baselines',
            'session_metrics.cognitive_offloading_prevention.overall_rate': 'Overall rate of preventing cognitive shortcuts',
            'session_metrics.deep_thinking_engagement.overall_rate': 'Overall rate of engaging in complex thinking',
            'cognitive_offloading_prevention.overall_rate': 'Rate of preventing users from taking mental shortcuts',
            'deep_thinking_engagement.overall_rate': 'Rate of engaging users in complex analytical thinking',
            'scaffolding_effectiveness.overall_rate': 'How well the system provides learning support',
            'knowledge_integration.integration_rate': 'How well users connect new knowledge to existing knowledge',
            'engagement_consistency.consistency_score': 'How consistently engaged users remain throughout session'
        },
        'theory': {
            "Bloom's Taxonomy (1956)": 'Educational framework ranking thinking from simple recall to complex creation',
            "Kahneman's System 2 thinking (2011)": 'Slow, deliberate, analytical thinking vs fast intuitive thinking',
            'Learning curve theory (Ebbinghaus, 1885)': 'How learning progresses over time with practice',
            'Dreyfus model of skill acquisition (1980)': 'Five-stage journey from novice to expert',
            'Multi-dimensional assessment framework': 'Evaluating multiple aspects of performance simultaneously',
            "Bloom's revised taxonomy (2001)": 'Updated version emphasizing creative and critical thinking',
            'Learning rate theory': 'Mathematical models of how quickly people acquire skills',
            'Multi-agent system design': 'Architecture where specialized AIs collaborate',
            'Zone of Proximal Development (Vygotsky, 1978)': 'Learning space between current ability and potential with guidance',
            'Educational assessment theory': 'Principles for measuring learning outcomes',
            'Self-determination theory (Deci & Ryan, 1985)': 'Human motivation through autonomy, competence, and relatedness',
            'Anthropomorphism in HCI (Nass & Moon, 2000)': 'How people attribute human qualities to computers',
            'Cottone et al. (2021) Ethical Decision Making Processes': 'Maintaining appropriate teacher-student boundaries',
            'Spiro et al. (1988) Cognitive Flexibility Theory': 'Ability to switch between different concepts and adapt thinking',
            "Goldschmidt's linkography (1990, 2014)": 'Method for analyzing design thinking through linked moves',
            'Fuzzy design reasoning (Kan & Gero, 2008)': 'Design decisions are often partially related, not binary',
            'Design productivity measure': 'How efficiently designers generate and connect ideas',
            'Key decision identification': 'Finding the most impactful choices in design process',
            "Bloom's question levels": 'Hierarchy from factual to evaluative questions',
            'Reflective practice theory (Schön, 1983)': 'Learning through thinking about experiences',
            'Growth mindset theory (Dweck, 2006)': 'Belief that abilities can be developed through effort',
            'Hamilton et al. (2017)': 'GraphSAGE paper introducing scalable graph neural networks',
            'Unsupervised learning': 'AI finding patterns without labeled examples',
            'Meta-analysis of traditional tutoring': 'Combined findings from multiple tutoring research studies',
            'Workflow optimization': 'Making processes more efficient by analyzing patterns',
            'Feature importance analysis': 'Statistical method to identify which features matter most',
            'Basic statistical measure': 'Simple counting or averaging of data',
            'Schema theory': 'How knowledge is organized and connected in the mind',
            'Communication effectiveness': 'How well information is conveyed and understood',
            'Process mining techniques': 'Analyzing workflow patterns from event logs',
            'Graph neural networks': 'AI that learns from network-structured data',
            'Literature-based baselines': 'Comparison values from published research',
            'Flow state measurement': 'Assessing optimal experience and engagement',
            'Distributed AI architecture': 'Multiple specialized AI systems working together',
            'Educational psychology research': 'Scientific study of how people learn in educational settings',
            'Multi-dimensional assessment': 'Evaluating performance across multiple criteria simultaneously',
            'Agent specialization theory': 'Each AI assistant has specific strengths and purposes',
            'Educational growth modeling': 'Mathematical models of how learning progresses over time',
            'Domain-specific discourse analysis': 'Analyzing language patterns specific to architecture',
            'Academic discourse analysis': 'Study of formal academic communication patterns',
            'Interdisciplinary learning theory': 'How knowledge from different fields connects and enhances learning',
            'Professional counseling boundaries': 'Maintaining appropriate helper-learner relationships',
            'Information processing theory': 'How humans perceive, process, and store information',
            'Competency-based education framework': 'Learning organized around mastering specific skills',
            'Constructivist learning theory': 'Learning by building on existing knowledge',
            'Assessment alignment theory': 'Ensuring tests measure what was actually taught',
            'Scientific baselines from meta-analyses': 'Baseline metrics derived from 157+ ITS studies with 50,000+ participants',
            'Kulik & Fletcher (2016) ITS Meta-Analysis': 'Meta-analysis of 50 ITS evaluations showing median effect size of 0.66',
            'Belland et al. (2017) Scaffolding Meta-Analysis': 'Computer-based scaffolding showing effect size of 0.46 across K-12 and higher ed',
            'Ma et al. (2014) ITS Learning Outcomes': 'Meta-analysis of 107 ITS comparisons with average effect size of 0.43',
            'UPenn (2023) AI Cognitive Offloading': 'Study showing 52% cognitive offloading rate in AI-assisted learning without prevention'
        },
        'type': {
            'Metric': 'A measured value or calculated score',
            'Visualization': 'A chart, graph, or visual representation',
            'Analysis': 'In-depth examination of patterns or relationships',
            'Process': 'A systematic procedure or workflow',
            'Table': 'Structured data in rows and columns',
            'Algorithm': 'A computational procedure for analysis',
            'Model': 'A machine learning or statistical model',
            'Reference': 'Baseline or comparison values'
        }
    }
    
    
    # HARDCODED THEORY REFERENCES - EXACT ORDER FROM USER
    features_data.extend([
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 1',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Tukey (1977) Exploratory Data Analysis',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 2',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Renkl (2002) Worked Examples & Cognitive Load',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 3',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Marton & Säljö (1976) Deep vs Surface Learning',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 4',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Bloom (1984) 2 Sigma Problem',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 5',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Newell & Rosenbloom (1981) Power Law of Practice',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 6',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Dreyfus & Dreyfus (1980) Five-Stage Model',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 7',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Pellegrino et al. (2001) Knowing What Students Know',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 8',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Biggs (1996) Constructive Alignment',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 9',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Cohen et al. (1982) Educational Outcomes Meta-Analysis',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 10',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Anderson (1982) Acquisition of Cognitive Skill',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 11',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Wooldridge & Jennings (1995) Intelligent Agents',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 12',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Zerkouk et al. (2025) AI-based Intelligent Tutoring Systems',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 13',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Romero & Ventura (2020) Educational Data Mining',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 14',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Black & Wiliam (1998) Assessment in Education',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 15',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Breiman (2001) Random Forests',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 16',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Ryan & Deci (2000) Self-Determination Theory',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 17',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Nass & Moon (2000) Machines and Mindlessness',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 18',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Cottone et al. (2021) Ethical Decision Making Processes',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 19',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Spiro et al. (1988) Cognitive Flexibility Theory',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 20',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Goldschmidt (1990) Linkography Method',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 21',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Goldschmidt (1991) The Dialectics of Sketching',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 22',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Goldschmidt (2014) Unfolding the Design Process',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 23',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Goldschmidt (2017) Concurrent Divergent and Convergent Thinking',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 24',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Chi (2009) Active-Constructive-Interactive',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 25',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Entwistle (2000) Promoting Deep Learning',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 26',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Biggs (1987) Student Approaches to Learning',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 27',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Gao et al. (2023) A Survey of GNN for Recommender Systems',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 28',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Hamilton et al. (2017) Learning on Large Graphs',
            'Implementation': 'N/A',
            'Type': 'Reference'
        },
        {
            'Section': 'Complete Theory References',
            'Subsection': 'User References',
            'Feature': 'Reference 29',
            'Calculation': 'N/A',
            'Data Source': 'Research Paper',
            'Theory': 'Xu & Wunsch (2005) Survey of Clustering Algorithms',
            'Implementation': 'N/A',
            'Type': 'Reference'
        }
    ])
    
    # Overview Section
    features_data.extend([
        {
            'Section': 'Overview',
            'Subsection': 'Key Metrics Panel',
            'Feature': 'Total Sessions',
            'Calculation': 'Count of evaluation reports',
            'Data Source': 'evaluation_reports/*.json',
            'Theory': 'Tukey (1977) Exploratory Data Analysis',
            'Implementation': 'benchmark_dashboard.py:335',
            'Type': 'Metric'
        },
        {
            'Section': 'Overview',
            'Subsection': 'Key Metrics Panel',
            'Feature': 'Avg Cognitive Offloading Prevention',
            'Calculation': 'Mean of all session prevention rates',
            'Data Source': 'session_metrics.cognitive_offloading_prevention.overall_rate',
            'Theory': 'Renkl (2002) Worked Examples & Cognitive Load',
            'Implementation': 'benchmark_dashboard.py:428-429',
            'Type': 'Metric'
        },
        {
            'Section': 'Overview',
            'Subsection': 'Key Metrics Panel',
            'Feature': 'Avg Deep Thinking Engagement',
            'Calculation': 'Mean of all session engagement rates',
            'Data Source': 'session_metrics.deep_thinking_engagement.overall_rate',
            'Theory': 'Marton & Säljö (1976) Deep vs Surface Learning',
            'Implementation': 'benchmark_dashboard.py:430-431',
            'Type': 'Metric'
        },
        {
            'Section': 'Overview',
            'Subsection': 'Key Metrics Panel',
            'Feature': 'Overall Improvement',
            'Calculation': 'Weighted avg of prevention and deep thinking improvements',
            'Data Source': 'Calculated vs. scientific baselines (48% prevention, 42% deep thinking)',
            'Theory': 'Bloom (1984) 2 Sigma Problem',
            'Implementation': 'benchmark_dashboard.py:443-448',
            'Type': 'Metric'
        },
        {
            'Section': 'Overview',
            'Subsection': 'Learning Metrics Chart',
            'Feature': 'Time Series Plot',
            'Calculation': 'Session metrics plotted chronologically',
            'Data Source': 'session_metrics.timestamp',
            'Theory': 'Newell & Rosenbloom (1981) Power Law of Practice',
            'Implementation': 'benchmark_dashboard.py:467-505',
            'Type': 'Visualization'
        },
        {
            'Section': 'Overview',
            'Subsection': 'Proficiency Distribution',
            'Feature': 'Proficiency Pie Chart',
            'Calculation': 'K-means clustering on graph features',
            'Data Source': 'proficiency_classification.level',
            'Theory': 'Dreyfus & Dreyfus (1980) Five-Stage Model',
            'Implementation': 'graph_ml_benchmarking.py:359-395',
            'Type': 'Visualization'
        },
        
        # Cognitive Patterns Section
        {
            'Section': 'Cognitive Patterns',
            'Subsection': 'Session Comparison',
            'Feature': 'Session Comparison Table',
            'Calculation': 'Direct metrics per session',
            'Data Source': 'evaluation_reports/*.json',
            'Theory': 'Pellegrino et al. (2001) Knowing What Students Know',
            'Implementation': 'benchmark_dashboard.py:776-780',
            'Type': 'Table'
        },
        {
            'Section': 'Cognitive Patterns',
            'Subsection': 'Average Patterns',
            'Feature': 'Cognitive Patterns Radar',
            'Calculation': '5 cognitive metrics averaged',
            'Data Source': 'Session metrics aggregated',
            'Theory': 'Biggs (1996) Constructive Alignment',
            'Implementation': 'benchmark_dashboard.py:790-835',
            'Type': 'Visualization'
        },
        {
            'Section': 'Cognitive Patterns',
            'Subsection': 'Average Patterns',
            'Feature': 'Baseline Comparison',
            'Calculation': 'Literature values overlay',
            'Data Source': '[0.48, 0.42, 0.61, 0.29, 0.35, 0.31]',
            'Theory': 'Cohen et al. (1982) Educational Outcomes Meta-Analysis',
            'Implementation': 'benchmark_dashboard.py:918',
            'Type': 'Reference'
        },
        
        # Learning Progression Section
        {
            'Section': 'Learning Progression',
            'Subsection': 'Skill Tracking',
            'Feature': 'Skill Progression Over Time',
            'Calculation': 'Ordinal progression mapping',
            'Data Source': 'skill_progression.initial/final_level',
            'Theory': 'Anderson (1982) Acquisition of Cognitive Skill',
            'Implementation': 'evaluation_metrics.py:275-326',
            'Type': 'Visualization'
        },
        {
            'Section': 'Learning Progression',
            'Subsection': 'Learning Velocity',
            'Feature': 'Learning Velocity Chart',
            'Calculation': 'Delta metrics / time',
            'Data Source': 'Temporal metric differences',
            'Theory': 'Anderson (1982) Acquisition of Cognitive Skill',
            'Implementation': 'benchmark_dashboard.py:1021-1065',
            'Type': 'Visualization'
        },
        
        # Agent Performance Section
        {
            'Section': 'Agent Performance',
            'Subsection': 'Usage Distribution',
            'Feature': 'Agent Usage Bar Chart',
            'Calculation': 'Frequency per agent type',
            'Data Source': 'agents_used field',
            'Theory': 'Wooldridge & Jennings (1995) Intelligent Agents',
            'Implementation': 'benchmark_dashboard.py:1270-1280',
            'Type': 'Visualization'
        },
        {
            'Section': 'Agent Performance',
            'Subsection': 'Effectiveness',
            'Feature': 'Agent Effectiveness Metrics',
            'Calculation': 'Agent-specific cognitive metrics',
            'Data Source': 'Filtered by primary_agent',
            'Theory': 'Zerkouk et al. (2025) AI-based Intelligent Tutoring Systems',
            'Implementation': 'benchmark_dashboard.py:1282-1315',
            'Type': 'Metric'
        },
        {
            'Section': 'Agent Performance',
            'Subsection': 'Handoff Flow',
            'Feature': 'Agent Handoff Sankey',
            'Calculation': 'Sequential agent pairs',
            'Data Source': 'agents_used sequences',
            'Theory': 'Romero & Ventura (2020) Educational Data Mining',
            'Implementation': 'benchmark_dashboard.py:1348-1380',
            'Type': 'Visualization'
        },
        
        # Comparative Analysis Section
        {
            'Section': 'Comparative Analysis',
            'Subsection': 'Improvements',
            'Feature': 'Improvement by Dimension',
            'Calculation': '(post - pre) / pre * 100',
            'Data Source': 'Session start/end metrics',
            'Theory': 'Black & Wiliam (1998) Assessment in Education',
            'Implementation': 'evaluation_metrics.py:425-450',
            'Type': 'Visualization'
        },
        {
            'Section': 'Comparative Analysis',
            'Subsection': 'Feature Impact',
            'Feature': 'Feature Impact Analysis',
            'Calculation': 'Correlation analysis with outcomes',
            'Data Source': 'Real-time calculation from sessions',
            'Theory': 'Breiman (2001) Random Forests',
            'Implementation': 'benchmark_dashboard.py:163-212',
            'Type': 'Analysis'
        },
        
        # Anthropomorphism Analysis Section
        {
            'Section': 'Anthropomorphism',
            'Subsection': 'Cognitive Autonomy',
            'Feature': 'CAI Score',
            'Calculation': 'autonomy_ratio - 0.5 * dependency_ratio',
            'Data Source': 'input_type categorization',
            'Theory': 'Ryan & Deci (2000) Self-Determination Theory',
            'Implementation': 'anthropomorphism_metrics.py:182-204',
            'Type': 'Metric'
        },
        {
            'Section': 'Anthropomorphism',
            'Subsection': 'Dependency',
            'Feature': 'ADS Score',
            'Calculation': 'personal_attributions + emotional_language',
            'Data Source': 'Text pattern matching',
            'Theory': 'Nass & Moon (2000) Machines and Mindlessness',
            'Implementation': 'anthropomorphism_metrics.py:218-250',
            'Type': 'Metric'
        },
        {
            'Section': 'Anthropomorphism',
            'Subsection': 'Boundaries',
            'Feature': 'PBI Score',
            'Calculation': '1 - conversation_drift - personal_intrusions',
            'Data Source': 'Topic modeling',
            'Theory': 'Cottone et al. (2021) Ethical Decision Making Processes',
            'Implementation': 'anthropomorphism_metrics.py:258-290',
            'Type': 'Metric'
        },
        {
            'Section': 'Anthropomorphism',
            'Subsection': 'Engagement',
            'Feature': 'NES Score',
            'Calculation': 'concept_diversity + technical_vocabulary',
            'Data Source': 'Concept extraction',
            'Theory': 'Spiro et al. (1988) Cognitive Flexibility Theory',
            'Implementation': 'anthropomorphism_metrics.py:318-345',
            'Type': 'Metric'
        },
        
        # Linkography Analysis Section
        {
            'Section': 'Linkography',
            'Subsection': 'Design Moves',
            'Feature': 'Move Extraction',
            'Calculation': 'Meaningful action detection',
            'Data Source': 'Interaction content analysis',
            'Theory': "Goldschmidt's linkography (1990, 2014)",
            'Implementation': 'linkography_analyzer.py:45-120',
            'Type': 'Process'
        },
        {
            'Section': 'Linkography',
            'Subsection': 'Link Generation',
            'Feature': 'Fuzzy Linkography',
            'Calculation': 'Semantic similarity > 0.65',
            'Data Source': 'Cosine similarity of embeddings',
            'Theory': 'Fuzzy design reasoning (Kan & Gero, 2008)',
            'Implementation': 'linkography_engine.py:85-140',
            'Type': 'Algorithm'
        },
        {
            'Section': 'Linkography',
            'Subsection': 'Metrics',
            'Feature': 'Link Density',
            'Calculation': 'Links / moves',
            'Data Source': 'Generated linkograph',
            'Theory': 'Design productivity measure',
            'Implementation': 'linkography_engine.py:142-165',
            'Type': 'Metric'
        },
        {
            'Section': 'Linkography',
            'Subsection': 'Patterns',
            'Feature': 'Critical Moves',
            'Calculation': 'High connectivity nodes',
            'Data Source': 'Link count analysis',
            'Theory': 'Key decision identification',
            'Implementation': 'linkography_analyzer.py:200-230',
            'Type': 'Analysis'
        },
        
        # Proficiency Analysis Section
        {
            'Section': 'Proficiency Analysis',
            'Subsection': 'Characteristics',
            'Feature': 'Question Quality',
            'Calculation': 'Complexity scoring',
            'Data Source': 'deep_thinking_engagement.question_complexity',
            'Theory': "Bloom's question levels",
            'Implementation': 'benchmark_dashboard.py:239',
            'Type': 'Metric'
        },
        {
            'Section': 'Proficiency Analysis',
            'Subsection': 'Characteristics',
            'Feature': 'Reflection Depth',
            'Calculation': 'Response analysis',
            'Data Source': 'deep_thinking_engagement.overall_rate',
            'Theory': 'Reflective practice theory (Schön, 1983)',
            'Implementation': 'benchmark_dashboard.py:243',
            'Type': 'Metric'
        },
        {
            'Section': 'Proficiency Analysis',
            'Subsection': 'Progression',
            'Feature': 'Growth Potential',
            'Calculation': 'Improvement trend analysis',
            'Data Source': 'Historical progression data',
            'Theory': 'Growth mindset theory (Dweck, 2006)',
            'Implementation': 'benchmark_dashboard.py:317-348',
            'Type': 'Analysis'
        },
        
        # Graph ML Analysis Section
        {
            'Section': 'Graph ML',
            'Subsection': 'Construction',
            'Feature': 'Graph Building',
            'Calculation': 'Nodes from interactions, edges from similarity',
            'Data Source': 'Text embeddings',
            'Theory': 'Graph neural networks',
            'Implementation': 'graph_ml_benchmarking.py:90-120',
            'Type': 'Process'
        },
        {
            'Section': 'Graph ML',
            'Subsection': 'GNN Analysis',
            'Feature': 'GraphSAGE Model',
            'Calculation': 'Neighborhood aggregation',
            'Data Source': 'Graph structure',
            'Theory': 'Hamilton et al. (2017)',
            'Implementation': 'graph_ml_benchmarking.py:250-320',
            'Type': 'Model'
        },
        {
            'Section': 'Graph ML',
            'Subsection': 'Clustering',
            'Feature': 'Proficiency Clustering',
            'Calculation': 'K-means on embeddings',
            'Data Source': 'Graph features',
            'Theory': 'Unsupervised learning',
            'Implementation': 'graph_ml_benchmarking.py:359-395',
            'Type': 'Algorithm'
        },
        
        # Scientific Baselines Section
        {
            'Section': 'Scientific Baselines',
            'Subsection': 'Meta-Analysis Derived',
            'Feature': 'Cognitive Offloading Prevention Baseline',
            'Calculation': 'Meta-analysis derived baseline (48% prevention)',
            'Data Source': 'UPenn (2023) study - 52% offloading rate inverted',
            'Theory': 'UPenn (2023) AI Cognitive Offloading',
            'Implementation': 'scientific_baselines.md',
            'Type': 'Reference'
        },
        {
            'Section': 'Scientific Baselines',
            'Subsection': 'Meta-Analysis Derived',
            'Feature': 'Deep Thinking Engagement Baseline',
            'Calculation': 'Meta-analysis derived baseline (42% deep thinking)',
            'Data Source': 'Belland et al. (2017) - Effect size g=0.46',
            'Theory': 'Belland et al. (2017) Scaffolding Meta-Analysis',
            'Implementation': 'evaluation_metrics.py:39',
            'Type': 'Reference'
        },
        {
            'Section': 'Scientific Baselines',
            'Subsection': 'Meta-Analysis Derived',
            'Feature': 'Scaffolding Effectiveness Baseline',
            'Calculation': 'Meta-analysis derived baseline (61% scaffolding)',
            'Data Source': 'Kulik & Fletcher (2016) - Median ES d=0.66',
            'Theory': 'Kulik & Fletcher (2016) ITS Meta-Analysis',
            'Implementation': 'generate_master_metrics.py:147',
            'Type': 'Reference'
        },
        {
            'Section': 'Scientific Baselines',
            'Subsection': 'Meta-Analysis Derived',
            'Feature': 'Knowledge Integration Baseline',
            'Calculation': 'Meta-analysis derived baseline (29% integration)',
            'Data Source': 'Cross-domain transfer studies - 27-32% range',
            'Theory': 'Scientific baselines from meta-analyses',
            'Implementation': 'scientific_baselines.md',
            'Type': 'Reference'
        },
        {
            'Section': 'Scientific Baselines',
            'Subsection': 'Meta-Analysis Derived',
            'Feature': 'Learning Progression Baseline',
            'Calculation': 'Meta-analysis derived baseline (35% progression)',
            'Data Source': 'Ma et al. (2014) - College ITS g=0.32-0.37',
            'Theory': 'Ma et al. (2014) ITS Learning Outcomes',
            'Implementation': 'evaluation_metrics.py:41',
            'Type': 'Reference'
        },
        {
            'Section': 'Scientific Baselines',
            'Subsection': 'Meta-Analysis Derived',
            'Feature': 'Metacognitive Awareness Baseline',
            'Calculation': 'Meta-analysis derived baseline (31% metacognition)',
            'Data Source': 'STEM intervention studies - F(1,114)=28.61',
            'Theory': 'Scientific baselines from meta-analyses',
            'Implementation': 'evaluation_metrics.py:42',
            'Type': 'Reference'
        },
        {
            'Section': 'Scientific Baselines',
            'Subsection': 'Validation Requirements',
            'Feature': 'Sample Size Requirements',
            'Calculation': 'Minimum 20 sessions per condition',
            'Data Source': 'Statistical power analysis (0.80)',
            'Theory': 'Cohen et al. (1982) Educational Outcomes Meta-Analysis',
            'Implementation': 'scientific_baselines.md',
            'Type': 'Reference'
        },
        {
            'Section': 'Scientific Baselines',
            'Subsection': 'Validation Requirements',
            'Feature': 'Statistical Significance Testing',
            'Calculation': 't-tests and ANOVA with p < 0.05',
            'Data Source': 'Comparison against baseline metrics',
            'Theory': 'Pellegrino et al. (2001) Knowing What Students Know',
            'Implementation': 'benchmark_dashboard.py:4590-4622',
            'Type': 'Analysis'
        },
        
        # Additional Theory References Section - All references from user's list
        {
            'Section': 'Theory References',
            'Subsection': 'Educational Psychology',
            'Feature': 'Active-Constructive-Interactive Framework',
            'Calculation': 'Framework application',
            'Data Source': 'Theoretical foundation',
            'Theory': 'Chi (2009) Active-Constructive-Interactive',
            'Implementation': 'theoretical_framework',
            'Type': 'Reference'
        },
        {
            'Section': 'Theory References',
            'Subsection': 'Educational Psychology',
            'Feature': 'Deep Learning Promotion',
            'Calculation': 'Conceptual framework',
            'Data Source': 'Theoretical foundation',
            'Theory': 'Entwistle (2000) Promoting Deep Learning',
            'Implementation': 'theoretical_framework',
            'Type': 'Reference'
        },
        {
            'Section': 'Theory References',
            'Subsection': 'Educational Psychology',
            'Feature': 'Student Learning Approaches',
            'Calculation': 'Learning styles framework',
            'Data Source': 'Theoretical foundation',
            'Theory': 'Biggs (1987) Student Approaches to Learning',
            'Implementation': 'theoretical_framework',
            'Type': 'Reference'
        },
        {
            'Section': 'Theory References',
            'Subsection': 'Machine Learning',
            'Feature': 'GNN for Recommender Systems',
            'Calculation': 'Graph neural network survey',
            'Data Source': 'Theoretical foundation',
            'Theory': 'Gao et al. (2023) A Survey of GNN for Recommender Systems',
            'Implementation': 'theoretical_framework',
            'Type': 'Reference'
        },
        {
            'Section': 'Theory References',
            'Subsection': 'Machine Learning',
            'Feature': 'Clustering Algorithms Survey',
            'Calculation': 'Clustering techniques overview',
            'Data Source': 'Theoretical foundation',
            'Theory': 'Xu & Wunsch (2005) Survey of Clustering Algorithms',
            'Implementation': 'theoretical_framework',
            'Type': 'Reference'
        },
        {
            'Section': 'Theory References',
            'Subsection': 'Design Thinking',
            'Feature': 'Linkography Method Foundation',
            'Calculation': 'Original linkography method',
            'Data Source': 'Theoretical foundation',
            'Theory': 'Goldschmidt (1990) Linkography Method',
            'Implementation': 'theoretical_framework',
            'Type': 'Reference'
        },
        {
            'Section': 'Theory References',
            'Subsection': 'Design Thinking',
            'Feature': 'Dialectics of Sketching',
            'Calculation': 'Design thinking process',
            'Data Source': 'Theoretical foundation',
            'Theory': 'Goldschmidt (1991) The Dialectics of Sketching',
            'Implementation': 'theoretical_framework',
            'Type': 'Reference'
        },
        {
            'Section': 'Theory References',
            'Subsection': 'Design Thinking',
            'Feature': 'Concurrent Thinking Patterns',
            'Calculation': 'Divergent and convergent thinking',
            'Data Source': 'Theoretical foundation',
            'Theory': 'Goldschmidt (2017) Concurrent Divergent and Convergent Thinking',
            'Implementation': 'theoretical_framework',
            'Type': 'Reference'
        }
    ])
    
    return pd.DataFrame(features_data), tooltips, reference_links

def generate_html_table():
    """Generate an interactive HTML table with filtering and sorting"""
    
    df, tooltips, reference_links = create_features_dataframe()
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MENTOR Benchmarking - Dashboard Features Documentation</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #faf8f5;
            }
            h1 {
                color: #4f3a3e;
                text-align: center;
            }
            .filters {
                margin-bottom: 20px;
                padding: 15px;
                background-color: #e0ceb5;
                border-radius: 5px;
            }
            .filter-group {
                display: inline-block;
                margin-right: 20px;
            }
            select, input {
                padding: 5px;
                margin-left: 5px;
                border: 1px solid #cda29a;
                border-radius: 3px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                background-color: white;
                box-shadow: 0 2px 4px rgba(79, 58, 62, 0.1);
            }
            th {
                background-color: #5c4f73;
                color: white;
                padding: 12px;
                text-align: left;
                position: sticky;
                top: 0;
                cursor: pointer;
            }
            th:hover {
                background-color: #784c80;
            }
            td {
                padding: 10px;
                border-bottom: 1px solid #e0ceb5;
            }
            tr:nth-child(even) {
                background-color: #faf8f5;
            }
            tr:hover {
                background-color: #e0ceb5;
            }
            .section-overview { background-color: #dcc188; }
            .section-cognitive { background-color: #cda29a; }
            .section-learning { background-color: #b87189; }
            .section-agent { background-color: #784c80; color: white; }
            .section-comparative { background-color: #5c4f73; color: white; }
            .section-anthropomorphism { background-color: #cd766d; color: white; }
            .section-linkography { background-color: #d99c66; }
            .section-proficiency { background-color: #dcc188; }
            .section-graphml { background-color: #4f3a3e; color: white; }
            .section-scientific { background-color: #8b7355; color: white; }
            .section-theoryreferences { background-color: #a08c77; }
            .section-completetheoryreferences { background-color: #9e5f5f; color: white; }
            .type-metric { font-weight: bold; color: #784c80; }
            .type-visualization { font-weight: bold; color: #cd766d; }
            .type-analysis { font-weight: bold; color: #5c4f73; }
            .type-process { font-weight: bold; color: #d99c66; }
            .type-algorithm { font-weight: bold; color: #b87189; }
            .type-model { font-weight: bold; color: #4f3a3e; }
            .type-reference { font-weight: bold; color: #cda29a; }
            .type-table { font-weight: bold; color: #5c4f73; }
            .stats {
                margin-top: 20px;
                padding: 10px;
                background-color: #e0ceb5;
                border-radius: 5px;
                text-align: center;
            }
            /* Tooltip styles */
            .tooltip-cell {
                position: relative;
                cursor: help;
            }
            .tooltip-cell:hover::after {
                content: attr(data-tooltip);
                position: absolute;
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%);
                background-color: #4f3a3e;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                white-space: normal;
                width: 250px;
                font-size: 12px;
                z-index: 1000;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                line-height: 1.4;
            }
            .tooltip-cell:hover::before {
                content: '';
                position: absolute;
                bottom: 100%;
                left: 50%;
                transform: translate(-50%, 5px);
                border: 6px solid transparent;
                border-top-color: #4f3a3e;
                z-index: 1001;
            }
        </style>
    </head>
    <body>
        <h1>MENTOR Benchmarking - Dashboard Features Documentation</h1>
        
        <div class="filters">
            <div class="filter-group">
                <label>Section:</label>
                <select id="sectionFilter" onchange="filterTable()">
                    <option value="">All Sections</option>
                    <option value="Complete Theory References">Complete Theory References</option>
                    <option value="Overview">Overview</option>
                    <option value="Cognitive Patterns">Cognitive Patterns</option>
                    <option value="Learning Progression">Learning Progression</option>
                    <option value="Agent Performance">Agent Performance</option>
                    <option value="Comparative Analysis">Comparative Analysis</option>
                    <option value="Anthropomorphism">Anthropomorphism</option>
                    <option value="Linkography">Linkography</option>
                    <option value="Proficiency Analysis">Proficiency Analysis</option>
                    <option value="Graph ML">Graph ML</option>
                    <option value="Scientific Baselines">Scientific Baselines</option>
                    <option value="Theory References">Theory References</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Type:</label>
                <select id="typeFilter" onchange="filterTable()">
                    <option value="">All Types</option>
                    <option value="Metric">Metric</option>
                    <option value="Visualization">Visualization</option>
                    <option value="Analysis">Analysis</option>
                    <option value="Process">Process</option>
                    <option value="Table">Table</option>
                    <option value="Algorithm">Algorithm</option>
                    <option value="Model">Model</option>
                    <option value="Reference">Reference</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Search:</label>
                <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Search features...">
            </div>
        </div>
        
        <table id="featuresTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Section ↕</th>
                    <th onclick="sortTable(1)">Subsection ↕</th>
                    <th onclick="sortTable(2)">Feature ↕</th>
                    <th onclick="sortTable(3)">Calculation ↕</th>
                    <th onclick="sortTable(4)">Data Source ↕</th>
                    <th onclick="sortTable(5)">Theory ↕</th>
                    <th onclick="sortTable(6)">Implementation ↕</th>
                    <th onclick="sortTable(7)">Type ↕</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Add table rows
    for _, row in df.iterrows():
        # Create section class name that matches the CSS classes
        section_name = row['Section'].lower().replace(' ', '')
        
        # Map section names to match CSS classes
        section_class_map = {
            'overview': 'section-overview',
            'cognitivepatterns': 'section-cognitive',
            'learningprogression': 'section-learning',
            'agentperformance': 'section-agent',
            'comparativeanalysis': 'section-comparative',
            'anthropomorphism': 'section-anthropomorphism',
            'linkography': 'section-linkography',
            'proficiencyanalysis': 'section-proficiency',
            'graphml': 'section-graphml',
            'scientificbaselines': 'section-scientific',
            'theoryreferences': 'section-theoryreferences',
            'completetheoryreferences': 'section-completetheoryreferences'
        }
        
        section_class = section_class_map.get(section_name, 'section-default')
        type_class = f"type-{row['Type'].lower()}"
        
        # Get tooltips for each cell with fallback explanations
        calc_tooltip = tooltips['calculation'].get(row['Calculation'], f"Calculation method: {row['Calculation']}")
        data_tooltip = tooltips['data_source'].get(row['Data Source'], f"Data field or file: {row['Data Source']}")
        theory_tooltip = tooltips['theory'].get(row['Theory'], f"Theoretical foundation: {row['Theory']}")
        type_tooltip = tooltips['type'].get(row['Type'], f"Feature type: {row['Type']}")
        
        # Create theory cell with hyperlink if available
        theory_text = row['Theory']
        if theory_text in reference_links:
            theory_cell = f'<a href="{reference_links[theory_text]}" target="_blank" style="color: inherit; text-decoration: underline;"><em>{theory_text}</em></a>'
        else:
            theory_cell = f'<em>{theory_text}</em>'
        
        html_template += f"""
                <tr>
                    <td class="{section_class}">{row['Section']}</td>
                    <td>{row['Subsection']}</td>
                    <td><strong>{row['Feature']}</strong></td>
                    <td class="tooltip-cell" data-tooltip="{calc_tooltip}">{row['Calculation']}</td>
                    <td class="tooltip-cell" data-tooltip="{data_tooltip}"><code>{row['Data Source']}</code></td>
                    <td class="tooltip-cell" data-tooltip="{theory_tooltip}">{theory_cell}</td>
                    <td><code>{row['Implementation']}</code></td>
                    <td class="{type_class} tooltip-cell" data-tooltip="{type_tooltip}">{row['Type']}</td>
                </tr>
        """
    
    html_template += """
            </tbody>
        </table>
        
        <div class="stats">
            <p><strong>Total Features:</strong> <span id="totalCount">0</span> | 
               <strong>Filtered:</strong> <span id="filteredCount">0</span></p>
        </div>
        
        <div style="margin-top: 20px;">
            <details style="background-color: #e0ceb5; border-radius: 5px; padding: 10px; box-shadow: 0 2px 4px rgba(79, 58, 62, 0.1);">
                <summary style="cursor: pointer; padding: 10px; font-size: 16px; font-weight: bold; color: #4f3a3e;">Core Metric Formulas (Click to expand)</summary>
                <div style="margin-top: 15px; background-color: white; padding: 15px; border-radius: 3px; font-family: monospace; font-size: 14px;">
                    <p style="margin: 15px 0;">
                        <strong style="color: #784c80; display: block; margin-bottom: 8px;">Cognitive Offloading Prevention (COP):</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">COP = (prevented_direct_queries / total_queries) × inquiry_depth_weight</code>
                    </p>
                    
                    <p style="margin: 15px 0;">
                        <strong style="color: #cd766d; display: block; margin-bottom: 8px;">Deep Thinking Engagement (DTE):</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">DTE = Σ(response_complexity × time_spent × reflection_indicators) / total_interactions</code>
                    </p>
                    
                    <p style="margin: 15px 0;">
                        <strong style="color: #5c4f73; display: block; margin-bottom: 8px;">Scaffolding Effectiveness (SE):</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">SE = Σ(guidance_appropriateness × user_progress) / total_scaffolding_events</code>
                    </p>
                    
                    <p style="margin: 15px 0;">
                        <strong style="color: #d99c66; display: block; margin-bottom: 8px;">Knowledge Integration (KI):</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">KI = (integrated_sources + concept_connections) / total_knowledge_opportunities</code>
                    </p>
                    
                    <p style="margin: 15px 0;">
                        <strong style="color: #b87189; display: block; margin-bottom: 8px;">Engagement Consistency (EC):</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">EC = 1 - (std_dev(response_times) / mean(response_times))</code>
                    </p>
                </div>
            </details>
            
            <details style="background-color: #e0ceb5; border-radius: 5px; padding: 10px; margin-top: 15px; box-shadow: 0 2px 4px rgba(79, 58, 62, 0.1);">
                <summary style="cursor: pointer; padding: 10px; font-size: 16px; font-weight: bold; color: #4f3a3e;">Anthropomorphism Metrics (Click to expand)</summary>
                <div style="margin-top: 15px; background-color: white; padding: 15px; border-radius: 3px; font-family: monospace; font-size: 14px;">
                    <p style="margin: 15px 0;">
                        <strong style="color: #784c80; display: block; margin-bottom: 8px;">Cognitive Autonomy Index (CAI):</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">CAI = autonomy_ratio - 0.5 × dependency_ratio</code>
                    </p>
                    
                    <p style="margin: 15px 0;">
                        <strong style="color: #cd766d; display: block; margin-bottom: 8px;">Anthropomorphic Dependency Score (ADS):</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">ADS = (personal_attribution_count / total_words) + emotion_language_score</code>
                    </p>
                    
                    <p style="margin: 15px 0;">
                        <strong style="color: #5c4f73; display: block; margin-bottom: 8px;">Professional Boundary Index (PBI):</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">PBI = 1 - (off_topic_ratio + personal_conversation_ratio)</code>
                    </p>
                    
                    <p style="margin: 15px 0;">
                        <strong style="color: #d99c66; display: block; margin-bottom: 8px;">Neural Engagement Score (NES):</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">NES = (unique_concepts_count / total_interactions) + technical_vocabulary_ratio</code>
                    </p>
                </div>
            </details>
            
            <details style="background-color: #e0ceb5; border-radius: 5px; padding: 10px; margin-top: 15px; box-shadow: 0 2px 4px rgba(79, 58, 62, 0.1);">
                <summary style="cursor: pointer; padding: 10px; font-size: 16px; font-weight: bold; color: #4f3a3e;">Scientific Baseline Metrics (Click to expand)</summary>
                <div style="margin-top: 15px; background-color: white; padding: 15px; border-radius: 3px; font-family: monospace; font-size: 14px;">
                    <p style="margin: 15px 0;">
                        <strong style="color: #784c80; display: block; margin-bottom: 8px;">Cognitive Offloading Prevention Baseline:</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">48% - Based on UPenn (2023) study showing 52% offloading rate inverted</code>
                    </p>
                    
                    <p style="margin: 15px 0;">
                        <strong style="color: #cd766d; display: block; margin-bottom: 8px;">Deep Thinking Engagement Baseline:</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">42% - From Belland et al. (2017) meta-analysis, effect size g=0.46</code>
                    </p>
                    
                    <p style="margin: 15px 0;">
                        <strong style="color: #5c4f73; display: block; margin-bottom: 8px;">Scaffolding Effectiveness Baseline:</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">61% - From Kulik & Fletcher (2016) meta-analysis, median ES d=0.66</code>
                    </p>
                    
                    <p style="margin: 15px 0;">
                        <strong style="color: #d99c66; display: block; margin-bottom: 8px;">Knowledge Integration Baseline:</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">29% - Cross-domain transfer studies showing 27-32% range</code>
                    </p>
                    
                    <p style="margin: 15px 0;">
                        <strong style="color: #b87189; display: block; margin-bottom: 8px;">Learning Progression Baseline:</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">35% - From Ma et al. (2014) college ITS meta-analysis, g=0.32-0.37</code>
                    </p>
                    
                    <p style="margin: 15px 0;">
                        <strong style="color: #8b7355; display: block; margin-bottom: 8px;">Metacognitive Awareness Baseline:</strong>
                        <code style="background-color: #faf8f5; padding: 5px; border-radius: 3px; display: block;">31% - STEM intervention studies, F(1,114)=28.61, p<0.001</code>
                    </p>
                </div>
            </details>
        </div>
        
        <script>
            function filterTable() {
                const sectionFilter = document.getElementById('sectionFilter').value.toLowerCase();
                const typeFilter = document.getElementById('typeFilter').value.toLowerCase();
                const searchFilter = document.getElementById('searchInput').value.toLowerCase();
                const table = document.getElementById('featuresTable');
                const tr = table.getElementsByTagName('tr');
                let visibleCount = 0;
                
                for (let i = 1; i < tr.length; i++) {
                    const td = tr[i].getElementsByTagName('td');
                    let shouldShow = true;
                    
                    // Check section filter
                    if (sectionFilter && td[0].textContent.toLowerCase() !== sectionFilter) {
                        shouldShow = false;
                    }
                    
                    // Check type filter
                    if (typeFilter && td[7].textContent.toLowerCase() !== typeFilter) {
                        shouldShow = false;
                    }
                    
                    // Check search filter
                    if (searchFilter) {
                        let found = false;
                        for (let j = 0; j < td.length; j++) {
                            if (td[j].textContent.toLowerCase().indexOf(searchFilter) > -1) {
                                found = true;
                                break;
                            }
                        }
                        if (!found) shouldShow = false;
                    }
                    
                    tr[i].style.display = shouldShow ? '' : 'none';
                    if (shouldShow) visibleCount++;
                }
                
                updateStats(visibleCount);
            }
            
            function sortTable(n) {
                const table = document.getElementById('featuresTable');
                let rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
                switching = true;
                dir = 'asc';
                
                while (switching) {
                    switching = false;
                    rows = table.rows;
                    
                    for (i = 1; i < (rows.length - 1); i++) {
                        shouldSwitch = false;
                        x = rows[i].getElementsByTagName('TD')[n];
                        y = rows[i + 1].getElementsByTagName('TD')[n];
                        
                        if (dir == 'asc') {
                            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                                shouldSwitch = true;
                                break;
                            }
                        } else if (dir == 'desc') {
                            if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                                shouldSwitch = true;
                                break;
                            }
                        }
                    }
                    
                    if (shouldSwitch) {
                        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                        switching = true;
                        switchcount++;
                    } else {
                        if (switchcount == 0 && dir == 'asc') {
                            dir = 'desc';
                            switching = true;
                        }
                    }
                }
            }
            
            function updateStats(visibleCount) {
                const total = document.getElementById('featuresTable').rows.length - 1;
                document.getElementById('totalCount').textContent = total;
                document.getElementById('filteredCount').textContent = visibleCount;
            }
            
            // Initialize stats on load
            window.onload = function() {
                const total = document.getElementById('featuresTable').rows.length - 1;
                updateStats(total);
            };
        </script>
    </body>
    </html>
    """
    
    # Save HTML file
    with open('dashboard_features_table.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    # Also save as CSV for Excel
    df.to_csv('dashboard_features_table.csv', index=False)
    
    print("Generated dashboard_features_table.html")
    print("Generated dashboard_features_table.csv")

if __name__ == "__main__":
    generate_html_table()