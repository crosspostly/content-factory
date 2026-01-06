# -*- coding: utf-8 -*-
import requests
import json
import time
import os

class RutubeUploader:
    """
    Класс для работы с API Rutube.
    Позволяет авторизоваться по логину/паролю и загружать видео по прямой ссылке (URL).
    """

    # Базовый URL API Rutube
    BASE_URL = "https://rutube.ru"

    def __init__(self, username, password):
        """
        Инициализация клиента.
        :param username: Email или телефон (логин)
        :param password: Ваш пароль
        """
        self.username = username
        self.password = password
        self.token = None # Здесь будем хранить Токен после авторизации
        self.session = requests.Session() # Используем сессию для оптимизации подключений

    def auth(self):
        """
        Метод авторизации.
        Отправляет POST запрос на /api/accounts/token_auth/ для получения токена.
        Сохраняет токен внутри экземпляра класса.
        """
        print(f"🔄 Попытка авторизации пользователя: {self.username}...")
        
        endpoint = f"{self.BASE_URL}/api/accounts/token_auth/"
        
        payload = {
            "username": self.username,
            "password": self.password
        }

        try:
            response = self.session.post(endpoint, data=payload)
            
            # Проверяем статус ответа (200 OK означает успех)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                print(f"✅ Авторизация успешна! Токен получен: {self.token[:10]}...")
                return True
            else:
                print(f"❌ Ошибка авторизации. Код: {response.status_code}")
                print(f"Ответ сервера: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Сетевая ошибка при авторизации: {e}")
            return False

    def upload_to_catbox(self, file_path):
        """
        Вспомогательный метод: загружает локальный файл на анонимный хостинг
        и возвращает ПРЯМУЮ ссылку на него.
        """
        print(f"📦 Превращаем файл в ссылку через Catbox...")
        url = "https://catbox.moe/user/api.php"
        files = {
            'reqtype': (None, 'fileupload'),
            'fileToUpload': open(file_path, 'rb')
        }
        try:
            response = requests.post(url, files=files)
            if response.status_code == 200:
                direct_url = response.text.strip()
                print(f"✅ Ссылка получена: {direct_url}")
                return direct_url
            else:
                print(f"❌ Ошибка хостинга: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Ошибка при создании ссылки: {e}")
            return None

    def upload_local_file(self, file_path, title, description="", category_id=13, is_hidden=False):
        """
        Главный метод: загружает локальный файл на Rutube через API.
        """
        # 1. Сначала делаем из файла ссылку
        video_url = self.upload_to_catbox(file_path)
        if not video_url:
            return None
        
        # 2. Передаем ссылку в API Rutube
        return self.upload_video_by_url(video_url, title, description, category_id, is_hidden)

    def upload_video_by_url(self, video_url, title, description="", category_id=13, is_hidden=False):
        """
        Загрузка видео по прямой ссылке (Remote Upload).
        
        :param video_url: Прямая ссылка на файл (должна быть доступна из интернета, например http://site.com/video.mp4)
        :param title: Название видео (Обязательно)
        :param description: Описание видео
        :param category_id: ID категории (13 = Хобби, 6 = Юмор и т.д.)
        :param is_hidden: Если True, видео будет скрыто (доступ по ссылке)
        :return: Словарь с ответом сервера (содержит video_id) или None при ошибке
        """
        
        # Если токена нет, пробуем авторизоваться
        if not self.token:
            if not self.auth():
                return None

        print(f"📤 Начинаем загрузку видео: '{title}'")
        print(f"🔗 Источник: {video_url}")

        endpoint = f"{self.BASE_URL}/api/video/"
        
        # Заголовки. Важно передать Token в формате "Token <значение>"
        headers = {
            "Authorization": f"Token {self.token}"
        }

        # Тело запроса
        payload = {
            "url": video_url,
            "title": title,
            "description": description,
            "category_id": category_id,
            "is_hidden": is_hidden
        }

        try:
            # Отправляем POST запрос
            response = self.session.post(endpoint, data=payload, headers=headers)

            # Проверяем успешные статусы (200 или 201 Created)
            if response.status_code in [200, 201]:
                data = response.json()
                video_id = data.get('video_id') or data.get('id')
                print(f"✅ Видео успешно добавлено в очередь загрузки!")
                print(f"🆔 ID видео: {video_id}")
                return data
            else:
                print(f"❌ Ошибка загрузки. Код: {response.status_code}")
                print(f"Ответ сервера: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Сетевая ошибка при загрузке: {e}")
            return None

    def get_video_status(self, video_id):
        """
        Получение информации о видео (статус обработки).
        :param video_id: ID видео (полученный при загрузке)
        """
        if not self.token:
            self.auth()

        endpoint = f"{self.BASE_URL}/api/video/{video_id}/"
        headers = {"Authorization": f"Token {self.token}"}

        try:
            response = self.session.get(endpoint, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Не удалось получить статус видео {video_id}")
                return None
        except Exception as e:
            print(f"Ошибка проверки статуса: {e}")
            return None

def schedule_upload_task(file_path, title, description, publish_date):
    """
    Function called by server.py to execute the upload.
    Returns (success: bool, message: str)
    """
    try:
        # Try importing config from the same package
        try:
            from . import config
        except ImportError:
            import config

        uploader = RutubeUploader(config.RUTUBE_LOGIN, config.RUTUBE_PASSWORD)
        
        # Note: publish_date is currently not used by RutubeUploader native upload,
        # but we pass it for future extensibility.
        print(f"Scheduling upload for {publish_date} (Note: Immediate upload initiated)")
        
        result = uploader.upload_local_file(file_path, title, description)
        
        if result and (result.get('video_id') or result.get('id')):
             return True, f"Uploaded successfully. ID: {result.get('video_id') or result.get('id')}"
        else:
             return False, "Upload failed (see logs)"
             
    except Exception as e:
        return False, str(e)

# ==========================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ (Блок запуска)
# ==========================================
if __name__ == "__main__":
    # 1. Настройка данных пользователя
    LOGIN = 'nlpkem@ya.ru'
    PASSWORD = '*V8u2p2r'
    
    # 2. Настройка видео (ЛОКАЛЬНЫЙ ФАЙЛ РЕЦЕПТА)
    LOCAL_FILE = os.path.join(os.path.dirname(__file__), "test_video.mp4")
    TITLE = "Рецепт дня: Идеальный стейк"
    DESC = "Ингредиенты: Говядина, соль, перец, розмарин. Готовим на сильном огне по 3 минуты с каждой стороны."
    
    # 3. Создаем экземпляр загрузчика
    uploader = RutubeUploader(LOGIN, PASSWORD)
    
    # 4. Запускаем загрузку
    result = uploader.upload_local_file(
        file_path=LOCAL_FILE,
        title=TITLE,
        description=DESC,
        category_id=13 # Категория Еда/Хобби
    )
    
    if result:
        print(f"🚀 Всё сработало! Видео ID: {result.get('video_id')}")
