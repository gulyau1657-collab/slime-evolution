"""
КАМЕРА
Следит за игроком, ограничивает область видимости миром
"""

from src.config import WORLD_WIDTH, WORLD_HEIGHT


class Camera:
    """Камера, следящая за игроком"""
    
    def __init__(self, width, height):
        """
        Инициализация камеры
        width, height: размеры экрана/окна
        """
        self.width = width
        self.height = height
        self.x = 0  # Позиция камеры в мировых координатах
        self.y = 0
        
        # Границы мира
        self.world_width = WORLD_WIDTH
        self.world_height = WORLD_HEIGHT
        
        # Плавное следование
        self.smoothing = 0.1  # Чем меньше, тем плавнее
        
        # Целевая позиция
        self.target_x = 0
        self.target_y = 0
    
    def update_size(self, width, height):
        """Обновление размеров экрана"""
        self.width = width
        self.height = height
    
    def follow(self, target_x, target_y, instant=False):
        """
        Следование за целью
        target_x, target_y: позиция цели в мировых координатах
        instant: если True, телепортируемся мгновенно
        """
        # Центрируем камеру на цели
        self.target_x = target_x - self.width / 2
        self.target_y = target_y - self.height / 2
        
        if instant:
            self.x = self.target_x
            self.y = self.target_y
        else:
            # Плавное движение к цели
            self.x += (self.target_x - self.x) * self.smoothing
            self.y += (self.target_y - self.y) * self.smoothing
        
        # Ограничиваем камеру границами мира
        self.clamp_to_world()
    
    def clamp_to_world(self):
        """Ограничение камеры границами мира"""
        # Левый край
        if self.x < 0:
            self.x = 0
        # Правый край
        if self.x + self.width > self.world_width:
            self.x = self.world_width - self.width
        # Нижний край
        if self.y < 0:
            self.y = 0
        # Верхний край
        if self.y + self.height > self.world_height:
            self.y = self.world_height - self.height
        
        # Если мир меньше экрана, центрируем
        if self.world_width < self.width:
            self.x = (self.world_width - self.width) / 2
        if self.world_height < self.height:
            self.y = (self.world_height - self.height) / 2
    
    def world_to_screen(self, world_x, world_y):
        """Преобразование мировых координат в экранные"""
        return world_x - self.x, world_y - self.y
    
    def screen_to_world(self, screen_x, screen_y):
        """Преобразование экранных координат в мировые"""
        return screen_x + self.x, screen_y + self.y
    
    def is_visible(self, x, y, width, height, margin=50):
        """
        Проверка, виден ли объект на экране
        margin: дополнительный отступ для предзагрузки
        """
        return (x + width > self.x - margin and
                x < self.x + self.width + margin and
                y + height > self.y - margin and
                y < self.y + self.height + margin)
    
    def get_visible_rect(self, margin=0):
        """Получить прямоугольник видимой области"""
        return (self.x - margin, 
                self.y - margin,
                self.width + margin * 2, 
                self.height + margin * 2)
    
    def shake(self, intensity=5, duration=0.3):
        """
        Тряска камеры (для эффекта урона)
        TODO: реализовать эффект тряски
        """
        pass