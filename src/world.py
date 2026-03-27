"""
ГЕНЕРАЦИЯ МИРА
Биомы, препятствия, тайлы
"""

import random
import math
from src.config import (
    WORLD_WIDTH, WORLD_HEIGHT, TILE_SIZE,
    BIOME_FIELDS, BIOME_DARK_FOREST, BIOME_FIRE_LANDS,
    BIOME_ICE_WASTES, BIOME_RUINS, BIOME_COLORS
)
from src.collision import Obstacle


class World:
    """Игровой мир"""
    
    def __init__(self):
        self.width = WORLD_WIDTH
        self.height = WORLD_HEIGHT
        self.tile_size = TILE_SIZE
        
        # Сетка тайлов для биомов
        self.tiles_x = self.width // self.tile_size
        self.tiles_y = self.height // self.tile_size
        
        # Карта биомов (2D массив)
        self.biome_map = [[None for _ in range(self.tiles_x)] for _ in range(self.tiles_y)]
        
        # Препятствия
        self.obstacles = []
        
        # Регионы биомов (для спавна)
        self.biome_regions = {
            BIOME_FIELDS: [],
            BIOME_DARK_FOREST: [],
            BIOME_FIRE_LANDS: [],
            BIOME_ICE_WASTES: [],
            BIOME_RUINS: [],
        }
        
        # Точка спавна игрока
        self.spawn_point = (self.width * 0.7, self.height * 0.2)
        
        # Генерируем мир
        self._generate_biomes()
        self._generate_obstacles()
    
    def _generate_biomes(self):
        """Генерация биомов"""
        center_x = self.tiles_x // 2
        center_y = self.tiles_y // 2
        
        # Радиус руин в центре
        ruins_radius = min(self.tiles_x, self.tiles_y) // 8
        
        for y in range(self.tiles_y):
            for x in range(self.tiles_x):
                # Расстояние от центра
                dx = x - center_x
                dy = y - center_y
                dist_from_center = math.sqrt(dx * dx + dy * dy)
                
                # Руины в центре
                if dist_from_center < ruins_radius:
                    biome = BIOME_RUINS
                else:
                    # Определяем биом по секторам
                    angle = math.atan2(dy, dx)
                    
                    # Нормализуем угол к 0-2π
                    if angle < 0:
                        angle += 2 * math.pi
                    
                    # Делим на секторы
                    # 0-π/2 (правый верхний) - Огненные земли
                    # π/2-π (левый верхний) - Ледяные пустоши
                    # π-3π/2 (левый нижний) - Тёмный лес
                    # 3π/2-2π (правый нижний) - Зелёные поля
                    
                    sector = angle / (math.pi / 2)
                    
                    if sector < 1:
                        # Правый верхний - огонь или поля (ближе к низу - поля)
                        if y > center_y + ruins_radius:
                            biome = BIOME_FIRE_LANDS
                        else:
                            biome = BIOME_FIELDS
                    elif sector < 2:
                        # Левый верхний - лёд
                        biome = BIOME_ICE_WASTES
                    elif sector < 3:
                        # Левый нижний - лес
                        biome = BIOME_DARK_FOREST
                    else:
                        # Правый нижний - поля (стартовая зона)
                        biome = BIOME_FIELDS
                    
                    # Добавляем переходные зоны
                    if ruins_radius < dist_from_center < ruins_radius * 1.5:
                        # Переходная зона к руинам
                        if random.random() < 0.3:
                            biome = BIOME_RUINS
                
                self.biome_map[y][x] = biome
                
                # Записываем в регионы
                world_x = x * self.tile_size + self.tile_size // 2
                world_y = y * self.tile_size + self.tile_size // 2
                self.biome_regions[biome].append((world_x, world_y))
    
    def _generate_obstacles(self):
        """Генерация препятствий"""
        # Деревья в лесу
        for point in self.biome_regions[BIOME_DARK_FOREST]:
            if random.random() < 0.15:
                x, y = point
                x += random.uniform(-20, 20)
                y += random.uniform(-20, 20)
                self.obstacles.append(Obstacle(x, y, 20, 'tree'))
        
        # Камни на полях
        for point in self.biome_regions[BIOME_FIELDS]:
            if random.random() < 0.05:
                x, y = point
                x += random.uniform(-20, 20)
                y += random.uniform(-20, 20)
                self.obstacles.append(Obstacle(x, y, 15, 'rock'))
        
        # Лава в огненных землях
        for point in self.biome_regions[BIOME_FIRE_LANDS]:
            if random.random() < 0.08:
                x, y = point
                x += random.uniform(-20, 20)
                y += random.uniform(-20, 20)
                self.obstacles.append(Obstacle(x, y, 25, 'lava'))
        
        # Лёд в ледяных пустошах
        for point in self.biome_regions[BIOME_ICE_WASTES]:
            if random.random() < 0.07:
                x, y = point
                x += random.uniform(-20, 20)
                y += random.uniform(-20, 20)
                self.obstacles.append(Obstacle(x, y, 18, 'ice'))
        
        # Руины - колонны
        for point in self.biome_regions[BIOME_RUINS]:
            if random.random() < 0.1:
                x, y = point
                x += random.uniform(-20, 20)
                y += random.uniform(-20, 20)
                self.obstacles.append(Obstacle(x, y, 22, 'rock'))
    
    def get_biome_at(self, x, y):
        """Получение биома в точке"""
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        
        if 0 <= tile_x < self.tiles_x and 0 <= tile_y < self.tiles_y:
            return self.biome_map[tile_y][tile_x]
        
        return BIOME_FIELDS
    
    def get_biome_color(self, x, y):
        """Получение цвета биома в точке"""
        biome = self.get_biome_at(x, y)
        return BIOME_COLORS.get(biome, (0.3, 0.7, 0.2, 1))
    
    def get_biome_region(self, biome):
        """Получение региона биома"""
        return self.biome_regions.get(biome, [])
    
    def get_random_point_in_biome(self, biome, min_distance_from_player=0, player=None):
        """Получение случайной точки в биоме"""
        points = self.biome_regions.get(biome, [])
        
        if not points:
            return None, None
        
        # Пытаемся найти подходящую точку
        for _ in range(50):
            point = random.choice(points)
            
            # Добавляем случайное смещение
            x = point[0] + random.uniform(-30, 30)
            y = point[1] + random.uniform(-30, 30)
            
            # Проверяем расстояние от игрока
            if player and min_distance_from_player > 0:
                dx = x - player.x
                dy = y - player.y
                if dx * dx + dy * dy < min_distance_from_player * min_distance_from_player:
                    continue
            
            # Проверяем, не на препятствии ли
            valid = True
            for obstacle in self.obstacles:
                dx = x - obstacle.x
                dy = y - obstacle.y
                if dx * dx + dy * dy < (obstacle.collision_radius + 30) ** 2:
                    valid = False
                    break
            
            if valid:
                return x, y
        
        # Если не нашли - возвращаем случайную точку без проверок
        point = random.choice(points)
        return point[0], point[1]
    
    def get_tiles_in_rect(self, x, y, width, height):
        """Получение тайлов в прямоугольнике (для отрисовки)"""
        start_tile_x = max(0, int(x // self.tile_size))
        start_tile_y = max(0, int(y // self.tile_size))
        end_tile_x = min(self.tiles_x, int((x + width) // self.tile_size) + 1)
        end_tile_y = min(self.tiles_y, int((y + height) // self.tile_size) + 1)
        
        tiles = []
        for ty in range(start_tile_y, end_tile_y):
            for tx in range(start_tile_x, end_tile_x):
                biome = self.biome_map[ty][tx]
                color = BIOME_COLORS.get(biome, (0.3, 0.7, 0.2, 1))
                tiles.append({
                    'x': tx * self.tile_size,
                    'y': ty * self.tile_size,
                    'biome': biome,
                    'color': color,
                })
        
        return tiles
    
    def get_obstacles_in_rect(self, x, y, width, height):
        """Получение препятствий в прямоугольнике"""
        result = []
        for obstacle in self.obstacles:
            if (obstacle.x + obstacle.collision_radius > x and
                obstacle.x - obstacle.collision_radius < x + width and
                obstacle.y + obstacle.collision_radius > y and
                obstacle.y - obstacle.collision_radius < y + height):
                result.append(obstacle)
        return result
    
    def get_spawn_point(self):
        """Получение точки спавна игрока"""
        return self.spawn_point