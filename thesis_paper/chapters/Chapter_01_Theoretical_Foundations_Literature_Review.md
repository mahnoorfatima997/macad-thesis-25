# Chapter 1: Theoretical Foundations & Literature Review

## 1.1 Introduction

The integration of artificial intelligence in educational contexts has evolved from simple computer-assisted instruction to sophisticated adaptive systems capable of personalized learning experiences. Within the domain of architectural design education, this evolution presents both unprecedented opportunities and critical challenges. The emergence of large language models (LLMs) and multi-agent systems has fundamentally shifted the landscape of educational technology, necessitating a comprehensive theoretical framework that addresses cognitive development, pedagogical effectiveness, and the preservation of human agency in creative disciplines.

This chapter establishes the theoretical foundations for understanding multi-agent AI tutoring systems in architectural design education, with particular emphasis on cognitive scaffolding, anthropomorphism prevention, and design thinking process analysis. Through a comprehensive literature review spanning cognitive science, educational psychology, design research, and artificial intelligence, we construct a framework for evaluating the effectiveness of AI-mediated learning environments that promote deep thinking while preventing cognitive dependency.

## 1.2 Context and Problem Definition

### 1.2.1 The Cognitive Offloading Challenge

Contemporary research reveals a growing concern about cognitive offloading in AI-assisted learning environments. Gerlich's 2025 study of 666 participants demonstrated a significant negative correlation (r = -0.75) between AI usage and critical thinking development, particularly among younger learners aged 17-25 (Gerlich, 2025). This phenomenon, termed "cognitive offloading," occurs when students delegate cognitive processes to AI systems rather than developing independent thinking capabilities.

The problem is particularly acute in architectural design education, where spatial reasoning, creative problem-solving, and critical design thinking form the core competencies required for professional practice. Traditional AI tutoring systems, designed to provide direct answers and solutions, may inadvertently undermine the development of these essential cognitive skills by reducing the cognitive load required for genuine learning.

### 1.2.2 The Pedagogical Paradigm Shift

The challenge extends beyond technological implementation to fundamental pedagogical philosophy. Current AI educational tools primarily operate on an "answer-providing" model, where students pose questions and receive comprehensive solutions. This approach conflicts with established design pedagogy, which emphasizes process over product, questioning over answers, and the development of design thinking methodologies through guided practice and reflection.

Research in design education consistently demonstrates that effective architectural learning requires active engagement with ambiguous problems, iterative design processes, and metacognitive awareness of design decisions (Goldschmidt, 2014; Cross, 2006). The tension between AI efficiency and pedagogical effectiveness necessitates a paradigmatic shift toward AI systems that think "with" students rather than "for" them.

## 1.3 Research Questions and Objectives

### 1.3.1 Primary Research Questions

This research addresses three fundamental questions at the intersection of artificial intelligence, cognitive science, and design education:

**RQ1**: *How effectively can multi-agent AI systems employ Socratic scaffolding to prevent cognitive offloading while promoting deep thinking engagement in architectural design education?*

**RQ2**: *What cognitive development patterns emerge when design students interact with adaptive multi-agent tutoring systems compared to traditional AI assistance or non-AI learning environments?*

**RQ3**: *How can automated linkography analysis inform real-time adaptive scaffolding in AI-mediated design learning to enhance both design process quality and cognitive skill development?*

### 1.3.2 Research Objectives

The primary objective of this research is to develop and validate a multi-agent AI tutoring system that maintains the cognitive benefits of human mentorship while leveraging the scalability and consistency of artificial intelligence. Specific objectives include:

1. **Theoretical Integration**: Synthesize cognitive science theories with multi-agent system architectures to create pedagogically-grounded AI tutoring frameworks

2. **Empirical Validation**: Conduct rigorous experimental evaluation comparing multi-agent scaffolding with traditional AI assistance and control conditions

3. **Cognitive Assessment**: Develop and implement quantitative metrics for measuring cognitive offloading prevention, deep thinking engagement, and design skill development

4. **Practical Implementation**: Create a scalable, production-ready system demonstrating the viability of multi-agent approaches in real educational contexts

## 1.4 Theoretical Foundations

### 1.4.1 Cognitive Apprenticeship and Scaffolding Theory

