"""
СИСТЕМА КОЛЛИЗИЙ
Проверка столкновений и пространственный хеш для оптимизации
"""

import math
from src.utils import SpatialHash, circles_collide, distance_squared


class CollisionSystem:
    """Система обработки коллизий"""
    
    def __init__(self, cell_size=100):
        self.spatial_hash = SpatialHash(cell_size)
        self.static_objects = []  # Препятствия (деревья, камни, вода)
        self.dynamic_objects = []  # Враги, снаряды
    
    def clear(self):
        """Очистка всех объектов"""
        self.spatial_hash.clear()
        self.static_objects.clear()
        self.dynamic_objects.clear()
    
    def add_static(self, obj):
        """Добавление статического препятствия"""
        self.static_objects.append(obj)
        self.spatial_hash.insert(
            obj,
            obj.x - obj.collision_radius,
            obj.y - obj.collision_radius,
            obj.collision_radius * 2,
            obj.collision_radius * 2
        )
    
    def add_dynamic(self, obj):
        """Добавление динамического объекта"""
        self.dynamic_objects.append(obj)
    
    def remove_dynamic(self, obj):
        """Удаление динамического объекта"""
        if obj in self.dynamic_objects:
            self.dynamic_objects.remove(obj)
    
    def update(self):
        """Обновление пространственного хеша для динамических объектов"""
        # Пересоздаём хеш (быстрее, чем обновлять отдельные объекты)
        self.spatial_hash.clear()
        
        # Добавляем статические объекты
        for obj in self.static_objects:
            self.spatial_hash.insert(
                obj,
                obj.x - obj.collision_radius,
                obj.y - obj.collision_radius,
                obj.collision_radius * 2,
                obj.collision_radius * 2
            )
        
        # Добавляем динамические объекты
        for obj in self.dynamic_objects:
            if hasattr(obj, 'collision_radius'):
                self.spatial_hash.insert(
                    obj,
                    obj.x - obj.collision_radius,
                    obj.y - obj.collision_radius,
                    obj.collision_radius * 2,
                    obj.collision_radius * 2
                )
    
    def get_nearby(self, x, y, radius):
        """Получение объектов рядом с точкой"""
        return self.spatial_hash.query(
            x - radius,
            y - radius,
            radius * 2,
            radius * 2
        )
    
    def check_circle_collision(self, x1, y1, r1, x2, y2, r2):
        """Проверка столкновения двух кругов"""
        return circles_collide(x1, y1, r1, x2, y2, r2)
    
    def check_point_in_circle(self, px, py, cx, cy, radius):
        """Проверка точки внутри круга"""
        return distance_squared(px, py, cx, cy) <= radius * radius
    
    def get_collisions_with_player(self, player):
        """Получение всех объектов, столкнувшихся с игроком"""
        collisions = []
        
        nearby = self.get_nearby(
            player.x, player.y,
            player.collision_radius + 100  # С запасом
        )
        
        for obj in nearby:
            if obj == player:
                continue
            
            if hasattr(obj, 'collision_radius'):
                if self.check_circle_collision(
                    player.x, player.y, player.collision_radius,
                    obj.x, obj.y, obj.collision_radius
                ):
                    collisions.append(obj)
        
        return collisions
    
    def check_player_obstacle_collision(self, player, new_x, new_y):
        """
        Проверка столкновения игрока с препятствиями при движении
        Возвращает скорректированные координаты
        """
        # Проверяем только статические объекты рядом
        nearby = self.get_nearby(new_x, new_y, player.collision_radius + 50)
        
        for obj in nearby:
            if not hasattr(obj, 'is_solid') or not obj.is_solid:
                continue
            
            if self.check_circle_collision(
                new_x, new_y, player.collision_radius,
                obj.x, obj.y, obj.collision_radius
            ):
                # Вычисляем выталкивание
                dx = new_x - obj.x
                dy = new_y - obj.y
                dist = math.sqrt(dx * dx + dy * dy)
                
                if dist > 0:
                    # Нормализуем и выталкиваем
                    overlap = player.collision_radius + obj.collision_radius - dist
                    new_x += (dx / dist) * overlap
                    new_y += (dy / dist) * overlap
        
        return new_x, new_y
    
    def raycast(self, start_x, start_y, end_x, end_y, ignore=None):
        """
        Трассировка луча от start до end
        Возвращает первый объект на пути или None
        """
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.sqrt(dx * dx + dy * dy)
        
        if length == 0:
            return None
        
        # Нормализуем
        dx /= length
        dy /= length
        
        # Шаг проверки
        step = 10
        
        for dist in range(0, int(length), step):
            check_x = start_x + dx * dist
            check_y = start_y + dy * dist
            
            nearby = self.get_nearby(check_x, check_y, step)
            
            for obj in nearby:
                if obj == ignore:
                    continue
                
                if hasattr(obj, 'collision_radius'):
                    if self.check_point_in_circle(
                        check_x, check_y,
                        obj.x, obj.y, obj.collision_radius
                    ):
                        return obj
        
        return None


class Obstacle:
    """Препятствие на карте"""
    
    def __init__(self, x, y, radius, obstacle_type='rock'):
        self.x = x
        self.y = y
        self.collision_radius = radius
        self.obstacle_type = obstacle_type
        self.is_solid = True
        
        # Цвета для разных типов
        self.colors = {
            'rock': (0.5, 0.5, 0.5, 1),
            'tree': (0.2, 0.5, 0.2, 1),
            'water': (0.2, 0.4, 0.8, 1),
            'lava': (1.0, 0.3, 0.0, 1),
            'ice': (0.7, 0.85, 1.0, 1),
        }
        
        self.color = self.colors.get(obstacle_type, (0.5, 0.5, 0.5, 1))
    
    def get_color(self):
        return self.color