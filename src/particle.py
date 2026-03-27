"""
СИСТЕМА ЧАСТИЦ
Визуальные эффекты: взрывы, поглощение, следы
"""

import random
import math
from kivy.graphics import Color, Ellipse, Rectangle
from src.config import MAX_PARTICLES, PARTICLE_LIFETIME


class Particle:
    """Одна частица"""
    
    def __init__(self, x, y, vx, vy, color, size, lifetime, gravity=0, fade=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = list(color)  # [r, g, b, a]
        self.size = size
        self.initial_size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.fade = fade
        self.alive = True
    
    def update(self, dt):
        """Обновление частицы"""
        if not self.alive:
            return
        
        # Движение
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Гравитация
        self.vy -= self.gravity * dt
        
        # Время жизни
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            self.alive = False
            return
        
        # Затухание
        if self.fade:
            progress = self.lifetime / self.max_lifetime
            self.color[3] = progress
            self.size = self.initial_size * progress


class ParticleSystem:
    """Система управления частицами"""
    
    def __init__(self):
        self.particles = []
    
    def update(self, dt):
        """Обновление всех частиц"""
        # Обновляем и удаляем мёртвые
        self.particles = [p for p in self.particles if p.alive]
        
        for particle in self.particles:
            particle.update(dt)
    
    def draw(self, canvas, camera):
        """Отрисовка частиц"""
        for p in self.particles:
            if not p.alive:
                continue
            
            # Преобразуем координаты
            screen_x, screen_y = camera.world_to_screen(p.x, p.y)
            
            # Проверяем видимость
            if not (-p.size <= screen_x <= camera.width + p.size and
                    -p.size <= screen_y <= camera.height + p.size):
                continue
            
            with canvas:
                Color(*p.color)
                Ellipse(
                    pos=(screen_x - p.size / 2, screen_y - p.size / 2),
                    size=(p.size, p.size)
                )
    
    def emit(self, x, y, count, color, size_range=(3, 8), speed_range=(50, 150),
             lifetime_range=(0.5, 1.5), spread=360, direction=0, gravity=0):
        """
        Испускание частиц
        
        x, y: позиция источника
        count: количество частиц
        color: базовый цвет (r, g, b, a)
        size_range: диапазон размеров
        speed_range: диапазон скоростей
        lifetime_range: диапазон времени жизни
        spread: угол разброса в градусах
        direction: направление в градусах (0 = вправо)
        gravity: гравитация (положительная = вниз)
        """
        # Ограничиваем максимум частиц
        available = MAX_PARTICLES - len(self.particles)
        count = min(count, available)
        
        for _ in range(count):
            # Случайные параметры
            size = random.uniform(*size_range)
            speed = random.uniform(*speed_range)
            lifetime = random.uniform(*lifetime_range)
            
            # Направление с разбросом
            angle_deg = direction + random.uniform(-spread / 2, spread / 2)
            angle_rad = math.radians(angle_deg)
            
            vx = math.cos(angle_rad) * speed
            vy = math.sin(angle_rad) * speed
            
            # Небольшая вариация цвета
            particle_color = [
                min(1, max(0, color[0] + random.uniform(-0.1, 0.1))),
                min(1, max(0, color[1] + random.uniform(-0.1, 0.1))),
                min(1, max(0, color[2] + random.uniform(-0.1, 0.1))),
                color[3] if len(color) > 3 else 1.0
            ]
            
            particle = Particle(
                x, y, vx, vy,
                particle_color, size, lifetime,
                gravity=gravity
            )
            
            self.particles.append(particle)
    
    def emit_explosion(self, x, y, color, count=20):
        """Эффект взрыва"""
        self.emit(
            x, y, count, color,
            size_range=(4, 12),
            speed_range=(100, 250),
            lifetime_range=(0.3, 0.8),
            spread=360,
            gravity=100
        )
    
    def emit_absorption(self, source_x, source_y, target_x, target_y, color, count=15):
        """Эффект поглощения (частицы летят к цели)"""
        dx = target_x - source_x
        dy = target_y - source_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return
        
        # Нормализуем направление
        dx /= distance
        dy /= distance
        
        for _ in range(count):
            # Начальная позиция вокруг источника
            offset_angle = random.uniform(0, 2 * math.pi)
            offset_dist = random.uniform(0, 20)
            px = source_x + math.cos(offset_angle) * offset_dist
            py = source_y + math.sin(offset_angle) * offset_dist
            
            # Скорость к цели
            speed = random.uniform(200, 400)
            vx = dx * speed
            vy = dy * speed
            
            particle_color = list(color) if len(color) >= 4 else list(color) + [1.0]
            
            particle = Particle(
                px, py, vx, vy,
                particle_color,
                size=random.uniform(5, 10),
                lifetime=distance / speed + 0.1
            )
            
            self.particles.append(particle)
    
    def emit_trail(self, x, y, color, direction=0):
        """Эффект следа за движущимся объектом"""
        self.emit(
            x, y, 3, color,
            size_range=(3, 6),
            speed_range=(20, 50),
            lifetime_range=(0.2, 0.4),
            spread=60,
            direction=direction + 180  # Противоположно движению
        )
    
    def emit_hit(self, x, y, color):
        """Эффект попадания"""
        self.emit(
            x, y, 10, color,
            size_range=(3, 8),
            speed_range=(80, 150),
            lifetime_range=(0.2, 0.5),
            spread=360
        )
    
    def emit_heal(self, x, y):
        """Эффект лечения"""
        self.emit(
            x, y, 8, (0.3, 1.0, 0.3, 1.0),
            size_range=(4, 8),
            speed_range=(30, 80),
            lifetime_range=(0.5, 1.0),
            spread=360,
            direction=90,  # Вверх
            gravity=-50    # Частицы поднимаются
        )
    
    def clear(self):
        """Удаление всех частиц"""
        self.particles.clear()