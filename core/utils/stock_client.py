"""Stock Client — загрузка видео, музыки и эффектов из API стоков"""
import hashlib
import json
from pathlib import Path
from typing import List, Optional
import requests

from core.utils.config_loader import ProjectConfig
from core.utils.secrets_manager import get_secret
from core.utils.logging_utils import log_success, log_error


class StockClient:
    """Клиент для работы с API стоков (Pixabay, Pexels, Unsplash)"""
    
    CACHE_DIR = Path(".cache/stocks")
    CACHE_TTL_DAYS = 7
    
    def __init__(self, config: ProjectConfig):
        self.config = config
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_video_background(
        self,
        video_type: str,
        keywords: List[str],
        duration_sec: int = 60
    ) -> List[str]:
        """
        Ищет подходящие видео-фоны по ключевым словам.
        
        На входе:
          - video_type: "shorts" | "long_form"
          - keywords: ["tarot", "stars", "mystical"]
          - duration_sec: минимальная длительность
        
        На выходе: список локальных путей к видеофайлам (или URL)
        
        Источники (по приоритету из config):
          1) Pixabay Videos (free, ~500 req/hour)
          2) Pexels Videos
          3) Unsplash
        """
        try:
            # Проверяем кэш
            cache_results = self._check_cache(video_type, keywords)
            if cache_results:
                log_success(f"Stock videos (cached): {len(cache_results)} found")
                return cache_results
            
            # Определяем предпочитаемый источник
            preferred = self.config.video.get(video_type, {}).get('preferred_source', 'pixabay_video')
            
            results = []
            
            try:
                if preferred == 'pixabay_video':
                    results = self._query_pixabay(keywords, duration_sec)
                elif preferred == 'pexels':
                    results = self._query_pexels(keywords, duration_sec)
                elif preferred == 'unsplash':
                    results = self._query_unsplash(keywords)
            
            except Exception as e:
                log_error(f"Failed to fetch from {preferred}", e)
                # Пробуем fallback
                if preferred != 'pixabay_video':
                    results = self._query_pixabay(keywords, duration_sec)
            
            # Кэшируем результаты
            if results:
                self._cache_results(video_type, keywords, results)
            
            log_success(f"Stock videos: {len(results)} found from {preferred}")
            return results
        
        except Exception as e:
            log_error(f"get_video_background failed", e)
            return []
    
    def get_music(
        self,
        style: str = "mysterious_ambient",
        duration_sec: int = 60
    ) -> Optional[str]:
        """
        Загружает фоновую музыку.
        
        На входе:
          - style: "mysterious_ambient", "epic", "calm" и т.д.
          - duration_sec: желаемая длительность
        
        На выходе: путь к .mp3 файлу
        
        Источники:
          1) Pixabay Music (free)
          2) Bensound (CC Attribution)
          3) Epidemic Sound (если есть подписка)
        """
        try:
            # Проверяем кэш
            cache_path = self._get_cache_path(f"music_{style}")
            if cache_path.exists():
                cached = json.loads(cache_path.read_text())
                log_success(f"Music (cached): {style}")
                return cached.get('path')
            
            # Ищем в Pixabay Music
            music_path = self._query_pixabay_music(style, duration_sec)
            
            if music_path:
                # Кэшируем
                cache_path.write_text(json.dumps({'path': music_path}))
                log_success(f"Music downloaded: {style}")
                return music_path
            
            return None
        
        except Exception as e:
            log_error(f"get_music failed", e)
            return None
    
    def get_sound_effect(self, effect_name: str) -> Optional[str]:
        """
        Загружает звуковой эффект по названию.
        
        Примеры:
          - "mystical_transition"
          - "zodiac_sign_appear"
          - "coin_sound"
        
        На выходе: путь к .wav файлу
        
        Источники:
          1) Pixabay SFX
          2) Freesound.org (CC Licensed)
        """
        try:
            # Проверяем кэш
            cache_path = self._get_cache_path(f"sfx_{effect_name}")
            if cache_path.exists():
                cached = json.loads(cache_path.read_text())
                return cached.get('path')
            
            # Ищем эффект
            effect_path = self._query_pixabay_sfx(effect_name)
            
            if effect_path:
                cache_path.write_text(json.dumps({'path': effect_path}))
                log_success(f"Sound effect downloaded: {effect_name}")
                return effect_path
            
            return None
        
        except Exception as e:
            log_error(f"get_sound_effect failed", e)
            return None
    
    # Private methods
    
    def _query_pixabay(self, keywords: List[str], duration_sec: int) -> List[str]:
        """Запрос к Pixabay Videos API"""
        try:
            api_key = get_secret('PIXABAY_API_KEY')
            query = ' '.join(keywords)
            
            url = "https://pixabay.com/api/videos/"
            params = {
                'key': api_key,
                'q': query,
                'min_duration': max(1, duration_sec - 10),
                'min_width': 1920,
                'per_page': 3
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for video in data.get('hits', []):
                # Берем высокое разрешение
                if 'videos' in video:
                    video_url = video['videos'].get('large', {}).get('url')
                    if video_url:
                        results.append(video_url)
            
            return results
        
        except Exception as e:
            log_error(f"Pixabay query failed", e)
            return []
    
    def _query_pexels(self, keywords: List[str], duration_sec: int) -> List[str]:
        """Запрос к Pexels Videos API"""
        try:
            api_key = get_secret('PEXELS_API_KEY')
            query = ' '.join(keywords)
            
            url = "https://api.pexels.com/videos/search"
            headers = {'Authorization': api_key}
            params = {'query': query, 'per_page': 3}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for video in data.get('videos', []):
                if 'video_files' in video:
                    # Берем с наибольшей шириной
                    video_files = sorted(
                        video['video_files'],
                        key=lambda x: x.get('width', 0),
                        reverse=True
                    )
                    if video_files:
                        results.append(video_files[0]['link'])
            
            return results
        
        except Exception as e:
            log_error(f"Pexels query failed", e)
            return []
    
    def _query_unsplash(self, keywords: List[str]) -> List[str]:
        """Запрос к Unsplash API (для картинок)"""
        try:
            api_key = get_secret('UNSPLASH_API_KEY')
            query = ' '.join(keywords)
            
            url = "https://api.unsplash.com/search/photos"
            params = {
                'query': query,
                'client_id': api_key,
                'per_page': 3
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for photo in data.get('results', []):
                if 'urls' in photo:
                    results.append(photo['urls']['regular'])
            
            return results
        
        except Exception as e:
            log_error(f"Unsplash query failed", e)
            return []
    
    def _query_pixabay_music(self, style: str, duration_sec: int) -> Optional[str]:
        """Поиск музыки в Pixabay Music"""
        try:
            api_key = get_secret('PIXABAY_API_KEY')
            
            url = "https://pixabay.com/api/music/"
            params = {
                'key': api_key,
                'q': style,
                'min_duration': max(1, duration_sec - 10),
                'per_page': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('hits'):
                return data['hits'][0].get('url')
        
        except Exception as e:
            log_error(f"Pixabay Music query failed", e)
        
        return None
    
    def _query_pixabay_sfx(self, effect_name: str) -> Optional[str]:
        """Поиск звуковых эффектов в Pixabay"""
        try:
            api_key = get_secret('PIXABAY_API_KEY')
            
            url = "https://pixabay.com/api/"
            params = {
                'key': api_key,
                'q': effect_name,
                'type': 'all',
                'per_page': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Пока возвращаем None (реализация зависит от API)
        
        except Exception as e:
            log_error(f"Pixabay SFX query failed", e)
        
        return None
    
    def _get_cache_path(self, key: str) -> Path:
        """Генерирует путь для кэша"""
        cache_key = hashlib.md5(key.encode()).hexdigest()
        return self.CACHE_DIR / f"{cache_key}.json"
    
    def _check_cache(self, video_type: str, keywords: List[str]) -> Optional[List[str]]:
        """Проверяет кэш (если существует и свежий)"""
        cache_key = f"{video_type}_{','.join(sorted(keywords))}"
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            try:
                data = json.loads(cache_path.read_text())
                # TODO: проверить TTL
                return data.get('results', [])
            except:
                pass
        
        return None
    
    def _cache_results(self, video_type: str, keywords: List[str], results: List[str]) -> None:
        """Сохраняет результаты в кэш"""
        cache_key = f"{video_type}_{','.join(sorted(keywords))}"
        cache_path = self._get_cache_path(cache_key)
        
        data = {
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        cache_path.write_text(json.dumps(data))


from datetime import datetime