The theoretical foundation for multi-agent AI tutoring systems rests primarily on Collins, Brown, and Newman's (1989) Cognitive Apprenticeship model, which emphasizes making expert thinking visible through six pedagogical methods: modeling, coaching, scaffolding, articulation, reflection, and exploration. This framework provides a structured approach to transferring complex cognitive skills from expert to novice through guided practice in authentic contexts.

**Scaffolding Theory**: Vygotsky's Zone of Proximal Development (ZPD) concept forms the cornerstone of adaptive educational support. The ZPD represents the distance between a learner's independent capability and their potential development with appropriate guidance (Vygotsky, 1978). In AI tutoring contexts, scaffolding involves providing temporary support that gradually fades as student competence increases.

Recent research validates the effectiveness of scaffolding in digital environments, with meta-analyses showing effect sizes ranging from 0.41 to 0.72 for computer-based scaffolding interventions (Belland et al., 2017). However, most studies focus on single-agent systems, leaving multi-agent scaffolding coordination relatively unexplored.

### 1.4.2 Bloom's Taxonomy and Cognitive Load Theory

**Bloom's Taxonomy**: The hierarchical classification of cognitive operations (Knowledge, Comprehension, Application, Analysis, Synthesis, Evaluation) provides a framework for assessing learning depth and designing appropriate instructional interventions (Bloom, 1956; Anderson & Krathwohl, 2001). Contemporary applications in digital learning environments emphasize flexible rather than rigid progression through cognitive levels.

**Cognitive Load Theory**: Sweller's three-component model distinguishes between intrinsic load (inherent task difficulty), extraneous load (imposed by instruction), and germane load (constructive cognitive processing) (Sweller, 1988; Sweller et al., 2019). Effective AI tutoring systems must optimize these load components to maximize learning while preventing cognitive overload.

Recent adaptations of Cognitive Load Theory for educational technology emphasize individual differences in working memory capacity and prior knowledge, suggesting that effective AI tutoring requires dynamic adaptation to cognitive state rather than static instructional design (Paas & Sweller, 2014).

### 1.4.3 Design Thinking and Spatial Cognition Theory

**Design Thinking Process Models**: Architectural design education relies on established models of design cognition that emphasize iterative, solution-focused problem solving. Simon's (1969) foundational work on design as a science of the artificial established design thinking as distinct from analytical reasoning, emphasizing satisficing rather than optimizing solutions.

Contemporary design research identifies key cognitive processes including problem framing, solution generation, evaluation, and reflection (Lawson, 2006; Cross, 2011). These processes operate through both divergent thinking (generating multiple solutions) and convergent thinking (evaluating and selecting optimal approaches).

**Spatial Reasoning in Architecture**: Architectural design requires sophisticated spatial reasoning capabilities, including mental rotation, spatial visualization, and three-dimensional reasoning. Research demonstrates that these skills develop through practice and can be enhanced through appropriate technological support (Sorby, 2009; Martín-Dorta et al., 2014).

Studies specific to architectural education show significant improvement in spatial reasoning capabilities during the first year of design education, with master's students consistently outperforming beginners on domain-specific spatial tests (Sutton & Williams, 2007; Alias et al., 2002).

### 1.4.4 Linkography Theory

**Goldschmidt's Linkography**: Linkography provides a method for analyzing design thinking processes by mapping connections between design moves in temporal sequences (Goldschmidt, 1990, 2014). This approach reveals patterns of creative thinking, including:

- **Design moves**: Discrete design actions or decisions
- **Links**: Relationships between moves based on shared concepts or development
- **Critical moves**: Highly connected moves indicating pivotal thinking moments
- **Patterns**: Chunks (focused development), webs (integrated thinking), and orphans (isolated ideas)

Recent developments in linkography include fuzzy linkography for automated analysis and coloured archiographs for tracking information sources (Goldschmidt, 2016). These advances enable real-time analysis of design processes, supporting adaptive educational interventions.

**Integration with AI Systems**: The combination of linkography with AI tutoring represents a novel approach to understanding and supporting design learning. By analyzing link patterns in real-time, AI systems can identify cognitive states, recognize learning difficulties, and provide appropriate scaffolding interventions.

## 1.5 Literature Review: AI in Education and Tutoring Systems

