# -*- coding: utf-8 -*-
import os

# Получаем настройки из переменных окружения (GitHub Secrets)
# Если переменной нет, используем пустую строку или дефолтное значение

RUTUBE_LOGIN = os.environ.get("RUTUBE_LOGIN", "")
RUTUBE_PASSWORD = os.environ.get("RUTUBE_PASSWORD", "")

# Канал
YOUTUBE_CHANNEL_URL = os.environ.get("YOUTUBE_CHANNEL_URL", "https://www.youtube.com/channel/UC8hbIF2zfPI5KwlZ2Zq5RmQ/videos")

# Сервер и пути
PUBLIC_IP = os.environ.get("PUBLIC_IP", "127.0.0.1")
SERVER_PORT = int(os.environ.get("SERVER_PORT", 5005))

# Пути (в контексте GitHub Actions будем запускать из корня или папки)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
DB_FILE = os.path.join(BASE_DIR, "sync_db.sqlite")

# Файлы куки (будут создаваться из Secrets)
YOUTUBE_COOKIES_FILE = os.path.join(BASE_DIR, "youtube_cookies.txt")
RUTUBE_COOKIES_FILE = os.path.join(BASE_DIR, "rutube_cookies.json")

# Путь к yt-dlp (будет установлен через pip или скачан)
YT_DLP_PATH = "yt-dlp" # В PATH
