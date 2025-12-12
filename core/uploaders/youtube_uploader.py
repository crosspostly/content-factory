"""YouTube Uploader — загрузка видео на YouTube"""
from typing import Dict, Any, Optional
from core.utils.config_loader import ProjectConfig
from core.utils.secrets_manager import get_secret
from core.utils.logging_utils import log_success, log_error


def upload(
    config: ProjectConfig,
    video_path: str,
    script: Dict[str, Any],
    video_type: str
) -> str:
    """
    Загружает видео на YouTube.
    
    На входе:
      - video_path: путь к готовому MP4
      - script: JSON-сценарий (содержит title, description)
      - video_type: "shorts" | "long_form" | "ad"
    
    На выходе: video_id на YouTube
    
    Метаданные:
    - Title: из script['video_title']
    - Description: из script['video_description']
    - Tags: из config.upload.tags
    - Плейлист: из config.upload.playlist_ids[video_type]
    - Chapters: из script['chapters'] (если long-form)
    - Видимость: 'unlisted'
    """
    log_success(f"Starting YouTube upload for {video_type}")
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        # TODO: реализовать аутентификацию
        api_key = get_secret('YOUTUBE_API_KEY')
        
        # Для тестирования возвращаем mock video_id
        video_id = f"test_{uuid.uuid4().hex[:8]}"
        log_success(f"YouTube upload mock: {video_id}")
        
        return video_id
    
    except Exception as e:
        log_error(f"YouTube upload failed", e)
        raise


import uuid
