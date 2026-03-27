"""
SLIME EVOLUTION - Главный файл приложения
Мобильная 2D RPG игра на Kivy

Запуск: python main.py
Сборка APK: buildozer android debug
"""

import os
import sys

# Устанавливаем путь к папке src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.config import Config
# Конфигурация должна быть ДО импорта других модулей Kivy
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'resizable', True)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.text import LabelBase
from kivy.utils import platform

# Импортируем наши модули
from src.game import GameWidget
from src.config import *
from src.save_system import SaveSystem


class MainMenuScreen(Screen):
    """Главное меню игры"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """Создаём интерфейс главного меню"""
        layout = FloatLayout()
        
        # Фон
        with layout.canvas.before:
            Color(0.1, 0.15, 0.2, 1)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        
        # Привязываем обновление фона к размеру окна
        layout.bind(size=self._update_bg)
        
        # Заголовок игры
        title = Label(
            text='[b]SLIME EVOLUTION[/b]',
            markup=True,
            font_size='48sp',
            color=(0.2, 1, 0.4, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        )
        layout.add_widget(title)
        
        # Подзаголовок
        subtitle = Label(
            text='Поглощай. Эволюционируй. Побеждай.',
            font_size='18sp',
            color=(0.7, 0.7, 0.7, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.65}
        )
        layout.add_widget(subtitle)
        
        # Контейнер для кнопок
        button_layout = BoxLayout(
            orientation='vertical',
            size_hint=(0.4, 0.35),
            pos_hint={'center_x': 0.5, 'center_y': 0.35},
            spacing=15
        )
        
        # Кнопка "Новая игра"
        btn_new = Button(
            text='Новая игра',
            font_size='24sp',
            background_color=(0.2, 0.8, 0.3, 1),
            on_press=self.start_new_game
        )
        button_layout.add_widget(btn_new)
        
        # Кнопка "Продолжить" (если есть сохранение)
        self.btn_continue = Button(
            text='Продолжить',
            font_size='24sp',
            background_color=(0.3, 0.5, 0.8, 1),
            on_press=self.continue_game
        )
        button_layout.add_widget(self.btn_continue)
        
        # Кнопка "Выход"
        btn_exit = Button(
            text='Выход',
            font_size='24sp',
            background_color=(0.8, 0.3, 0.3, 1),
            on_press=self.exit_game
        )
        button_layout.add_widget(btn_exit)
        
        layout.add_widget(button_layout)
        
        # Версия игры
        version = Label(
            text='v1.0.0',
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1),
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )
        layout.add_widget(version)
        
        self.add_widget(layout)
        
        # Проверяем наличие сохранения
        self.check_save()
    
    def _update_bg(self, instance, value):
        """Обновляем размер фона при изменении окна"""
        self.bg_rect.size = instance.size
    
    def check_save(self):
        """Проверяем наличие сохранённой игры"""
        save_system = SaveSystem()
        if save_system.has_save():
            self.btn_continue.disabled = False
            self.btn_continue.opacity = 1
        else:
            self.btn_continue.disabled = True
            self.btn_continue.opacity = 0.5
    
    def start_new_game(self, instance):
        """Начинаем новую игру"""
        app = App.get_running_app()
        app.start_game(new_game=True)
    
    def continue_game(self, instance):
        """Продолжаем сохранённую игру"""
        app = App.get_running_app()
        app.start_game(new_game=False)
    
    def exit_game(self, instance):
        """Выходим из игры"""
        App.get_running_app().stop()


class GameScreen(Screen):
    """Экран с самой игрой"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_widget = None
    
    def on_enter(self):
        """Вызывается при переходе на этот экран"""
        pass
    
    def start_game(self, new_game=True):
        """Запускаем игру"""
        # Удаляем старый виджет игры, если есть
        if self.game_widget:
            self.remove_widget(self.game_widget)
        
        # Создаём новый виджет игры
        self.game_widget = GameWidget(new_game=new_game)
        self.add_widget(self.game_widget)
    
    def on_leave(self):
        """Вызывается при уходе с этого экрана"""
        if self.game_widget:
            self.game_widget.pause_game()