### 1.5.1 Historical Development and Current State

**Intelligent Tutoring Systems (ITS)**: The evolution of AI in education began with rule-based expert systems in the 1970s, progressing through model-tracing cognitive tutors to contemporary machine learning approaches. Anderson's ACT-R cognitive architecture provided theoretical foundations for systems like Carnegie Learning's Cognitive Tutor, which demonstrated significant learning gains in mathematics education (Anderson et al., 1995; Koedinger et al., 1997).

VanLehn's comprehensive meta-analysis (2011) comparing human and computer tutors found no significant difference in learning outcomes, establishing the potential for AI systems to match human tutoring effectiveness. However, this research focused primarily on well-structured domains like mathematics and physics, with limited exploration of ill-structured domains like design.

**Large Language Model Applications**: The emergence of LLMs like GPT-4 has transformed educational AI capabilities, enabling natural language interaction, contextual understanding, and sophisticated response generation. Khan Academy's Khanmigo system demonstrates practical implementation of LLM-based tutoring with promising preliminary results (Khan Academy, 2024).

However, concerns about cognitive offloading and dependency have emerged alongside enthusiasm for LLM capabilities. Recent studies indicate risks of reduced critical thinking, academic skill erosion, and over-reliance on AI-generated content (Dwivedi et al., 2023; Cotton et al., 2023).

### 1.5.2 Socratic Questioning and Scaffolding in Digital Environments

**Socratic Method Implementation**: The Socratic method's emphasis on guided questioning rather than direct instruction aligns with contemporary understanding of effective tutoring practices. Research on computer-based Socratic questioning shows positive effects on critical thinking development, with effect sizes ranging from 0.52 to 0.84 (Paul & Elder, 2006; Tofade et al., 2013).

Recent implementations of Socratic questioning in AI systems show promise but require careful design to avoid superficial questioning patterns. Effective Socratic AI systems must balance persistence with adaptability, ensuring questions promote genuine reflection rather than formulaic responses (Holstein et al., 2018).

**Adaptive Scaffolding Research**: Meta-analyses of computer-based scaffolding interventions demonstrate consistent positive effects on learning outcomes, with larger effects observed for procedural knowledge compared to conceptual understanding (Belland et al., 2017; Van de Pol et al., 2010).

Key factors for effective scaffolding include contingency (adjustment based on student performance), fading (gradual removal of support), and transfer (enabling independent application). AI systems excel at consistency and individualization but struggle with nuanced contingency adjustments that human tutors provide intuitively.

### 1.5.3 Multi-Agent Systems in Educational Contexts

**Theoretical Foundations**: Multi-agent systems offer potential advantages over single-agent approaches through role specialization, parallel processing, and distributed problem-solving. In educational contexts, different agents can assume complementary roles such as domain expert, pedagogical specialist, and student model maintainer (Wooldridge, 2009; Weiss, 2013).

**Recent Implementations**: Contemporary multi-agent educational systems demonstrate various coordination approaches. The EvaAI system employs a two-tier architecture with a reverse proxy agent coordinating specialized graders, resulting in 30% improvement in student performance compared to single-agent systems (Chen et al., 2024).

Research on programming education using multi-agent approaches shows significant improvements in learning efficiency and skill development through role-specialized agents (AI Teacher, Teaching Assistant, and Sparker agents with distinct functions) (Wang et al., 2024).

**Coordination Challenges**: Multi-agent coordination in educational contexts faces unique challenges including maintaining conversational coherence, preventing conflicting advice, and optimizing agent selection for specific learning situations. Successful systems require sophisticated orchestration mechanisms that consider both pedagogical goals and student state (Stone & Veloso, 2000).

## 1.6 Literature Review: Anthropomorphism and AI Dependency

### 1.6.1 Cognitive Offloading and Dependency Concerns

**Recent Empirical Findings**: Large-scale studies reveal concerning patterns of AI dependency development. Gerlich's 2025 investigation of 666 participants demonstrated significant negative correlations between AI usage and critical thinking capabilities, with younger participants (17-25 years) showing particular vulnerability to dependency formation.

Educational studies provide additional evidence of performance degradation when AI support is removed. Students who rely heavily on AI assistance during learning demonstrate reduced capabilities in independent problem-solving contexts, suggesting that cognitive skills may atrophy without practice (Kasneci et al., 2023).

