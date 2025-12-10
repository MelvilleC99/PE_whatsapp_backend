"""
Transcription Tool - Convert voice notes to text using Whisper

Handles:
1. Download audio from Meta's servers
2. Transcribe via OpenAI Whisper API
3. Save transcription to Firebase
4. Return transcribed text
"""
import os
import tempfile
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .registry import BaseTool, ToolParameter


class TranscriptionTool(BaseTool):
    """Tool for transcribing voice notes to text."""
    
    name = "transcription"
    
    description = """Convert a WhatsApp voice note to text using Whisper.
    Use this tool when you receive an audio message that needs to be 
    transcribed before further processing. The transcription is automatically
    saved to Firebase for audit trail."""
    
    parameters = [
        ToolParameter(
            name="audio_id",
            type="string",
            description="The WhatsApp media ID of the audio file to transcribe",
            required=True
        ),
        ToolParameter(
            name="phone",
            type="string",
            description="Sender's phone number in international format (e.g., 27821234567)",
            required=True
        ),
        ToolParameter(
            name="profile_name",
            type="string",
            description="Sender's WhatsApp display name",
            required=False
        ),
        ToolParameter(
            name="message_id",
            type="string",
            description="WhatsApp message ID for reference",
            required=False
        ),
        ToolParameter(
            name="timestamp",
            type="string",
            description="Original message timestamp",
            required=False
        ),
        ToolParameter(
            name="mime_type",
            type="string",
            description="Audio MIME type (e.g., audio/ogg, audio/mpeg)",
            required=False,
            default="audio/ogg"
        ),
    ]
    
    examples = [
        {"when": "User sends a voice note with listing details"},
        {"when": "User sends audio instead of typing a message"},
        {"when": "Message type is 'audio' in the webhook payload"},
    ]
    
    output_description = """Returns dict with:
    - status: 'success' or 'error'
    - text: The transcribed text (if successful)
    - transcription_id: Firebase document ID
    - audio_id: Original audio ID
    - error: Error message (if failed)"""
    
    def __init__(self):
        from src.clients.whatsapp import WhatsAppClient
        from src.clients.firebase import FirebaseClient
        from src.config import settings
        
        self.whatsapp = WhatsAppClient()
        self.firebase = FirebaseClient()
        self.openai_api_key = settings.openai_api_key
        
        # Check if OpenAI is configured
        if not self.openai_api_key:
            logger.warning("OpenAI API key not configured - transcription will fail")
    
    def execute(
        self, 
        audio_id: str,
        phone: str = None,
        profile_name: str = None,
        message_id: str = None,
        timestamp: str = None,
        mime_type: str = "audio/ogg",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.
        
        Args:
            audio_id: WhatsApp audio message ID
            phone: Sender's phone number
            profile_name: Sender's WhatsApp profile name
            message_id: WhatsApp message ID
            timestamp: Message timestamp
            mime_type: Audio MIME type
            
        Returns:
            Result with transcribed text
        """
        logger.info(f"Transcription requested for audio: {audio_id} from {phone}")
        
        try:
            # Step 1: Download audio from Meta
            audio_data = self._download_audio(audio_id)
            
            if not audio_data:
                return {
                    'status': 'error',
                    'error': 'Failed to download audio from WhatsApp',
                    'audio_id': audio_id,
                    'text': None
                }
            
            # Step 2: Transcribe via Whisper
            text = self._transcribe_audio(audio_data, mime_type)
            
            if not text:
                return {
                    'status': 'error',
                    'error': 'Failed to transcribe audio',
                    'audio_id': audio_id,
                    'text': None
                }
            
            # Step 3: Save to Firebase
            transcription_id = self._save_transcription(
                phone=phone,
                profile_name=profile_name,
                audio_id=audio_id,
                message_id=message_id,
                text=text,
                timestamp=timestamp,
                mime_type=mime_type
            )
            
            logger.success(f"Transcription complete: {text[:100]}...")
            
            return {
                'status': 'success',
                'audio_id': audio_id,
                'text': text,
                'transcription_id': transcription_id,
                'phone': phone
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'audio_id': audio_id,
                'text': None
            }
    
    def _download_audio(self, audio_id: str) -> Optional[bytes]:
        """Download audio file from WhatsApp."""
        logger.info(f"Downloading audio: {audio_id}")
        try:
            data = self.whatsapp.download_media(audio_id)
            if data:
                logger.info(f"Downloaded {len(data)} bytes")
            else:
                logger.error("download_media returned None")
            return data
        except Exception as e:
            logger.error(f"Download failed with exception: {e}")
            return None
    
    def _transcribe_audio(self, audio_data: bytes, mime_type: str) -> Optional[str]:
        """
        Transcribe audio using OpenAI Whisper API via direct HTTP.
        
        Uses requests library directly to avoid OpenAI client version issues.
        """
        if not self.openai_api_key:
            logger.error("OpenAI API key not configured")
            return None
        
        try:
            import requests
            
            logger.info(f"Starting Whisper transcription, audio size: {len(audio_data)} bytes, mime: {mime_type}")
            
            # Determine file extension from mime type
            extension = self._get_extension(mime_type)
            logger.info(f"Using extension: {extension}")
            
            # Write to temp file
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            logger.info(f"Temp file created: {tmp_path}")
            
            try:
                # Call Whisper API directly via HTTP
                with open(tmp_path, 'rb') as audio_file:
                    response = requests.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers={
                            "Authorization": f"Bearer {self.openai_api_key}"
                        },
                        files={
                            "file": (f"audio{extension}", audio_file, mime_type)
                        },
                        data={
                            "model": "whisper-1"
                        },
                        timeout=60
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get('text', '')
                    logger.info(f"Whisper response received: {text[:50]}...")
                    return text
                else:
                    logger.error(f"Whisper API error {response.status_code}: {response.text}")
                    return None
                
            finally:
                # Clean up temp file
                os.unlink(tmp_path)
                
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _save_transcription(
        self,
        phone: str,
        profile_name: str,
        audio_id: str,
        message_id: str,
        text: str,
        timestamp: str,
        mime_type: str
    ) -> str:
        """
        Save transcription to Firebase.
        
        Returns:
            Transcription document ID
        """
        # Create document ID: phone_timestamp
        now = datetime.now()
        doc_id = f"{phone}_{now.strftime('%Y%m%d_%H%M%S')}"
        
        data = {
            'phone': phone,
            'profile_name': profile_name,
            'audio_id': audio_id,
            'message_id': message_id,
            'text': text,
            'original_timestamp': timestamp,
            'transcribed_at': now.isoformat(),
            'mime_type': mime_type,
            'word_count': len(text.split()) if text else 0
        }
        
        try:
            self.firebase.set_document(
                collection='transcriptions',
                doc_id=doc_id,
                data=data,
                merge=False
            )
            logger.info(f"Saved transcription: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")
            return None
    
    def _get_extension(self, mime_type: str) -> str:
        """Get file extension from MIME type."""
        mime_map = {
            'audio/ogg': '.ogg',
            'audio/ogg; codecs=opus': '.ogg',
            'audio/mpeg': '.mp3',
            'audio/mp4': '.m4a',
            'audio/wav': '.wav',
            'audio/webm': '.webm',
        }
        return mime_map.get(mime_type, '.ogg')
