"""
СИСТЕМА СОХРАНЕНИЙ
Сохранение и загрузка прогресса игры
"""

import json
import os
from kivy.utils import platform

from src.config import SAVE_FOLDER, SAVE_FILE


class SaveSystem:
    """Система сохранения игры"""
    
    def __init__(self):
        self.save_folder = self._get_save_folder()
        self.save_path = os.path.join(self.save_folder, SAVE_FILE)
        
        # Создаём папку, если не существует
        self._ensure_folder_exists()
    
    def _get_save_folder(self):
        """Получение пути к папке сохранений"""
        if platform == 'android':
            # На Android используем внутреннее хранилище приложения
            from android.storage import app_storage_path
            return os.path.join(app_storage_path(), SAVE_FOLDER)
        else:
            # На десктопе - папка рядом с игрой
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base_path, SAVE_FOLDER)
    
    def _ensure_folder_exists(self):
        """Создание папки сохранений"""
        try:
            if not os.path.exists(self.save_folder):
                os.makedirs(self.save_folder)
        except Exception as e:
            print(f"Ошибка создания папки сохранений: {e}")
    
    def save(self, data):
        """
        Сохранение данных игры
        
        data: словарь с данными для сохранения
        """
        try:
            # Преобразуем данные в JSON
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Записываем в файл
            with open(self.save_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            self._log_error(f"Save error: {e}")
            return False
    
    def load(self):
        """
        Загрузка данных игры
        
        Возвращает словарь с данными или None
        """
        try:
            if not os.path.exists(self.save_path):
                return None
            
            with open(self.save_path, 'r', encoding='utf-8') as f:
                json_data = f.read()
            
            data = json.loads(json_data)
            return data
            
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            self._log_error(f"Load error: {e}")
            return None
    
    def has_save(self):
        """Проверка наличия сохранения"""
        return os.path.exists(self.save_path)
    
    def delete_save(self):
        """Удаление сохранения"""
        try:
            if os.path.exists(self.save_path):
                os.remove(self.save_path)
            return True
        except Exception as e:
            print(f"Ошибка удаления сохранения: {e}")
            return False
    
    def _log_error(self, message):
        """Логирование ошибок"""
        try:
            log_path = os.path.join(self.save_folder, 'error.log')
            
            with open(log_path, 'a', encoding='utf-8') as f:
                import datetime
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] {message}\n")
                
        except Exception:
            pass  # Игнорируем ошибки логирования