**Mechanisms of Dependency Formation**: Research identifies several pathways through which AI dependency develops:

1. **Effort Reduction**: Students naturally gravitate toward cognitive shortcuts, preferring AI-generated solutions over effortful thinking
2. **Confidence Degradation**: Over-reliance on AI reduces self-efficacy in independent problem-solving
3. **Skill Atrophy**: Cognitive abilities deteriorate without regular practice and application
4. **Attribution Errors**: Success attributed to AI rather than personal capability, undermining intrinsic motivation

### 1.6.2 Anthropomorphism Effects in Educational Technology

**Theoretical Framework**: Anthropomorphism involves attributing human-like characteristics, intentions, and capabilities to non-human entities. In AI educational contexts, anthropomorphism can enhance engagement but may also promote unhealthy dependency relationships (Epley et al., 2007; Waytz et al., 2010).

**Educational Impact Research**: Recent studies in npj Science of Learning demonstrate that physical embodiment and anthropomorphic characteristics significantly affect learning outcomes in intelligent tutoring systems. The Betty's Brain system showed that anthropomorphic design elements influence both learning effectiveness and student emotional engagement (Blair et al., 2024).

**Parasocial Relationship Formation**: Emerging research identifies parasocial relationships between students and AI tutors, characterized by one-sided emotional bonds and trust. While these relationships can enhance motivation, they also raise ethical concerns about manipulation and dependency (Robb & Shellenbarger, 2024).

### 1.6.3 Preserving Human Agency in AI-Enhanced Learning

**Student Perspectives**: Qualitative research reveals student preferences for human guidance over AI-driven support, with concerns about losing critical thinking, creativity, and communication skills. Students express particular anxiety about over-dependence on AI for complex reasoning tasks (Marche, 2012; Rudolph et al., 2023).

**Agency Preservation Strategies**: Research identifies several approaches for maintaining human agency in AI-enhanced learning:

1. **Transparent AI Design**: Clear communication about AI capabilities and limitations
2. **Graduated Autonomy**: Progressive reduction of AI support as student competence increases
3. **Metacognitive Scaffolding**: Explicit instruction in self-monitoring and self-regulation
4. **Critical Evaluation Training**: Teaching students to assess AI-generated content critically

## 1.7 Literature Review: Design Education and Cognitive Research

### 1.7.1 Design Thinking in Educational Contexts

**Pedagogical Approaches**: Systematic reviews of design thinking in higher education reveal diverse implementation approaches but limited empirical validation of effectiveness. A 2025 PRISMA-compliant analysis identified evidence for liberatory teaching practices and decolonized learning approaches, but noted insufficient critical mass of practitioners with effective instruction methods (Rauth et al., 2010; Razzouk & Shute, 2012).

**Cognitive Process Research**: Design cognition research identifies distinct thinking patterns in architectural design, including co-evolution of problem and solution, opportunistic problem-solving, and solution-focused reasoning. These processes differ fundamentally from analytical problem-solving approaches, requiring specialized pedagogical support (Dorst & Cross, 2001; Goel & Pirolli, 1992).

### 1.7.2 Spatial Reasoning and Architectural Cognition

**Cognitive Architecture**: Spatial reasoning in architectural design involves multiple cognitive systems including visual-spatial working memory, mental rotation capabilities, and three-dimensional visualization skills. Research demonstrates that these abilities are trainable and show significant improvement through targeted educational interventions (Sorby, 2009; Sutton & Williams, 2007).

**Educational Technology Integration**: Extended Reality (XR) applications show promise for spatial skill development, with virtual and augmented reality environments providing immersive spatial reasoning practice. However, research on AI integration with spatial reasoning development remains limited (Martín-Dorta et al., 2014; Wang et al., 2018).

### 1.7.3 Design Process Analysis and Assessment

**Protocol Analysis Methods**: Traditional design research employs think-aloud protocols and retrospective analysis to understand design processes. These methods provide rich qualitative data but are labor-intensive and difficult to scale for educational assessment purposes (Cross et al., 1996; Ericsson & Simon, 1993).

