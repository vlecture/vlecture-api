import http

from fastapi import APIRouter, Depends

from services.transcription import TranscriptionService