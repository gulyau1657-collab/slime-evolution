"""
ВРАГИ
Базовый класс и все типы врагов с их ИИ
"""

import math
import random
from src.config import (
    ENEMY_TYPES, AI_PASSIVE, AI_TERRITORIAL, AI_AGGRESSIVE,
    AI_STATIONARY, AI_PACK, DETECTION_RANGE_TERRITORIAL,
    DETECTION_RANGE_AGGRESSIVE, DETECTION_RANGE_STATIONARY,
    BODY_DECAY_TIME, WORLD_WIDTH, WORLD_HEIGHT, ABILITIES
)
from src.utils import distance, normalize, generate_enemy_texture


class Enemy:
    """Базовый класс врага"""
    
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        
        # Загружаем данные из конфига
        data = ENEMY_TYPES.get(enemy_type, {})
        
        self.name = data.get('name', 'Unknown')
        self.max_hp = data.get('hp', 50)
        self.hp = self.max_hp
        self.damage = data.get('damage', 10)
        self.speed = data.get('speed', 100)
        self.size = data.get('size', 32)
        self.collision_radius = self.size / 2
        self.color = data.get('color', (0.5, 0.5, 0.5, 1))
        self.ai_type = data.get('ai', AI_TERRITORIAL)
        self.biome = data.get('biome', 'fields')
        self.abilities = data.get('abilities', [])
        self.exp = data.get('exp', 10)
        self.is_boss = data.get('is_boss', False)
        
        # Состояние
        self.alive = True
        self.target = None  # Цель для преследования
        self.state = 'idle'  # idle, patrol, chase, attack, flee
        
        # Патрулирование
        self.patrol_point = (x, y)
        self.patrol_radius = 150
        self.patrol_target = None
        self.patrol_wait_timer = 0
        
        # Атака
        self.attack_cooldown = 0
        self.attack_range = 50
        self.ability_cooldowns = {}
        
        # Движение
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Баффы/дебаффы
        self.slow_factor = 1.0
        self.slow_duration = 0
        self.stunned = False
        self.stun_duration = 0
        
        # Стайное поведение
        self.pack = None
        self.pack_alert = False
        
        # Текстура
        self.texture = generate_enemy_texture(
            int(self.size), self.color, enemy_type
        )
    
    def update(self, dt, player, game_manager):
        """Обновление врага"""
        if not self.alive:
            return
        
        # Обновляем дебаффы
        self._update_debuffs(dt)
        
        # Обновляем кулдауны
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        for ability_id in self.ability_cooldowns:
            if self.ability_cooldowns[ability_id] > 0:
                self.ability_cooldowns[ability_id] -= dt
        
        # Если оглушён - не делаем ничего
        if self.stunned:
            return
        
        # ИИ поведение
        self._update_ai(dt, player, game_manager)
        
        # Движение
        actual_speed = self.speed * self.slow_factor
        self.x += self.velocity_x * actual_speed * dt
        self.y += self.velocity_y * actual_speed * dt
        
        # Ограничение миром
        self.x = max(self.collision_radius, min(WORLD_WIDTH - self.collision_radius, self.x))
        self.y = max(self.collision_radius, min(WORLD_HEIGHT - self.collision_radius, self.y))
    
    def _update_debuffs(self, dt):
        """Обновление дебаффов"""
        if self.slow_duration > 0:
            self.slow_duration -= dt
            if self.slow_duration <= 0:
                self.slow_factor = 1.0
        
        if self.stun_duration > 0:
            self.stun_duration -= dt
            if self.stun_duration <= 0:
                self.stunned = False
    
    def _update_ai(self, dt, player, game_manager):
        """Обновление ИИ поведения"""
        dist_to_player = distance(self.x, self.y, player.x, player.y)
        
        if self.ai_type == AI_PASSIVE:
            self._ai_passive(dt, player, dist_to_player)
        elif self.ai_type == AI_TERRITORIAL:
            self._ai_territorial(dt, player, dist_to_player, game_manager)
        elif self.ai_type == AI_AGGRESSIVE:
            self._ai_aggressive(dt, player, dist_to_player, game_manager)
        elif self.ai_type == AI_STATIONARY:
            self._ai_stationary(dt, player, dist_to_player, game_manager)
        elif self.ai_type == AI_PACK:
            self._ai_pack(dt, player, dist_to_player, game_manager)
    
    def _ai_passive(self, dt, player, dist_to_player):
        """ИИ пассивного существа (убегает при атаке)"""
        if self.state == 'flee':
            # Убегаем от игрока
            if dist_to_player > 300:
                self.state = 'idle'
            else:
                dx, dy = normalize(self.x - player.x, self.y - player.y)
                self.velocity_x = dx
                self.velocity_y = dy
        else:
            # Случайное блуждание
            self._patrol(dt)
    
    def _ai_territorial(self, dt, player, dist_to_player, game_manager):
        """ИИ территориального существа"""
        if dist_to_player < DETECTION_RANGE_TERRITORIAL:
            self.state = 'chase'
            self._chase_player(player)
            
            # Атакуем если близко
            if dist_to_player < self.attack_range + player.collision_radius:
                self._attack_player(player, game_manager)
        else:
            self.state = 'patrol'
            self._patrol(dt)
    
    def _ai_aggressive(self, dt, player, dist_to_player, game_manager):
        """ИИ агрессивного существа"""
        if dist_to_player < DETECTION_RANGE_AGGRESSIVE:
            self.state = 'chase'
            self._chase_player(player)
            
            if dist_to_player < self.attack_range + player.collision_radius:
                self._attack_player(player, game_manager)
        else:
            self.state = 'patrol'
            self._patrol(dt)
    
    def _ai_stationary(self, dt, player, dist_to_player, game_manager):
        """ИИ стационарного существа (турель)"""
        self.velocity_x = 0
        self.velocity_y = 0
        
        if dist_to_player < DETECTION_RANGE_STATIONARY:
            self.state = 'attack'
            # Используем дальнобойные способности
            self._use_ranged_ability(player, game_manager)
        else:
            self.state = 'idle'
    
    def _ai_pack(self, dt, player, dist_to_player, game_manager):
        """ИИ стайного существа"""
        # Если стая атертована - все атакуют
        if self.pack_alert or dist_to_player < DETECTION_RANGE_TERRITORIAL:
            self.pack_alert = True
            
            # Оповещаем стаю
            if self.pack:
                for member in self.pack:
                    if member != self and member.alive:
                        member.pack_alert = True
            
            self.state = 'chase'
            self._chase_player(player)
            
            if dist_to_player < self.attack_range + player.collision_radius:
                self._attack_player(player, game_manager)
        else:
            self.state = 'patrol'
            self._patrol(dt)
    
    def _patrol(self, dt):
        """Патрулирование"""
        if self.patrol_wait_timer > 0:
            self.patrol_wait_timer -= dt
            self.velocity_x = 0
            self.velocity_y = 0
            return
        
        # Если нет цели патруля - создаём новую
        if self.patrol_target is None:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(50, self.patrol_radius)
            self.patrol_target = (
                self.patrol_point[0] + math.cos(angle) * dist,
                self.patrol_point[1] + math.sin(angle) * dist
            )
        
        # Двигаемся к цели
        dx = self.patrol_target[0] - self.x
        dy = self.patrol_target[1] - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist < 10:
            # Достигли цели
            self.patrol_target = None
            self.patrol_wait_timer = random.uniform(1, 3)
            self.velocity_x = 0
            self.velocity_y = 0
        else:
            self.velocity_x = dx / dist
            self.velocity_y = dy / dist
    
    def _chase_player(self, player):
        """Преследование игрока"""
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            self.velocity_x = dx / dist
            self.velocity_y = dy / dist
        else:
            self.velocity_x = 0
            self.velocity_y = 0
    
    def _attack_player(self, player, game_manager):
        """Атака игрока"""
        if self.attack_cooldown > 0:
            return
        
        self.attack_cooldown = 1.0
        player.take_damage(self.damage, self)
        
        # Эффект попадания
        game_manager.particle_system.emit_hit(player.x, player.y, (1, 0.3, 0.3, 1))
    
    def _use_ranged_ability(self, player, game_manager):
        """Использование дальнобойной способности"""
        for ability_id in self.abilities:
            ability_data = ABILITIES.get(ability_id, {})
            
            # Проверяем кулдаун
            if ability_id not in self.ability_cooldowns:
                self.ability_cooldowns[ability_id] = 0
            
            if self.ability_cooldowns[ability_id] > 0:
                continue
            
            # Проверяем тип способности
            if 'projectile_speed' in ability_data:
                # Стреляем снарядом
                self._fire_projectile(ability_id, player, game_manager)
                self.ability_cooldowns[ability_id] = ability_data.get('cooldown', 2.0)
                return
    
    def _fire_projectile(self, ability_id, target, game_manager):
        """Выстрел снарядом"""
        from src.ability import Projectile
        
        ability_data = ABILITIES.get(ability_id, {})
        
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            dx /= dist
            dy /= dist
        
        speed = ability_data.get('projectile_speed', 300)
        damage = ability_data.get('damage', self.damage)
        range_ = ability_data.get('range', 300)
        
        projectile = Projectile(
            x=self.x,
            y=self.y,
            vx=dx * speed,
            vy=dy * speed,
            damage=damage,
            max_range=range_,
            owner=self,
            color=ability_data.get('icon_color', (1, 0.5, 0, 1)),
            ability_id=ability_id
        )
        
        game_manager.add_projectile(projectile)
    
    def take_damage(self, amount, source=None):
        """Получение урона"""
        self.hp -= amount
        
        # Переключаем пассивных в режим побега
        if self.ai_type == AI_PASSIVE:
            self.state = 'flee'
        
        # Оповещаем стаю
        if self.ai_type == AI_PACK and self.pack:
            for member in self.pack:
                member.pack_alert = True
        
        if self.hp <= 0:
            self.hp = 0
            self.die(source)
    
    def apply_slow(self, factor, duration):
        """Применение замедления"""
        self.slow_factor = min(self.slow_factor, 1 - factor)
        self.slow_duration = max(self.slow_duration, duration)
    
    def apply_stun(self, duration):
        """Оглушение"""
        self.stunned = True
        self.stun_duration = max(self.stun_duration, duration)
        self.velocity_x = 0
        self.velocity_y = 0
    
    def die(self, killer=None):
        """Смерть врага"""
        self.alive = False
        
        if killer and hasattr(killer, 'kills'):
            killer.kills += 1
    
    def get_body(self):
        """Создание тела для поглощения"""
        return EnemyBody(self.x, self.y, self.enemy_type, self.color)


