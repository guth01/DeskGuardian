from utils.enums import SystemState


class StateManager:
    """
    Handles system state transitions
    based on predefined valid transitions
    from the State Transition Diagram.
    """

    def __init__(self):
        self.current_state = SystemState.IDLE

        # Define valid transitions
        self.valid_transitions = {
            SystemState.IDLE: [
                SystemState.INITIALIZING,
                SystemState.STOPPED
            ],

            SystemState.INITIALIZING: [
                SystemState.MONITORING,
                SystemState.WEBCAM_ERROR
            ],

            SystemState.WEBCAM_ERROR: [
                SystemState.IDLE
            ],

            SystemState.MONITORING: [
                SystemState.GOOD_POSTURE,
                SystemState.BAD_POSTURE,
                SystemState.IDLE_DETECTED,
                SystemState.BURNOUT_CHECK,
                SystemState.STOPPED
            ],

            SystemState.GOOD_POSTURE: [
                SystemState.MONITORING
            ],

            SystemState.BAD_POSTURE: [
                SystemState.MONITORING
            ],

            SystemState.IDLE_DETECTED: [
                SystemState.BREAK_DETECTED,
                SystemState.MONITORING
            ],

            SystemState.BREAK_DETECTED: [
                SystemState.MONITORING
            ],

            SystemState.BURNOUT_CHECK: [
                SystemState.LOW_RISK,
                SystemState.HIGH_RISK
            ],

            SystemState.LOW_RISK: [
                SystemState.MONITORING
            ],

            SystemState.HIGH_RISK: [
                SystemState.MONITORING
            ],

            SystemState.STOPPED: []
        }

    # ======================================
    # GET CURRENT STATE
    # ======================================

    def get_state(self):
        return self.current_state

    # ======================================
    # TRANSITION TO NEW STATE
    # ======================================

    def transition(self, new_state: SystemState):
        if new_state in self.valid_transitions[self.current_state]:
            print(f"[STATE] {self.current_state.value} → {new_state.value}")
            self.current_state = new_state
        else:
            raise Exception(
                f"Invalid transition from {self.current_state.value} "
                f"to {new_state.value}"
            )
