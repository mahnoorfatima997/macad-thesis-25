from langgraph.graph import StateGraph, END


def build_workflow(state_cls, handlers, route_decision_fn):
    """Construct the StateGraph with nodes and edges mirroring original wiring.

    handlers is a simple namespace/object with attributes:
      context, router, analysis, domain_expert, socratic, cognitive, synthesizer
    route_decision_fn(state) -> str is used in conditional edges for the router.
    """
    workflow = StateGraph(state_cls)

    workflow.add_node("context_agent", handlers.context)
    workflow.add_node("router", handlers.router)
    workflow.add_node("analysis_agent", handlers.analysis)
    workflow.add_node("domain_expert", handlers.domain_expert)
    workflow.add_node("socratic_tutor", handlers.socratic)
    workflow.add_node("cognitive_enhancement", handlers.cognitive)
    workflow.add_node("synthesizer", handlers.synthesizer)

    workflow.set_entry_point("context_agent")
    workflow.add_edge("context_agent", "router")

    workflow.add_conditional_edges(
        "router",
        route_decision_fn,
        {
            "progressive_opening": "synthesizer",
            "topic_transition": "synthesizer",
            "cognitive_intervention": "cognitive_enhancement",
            "socratic_exploration": "socratic_tutor",
            "design_guidance": "analysis_agent",
            "multi_agent_comprehensive": "analysis_agent",
            "knowledge_with_challenge": "analysis_agent",
            "socratic_clarification": "socratic_tutor",
            "supportive_scaffolding": "socratic_tutor",
            "cognitive_challenge": "cognitive_enhancement",
            "foundational_building": "socratic_tutor",
            "balanced_guidance": "analysis_agent",
            "knowledge_only": "domain_expert",
            "socratic_focus": "analysis_agent",
            "default": "analysis_agent",
        },
    )

    # After analysis
    def after_analysis_routing(state):
        return "to_domain_expert"

    workflow.add_conditional_edges(
        "analysis_agent",
        after_analysis_routing,
        {
            "to_domain_expert": "domain_expert",
            "to_socratic": "socratic_tutor",
            "to_cognitive": "cognitive_enhancement",
            "to_synthesizer": "synthesizer",
        },
    )

    # After domain expert
    def after_domain_expert(state):
        return "to_socratic"

    workflow.add_conditional_edges(
        "domain_expert",
        after_domain_expert,
        {
            "to_socratic": "socratic_tutor",
            "to_synthesizer": "synthesizer",
        },
    )

    # After socratic tutor
    def after_socratic_tutor(state):
        return "to_cognitive"

    workflow.add_conditional_edges(
        "socratic_tutor",
        after_socratic_tutor,
        {
            "to_cognitive": "cognitive_enhancement",
            "to_synthesizer": "synthesizer",
        },
    )

    workflow.add_edge("cognitive_enhancement", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()


