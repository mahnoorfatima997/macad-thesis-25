class Validators:
    def __init__(self, state_validator, state_monitor):
        self.state_validator = state_validator
        self.state_monitor = state_monitor

    def validate(self, arch_state):
        return self.state_validator.validate_state(arch_state)

    def record(self, arch_state, label: str):
        return self.state_monitor.record_state_change(arch_state, label)


