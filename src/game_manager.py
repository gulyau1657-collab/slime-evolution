"""
МЕНЕДЖЕР ИГРЫ
Управление состоянием, снарядами, респавном
"""

import math
from src.config import ABILITIES, WORLD_WIDTH, WORLD_HEIGHT
from src.world import World
from src.player import Player
from src.enemy import EnemySpawner
from src.collision import CollisionSystem
from src.particle import ParticleSystem
from src.camera import Camera
from src.save_system import SaveSystem
from src.utils import format_time


class GameManager:
    """Центральный менеджер игры"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Основные системы
        self.world = None
        self.player = None
        self.enemy_spawner = None
        self.collision_system = None
        self.particle_system = None
        self.camera = None
        self.save_system = SaveSystem()
        
        # Снаряды
        self.projectiles = []
        
        # Состояние игры
        self.is_running = False
        self.is_paused = False
        self.game_over = False
        self.victory = False
        
        # Callbacks для UI
        self.on_notification = None
        self.on_game_over = None
        self.on_victory = None
        
        # Ближайшее тело для поглощения
        self.nearest_body = None
    
    def new_game(self):
        """Начало новой игры"""
        # Создаём мир
        self.world = World()
        
        # Создаём игрока
        spawn_x, spawn_y = self.world.get_spawn_point()
        self.player = Player(spawn_x, spawn_y)
        
        # Система врагов
        self.enemy_spawner = EnemySpawner()
        self.enemy_spawner.spawn_initial_enemies(self.world)
        
        # Коллизии
        self.collision_system = CollisionSystem()
        for obstacle in self.world.obstacles:
            self.collision_system.add_static(obstacle)
        
        # Частицы
        self.particle_system = ParticleSystem()
        
        # Камера
        self.camera = Camera(self.screen_width, self.screen_height)
        self.camera.follow(self.player.x, self.player.y, instant=True)
        
        # Снаряды
        self.projectiles.clear()
        
        # Состояние
        self.is_running = True
        self.is_paused = False
        self.game_over = False
        self.victory = False
    
    def load_game(self):
        """Загрузка сохранённой игры"""
        save_data = self.save_system.load()
        
        if not save_data:
            # Нет сохранения - начинаем новую игру
            self.new_game()
            return
        
        # Создаём мир
        self.world = World()
        
        # Создаём игрока
        spawn_x, spawn_y = self.world.get_spawn_point()
        self.player = Player(spawn_x, spawn_y)
        self.player.load_save_data(save_data.get('player', {}))
        
        # Система врагов
        self.enemy_spawner = EnemySpawner()
        enemy_data = save_data.get('enemies', {})
        
        if enemy_data.get('enemies'):
            self.enemy_spawner.load_save_data(enemy_data)
        else:
            self.enemy_spawner.spawn_initial_enemies(self.world)
        
        # Коллизии
        self.collision_system = CollisionSystem()
        for obstacle in self.world.obstacles:
            self.collision_system.add_static(obstacle)
        
        # Частицы
        self.particle_system = ParticleSystem()
        
        # Камера
        self.camera = Camera(self.screen_width, self.screen_height)
        self.camera.follow(self.player.x, self.player.y, instant=True)
        
        # Снаряды
        self.projectiles.clear()
        
        # Состояние
        self.is_running = True
        self.is_paused = False
        self.game_over = False
        self.victory = False
        
        self.show_notification("Игра загружена!")
    
    def save_game(self):
        """Сохранение игры"""
        if not self.player:
            return
        
        save_data = {
            'player': self.player.get_save_data(),
            'enemies': self.enemy_spawner.get_save_data(),
        }
        
        self.save_system.save(save_data)
    
    def update(self, dt):
        """Обновление игрового состояния"""
        if not self.is_running or self.is_paused:
            return
        
        if self.game_over or self.victory:
            return
        
        # Обновляем камеру
        self.camera.follow(self.player.x, self.player.y)
        
        # Обновляем врагов
        self.enemy_spawner.update(dt, self.player, self, self.world)
        
        # Обновляем снаряды
        self._update_projectiles(dt)
        
        # Обновляем частицы
        self.particle_system.update(dt)
        
        # Обновляем коллизии
        self.collision_system.update()
        
        # Проверяем ближайшее тело для поглощения
        self.nearest_body = self.enemy_spawner.get_nearest_body(
            self.player.x, self.player.y, 80
        )
        
        # Проверяем победу/поражение
        self._check_game_state()
    
    def _update_projectiles(self, dt):
        """Обновление снарядов"""
        alive_projectiles = []
        
        for projectile in self.projectiles:
            projectile.update(dt)
            
            if not projectile.alive:
                continue
            
            # Проверяем столкновения
            hit = False
            
            # Снаряд игрока попадает по врагам
            if projectile.owner == self.player:
                for enemy in self.enemy_spawner.enemies:
                    if not enemy.alive:
                        continue
                    
                    dx = projectile.x - enemy.x
                    dy = projectile.y - enemy.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    
                    if dist < projectile.collision_radius + enemy.collision_radius:
                        projectile.on_hit(enemy, self)
                        hit = True
                        break
            else:
                # Снаряд врага попадает по игроку
                dx = projectile.x - self.player.x
                dy = projectile.y - self.player.y
                dist = math.sqrt(dx * dx + dy * dy)
                
                if dist < projectile.collision_radius + self.player.collision_radius:
                    projectile.on_hit(self.player, self)
                    hit = True
            
            if not hit and projectile.alive:
                alive_projectiles.append(projectile)
        
        self.projectiles = alive_projectiles
    
    def _check_game_state(self):
        """Проверка состояния игры"""
        # Поражение
        if not self.player.is_alive():
            self.game_over = True
            self.is_running = False
            
            if self.on_game_over:
                stats = self._get_final_stats()
                self.on_game_over(stats)
            return
        
        # Победа - проверяем, убит ли босс
        boss_alive = False
        for enemy in self.enemy_spawner.enemies:
            if enemy.is_boss and enemy.alive:
                boss_alive = True
                break
        
        # Также проверяем, был ли босс вообще
        boss_existed = any(
            enemy.is_boss for enemy in self.enemy_spawner.enemies
        ) or any(
            'ruins_keeper' in str(item) for item in self.enemy_spawner.respawn_queue
        )
        
        # Если босс был и его больше нет - победа
        if not boss_alive and self.player.kills > 0:
            # Проверяем, поглотил ли игрок босса
            if 'ruins_keeper' in self.player.absorbed_enemies:
                self.victory = True
                self.is_running = False
                
                if self.on_victory:
                    stats = self._get_final_stats()
                    self.on_victory(stats)
    
    def _get_final_stats(self):
        """Получение финальной статистики"""
        stats = self.player.get_stats()
        stats['time'] = format_time(stats['time'])
        return stats
    
    def add_projectile(self, projectile):
        """Добавление снаряда"""
        self.projectiles.append(projectile)
    
    def get_enemies_in_radius(self, x, y, radius):
        """Получение врагов в радиусе"""
        return self.enemy_spawner.get_enemies_in_radius(x, y, radius)
    
    def get_enemies_in_line(self, x1, y1, x2, y2, width):
        """Получение врагов на линии"""
        result = []
        
        # Упрощённая проверка - делим линию на сегменты
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        
        if length == 0:
            return result
        
        steps = int(length / 20)
        dx /= length
        dy /= length
        
        checked = set()
        
        for i in range(steps + 1):
            check_x = x1 + dx * i * 20
            check_y = y1 + dy * i * 20
            
            for enemy in self.enemy_spawner.enemies:
                if enemy in checked or not enemy.alive:
                    continue
                
                ex = enemy.x - check_x
                ey = enemy.y - check_y
                
                if ex * ex + ey * ey < (width + enemy.collision_radius) ** 2:
                    result.append(enemy)
                    checked.add(enemy)
        
        return result
    
    def show_notification(self, text, duration=3.0, color=None):
        """Показ уведомления"""
        if self.on_notification:
            self.on_notification(text, duration, color)
    
    def get_ability_name(self, ability_id):
        """Получение названия способности"""
        return ABILITIES.get(ability_id, {}).get('name', ability_id)
    
    def update_screen_size(self, width, height):
        """Обновление размера экрана"""
        self.screen_width = width
        self.screen_height = height
        
        if self.camera:
            self.camera.update_size(width, height)
    
    def pause(self):
        """Пауза игры"""
        self.is_paused = True
    
    def resume(self):
        """Продолжение игры"""
        self.is_paused = False
    
    def try_absorb(self):
        """Попытка поглотить ближайшее тело"""
        if self.nearest_body and not self.nearest_body.absorbed:
            self.nearest_body.absorbed = True
            self.player.absorb(self.nearest_body, self)
            return True
        return False