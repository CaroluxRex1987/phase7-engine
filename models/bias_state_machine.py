class BiasStateMachine:
    """
    Phase‑7 Bias State Machine

    States:
        - LONG
        - SHORT
        - NEUTRAL

    Transition rules:
        - Strong bias score → commit to LONG/SHORT
        - Weak bias score → revert to NEUTRAL
        - Smooth transitions (no abrupt flips)
    """

    def __init__(self):
        self.state = "NEUTRAL"

    def transition(self, raw_bias, bias_score):
        """
        Transition logic:
            - If bias_score >= 60 → adopt raw_bias
            - If bias_score <= 30 → revert to NEUTRAL
            - Otherwise → keep current state (smooth transition)
        """

        # Strong conviction → adopt raw bias
        if bias_score >= 60:
            self.state = raw_bias

        # Weak conviction → neutralize
        elif bias_score <= 30:
            self.state = "NEUTRAL"

        # Otherwise → keep previous state (smooth transitions)
        return self.state

