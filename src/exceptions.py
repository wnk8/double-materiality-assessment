"""Custom exceptions for the Double Materiality Assessment Tool."""


class InvalidScoreError(Exception):
    """Raised when a score value is outside the valid range (1–5)."""

    def __init__(self, iro_id: str, field: str, value):
        self.iro_id = iro_id
        self.field = field
        self.value = value
        super().__init__(
            f"IRO '{iro_id}': field '{field}' has invalid value '{value}'. "
            f"Expected an integer between 1 and 5."
        )


class MissingIROError(Exception):
    """Raised when an expected IRO row is missing from the input file."""

    def __init__(self, iro_id: str):
        self.iro_id = iro_id
        super().__init__(
            f"IRO '{iro_id}' is missing from the input file. "
            f"Ensure all 20 IRO rows are present in the 'IRO_Eingabe' sheet."
        )