class PauseScreen(Screen):
    """Экран паузы"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """Создаём интерфейс паузы"""
        layout = FloatLayout()
        
        # Полупрозрачный фон
        with layout.canvas.before:
            Color(0, 0, 0, 0.7)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        
        layout.bind(size=self._update_bg)
        
        # Заголовок
        title = Label(
            text='ПАУЗА',
            font_size='42sp',
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.7}
        )
        layout.add_widget(title)
        
        # Кнопки
        button_layout = BoxLayout(
            orientation='vertical',
            size_hint=(0.35, 0.3),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            spacing=15
        )
        
        btn_resume = Button(
            text='Продолжить',
            font_size='22sp',
            background_color=(0.2, 0.8, 0.3, 1),
            on_press=self.resume_game
        )
        button_layout.add_widget(btn_resume)
        
        btn_save = Button(
            text='Сохранить',
            font_size='22sp',
            background_color=(0.3, 0.5, 0.8, 1),
            on_press=self.save_game
        )
        button_layout.add_widget(btn_save)
        
        btn_menu = Button(
            text='В главное меню',
            font_size='22sp',
            background_color=(0.8, 0.3, 0.3, 1),
            on_press=self.goto_menu
        )
        button_layout.add_widget(btn_menu)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
    
    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
    
    def resume_game(self, instance):
        """Возвращаемся в игру"""
        app = App.get_running_app()
        app.sm.current = 'game'
        app.sm.get_screen('game').game_widget.resume_game()
    
    def save_game(self, instance):
        """Сохраняем игру"""
        app = App.get_running_app()
        game_screen = app.sm.get_screen('game')
        if game_screen.game_widget:
            game_screen.game_widget.save_game()
            # Показываем уведомление
            instance.text = 'Сохранено!'
            Clock.schedule_once(lambda dt: setattr(instance, 'text', 'Сохранить'), 1.5)
    
    def goto_menu(self, instance):
        """Переходим в главное меню"""
        app = App.get_running_app()
        # Сохраняем перед выходом
        game_screen = app.sm.get_screen('game')
        if game_screen.game_widget:
            game_screen.game_widget.save_game()
        app.sm.current = 'menu'


class GameOverScreen(Screen):
    """Экран поражения"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stats = {}
        self.build_ui()
    
    def build_ui(self):
        """Создаём интерфейс Game Over"""
        self.layout = FloatLayout()
        
        with self.layout.canvas.before:
            Color(0.15, 0.05, 0.05, 1)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        
        self.layout.bind(size=self._update_bg)
        
        # Заголовок
        title = Label(
            text='[b]GAME OVER[/b]',
            markup=True,
            font_size='48sp',
            color=(0.9, 0.2, 0.2, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.8}
        )
        self.layout.add_widget(title)
        
        # Статистика (будет обновляться)
        self.stats_label = Label(
            text='',
            font_size='18sp',
            color=(0.8, 0.8, 0.8, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            halign='center'
        )
        self.layout.add_widget(self.stats_label)
        
        # Кнопка "Заново"
        btn_retry = Button(
            text='Начать заново',
            font_size='24sp',
            size_hint=(0.35, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            background_color=(0.3, 0.6, 0.3, 1),
            on_press=self.retry
        )
        self.layout.add_widget(btn_retry)
        
        self.add_widget(self.layout)
    
    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
    
    def set_stats(self, stats):
        """Устанавливаем статистику игры"""
        self.stats = stats
        text = f"""
Время игры: {stats.get('time', '0:00')}

Поглощено существ: {stats.get('absorptions', 0)}

Убито врагов: {stats.get('kills', 0)}

Полученные способности: {stats.get('abilities_count', 0)}

Максимальное HP: {stats.get('max_hp', 100)}
"""
        self.stats_label.text = text
    
    def retry(self, instance):
        """Начинаем игру заново"""
        app = App.get_running_app()
        app.start_game(new_game=True)


class VictoryScreen(Screen):
    """Экран победы"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stats = {}
        self.build_ui()
    
    def build_ui(self):
        """Создаём интерфейс победы"""
        self.layout = FloatLayout()
        
        with self.layout.canvas.before:
            Color(0.1, 0.15, 0.1, 1)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        
        self.layout.bind(size=self._update_bg)
        
        # Заголовок
        title = Label(
            text='[b]ПОБЕДА![/b]',
            markup=True,
            font_size='52sp',
            color=(0.2, 1, 0.3, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.85}
        )
        self.layout.add_widget(title)
        
        subtitle = Label(
            text='Хранитель Руин повержен!',
            font_size='22sp',
            color=(0.8, 0.9, 0.8, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        )
        self.layout.add_widget(subtitle)
        
        # Статистика
        self.stats_label = Label(
            text='',
            font_size='18sp',
            color=(0.8, 0.8, 0.8, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            halign='center'
        )
        self.layout.add_widget(self.stats_label)
        
        # Кнопка "Играть снова"
        btn_play = Button(
            text='Играть снова',
            font_size='24sp',
            size_hint=(0.35, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.15},
            background_color=(0.3, 0.7, 0.3, 1),
            on_press=self.play_again
        )
        self.layout.add_widget(btn_play)
        
        self.add_widget(self.layout)
    
    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
    
    def set_stats(self, stats):
        """Устанавливаем финальную статистику"""
        self.stats = stats
        text = f"""
╔══════════════════════════════╗
║     ФИНАЛЬНАЯ СТАТИСТИКА     ║
╠══════════════════════════════╣
║  Время прохождения: {stats.get('time', '0:00'):>8} ║
║  Поглощено существ: {stats.get('absorptions', 0):>8} ║
║  Всего убито: {stats.get('kills', 0):>14} ║
║  Способностей: {stats.get('abilities_count', 0):>13} ║
║  Финальное HP: {stats.get('max_hp', 100):>13} ║
║  Финальный урон: {stats.get('damage', 10):>11} ║
╚══════════════════════════════╝
"""
        self.stats_label.text = text
    
    def play_again(self, instance):
        """Начинаем новую игру"""
        app = App.get_running_app()
        app.start_game(new_game=True)


class SlimeEvolutionApp(App):
    """Главный класс приложения"""
    
    def build(self):
        """Создаём приложение"""
        self.title = 'Slime Evolution'
        
        # Создаём менеджер экранов
        self.sm = ScreenManager(transition=FadeTransition())
        
        # Добавляем экраны
        self.sm.add_widget(MainMenuScreen(name='menu'))
        self.sm.add_widget(GameScreen(name='game'))
        self.sm.add_widget(PauseScreen(name='pause'))
        self.sm.add_widget(GameOverScreen(name='gameover'))
        self.sm.add_widget(VictoryScreen(name='victory'))
        
        # Обработка кнопки "Назад" на Android
        Window.bind(on_keyboard=self.on_keyboard)
        
        return self.sm
    
    def on_keyboard(self, window, key, *args):
        """Обработка нажатий клавиш"""
        # Esc или кнопка "Назад" на Android
        if key == 27:
            current = self.sm.current
            if current == 'game':
                # Ставим паузу
                game_screen = self.sm.get_screen('game')
                if game_screen.game_widget:
                    game_screen.game_widget.pause_game()
                self.sm.current = 'pause'
                return True
            elif current == 'pause':
                # Снимаем паузу
                self.sm.current = 'game'
                game_screen = self.sm.get_screen('game')
                if game_screen.game_widget:
                    game_screen.game_widget.resume_game()
                return True
            elif current in ['gameover', 'victory']:
                self.sm.current = 'menu'
                return True
        return False
    
    def start_game(self, new_game=True):
        """Запускаем игру"""
        self.sm.current = 'game'
        game_screen = self.sm.get_screen('game')
        game_screen.start_game(new_game=new_game)
    
    def show_game_over(self, stats):
        """Показываем экран поражения"""
        screen = self.sm.get_screen('gameover')
        screen.set_stats(stats)
        self.sm.current = 'gameover'
    
    def show_victory(self, stats):
        """Показываем экран победы"""
        screen = self.sm.get_screen('victory')
        screen.set_stats(stats)
        self.sm.current = 'victory'
    
    def show_pause(self):
        """Показываем паузу"""
        self.sm.current = 'pause'


# Точка входа
if __name__ == '__main__':
    SlimeEvolutionApp().run()