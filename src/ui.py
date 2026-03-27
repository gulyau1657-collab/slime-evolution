"""
ИНТЕРФЕЙС ПОЛЬЗОВАТЕЛЯ
HP бар, способности, уведомления, мини-карта
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock

from src.config import (
    HP_BAR_WIDTH, HP_BAR_HEIGHT, ABILITY_SLOT_SIZE, MINIMAP_SIZE,
    COLOR_HP_BAR, COLOR_HP_BAR_BG, COLOR_TEXT, COLOR_NOTIFICATION,
    WORLD_WIDTH, WORLD_HEIGHT, BIOME_COLORS
)


class Notification:
    """Уведомление на экране"""
    
    def __init__(self, text, duration=3.0, color=COLOR_NOTIFICATION):
        self.text = text
        self.duration = duration
        self.remaining = duration
        self.color = color
        self.alpha = 1.0
    
    def update(self, dt):
        """Обновление уведомления"""
        self.remaining -= dt
        
        # Затухание в последнюю секунду
        if self.remaining < 1.0:
            self.alpha = max(0, self.remaining)
        
        return self.remaining > 0


class GameUI(Widget):
    """Игровой интерфейс"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.player = None
        self.game_manager = None
        
        # Уведомления
        self.notifications = []
        
        # Кэш текстур текста
        self.text_cache = {}
        
        # Флаги отображения
        self.show_minimap = True
        self.show_ability_bar = True
    
    def set_player(self, player):
        """Установка ссылки на игрока"""
        self.player = player
    
    def set_game_manager(self, game_manager):
        """Установка ссылки на менеджер игры"""
        self.game_manager = game_manager
    
    def add_notification(self, text, duration=3.0, color=None):
        """Добавление уведомления"""
        if color is None:
            color = COLOR_NOTIFICATION
        
        notification = Notification(text, duration, color)
        self.notifications.append(notification)
        
        # Ограничиваем количество уведомлений
        if len(self.notifications) > 5:
            self.notifications.pop(0)
    
    def update(self, dt):
        """Обновление UI"""
        # Обновляем уведомления
        self.notifications = [n for n in self.notifications if n.update(dt)]
    
    def draw(self, canvas):
        """Отрисовка интерфейса"""
        if not self.player:
            return
        
        canvas.clear()
        
        with canvas:
            # HP бар
            self._draw_hp_bar(canvas)
            
            # Счётчик поглощений
            self._draw_absorption_counter(canvas)
            
            # Мини-карта
            if self.show_minimap:
                self._draw_minimap(canvas)
            
            # Уведомления
            self._draw_notifications(canvas)
            
            # Индикатор биома
            self._draw_biome_indicator(canvas)
    
    def _draw_hp_bar(self, canvas):
        """Отрисовка полосы здоровья"""
        padding = 20
        x = padding
        y = self.height - padding - HP_BAR_HEIGHT
        
        # Фон
        Color(*COLOR_HP_BAR_BG)
        Rectangle(pos=(x, y), size=(HP_BAR_WIDTH, HP_BAR_HEIGHT))
        
        # Заполнение
        hp_ratio = self.player.hp / self.player.max_hp
        fill_width = HP_BAR_WIDTH * hp_ratio
        
        # Цвет зависит от уровня здоровья
        if hp_ratio > 0.5:
            Color(0.2, 0.8, 0.2, 1)
        elif hp_ratio > 0.25:
            Color(0.9, 0.7, 0.1, 1)
        else:
            Color(0.9, 0.2, 0.2, 1)
        
        Rectangle(pos=(x, y), size=(fill_width, HP_BAR_HEIGHT))
        
        # Рамка
        Color(1, 1, 1, 0.8)
        Line(rectangle=(x, y, HP_BAR_WIDTH, HP_BAR_HEIGHT), width=1.5)
        
        # Текст HP
        hp_text = f"{int(self.player.hp)}/{int(self.player.max_hp)}"
        self._draw_text(canvas, hp_text, x + HP_BAR_WIDTH / 2, y + HP_BAR_HEIGHT / 2,
                       font_size=14, anchor_x='center', anchor_y='center')
    
    def _draw_absorption_counter(self, canvas):
        """Отрисовка счётчика поглощений"""
        padding = 20
        x = self.width - padding
        y = self.height - padding - 30
        
        text = f"Поглощено: {self.player.absorptions_count}"
        self._draw_text(canvas, text, x, y, font_size=16, 
                       anchor_x='right', color=(0.8, 1, 0.8, 1))
        
        # Убийства
        kills_text = f"Убито: {self.player.kills}"
        self._draw_text(canvas, kills_text, x, y - 25, font_size=14,
                       anchor_x='right', color=(1, 0.8, 0.8, 1))
    
    def _draw_minimap(self, canvas):
        """Отрисовка мини-карты"""
        padding = 20
        size = MINIMAP_SIZE
        x = self.width - padding - size
        y = self.height - padding - 80 - size
        
        # Фон мини-карты
        Color(0.1, 0.1, 0.15, 0.8)
        Rectangle(pos=(x, y), size=(size, size))
        
        # Масштаб
        scale_x = size / WORLD_WIDTH
        scale_y = size / WORLD_HEIGHT
        
        # Рисуем биомы (упрощённо)
        biome_size = 10
        for by in range(0, size, biome_size):
            for bx in range(0, size, biome_size):
                world_x = bx / scale_x
                world_y = by / scale_y
                
                if self.game_manager:
                    biome = self.game_manager.world.get_biome_at(world_x, world_y)
                    color = BIOME_COLORS.get(biome, (0.3, 0.5, 0.3, 1))
                    Color(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, 0.6)
                    Rectangle(pos=(x + bx, y + by), size=(biome_size, biome_size))
        
        # Позиция игрока
        player_x = x + self.player.x * scale_x
        player_y = y + self.player.y * scale_y
        
        Color(0.2, 1, 0.3, 1)
        Ellipse(pos=(player_x - 4, player_y - 4), size=(8, 8))
        
        # Враги на мини-карте
        if self.game_manager:
            for enemy in self.game_manager.enemy_spawner.enemies:
                if enemy.alive:
                    ex = x + enemy.x * scale_x
                    ey = y + enemy.y * scale_y
                    
                    if enemy.is_boss:
                        Color(1, 0.2, 1, 1)
                        Ellipse(pos=(ex - 4, ey - 4), size=(8, 8))
                    else:
                        Color(1, 0.3, 0.3, 0.8)
                        Ellipse(pos=(ex - 2, ey - 2), size=(4, 4))
        
        # Рамка
        Color(1, 1, 1, 0.5)
        Line(rectangle=(x, y, size, size), width=1)
    
    def _draw_notifications(self, canvas):
        """Отрисовка уведомлений"""
        y_offset = self.height - 120
        
        for notification in self.notifications:
            Color(notification.color[0], notification.color[1],
                  notification.color[2], notification.alpha)
            
            self._draw_text(
                canvas,
                notification.text,
                self.width / 2,
                y_offset,
                font_size=20,
                anchor_x='center',
                color=(notification.color[0], notification.color[1],
                       notification.color[2], notification.alpha)
            )
            
            y_offset -= 30
    
    def _draw_biome_indicator(self, canvas):
        """Отрисовка индикатора текущего биома"""
        if not self.game_manager:
            return
        
        biome = self.game_manager.world.get_biome_at(self.player.x, self.player.y)
        
        # Названия биомов
        biome_names = {
            'fields': 'Зелёные поля',
            'dark_forest': 'Тёмный лес',
            'fire_lands': 'Огненные земли',
            'ice_wastes': 'Ледяные пустоши',
            'ruins': 'Руины',
        }
        
        biome_name = biome_names.get(biome, 'Неизвестно')
        color = BIOME_COLORS.get(biome, (1, 1, 1, 1))
        
        # Индикатор опасности - рамка вокруг экрана
        danger_colors = {
            'fields': (0.2, 0.8, 0.2, 0.3),
            'dark_forest': (0.5, 0.3, 0.5, 0.4),
            'fire_lands': (0.8, 0.3, 0.1, 0.4),
            'ice_wastes': (0.3, 0.5, 0.8, 0.4),
            'ruins': (0.8, 0.2, 0.2, 0.5),
        }
        
        danger_color = danger_colors.get(biome, (0.5, 0.5, 0.5, 0.3))
        
        # Рамка опасности
        Color(*danger_color)
        border = 5
        Line(rectangle=(border, border, self.width - border * 2, self.height - border * 2), width=border)
        
        # Название биома
        self._draw_text(
            canvas,
            biome_name,
            self.width / 2,
            30,
            font_size=16,
            anchor_x='center',
            color=color
        )
    
    def _draw_text(self, canvas, text, x, y, font_size=16, anchor_x='left', 
                   anchor_y='bottom', color=COLOR_TEXT):
        """Отрисовка текста"""
        # Создаём метку
        cache_key = f"{text}_{font_size}_{color}"
        
        if cache_key not in self.text_cache:
            label = CoreLabel(text=text, font_size=font_size)
            label.refresh()
            self.text_cache[cache_key] = label
            
            # Ограничиваем размер кэша
            if len(self.text_cache) > 100:
                # Удаляем старые записи
                keys = list(self.text_cache.keys())
                for key in keys[:50]:
                    del self.text_cache[key]
        
        label = self.text_cache[cache_key]
        texture = label.texture
        
        # Вычисляем позицию
        tex_width, tex_height = texture.size
        
        if anchor_x == 'center':
            x -= tex_width / 2
        elif anchor_x == 'right':
            x -= tex_width
        
        if anchor_y == 'center':
            y -= tex_height / 2
        elif anchor_y == 'top':
            y -= tex_height
        
        # Рисуем
        Color(*color)
        Rectangle(texture=texture, pos=(x, y), size=texture.size)
    
    def draw_entity_hp_bar(self, canvas, entity, screen_x, screen_y, camera):
        """Отрисовка HP бара над существом"""
        if not hasattr(entity, 'hp') or not hasattr(entity, 'max_hp'):
            return
        
        bar_width = entity.size * 1.2
        bar_height = 6
        x = screen_x - bar_width / 2
        y = screen_y + entity.size / 2 + 5
        
        hp_ratio = entity.hp / entity.max_hp
        
        # Фон
        Color(0.2, 0.2, 0.2, 0.8)
        Rectangle(pos=(x, y), size=(bar_width, bar_height))
        
        # Заполнение
        if hp_ratio > 0.5:
            Color(0.2, 0.8, 0.2, 1)
        elif hp_ratio > 0.25:
            Color(0.9, 0.7, 0.1, 1)
        else:
            Color(0.9, 0.2, 0.2, 1)
        
        Rectangle(pos=(x, y), size=(bar_width * hp_ratio, bar_height))


class AbilityBar(Widget):
    """Панель способностей"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = None
        self.slot_size = ABILITY_SLOT_SIZE
    
    def set_player(self, player):
        """Установка ссылки на игрока"""
        self.player = player
    
    def draw(self, canvas, controls_manager):
        """Отрисовка панели способностей"""
        if not self.player:
            return
        
        # Обновляем кнопки способностей
        for i in range(6):
            ability_info = self.player.ability_manager.get_ability_info(i)
            
            if ability_info:
                controls_manager.update_ability_button(i, ability_info)
                
                # Обновляем кулдаун на кнопке
                btn = controls_manager.ability_buttons[i]
                btn.set_cooldown(ability_info['cooldown_progress'])
            else:
                controls_manager.update_ability_button(i, None)