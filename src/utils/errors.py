
TIMEOUT_JOB_MSG="Timeout while processing transcription job."
FAILED_JOB_MSG="Audio Transcription job failed."

class OTPError(Exception):
  """Raise when error during creating OTP"""
  def __init__(self, message: str, *args) -> None:
    self.message = message

    super(OTPError, self).__init__(message, *args)