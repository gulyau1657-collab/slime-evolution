"""
ИГРОК (СЛАЙМ)
Управление, атака, поглощение, визуальная эволюция
"""

import math
import random
from src.config import (
    PLAYER_START_HP, PLAYER_START_DAMAGE, PLAYER_START_SPEED,
    PLAYER_SIZE, PLAYER_ATTACK_RANGE, PLAYER_ATTACK_COOLDOWN,
    ABSORPTION_HP_GAIN, ABSORPTION_DAMAGE_GAIN, ABSORPTION_SPEED_GAIN,
    ABSORPTION_SIZE_GAIN, MAX_SPEED_BONUS, MAX_SIZE_BONUS,
    MAX_ABILITIES, WORLD_WIDTH, WORLD_HEIGHT, ENEMY_TYPES
)
from src.ability import AbilityManager
from src.utils import generate_slime_texture, distance, normalize


class Player:
    """Класс игрока - эволюционирующий слайм"""
    
    def __init__(self, x, y):
        # Позиция
        self.x = x
        self.y = y
        
        # Базовые характеристики
        self.max_hp = PLAYER_START_HP
        self.hp = self.max_hp
        self.base_damage = PLAYER_START_DAMAGE
        self.damage = self.base_damage
        self.base_speed = PLAYER_START_SPEED
        self.speed = self.base_speed
        
        # Размер и коллизия
        self.base_size = PLAYER_SIZE
        self.size = self.base_size
        self.collision_radius = self.size / 2
        
        # Множители от поглощения
        self.speed_multiplier = 1.0
        self.size_multiplier = 1.0
        
        # Атака
        self.attack_cooldown = 0
        self.attack_range = PLAYER_ATTACK_RANGE
        self.is_attacking = False
        
        # Способности
        self.ability_manager = AbilityManager(MAX_ABILITIES)
        
        # Поглощение
        self.absorptions_count = 0
        self.absorbed_enemies = []  # Список поглощённых типов врагов
        self.visual_layers = []  # Визуальные слои [(color, opacity), ...]
        
        # Баффы и дебаффы
        self.buffs = {}  # {buff_id: {effect: value, duration: time}}
        self.slow_factor = 1.0
        self.slow_duration = 0
        
        # Неуязвимость после получения урона
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 0.5
        
        # Статистика
        self.kills = 0
        self.play_time = 0
        
        # Текстура
        self.texture = None
        self.update_texture()
        
        # Направление взгляда (для атаки)
        self.facing_x = 1
        self.facing_y = 0
    
    def update_texture(self):
        """Обновление текстуры слайма с учётом поглощений"""
        base_color = (0.2, 0.9, 0.3, 1.0)  # Зелёный слайм
        
        # Создаём текстуру с слоями
        self.texture = generate_slime_texture(
            int(self.size),
            base_color,
            self.visual_layers
        )
    
    def update(self, dt, move_x, move_y, game_manager):
        """Обновление игрока"""
        self.play_time += dt
        
        # Обновляем способности
        self.ability_manager.update(dt)
        
        # Обновляем баффы
        self._update_buffs(dt)
        
        # Обновляем замедление
        if self.slow_duration > 0:
            self.slow_duration -= dt
            if self.slow_duration <= 0:
                self.slow_factor = 1.0
        
        # Неуязвимость
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        # Атака кулдаун
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Движение
        if move_x != 0 or move_y != 0:
            # Нормализуем направление
            norm_x, norm_y = normalize(move_x, move_y)
            
            # Запоминаем направление взгляда
            self.facing_x = norm_x
            self.facing_y = norm_y
            
            # Вычисляем новую позицию
            actual_speed = self.speed * self.speed_multiplier * self.slow_factor
            new_x = self.x + norm_x * actual_speed * dt
            new_y = self.y + norm_y * actual_speed * dt
            
            # Проверяем коллизии с препятствиями
            new_x, new_y = game_manager.collision_system.check_player_obstacle_collision(
                self, new_x, new_y
            )
            
            # Ограничиваем границами мира
            new_x = max(self.collision_radius, min(WORLD_WIDTH - self.collision_radius, new_x))
            new_y = max(self.collision_radius, min(WORLD_HEIGHT - self.collision_radius, new_y))
            
            self.x = new_x
            self.y = new_y
        
        # Пассивная регенерация
        hp_regen = self.ability_manager.get_passive_effect('hp_regen', 0)
        if hp_regen > 0:
            self.heal(hp_regen * dt)
        
        # Горящая аура (урон врагам рядом)
        aura_damage = self.ability_manager.get_passive_effect('aura_damage', 0)
        if aura_damage > 0:
            aura_radius = self.ability_manager.get_passive_effect('aura_radius', 80)
            enemies = game_manager.get_enemies_in_radius(self.x, self.y, aura_radius)
            for enemy in enemies:
                enemy.take_damage(aura_damage * dt, self)
    
    def _update_buffs(self, dt):
        """Обновление активных баффов"""
        expired = []
        
        for buff_id, buff_data in self.buffs.items():
            buff_data['duration'] -= dt
            if buff_data['duration'] <= 0:
                expired.append(buff_id)
        
        for buff_id in expired:
            del self.buffs[buff_id]
    
    def attack(self, target_x, target_y, game_manager):
        """Базовая атака"""
        if self.attack_cooldown > 0:
            return False
        
        self.attack_cooldown = PLAYER_ATTACK_COOLDOWN
        self.is_attacking = True
        
        # Направление атаки
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            self.facing_x = dx / dist
            self.facing_y = dy / dist
        
        # Находим врагов в радиусе атаки
        attack_x = self.x + self.facing_x * self.attack_range
        attack_y = self.y + self.facing_y * self.attack_range
        
        hit_enemies = game_manager.get_enemies_in_radius(
            attack_x, attack_y, self.attack_range
        )
        
        # Наносим урон
        total_damage = self.get_total_damage()
        
        for enemy in hit_enemies:
            # Шанс крита
            crit_chance = 0.05 + self.ability_manager.get_passive_effect('crit_chance', 0)
            is_crit = random.random() < crit_chance
            
            damage = total_damage * (2.0 if is_crit else 1.0)
            enemy.take_damage(damage, self)
            
            # Эффект попадания
            game_manager.particle_system.emit_hit(
                enemy.x, enemy.y,
                (1, 0.5, 0.2, 1) if is_crit else (1, 1, 1, 1)
            )
        
        return len(hit_enemies) > 0
    
    def use_ability(self, index, target_x, target_y, game_manager):
        """Использование способности"""
        return self.ability_manager.use_ability(
            index, self, target_x, target_y, game_manager
        )
    
    def take_damage(self, amount, source=None):
        """Получение урона"""
        if self.invulnerable:
            return 0
        
        # Шанс уклонения
        dodge_chance = self.ability_manager.get_passive_effect('dodge_chance', 0)
        if random.random() < dodge_chance:
            return 0
        
        # Защита от баффов
        defense = 0
        for buff_data in self.buffs.values():
            defense += buff_data.get('effect', {}).get('defense', 0)
        
        # Снижение урона
        damage_reduction = 0
        for buff_data in self.buffs.values():
            damage_reduction += buff_data.get('effect', {}).get('damage_reduction', 0)
        
        actual_damage = max(1, amount - defense) * (1 - damage_reduction)
        
        self.hp -= actual_damage
        
        # Включаем неуязвимость
        self.invulnerable = True
        self.invulnerable_timer = self.invulnerable_duration
        
        if self.hp < 0:
            self.hp = 0
        
        return actual_damage
    
    def heal(self, amount):
        """Лечение"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def is_alive(self):
        """Проверка жив ли игрок"""
        return self.hp > 0
    
    def apply_buff(self, buff_id, effect, duration):
        """Применение баффа"""
        self.buffs[buff_id] = {
            'effect': effect,
            'duration': duration
        }
    
    def apply_slow(self, factor, duration):
        """Применение замедления"""
        self.slow_factor = min(self.slow_factor, 1 - factor)
        self.slow_duration = max(self.slow_duration, duration)
    
    def absorb(self, enemy_body, game_manager):
        """
        Поглощение тела врага
        enemy_body: объект мёртвого врага
        """
        enemy_type = enemy_body.enemy_type
        enemy_data = ENEMY_TYPES.get(enemy_type, {})
        
        # Увеличиваем HP
        hp_gain = int(enemy_data.get('hp', 0) * ABSORPTION_HP_GAIN)
        self.max_hp += hp_gain
        self.hp += hp_gain // 4  # Восстанавливаем 25%
        
        # Увеличиваем урон
        damage_gain = int(enemy_data.get('damage', 0) * ABSORPTION_DAMAGE_GAIN)
        self.damage += damage_gain
        
        # Увеличиваем скорость (с ограничением)
        self.speed_multiplier = min(
            1.0 + MAX_SPEED_BONUS,
            self.speed_multiplier + ABSORPTION_SPEED_GAIN
        )
        
        # Увеличиваем размер (с ограничением)
        self.size_multiplier = min(
            1.0 + MAX_SIZE_BONUS,
            self.size_multiplier + ABSORPTION_SIZE_GAIN
        )
        self.size = self.base_size * self.size_multiplier
        self.collision_radius = self.size / 2
        
        # Получаем случайную способность
        abilities = enemy_data.get('abilities', [])
        if abilities:
            ability_id = random.choice(abilities)
            added = self.ability_manager.add_ability(ability_id)
            
            if added:
                # Показываем уведомление
                ability_name = game_manager.get_ability_name(ability_id)
                game_manager.show_notification(f"Получена способность: {ability_name}!")
        
        # Добавляем визуальный слой
        enemy_color = enemy_data.get('color', (0.5, 0.5, 0.5, 1))
        layer_opacity = max(0.2, 0.6 - len(self.visual_layers) * 0.15)
        self.visual_layers.append((enemy_color, layer_opacity))
        
        # Ограничиваем количество слоёв (оставляем последние 5)
        if len(self.visual_layers) > 5:
            self.visual_layers = self.visual_layers[-5:]
        
        # Обновляем текстуру
        self.update_texture()
        
        # Записываем поглощение
        self.absorptions_count += 1
        if enemy_type not in self.absorbed_enemies:
            self.absorbed_enemies.append(enemy_type)
        
        # Эффект поглощения
        game_manager.particle_system.emit_absorption(
            enemy_body.x, enemy_body.y,
            self.x, self.y,
            enemy_color
        )
        
        game_manager.particle_system.emit_heal(self.x, self.y)
    
    def get_total_damage(self):
        """Получение полного урона с учётом баффов"""
        total = self.damage
        
        # Баффы урона
        for buff_data in self.buffs.values():
            total += buff_data.get('effect', {}).get('bonus_damage', 0)
        
        return total
    
    def get_stats(self):
        """Получение статистики игрока"""
        return {
            'hp': self.hp,
            'max_hp': self.max_hp,
            'damage': self.get_total_damage(),
            'speed': self.speed * self.speed_multiplier,
            'absorptions': self.absorptions_count,
            'kills': self.kills,
            'abilities_count': len(self.ability_manager.abilities),
            'time': self.play_time,
        }
    
    def get_save_data(self):
        """Получение данных для сохранения"""
        return {
            'x': self.x,
            'y': self.y,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'damage': self.damage,
            'speed_multiplier': self.speed_multiplier,
            'size_multiplier': self.size_multiplier,
            'absorptions_count': self.absorptions_count,
            'absorbed_enemies': self.absorbed_enemies,
            'visual_layers': self.visual_layers,
            'abilities': self.ability_manager.get_all_ability_ids(),
            'kills': self.kills,
            'play_time': self.play_time,
        }
    
    def load_save_data(self, data):
        """Загрузка данных из сохранения"""
        self.x = data.get('x', self.x)
        self.y = data.get('y', self.y)
        self.hp = data.get('hp', self.hp)
        self.max_hp = data.get('max_hp', self.max_hp)
        self.damage = data.get('damage', self.damage)
        self.speed_multiplier = data.get('speed_multiplier', 1.0)
        self.size_multiplier = data.get('size_multiplier', 1.0)
        self.size = self.base_size * self.size_multiplier
        self.collision_radius = self.size / 2
        self.absorptions_count = data.get('absorptions_count', 0)
        self.absorbed_enemies = data.get('absorbed_enemies', [])
        self.visual_layers = data.get('visual_layers', [])
        self.kills = data.get('kills', 0)
        self.play_time = data.get('play_time', 0)
        
        # Восстанавливаем способности
        for ability_id in data.get('abilities', []):
            self.ability_manager.add_ability(ability_id)
        
        # Обновляем текстуру
        self.update_texture()