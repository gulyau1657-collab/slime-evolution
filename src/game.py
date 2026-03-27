"""
ОСНОВНОЙ ИГРОВОЙ ВИДЖЕТ
Объединяет все системы и управляет игровым циклом
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, PushMatrix, PopMatrix, Translate
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.app import App

from src.config import (
    TARGET_FPS, AUTOSAVE_INTERVAL, TILE_SIZE,
    WORLD_WIDTH, WORLD_HEIGHT
)
from src.game_manager import GameManager
from src.controls import ControlsManager
from src.ui import GameUI, AbilityBar
from src.utils import format_time


class GameWidget(Widget):
    """Основной виджет игры"""
    
    def __init__(self, new_game=True, **kwargs):
        super().__init__(**kwargs)
        
        # Размеры
        self.game_width = Window.width
        self.game_height = Window.height
        
        # Менеджер игры
        self.game_manager = GameManager(self.game_width, self.game_height)
        
        # Запускаем игру
        if new_game:
            self.game_manager.new_game()
        else:
            self.game_manager.load_game()
        
        # UI
        self.game_ui = GameUI()
        self.game_ui.set_player(self.game_manager.player)
        self.game_ui.set_game_manager(self.game_manager)
        
        self.ability_bar = AbilityBar()
        self.ability_bar.set_player(self.game_manager.player)
        
        # Управление
        self.controls = ControlsManager()
        self.add_widget(self.controls)
        
        # Настраиваем callbacks
        self.game_manager.on_notification = self.game_ui.add_notification
        self.game_manager.on_game_over = self._on_game_over
        self.game_manager.on_victory = self._on_victory
        
        # Настраиваем кнопки
        self.controls.attack_button.on_press_callback = self._on_attack
        self.controls.absorb_button.on_press_callback = self._on_absorb
        
        for i, btn in enumerate(self.controls.ability_buttons):
            btn.on_press_callback = lambda idx=i: self._on_ability(idx)
        
        # Автосохранение
        self.autosave_timer = 0
        
        # Запускаем игровой цикл
        self.update_event = Clock.schedule_interval(self.update, 1.0 / TARGET_FPS)
        
        # Привязываем размер
        self.bind(size=self._on_resize)
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_resize(self, instance, value):
        """Обработка изменения размера виджета"""
        self.game_width = self.width
        self.game_height = self.height
        
        self.game_ui.size = self.size
        self.game_ui.pos = self.pos
        
        self.ability_bar.size = self.size
        self.ability_bar.pos = self.pos
        
        self.controls.size = self.size
        self.controls.pos = self.pos
        
        self.game_manager.update_screen_size(self.width, self.height)
    
    def _on_window_resize(self, window, width, height):
        """Обработка изменения размера окна"""
        self.game_width = width
        self.game_height = height
        self.game_manager.update_screen_size(width, height)
    
    def update(self, dt):
        """Игровой цикл"""
        if self.game_manager.is_paused:
            return
        
        # Получаем ввод
        move_x, move_y = self.controls.get_movement()
        
        # Обновляем игрока
        self.game_manager.player.update(
            dt, move_x, move_y, self.game_manager
        )
        
        # Обновляем игру
        self.game_manager.update(dt)
        
        # Обновляем UI
        self.game_ui.update(dt)
        
        # Проверяем ближайшее тело для поглощения
        if self.game_manager.nearest_body:
            self.controls.show_absorb_button()
        else:
            self.controls.hide_absorb_button()
        
        # Автосохранение
        self.autosave_timer += dt
        if self.autosave_timer >= AUTOSAVE_INTERVAL:
            self.autosave_timer = 0
            self.game_manager.save_game()
        
        # Перерисовка
        self._draw()
    
    def _draw(self):
        """Отрисовка всего"""
        self.canvas.clear()
        
        camera = self.game_manager.camera
        player = self.game_manager.player
        world = self.game_manager.world
        
        with self.canvas:
            # ===== ФОН / ТАЙЛЫ =====
            visible_rect = camera.get_visible_rect(margin=TILE_SIZE)
            tiles = world.get_tiles_in_rect(*visible_rect)
            
            for tile in tiles:
                screen_x, screen_y = camera.world_to_screen(tile['x'], tile['y'])
                Color(*tile['color'])
                Rectangle(
                    pos=(screen_x, screen_y),
                    size=(TILE_SIZE + 1, TILE_SIZE + 1)  # +1 чтобы не было щелей
                )
            
            # ===== ПРЕПЯТСТВИЯ =====
            obstacles = world.get_obstacles_in_rect(*visible_rect)
            
            for obstacle in obstacles:
                screen_x, screen_y = camera.world_to_screen(obstacle.x, obstacle.y)
                
                Color(*obstacle.get_color())
                Ellipse(
                    pos=(screen_x - obstacle.collision_radius,
                         screen_y - obstacle.collision_radius),
                    size=(obstacle.collision_radius * 2, obstacle.collision_radius * 2)
                )
            
            # ===== ТЕЛА ВРАГОВ =====
            for body in self.game_manager.enemy_spawner.bodies:
                if not camera.is_visible(body.x, body.y, body.size, body.size):
                    continue
                
                screen_x, screen_y = camera.world_to_screen(body.x, body.y)
                
                # Полупрозрачное тело
                opacity = body.get_opacity()
                Color(body.color[0], body.color[1], body.color[2], opacity * 0.7)
                Ellipse(
                    pos=(screen_x - body.size / 2, screen_y - body.size / 2),
                    size=(body.size, body.size)
                )
            
            # ===== ВРАГИ =====
            for enemy in self.game_manager.enemy_spawner.enemies:
                if not enemy.alive:
                    continue
                
                if not camera.is_visible(enemy.x, enemy.y, enemy.size, enemy.size):
                    continue
                
                screen_x, screen_y = camera.world_to_screen(enemy.x, enemy.y)
                
                # Тело врага
                Color(*enemy.color)
                
                if enemy.texture:
                    Rectangle(
                        texture=enemy.texture,
                        pos=(screen_x - enemy.size / 2, screen_y - enemy.size / 2),
                        size=(enemy.size, enemy.size)
                    )
                else:
                    Ellipse(
                        pos=(screen_x - enemy.size / 2, screen_y - enemy.size / 2),
                        size=(enemy.size, enemy.size)
                    )
                
                # HP бар врага
                self.game_ui.draw_entity_hp_bar(
                    self.canvas, enemy, screen_x, screen_y, camera
                )
            
            # ===== СНАРЯДЫ =====
            for projectile in self.game_manager.projectiles:
                if not projectile.alive:
                    continue
                
                screen_x, screen_y = camera.world_to_screen(projectile.x, projectile.y)
                
                Color(*projectile.color)
                Ellipse(
                    pos=(screen_x - projectile.size / 2, screen_y - projectile.size / 2),
                    size=(projectile.size, projectile.size)
                )
            
            # ===== ИГРОК =====
            screen_x, screen_y = camera.world_to_screen(player.x, player.y)
            
            # Мигание при неуязвимости
            if player.invulnerable:
                import time
                if int(time.time() * 10) % 2 == 0:
                    Color(1, 1, 1, 0.5)
                else:
                    Color(1, 1, 1, 1)
            else:
                Color(1, 1, 1, 1)
            
            if player.texture:
                Rectangle(
                    texture=player.texture,
                    pos=(screen_x - player.size / 2, screen_y - player.size / 2),
                    size=(player.size, player.size)
                )
            else:
                # Заглушка - зелёный круг
                Color(0.2, 0.9, 0.3, 1)
                Ellipse(
                    pos=(screen_x - player.size / 2, screen_y - player.size / 2),
                    size=(player.size, player.size)
                )
            
            # ===== ЧАСТИЦЫ =====
            self.game_manager.particle_system.draw(self.canvas, camera)
        
        # ===== UI (поверх всего) =====
        self.game_ui.size = self.size
        self.game_ui.draw(self.canvas)
        
        # Обновляем панель способностей
        self.ability_bar.draw(self.canvas, self.controls)
    
    def _on_attack(self):
        """Обработка атаки"""
        # Атакуем в направлении взгляда
        target_x = self.game_manager.player.x + self.game_manager.player.facing_x * 100
        target_y = self.game_manager.player.y + self.game_manager.player.facing_y * 100
        
        self.game_manager.player.attack(target_x, target_y, self.game_manager)
    
    def _on_absorb(self):
        """Обработка поглощения"""
        self.game_manager.try_absorb()
    
    def _on_ability(self, index):
        """Обработка использования способности"""
        # Используем способность в направлении взгляда
        target_x = self.game_manager.player.x + self.game_manager.player.facing_x * 200
        target_y = self.game_manager.player.y + self.game_manager.player.facing_y * 200
        
        self.game_manager.player.use_ability(
            index, target_x, target_y, self.game_manager
        )
    
    def _on_game_over(self, stats):
        """Обработка поражения"""
        self.pause_game()
        
        app = App.get_running_app()
        if app:
            app.show_game_over(stats)
    
    def _on_victory(self, stats):
        """Обработка победы"""
        self.pause_game()
        
        # Удаляем сохранение (игра пройдена)
        self.game_manager.save_system.delete_save()
        
        app = App.get_running_app()
        if app:
            app.show_victory(stats)
    
    def pause_game(self):
        """Пауза игры"""
        self.game_manager.pause()
    
    def resume_game(self):
        """Продолжение игры"""
        self.game_manager.resume()
    
    def save_game(self):
        """Сохранение игры"""
        self.game_manager.save_game()
    
    def on_touch_down(self, touch):
        """Обработка касания"""
        # Сначала проверяем UI элементы
        if self.controls.on_touch_down(touch):
            return True
        
        # Касание на игровом поле - атакуем в эту точку
        if not self.game_manager.is_paused:
            # Преобразуем координаты касания в мировые
            world_x, world_y = self.game_manager.camera.screen_to_world(touch.x, touch.y)
            self.game_manager.player.attack(world_x, world_y, self.game_manager)
        
        return True
    
    def on_touch_move(self, touch):
        """Обработка движения касания"""
        return self.controls.on_touch_move(touch)
    
    def on_touch_up(self, touch):
        """Обработка отпускания"""
        return self.controls.on_touch_up(touch)
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.update_event:
            self.update_event.cancel()
        
        self.game_manager.save_game()