class EnemyBody:
    """Тело мёртвого врага (можно поглотить)"""
    
    def __init__(self, x, y, enemy_type, color):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.color = color
        self.decay_timer = BODY_DECAY_TIME
        self.size = ENEMY_TYPES.get(enemy_type, {}).get('size', 32)
        self.collision_radius = self.size / 2
        self.absorbed = False
    
    def update(self, dt):
        """Обновление таймера распада"""
        self.decay_timer -= dt
        return self.decay_timer > 0 and not self.absorbed
    
    def get_opacity(self):
        """Прозрачность тела (исчезает со временем)"""
        return min(1.0, self.decay_timer / (BODY_DECAY_TIME * 0.3))


class EnemySpawner:
    """Система спавна врагов"""
    
    def __init__(self):
        self.enemies = []
        self.bodies = []
        self.respawn_queue = []  # [(enemy_type, biome, respawn_time), ...]
        self.packs = []  # Группы для стайных врагов
    
    def spawn_initial_enemies(self, world):
        """Спавн начальной популяции врагов"""
        from src.config import ENEMY_SPAWN_CONFIG
        
        for biome, enemy_list in ENEMY_SPAWN_CONFIG.items():
            biome_region = world.get_biome_region(biome)
            
            for enemy_type, count in enemy_list:
                enemy_data = ENEMY_TYPES.get(enemy_type, {})
                is_pack = enemy_data.get('ai') == AI_PACK
                
                if is_pack:
                    # Спавним группами
                    pack_size_range = enemy_data.get('pack_size', (3, 5))
                    spawned = 0
                    
                    while spawned < count:
                        pack_size = min(
                            random.randint(*pack_size_range),
                            count - spawned
                        )
                        
                        # Центр стаи
                        center_x, center_y = world.get_random_point_in_biome(biome)
                        
                        pack = []
                        for _ in range(pack_size):
                            offset_x = random.uniform(-50, 50)
                            offset_y = random.uniform(-50, 50)
                            
                            enemy = Enemy(
                                center_x + offset_x,
                                center_y + offset_y,
                                enemy_type
                            )
                            enemy.pack = pack
                            pack.append(enemy)
                            self.enemies.append(enemy)
                        
                        self.packs.append(pack)
                        spawned += pack_size
                else:
                    # Обычный спавн
                    for _ in range(count):
                        x, y = world.get_random_point_in_biome(biome)
                        enemy = Enemy(x, y, enemy_type)
                        enemy.patrol_point = (x, y)
                        self.enemies.append(enemy)
    
    def update(self, dt, player, game_manager, world):
        """Обновление всех врагов"""
        # Обновляем живых врагов
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(dt, player, game_manager)
        
        # Обновляем тела
        self.bodies = [body for body in self.bodies if body.update(dt)]
        
        # Проверяем респавн
        new_respawn_queue = []
        for enemy_type, biome, respawn_time in self.respawn_queue:
            respawn_time -= dt
            if respawn_time <= 0:
                # Респавним врага
                x, y = world.get_random_point_in_biome(biome, min_distance_from_player=500, player=player)
                if x is not None:
                    enemy = Enemy(x, y, enemy_type)
                    enemy.patrol_point = (x, y)
                    self.enemies.append(enemy)
            else:
                new_respawn_queue.append((enemy_type, biome, respawn_time))
        
        self.respawn_queue = new_respawn_queue
        
        # Удаляем мёртвых врагов и создаём тела
        alive_enemies = []
        for enemy in self.enemies:
            if enemy.alive:
                alive_enemies.append(enemy)
            else:
                # Создаём тело
                body = enemy.get_body()
                self.bodies.append(body)
                
                # Добавляем в очередь респавна (если не босс)
                if not enemy.is_boss:
                    from src.config import RESPAWN_TIME
                    self.respawn_queue.append(
                        (enemy.enemy_type, enemy.biome, RESPAWN_TIME)
                    )
        
        self.enemies = alive_enemies
    
    def get_enemies_in_radius(self, x, y, radius):
        """Получение врагов в радиусе"""
        result = []
        radius_sq = radius * radius
        
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            dx = enemy.x - x
            dy = enemy.y - y
            if dx * dx + dy * dy <= radius_sq:
                result.append(enemy)
        
        return result
    
    def get_bodies_in_radius(self, x, y, radius):
        """Получение тел в радиусе"""
        result = []
        radius_sq = radius * radius
        
        for body in self.bodies:
            if body.absorbed:
                continue
            
            dx = body.x - x
            dy = body.y - y
            if dx * dx + dy * dy <= radius_sq:
                result.append(body)
        
        return result
    
    def get_nearest_body(self, x, y, max_radius=100):
        """Получение ближайшего тела"""
        nearest = None
        nearest_dist = max_radius * max_radius
        
        for body in self.bodies:
            if body.absorbed:
                continue
            
            dx = body.x - x
            dy = body.y - y
            dist_sq = dx * dx + dy * dy
            
            if dist_sq < nearest_dist:
                nearest_dist = dist_sq
                nearest = body
        
        return nearest
    
    def get_save_data(self):
        """Данные для сохранения"""
        enemies_data = []
        for enemy in self.enemies:
            if enemy.alive:
                enemies_data.append({
                    'type': enemy.enemy_type,
                    'x': enemy.x,
                    'y': enemy.y,
                    'hp': enemy.hp,
                    'patrol_point': enemy.patrol_point,
                })
        
        return {
            'enemies': enemies_data,
            'respawn_queue': self.respawn_queue,
        }
    
    def load_save_data(self, data):
        """Загрузка из сохранения"""
        self.enemies.clear()
        self.bodies.clear()
        
        for enemy_data in data.get('enemies', []):
            enemy = Enemy(
                enemy_data['x'],
                enemy_data['y'],
                enemy_data['type']
            )
            enemy.hp = enemy_data.get('hp', enemy.max_hp)
            enemy.patrol_point = tuple(enemy_data.get('patrol_point', (enemy.x, enemy.y)))
            self.enemies.append(enemy)
        
        self.respawn_queue = data.get('respawn_queue', [])