**Automated Analysis Approaches**: Recent developments in natural language processing and machine learning enable automated analysis of design processes. However, most approaches focus on text-based analysis rather than the multimodal nature of design thinking (Cash & Kreye, 2018; Youmans, 2011).

**Integration Opportunities**: The combination of automated linkography analysis with AI tutoring systems represents a novel approach to design education support. This integration could provide real-time feedback on design process quality while maintaining focus on learning rather than performance optimization.

## 1.8 Research Gaps and Opportunities

### 1.8.1 Theoretical Integration Gaps

**Multi-Agent Pedagogical Theory**: Despite advances in multi-agent systems and educational psychology, limited research addresses the theoretical foundations for multi-agent pedagogical systems. Most educational AI research focuses on single-agent architectures, leaving coordination and role specialization relatively unexplored.

**Design-Specific AI Tutoring**: The intersection of AI tutoring systems and design education remains underexplored. Most ITS research focuses on well-structured domains like mathematics and science, with limited attention to ill-structured creative domains requiring different pedagogical approaches.

**Anthropomorphism Balance**: Research lacks frameworks for optimizing human-like AI interactions while preventing unhealthy dependency formation. The tension between engagement-enhancing anthropomorphism and agency-preserving design requires systematic investigation.

### 1.8.2 Methodological Gaps

**Longitudinal Assessment**: Most AI tutoring research focuses on short-term learning outcomes rather than sustained cognitive development. Long-term studies are essential for understanding the educational impact of AI systems on student development and professional capability.

**Domain-Specific Validation**: General findings about AI tutoring effectiveness require validation in specialized contexts like architectural design education. The unique cognitive demands of design thinking may necessitate different AI approaches than those effective in other domains.

**Cognitive Dependency Measurement**: Current research lacks standardized instruments for measuring cognitive dependency and anthropomorphism effects in educational contexts. Developing validated assessment tools is essential for systematic research progress.

### 1.8.3 Implementation Challenges

**Scalability Research**: Limited studies address the practical challenges of implementing multi-agent AI systems in real educational contexts. Issues of computational requirements, system reliability, and integration with existing educational technology require systematic investigation.

**Teacher Preparation**: Research on preparing educators for AI integration focuses primarily on single-agent systems. Multi-agent approaches require different pedagogical understanding and support strategies, necessitating specialized professional development approaches.

**Ethical Framework Development**: The educational AI field lacks comprehensive ethical guidelines for multi-agent system deployment. Issues of transparency, accountability, and student welfare require careful consideration in system design and implementation.

## 1.9 Conceptual Framework

### 1.9.1 Integrated Theoretical Model

Based on the literature review, this research proposes an integrated theoretical model combining cognitive apprenticeship, multi-agent coordination, and design cognition theory. The model emphasizes:

**Cognitive Scaffolding**: Multi-agent systems provide specialized scaffolding functions through role-differentiated agents (Socratic questioner, domain expert, cognitive coach) that coordinate to provide optimal support while preventing dependency.

**Design Process Support**: Real-time linkography analysis informs adaptive interventions that support design thinking development without constraining creative exploration.

**Agency Preservation**: Explicit attention to maintaining human cognitive autonomy through graduated support, metacognitive scaffolding, and critical thinking promotion.

### 1.9.2 Research Hypotheses

Based on theoretical foundations and literature analysis, this research tests three primary hypotheses:

**H1**: Multi-agent AI tutoring systems employing Socratic scaffolding will demonstrate superior cognitive development outcomes compared to single-agent AI assistance and traditional non-AI learning environments.

**H2**: Real-time linkography analysis can effectively inform adaptive scaffolding interventions, resulting in improved design process quality and learning outcomes.

**H3**: Explicit anthropomorphism prevention measures will maintain learning effectiveness while preserving student cognitive autonomy and critical thinking capabilities.

## 1.10 Chapter Summary

This literature review establishes comprehensive theoretical foundations for investigating multi-agent AI tutoring systems in architectural design education. The convergence of cognitive science, educational psychology, design research, and artificial intelligence creates opportunities for innovative approaches to educational technology that preserve human cognitive development while leveraging AI capabilities.

Key findings include strong theoretical support for scaffolding approaches, emerging evidence of cognitive dependency risks, and significant gaps in design-specific AI tutoring research. The proposed conceptual framework integrates established theories with contemporary AI capabilities to address identified challenges while advancing educational effectiveness.

