"""
Система снарядов: огненные шары, ледяные стрелы, кости и т.д.
"""

import pygame
import math
from src.utils import distance


class Projectile:
    """Один летящий снаряд."""

    def __init__(self, x, y, dx, dy, speed, damage, max_range, color,
                 owner=None, slow_factor=0, slow_duration=0,
                 dot_damage=0, dot_duration=0, radius=5):
        self.x = x
        self.y = y
        self.dx = dx  # направление (единичный)
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.max_range = max_range
        self.color = color
        self.owner = owner  # 'player' или ссылка на врага
        self.slow_factor = slow_factor
        self.slow_duration = slow_duration
        self.dot_damage = dot_damage
        self.dot_duration = dot_duration
        self.radius = radius
        self.start_x = x
        self.start_y = y
        self.alive = True

    def update(self, dt):
        if not self.alive:
            return
        self.x += self.dx * self.speed * dt * 60
        self.y += self.dy * self.speed * dt * 60
        # Проверить дальность
        if distance(self.start_x, self.start_y, self.x, self.y) > self.max_range:
            self.alive = False

    def draw(self, surface, cam_x, cam_y):
        if not self.alive:
            return
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        pygame.draw.circle(surface, self.color, (sx, sy), self.radius)
        # Светлый центр
        inner = tuple(min(c + 80, 255) for c in self.color[:3])
        pygame.draw.circle(surface, inner, (sx, sy), max(1, self.radius // 2))


class ProjectileManager:
    """Управляет всеми снарядами в игре."""

    def __init__(self):
        self.projectiles = []

    def add(self, proj):
        self.projectiles.append(proj)

    def update(self, dt):
        for p in self.projectiles:
            p.update(dt)
        self.projectiles = [p for p in self.projectiles if p.alive]

    def draw(self, surface, cam_x, cam_y):
        for p in self.projectiles:
            p.draw(surface, cam_x, cam_y)