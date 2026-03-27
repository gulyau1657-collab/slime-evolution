"""
СИСТЕМА УПРАВЛЕНИЯ
Виртуальный джойстик и кнопки для мобильных устройств
"""

import math
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.properties import NumericProperty, BooleanProperty
from src.config import JOYSTICK_SIZE, JOYSTICK_DEAD_ZONE, ACTION_BUTTON_SIZE


class VirtualJoystick(Widget):
    """Виртуальный джойстик для управления движением"""
    
    # Значения направления (-1 до 1)
    direction_x = NumericProperty(0)
    direction_y = NumericProperty(0)
    is_active = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.size_hint = (None, None)
        self.size = (JOYSTICK_SIZE, JOYSTICK_SIZE)
        
        # Позиция центра джойстика
        self.center_x_pos = 0
        self.center_y_pos = 0
        
        # Позиция стика
        self.stick_x = 0
        self.stick_y = 0
        
        # ID касания (для мультитача)
        self.touch_id = None
        
        # Радиусы
        self.outer_radius = JOYSTICK_SIZE / 2
        self.inner_radius = JOYSTICK_SIZE / 4
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.draw_joystick()
    
    def draw_joystick(self):
        """Отрисовка джойстика"""
        self.canvas.clear()
        
        with self.canvas:
            # Внешний круг (фон)
            Color(0.3, 0.3, 0.3, 0.5)
            self.outer_circle = Ellipse(
                pos=(self.x, self.y),
                size=(JOYSTICK_SIZE, JOYSTICK_SIZE)
            )
            
            # Внутренний круг (стик)
            Color(0.6, 0.6, 0.6, 0.8)
            stick_size = self.inner_radius * 2
            self.inner_circle = Ellipse(
                pos=(self.center_x - self.inner_radius,
                     self.center_y - self.inner_radius),
                size=(stick_size, stick_size)
            )
    
    def update_graphics(self, *args):
        """Обновление графики при изменении позиции/размера"""
        self.center_x_pos = self.x + self.width / 2
        self.center_y_pos = self.y + self.height / 2
        
        if hasattr(self, 'outer_circle'):
            self.outer_circle.pos = (self.x, self.y)
            self.update_stick_position(self.center_x_pos, self.center_y_pos)
    
    def update_stick_position(self, touch_x, touch_y):
        """Обновление позиции стика"""
        dx = touch_x - self.center_x_pos
        dy = touch_y - self.center_y_pos
        
        # Расстояние от центра
        distance = math.sqrt(dx * dx + dy * dy)
        max_distance = self.outer_radius - self.inner_radius
        
        if distance > max_distance:
            # Ограничиваем радиусом
            scale = max_distance / distance
            dx *= scale
            dy *= scale
        
        self.stick_x = self.center_x_pos + dx
        self.stick_y = self.center_y_pos + dy
        
        if hasattr(self, 'inner_circle'):
            self.inner_circle.pos = (
                self.stick_x - self.inner_radius,
                self.stick_y - self.inner_radius
            )
        
        # Вычисляем направление
        if distance > JOYSTICK_DEAD_ZONE * self.outer_radius:
            norm_distance = min(distance, max_distance) / max_distance
            self.direction_x = (dx / max_distance) * norm_distance
            self.direction_y = (dy / max_distance) * norm_distance
        else:
            self.direction_x = 0
            self.direction_y = 0
    
    def on_touch_down(self, touch):
        """Обработка нажатия"""
        if self.collide_point(*touch.pos):
            self.touch_id = touch.uid
            self.is_active = True
            self.update_stick_position(touch.x, touch.y)
            return True
        return False
    
    def on_touch_move(self, touch):
        """Обработка движения"""
        if touch.uid == self.touch_id:
            self.update_stick_position(touch.x, touch.y)
            return True
        return False
    
    def on_touch_up(self, touch):
        """Обработка отпускания"""
        if touch.uid == self.touch_id:
            self.touch_id = None
            self.is_active = False
            self.direction_x = 0
            self.direction_y = 0
            self.update_stick_position(self.center_x_pos, self.center_y_pos)
            return True
        return False