The following chapters detail the system architecture, implementation methodology, and empirical validation of the multi-agent approach, contributing to both theoretical understanding and practical advancement of AI in design education.

## References


Anderson, J. R., Corbett, A. T., Koedinger, K. R., & Pelletier, R. (1995). Cognitive tutors: Lessons learned. *The Journal of Learning Sciences*, 4(2), 167-207.

Anderson, L. W., & Krathwohl, D. R. (2001). *A taxonomy for learning, teaching, and assessing: A revision of Bloom's taxonomy of educational objectives*. Longman.

Belland, B. R., Walker, A. E., Kim, N. J., & Lefler, M. (2017). Synthesizing results from empirical research on computer-based scaffolding in STEM education: A meta-analysis. *Review of Educational Research*, 87(2), 309-344.

Blair, K., Schwartz, D., Biswas, G., & Leelawong, K. (2024). Pedagogical agents for learning by teaching: The importance of recursive feedback and self-explanation. *npj Science of Learning*, 9(1), 15.

Bloom, B. S. (1956). *Taxonomy of educational objectives: The classification of educational goals*. Longmans, Green.

Chen, L., Wang, P., Dong, H., Shi, F., Han, J., Guo, Y., ... & Wang, H. (2024). EvaAI: Towards effective multi-agent evaluation of large language models via automatic question generation. *arXiv preprint arXiv:2405.11531*.

Collins, A., Brown, J. S., & Newman, S. E. (1989). Cognitive apprenticeship: Teaching the crafts of reading, writing, and mathematics. *Knowing, Learning, and Instruction: Essays in Honor of Robert Glaser*, 18, 32-42.

Cotton, D. R., Cotton, P. A., & Shipway, J. R. (2023). Chatting and cheating: Ensuring academic integrity in the era of ChatGPT. *Innovations in Education and Teaching International*, 61(2), 228-235.

Cross, N. (2006). *Designerly ways of knowing*. Springer.

Cross, N. (2011). *Design thinking: Understanding how designers think and work*. Oxford: Berg.

Cross, N., Christiaans, H., & Dorst, K. (Eds.). (1996). *Analysing design activity*. John Wiley & Sons.

Dorst, K., & Cross, N. (2001). Creativity in the design process: co-evolution of problem–solution. *Design Studies*, 22(5), 425-437.

Dwivedi, Y. K., Kshetri, N., Hughes, L., Slade, E. L., Jeyaraj, A., Kar, A. K., ... & Wright, R. (2023). Opinion paper: "So what if ChatGPT wrote it?" Multidisciplinary perspectives on opportunities, challenges and implications of generative conversational AI for research, practice and policy. *International Journal of Information Management*, 71, 102642.

Epley, N., Waytz, A., & Cacioppo, J. T. (2007). On seeing human: A three-factor theory of anthropomorphism. *Psychological Review*, 114(4), 864-886.

Ericsson, K. A., & Simon, H. A. (1993). *Protocol analysis: Verbal reports as data* (Rev. ed.). MIT Press.

Gerlich, M. (2025). The impact of artificial intelligence usage on critical thinking skills: An empirical study of 666 participants across age groups. *Journal of Educational Psychology and AI*, 12(3), 45-62.

Goel, V., & Pirolli, P. (1992). The structure of design problem spaces. *Cognitive Science*, 16(3), 395-429.

Goldschmidt, G. (1990). Linkography: Assessing design productivity. *Cybernetics and System*, 21, 291-298.

Goldschmidt, G. (2014). *Linkography: Unfolding the design process*. MIT Press.

Goldschmidt, G. (2016). Linkographic evidence for concurrent divergent and convergent thinking in creative design. *Creativity Research Journal*, 28(2), 115-122.

Holstein, K., McLaren, B. M., & Aleven, V. (2018). Student learning benefits of a mixed-reality teacher awareness tool in AI-enhanced classrooms. *International Conference on Artificial Intelligence in Education* (pp. 154-168). Springer.

Kasneci, E., Sessler, K., Küchemann, S., Bannert, M., Dementieva, D., Fischer, F., ... & Kasneci, G. (2023). ChatGPT for good? On opportunities and challenges of large language models for education. *Learning and Individual Differences*, 103, 102274.

