"""
СИСТЕМА СПОСОБНОСТЕЙ
Базовый класс и все типы способностей
"""

import math
import random
from src.config import ABILITIES, ABILITY_ACTIVE, ABILITY_PASSIVE


class Ability:
    """Базовый класс способности"""
    
    def __init__(self, ability_id):
        self.id = ability_id
        self.data = ABILITIES.get(ability_id, {})
        
        self.name = self.data.get('name', 'Unknown')
        self.ability_type = self.data.get('type', ABILITY_ACTIVE)
        self.description = self.data.get('description', '')
        self.icon_color = self.data.get('icon_color', (0.5, 0.5, 0.5, 1))
        
        # Для активных способностей
        self.cooldown = self.data.get('cooldown', 1.0)
        self.current_cooldown = 0
        
        # Параметры
        self.damage = self.data.get('damage', 0)
        self.range = self.data.get('range', 0)
        self.duration = self.data.get('duration', 0)
        self.projectile_speed = self.data.get('projectile_speed', 0)
        
    def is_ready(self):
        """Проверка готовности способности"""
        return self.current_cooldown <= 0
    
    def get_cooldown_progress(self):
        """Прогресс перезарядки (0-1)"""
        if self.cooldown <= 0:
            return 1.0
        return 1.0 - (self.current_cooldown / self.cooldown)
    
    def update(self, dt):
        """Обновление кулдауна"""
        if self.current_cooldown > 0:
            self.current_cooldown -= dt
            if self.current_cooldown < 0:
                self.current_cooldown = 0
    
    def use(self, caster, target_x, target_y, game_manager):
        """
        Использование способности
        Возвращает True если способность была использована
        """
        if not self.is_ready():
            return False
        
        # Запускаем кулдаун
        self.current_cooldown = self.cooldown
        
        # Переопределяется в подклассах
        return self._execute(caster, target_x, target_y, game_manager)
    
    def _execute(self, caster, target_x, target_y, game_manager):
        """Выполнение способности (переопределяется)"""
        return True
    
    def get_passive_effects(self):
        """Получение пассивных эффектов"""
        if self.ability_type != ABILITY_PASSIVE:
            return {}
        return self.data.get('effect', {})


class ProjectileAbility(Ability):
    """Способность, создающая снаряд"""
    
    def _execute(self, caster, target_x, target_y, game_manager):
        """Создание снаряда"""
        # Направление к цели
        dx = target_x - caster.x
        dy = target_y - caster.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            dx /= dist
            dy /= dist
        else:
            dx, dy = 1, 0
        
        # Создаём снаряд
        projectile = Projectile(
            x=caster.x,
            y=caster.y,
            vx=dx * self.projectile_speed,
            vy=dy * self.projectile_speed,
            damage=self.damage + caster.damage * 0.5,
            max_range=self.range,
            owner=caster,
            color=self.icon_color,
            ability_id=self.id
        )
        
        game_manager.add_projectile(projectile)
        return True


class AreaAbility(Ability):
    """Способность с АоЕ эффектом"""
    
    def _execute(self, caster, target_x, target_y, game_manager):
        """АоЕ урон/эффект"""
        radius = self.data.get('radius', 100)
        
        # Находим всех врагов в радиусе
        targets = game_manager.get_enemies_in_radius(
            caster.x, caster.y, radius
        )
        
        for enemy in targets:
            if enemy != caster:
                enemy.take_damage(self.damage, caster)
        
        # Визуальный эффект
        game_manager.particle_system.emit_explosion(
            caster.x, caster.y, self.icon_color, count=25
        )
        
        return True


class DashAbility(Ability):
    """Способность рывка"""
    
    def _execute(self, caster, target_x, target_y, game_manager):
        """Рывок в направлении"""
        distance = self.data.get('distance', 200)
        
        # Направление к цели
        dx = target_x - caster.x
        dy = target_y - caster.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            dx /= dist
            dy /= dist
        else:
            dx, dy = 1, 0
        
        # Перемещаем
        new_x = caster.x + dx * distance
        new_y = caster.y + dy * distance
        
        # Урон по пути (если есть)
        if self.damage > 0:
            enemies = game_manager.get_enemies_in_line(
                caster.x, caster.y, new_x, new_y, 30
            )
            for enemy in enemies:
                enemy.take_damage(self.damage, caster)
        
        caster.x = new_x
        caster.y = new_y
        
        # Эффект следа
        game_manager.particle_system.emit_trail(
            caster.x, caster.y, self.icon_color
        )
        
        return True


class BuffAbility(Ability):
    """Способность баффа"""
    
    def _execute(self, caster, target_x, target_y, game_manager):
        """Наложение баффа"""
        effect = self.data.get('effect', {})
        duration = self.data.get('duration', 5.0)
        
        caster.apply_buff(self.id, effect, duration)
        
        # Визуальный эффект
        game_manager.particle_system.emit(
            caster.x, caster.y, 15, self.icon_color,
            size_range=(5, 10),
            speed_range=(30, 60),
            spread=360
        )
        
        return True