class ActionButton(Widget):
    """Кнопка действия (атака, способность)"""
    
    is_pressed = BooleanProperty(False)
    is_ready = BooleanProperty(True)  # Готова ли способность
    cooldown_progress = NumericProperty(1.0)  # 1.0 = готово, 0.0 = на перезарядке
    
    def __init__(self, text='', color=(0.5, 0.5, 0.8, 0.8), **kwargs):
        super().__init__(**kwargs)
        
        self.text = text
        self.button_color = color
        self.size_hint = (None, None)
        self.size = (ACTION_BUTTON_SIZE, ACTION_BUTTON_SIZE)
        self.touch_id = None
        
        # Callback при нажатии
        self.on_press_callback = None
        
        self.bind(pos=self.draw_button, size=self.draw_button)
        self.draw_button()
    
    def draw_button(self, *args):
        """Отрисовка кнопки"""
        self.canvas.clear()
        
        with self.canvas:
            # Фон кнопки
            if self.is_pressed:
                Color(self.button_color[0] * 0.7,
                      self.button_color[1] * 0.7,
                      self.button_color[2] * 0.7,
                      self.button_color[3])
            else:
                Color(*self.button_color)
            
            Ellipse(pos=self.pos, size=self.size)
            
            # Затемнение при перезарядке
            if not self.is_ready:
                Color(0.2, 0.2, 0.2, 0.7)
                # Рисуем сектор перезарядки
                angle = 360 * (1 - self.cooldown_progress)
                if angle > 0:
                    Ellipse(
                        pos=self.pos,
                        size=self.size,
                        angle_start=90,
                        angle_end=90 + angle
                    )
            
            # Рамка
            Color(1, 1, 1, 0.5)
            Line(ellipse=(self.x, self.y, self.width, self.height), width=2)
    
    def on_touch_down(self, touch):
        """Обработка нажатия"""
        if self.collide_point(*touch.pos) and self.is_ready:
            self.touch_id = touch.uid
            self.is_pressed = True
            self.draw_button()
            
            if self.on_press_callback:
                self.on_press_callback()
            
            return True
        return False
    
    def on_touch_up(self, touch):
        """Обработка отпускания"""
        if touch.uid == self.touch_id:
            self.touch_id = None
            self.is_pressed = False
            self.draw_button()
            return True
        return False
    
    def set_cooldown(self, progress):
        """Установка прогресса перезарядки (0-1)"""
        self.cooldown_progress = progress
        self.is_ready = progress >= 1.0
        self.draw_button()


class AttackButton(ActionButton):
    """Специальная кнопка атаки"""
    
    def __init__(self, **kwargs):
        super().__init__(
            text='ATK',
            color=(0.8, 0.3, 0.3, 0.8),
            **kwargs
        )


class AbilityButton(ActionButton):
    """Кнопка способности"""
    
    def __init__(self, ability_name='', ability_color=(0.3, 0.5, 0.8, 0.8), **kwargs):
        super().__init__(
            text=ability_name[:3] if ability_name else '',
            color=ability_color,
            **kwargs
        )
        self.ability_name = ability_name


class AbsorbButton(ActionButton):
    """Кнопка поглощения"""
    
    def __init__(self, **kwargs):
        super().__init__(
            text='E',
            color=(0.2, 0.8, 0.4, 0.8),
            **kwargs
        )
        self.is_visible = False
    
    def show(self):
        """Показать кнопку"""
        self.is_visible = True
        self.opacity = 1
    
    def hide(self):
        """Скрыть кнопку"""
        self.is_visible = False
        self.opacity = 0


class ControlsManager(Widget):
    """Менеджер всех элементов управления"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Виртуальный джойстик (слева внизу)
        self.joystick = VirtualJoystick()
        self.add_widget(self.joystick)
        
        # Кнопка атаки (справа внизу)
        self.attack_button = AttackButton()
        self.add_widget(self.attack_button)
        
        # Кнопка поглощения (над кнопкой атаки)
        self.absorb_button = AbsorbButton()
        self.absorb_button.opacity = 0
        self.add_widget(self.absorb_button)
        
        # Кнопки способностей (справа, в столбик)
        self.ability_buttons = []
        for i in range(6):
            btn = AbilityButton()
            btn.opacity = 0  # Изначально скрыты
            self.ability_buttons.append(btn)
            self.add_widget(btn)
        
        self.bind(size=self.update_positions, pos=self.update_positions)
    
    def update_positions(self, *args):
        """Обновление позиций элементов управления"""
        padding = 20
        
        # Джойстик (слева внизу)
        self.joystick.pos = (padding, padding)
        
        # Кнопка атаки (справа внизу)
        self.attack_button.pos = (
            self.width - ACTION_BUTTON_SIZE - padding,
            padding
        )
        
        # Кнопка поглощения (над атакой)
        self.absorb_button.pos = (
            self.width - ACTION_BUTTON_SIZE - padding,
            padding + ACTION_BUTTON_SIZE + 15
        )
        
        # Кнопки способностей (справа, выше кнопки атаки)
        ability_start_y = padding + ACTION_BUTTON_SIZE * 2 + 30
        for i, btn in enumerate(self.ability_buttons):
            row = i // 2
            col = i % 2
            btn.pos = (
                self.width - ACTION_BUTTON_SIZE * (2 - col) - padding - col * 10,
                ability_start_y + row * (ACTION_BUTTON_SIZE + 10)
            )
    
    def get_movement(self):
        """Получить направление движения"""
        return self.joystick.direction_x, self.joystick.direction_y
    
    def is_attacking(self):
        """Проверка, нажата ли кнопка атаки"""
        return self.attack_button.is_pressed
    
    def update_ability_button(self, index, ability_data=None):
        """Обновить кнопку способности"""
        if 0 <= index < len(self.ability_buttons):
            btn = self.ability_buttons[index]
            if ability_data:
                btn.ability_name = ability_data.get('name', '')
                btn.button_color = ability_data.get('icon_color', (0.5, 0.5, 0.5, 0.8))
                btn.opacity = 1
                btn.draw_button()
            else:
                btn.opacity = 0
    
    def show_absorb_button(self):
        """Показать кнопку поглощения"""
        self.absorb_button.show()
    
    def hide_absorb_button(self):
        """Скрыть кнопку поглощения"""
        self.absorb_button.hide()