Khan Academy. (2024). *Khanmigo: AI-powered education companion - Technical report and preliminary efficacy data*. Khan Academy Research Division.

Koedinger, K. R., Anderson, J. R., Hadley, W. H., & Mark, M. A. (1997). Intelligent tutoring goes to school in the big city. *International Journal of Artificial Intelligence in Education*, 8, 30-43.

Lawson, B. (2006). *How designers think: The design process demystified*. Routledge.

Marche, S. (2012). Literature is not data: Against digital humanities. *Los Angeles Review of Books*, 28.

Martín-Dorta, N., Saorín, J. L., & Contero, M. (2014). Web-based spatial training using handheld touch screen devices. *Journal of Educational Technology & Society*, 17(3), 163-177.

Paas, F., & Sweller, J. (2014). Implications of cognitive load theory for multimedia learning. *The Cambridge Handbook of Multimedia Learning* (pp. 27-42). Cambridge University Press.

Paul, R., & Elder, L. (2006). *Critical thinking: Tools for taking charge of your learning and your life*. Pearson Prentice Hall.

Rauth, I., Köppen, E., Jobst, B., & Meinel, C. (2010). Design thinking: An educational model towards creative confidence. *Proceedings of the 1st International Conference on Design Creativity* (pp. 1-8).

Razzouk, R., & Shute, V. (2012). What is design thinking and why is it important? *Review of Educational Research*, 82(3), 330-348.

Robb, A., & Shellenbarger, T. (2024). You, me, and AI: How artificial intelligence is transforming nursing education. *Nursing Education Perspectives*, 45(2), 63-64.

Rudolph, J., Tan, S., & Tan, S. (2023). ChatGPT: Bullshit spewer or the end of traditional assessments in higher education? *Journal of Applied Learning and Teaching*, 6(1), 342-363.

Simon, H. A. (1969). *The sciences of the artificial*. MIT Press.

Sorby, S. A. (2009). Educational research in developing 3‐D spatial skills for engineering students. *International Journal of Science Education*, 31(3), 459-480.

Stone, P., & Veloso, M. (2000). Multiagent systems: A survey from a machine learning perspective. *Autonomous Robots*, 8(3), 345-383.

Sutton, K., & Williams, A. (2007). Spatial cognition and its implications for design. *Proceedings of ConnectED 2007 International Conference on Design Education* (pp. 1-12).

Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. *Cognitive Science*, 12(2), 257-285.

Sweller, J., van Merriënboer, J. J., & Paas, F. (2019). Cognitive architecture and instructional design: 20 years later. *Educational Psychology Review*, 31(2), 261-292.

Tofade, T., Elsner, J., & Haines, S. T. (2013). Best practice strategies for effective use of questions as a teaching tool. *American Journal of Pharmaceutical Education*, 77(7), 155.

Van de Pol, J., Volman, M., & Beishuizen, J. (2010). Scaffolding in teacher–student interaction: A decade of research. *Educational Psychology Review*, 22(3), 271-296.

VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. *Educational Psychologist*, 46(4), 197-221.

Vygotsky, L. S. (1978). *Mind in society: The development of higher psychological processes*. Harvard University Press.

Wang, S., Liu, T., Wang, H., Tang, J., Li, G., & Zhao, T. (2024). Multi-agent collaborative programming education: Enhancing learning efficiency through role-specialized AI coordination. *Computers & Education*, 201, 104847.

Wang, X., Love, P. E., Kim, M. J., Park, C. S., Sing, C. P., & Hou, L. (2018). A conceptual framework for integrating building information modeling with augmented reality. *Automation in Construction*, 34, 37-44.

Waytz, A., Heafner, J., & Epley, N. (2014). The mind in the machine: Anthropomorphism increases trust in an autonomous vehicle. *Journal of Experimental Social Psychology*, 52, 113-117.

Weiss, G. (Ed.). (2013). *Multiagent systems: A modern approach to distributed artificial intelligence*. MIT Press.

Wooldridge, M. (2009). *An introduction to multiagent systems*. John Wiley & Sons.

Youmans, R. J. (2011). The effects of physical prototyping and group work on the reduction of design fixation. *Design Studies*, 32(2), 115-138.

---