class SummonAbility(Ability):
    """Способность призыва"""
    
    def _execute(self, caster, target_x, target_y, game_manager):
        """Призыв существа"""
        summon_count = self.data.get('summon_count', 1)
        
        for _ in range(summon_count):
            # Позиция рядом с кастером
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(50, 100)
            x = caster.x + math.cos(angle) * dist
            y = caster.y + math.sin(angle) * dist
            
            # Создаём призванное существо
            # TODO: реализовать полноценный призыв
            game_manager.particle_system.emit_explosion(
                x, y, self.icon_color, count=10
            )
        
        return True


class Projectile:
    """Снаряд (огненный шар, ледяная стрела и т.д.)"""
    
    def __init__(self, x, y, vx, vy, damage, max_range, owner, 
                 color=(1, 1, 1, 1), ability_id=''):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.max_range = max_range
        self.owner = owner
        self.color = color
        self.ability_id = ability_id
        
        self.size = 10
        self.collision_radius = 8
        self.alive = True
        
        # Дополнительные эффекты
        self.aoe_radius = ABILITIES.get(ability_id, {}).get('aoe_radius', 0)
        self.slow_effect = ABILITIES.get(ability_id, {}).get('slow_effect', 0)
        self.slow_duration = ABILITIES.get(ability_id, {}).get('slow_duration', 0)
    
    def update(self, dt):
        """Обновление позиции"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Проверяем дальность
        dx = self.x - self.start_x
        dy = self.y - self.start_y
        traveled = math.sqrt(dx * dx + dy * dy)
        
        if traveled >= self.max_range:
            self.alive = False
    
    def on_hit(self, target, game_manager):
        """Вызывается при попадании"""
        target.take_damage(self.damage, self.owner)
        
        # АоЕ урон
        if self.aoe_radius > 0:
            enemies = game_manager.get_enemies_in_radius(
                self.x, self.y, self.aoe_radius
            )
            for enemy in enemies:
                if enemy != target:
                    enemy.take_damage(self.damage * 0.5, self.owner)
        
        # Замедление
        if self.slow_effect > 0:
            target.apply_slow(self.slow_effect, self.slow_duration)
        
        # Эффект попадания
        game_manager.particle_system.emit_hit(self.x, self.y, self.color)
        
        self.alive = False


class AbilityManager:
    """Менеджер способностей игрока"""
    
    def __init__(self, max_abilities=6):
        self.abilities = []  # Список активных способностей
        self.max_abilities = max_abilities
        self.passive_effects = {}  # Суммарные пассивные эффекты
    
    def add_ability(self, ability_id):
        """
        Добавление способности
        Возвращает True если добавлена, False если нужно выбрать замену
        """
        if ability_id in [a.id for a in self.abilities]:
            return True  # Уже есть
        
        ability = self._create_ability(ability_id)
        
        if len(self.abilities) < self.max_abilities:
            self.abilities.append(ability)
            self._recalculate_passives()
            return True
        
        return False  # Нужно выбрать замену
    
    def replace_ability(self, index, ability_id):
        """Замена способности по индексу"""
        if 0 <= index < len(self.abilities):
            ability = self._create_ability(ability_id)
            self.abilities[index] = ability
            self._recalculate_passives()
    
    def _create_ability(self, ability_id):
        """Создание объекта способности по ID"""
        data = ABILITIES.get(ability_id, {})
        
        # Определяем тип способности
        if 'projectile_speed' in data:
            return ProjectileAbility(ability_id)
        elif 'radius' in data and 'duration' not in data:
            return AreaAbility(ability_id)
        elif 'distance' in data:
            return DashAbility(ability_id)
        elif 'summon_count' in data:
            return SummonAbility(ability_id)
        elif data.get('type') == ABILITY_ACTIVE and 'duration' in data:
            return BuffAbility(ability_id)
        else:
            return Ability(ability_id)
    
    def _recalculate_passives(self):
        """Пересчёт пассивных эффектов"""
        self.passive_effects = {}
        
        for ability in self.abilities:
            effects = ability.get_passive_effects()
            for key, value in effects.items():
                if key in self.passive_effects:
                    self.passive_effects[key] += value
                else:
                    self.passive_effects[key] = value
    
    def update(self, dt):
        """Обновление кулдаунов"""
        for ability in self.abilities:
            ability.update(dt)
    
    def use_ability(self, index, caster, target_x, target_y, game_manager):
        """Использование способности по индексу"""
        if 0 <= index < len(self.abilities):
            ability = self.abilities[index]
            if ability.ability_type == ABILITY_ACTIVE:
                return ability.use(caster, target_x, target_y, game_manager)
        return False
    
    def get_ability_info(self, index):
        """Получение информации о способности"""
        if 0 <= index < len(self.abilities):
            ability = self.abilities[index]
            return {
                'name': ability.name,
                'icon_color': ability.icon_color,
                'cooldown_progress': ability.get_cooldown_progress(),
                'is_ready': ability.is_ready(),
                'type': ability.ability_type,
            }
        return None
    
    def get_passive_effect(self, effect_name, default=0):
        """Получение значения пассивного эффекта"""
        return self.passive_effects.get(effect_name, default)
    
    def get_all_ability_ids(self):
        """Получение списка ID всех способностей"""
        return [a.id for a in self.abilities]