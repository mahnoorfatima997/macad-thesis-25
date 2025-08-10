class ProgressionGlue:
    def __init__(self, progression_manager, first_response_generator):
        self.progression_manager = progression_manager
        self.first_response_generator = first_response_generator

    def update_state(self, student_state):
        return self.progression_manager.update_state(student_state)

    def analyze_first_message(self, user_input, student_state):
        return self.progression_manager.analyze_first_message(user_input, student_state)

    def progress_conversation(self, user_input, last_assistant_message, student_state):
        return self.progression_manager.progress_conversation(user_input, last_assistant_message, student_state)

    def get_milestone_guidance(self, user_input, student_state):
        return self.progression_manager.get_milestone_driven_agent_guidance(user_input, student_state)


