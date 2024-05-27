class QuotaError(Exception):
    """Exception raised when the user's quota is exceeded."""

    def __init__(self, message="Quota exceeded, cannot proceed with transcription"):
        self.message = message
        super().__init__(self.message)