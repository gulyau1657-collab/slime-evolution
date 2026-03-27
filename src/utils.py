"""
ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
Математика, загрузка ресурсов, генерация заглушек
"""

import math
import random
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage
import os


def distance(x1, y1, x2, y2):
    """Расстояние между двумя точками"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distance_squared(x1, y1, x2, y2):
    """Квадрат расстояния (быстрее, без sqrt)"""
    return (x2 - x1) ** 2 + (y2 - y1) ** 2


def normalize(x, y):
    """Нормализация вектора"""
    length = math.sqrt(x * x + y * y)
    if length == 0:
        return 0, 0
    return x / length, y / length


def angle_to(x1, y1, x2, y2):
    """Угол от точки 1 к точке 2 в радианах"""
    return math.atan2(y2 - y1, x2 - x1)


def direction_to(x1, y1, x2, y2):
    """Нормализованное направление от точки 1 к точке 2"""
    dx = x2 - x1
    dy = y2 - y1
    return normalize(dx, dy)


def clamp(value, min_val, max_val):
    """Ограничение значения в диапазоне"""
    return max(min_val, min(max_val, value))


def lerp(a, b, t):
    """Линейная интерполяция"""
    return a + (b - a) * t


def random_point_in_circle(cx, cy, radius):
    """Случайная точка внутри круга"""
    angle = random.uniform(0, 2 * math.pi)
    r = radius * math.sqrt(random.random())
    return cx + r * math.cos(angle), cy + r * math.sin(angle)


def random_point_on_circle(cx, cy, radius):
    """Случайная точка на окружности"""
    angle = random.uniform(0, 2 * math.pi)
    return cx + radius * math.cos(angle), cy + radius * math.sin(angle)


def circles_collide(x1, y1, r1, x2, y2, r2):
    """Проверка столкновения двух кругов"""
    return distance_squared(x1, y1, x2, y2) < (r1 + r2) ** 2


def point_in_rect(px, py, rx, ry, rw, rh):
    """Точка внутри прямоугольника"""
    return rx <= px <= rx + rw and ry <= py <= ry + rh


def rects_collide(x1, y1, w1, h1, x2, y2, w2, h2):
    """Проверка столкновения двух прямоугольников"""
    return (x1 < x2 + w2 and x1 + w1 > x2 and 
            y1 < y2 + h2 and y1 + h1 > y2)


def format_time(seconds):
    """Форматирование времени в MM:SS"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def generate_color_texture(width, height, color):
    """
    Генерация текстуры заливки одним цветом
    color: кортеж (r, g, b, a) со значениями 0-1
    """
    # Преобразуем цвет в байты
    r = int(color[0] * 255)
    g = int(color[1] * 255)
    b = int(color[2] * 255)
    a = int(color[3] * 255) if len(color) > 3 else 255
    
    # Создаём данные пикселей
    size = width * height * 4
    buf = bytes([r, g, b, a] * (width * height))
    
    # Создаём текстуру
    texture = Texture.create(size=(width, height), colorfmt='rgba')
    texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
    
    return texture


def generate_circle_texture(size, color, border_color=None, border_width=2):
    """
    Генерация текстуры круга (для слайма и врагов)
    """
    from array import array
    
    center = size // 2
    radius = center - 2
    inner_radius = radius - border_width if border_color else radius
    
    # Создаём массив пикселей
    pixels = []
    
    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist <= inner_radius:
                # Внутренняя часть
                r = int(color[0] * 255)
                g = int(color[1] * 255)
                b = int(color[2] * 255)
                a = int(color[3] * 255) if len(color) > 3 else 255
            elif dist <= radius and border_color:
                # Граница
                r = int(border_color[0] * 255)
                g = int(border_color[1] * 255)
                b = int(border_color[2] * 255)
                a = int(border_color[3] * 255) if len(border_color) > 3 else 255
            else:
                # Прозрачный фон
                r, g, b, a = 0, 0, 0, 0
            
            pixels.extend([r, g, b, a])
    
    # Создаём текстуру
    texture = Texture.create(size=(size, size), colorfmt='rgba')
    texture.blit_buffer(bytes(pixels), colorfmt='rgba', bufferfmt='ubyte')
    texture.flip_vertical()
    
    return texture


def generate_slime_texture(size, base_color, layers=None):
    """
    Генерация текстуры слайма с возможными слоями поглощённых врагов
    layers: список кортежей (color, opacity) для каждого слоя
    """
    from array import array
    
    center = size // 2
    radius = center - 2
    
    # Базовые пиксели
    pixels = [[0, 0, 0, 0] for _ in range(size * size)]
    
    # Рисуем базовый круг слайма
    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist <= radius:
                # Градиент для объёма
                gradient = 1.0 - (dist / radius) * 0.3
                
                idx = y * size + x
                pixels[idx][0] = int(base_color[0] * 255 * gradient)
                pixels[idx][1] = int(base_color[1] * 255 * gradient)
                pixels[idx][2] = int(base_color[2] * 255 * gradient)
                pixels[idx][3] = int(base_color[3] * 255) if len(base_color) > 3 else 255
    
    # Добавляем слои поглощённых врагов
    if layers:
        for layer_color, layer_opacity in layers:
            for y in range(size):
                for x in range(size):
                    idx = y * size + x
                    if pixels[idx][3] > 0:  # Только внутри слайма
                        # Смешиваем цвета
                        for c in range(3):
                            old_val = pixels[idx][c] / 255.0
                            new_val = layer_color[c]
                            pixels[idx][c] = int((old_val * (1 - layer_opacity) + 
                                                  new_val * layer_opacity) * 255)
    
    # Добавляем глаза слайма
    eye_offset = size // 5
    eye_size = size // 8
    for eye_x in [center - eye_offset, center + eye_offset]:
        eye_y = center + size // 8
        for dy in range(-eye_size, eye_size + 1):
            for dx in range(-eye_size, eye_size + 1):
                if dx * dx + dy * dy <= eye_size * eye_size:
                    px, py = eye_x + dx, eye_y + dy
                    if 0 <= px < size and 0 <= py < size:
                        idx = py * size + px
                        # Белок
                        pixels[idx] = [255, 255, 255, 255]
        # Зрачок
        pupil_size = eye_size // 2
        for dy in range(-pupil_size, pupil_size + 1):
            for dx in range(-pupil_size, pupil_size + 1):
                if dx * dx + dy * dy <= pupil_size * pupil_size:
                    px, py = eye_x + dx, eye_y + dy
                    if 0 <= px < size and 0 <= py < size:
                        idx = py * size + px
                        pixels[idx] = [0, 0, 0, 255]
    
    # Конвертируем в байты
    flat_pixels = []
    for p in pixels:
        flat_pixels.extend(p)
    
    texture = Texture.create(size=(size, size), colorfmt='rgba')
    texture.blit_buffer(bytes(flat_pixels), colorfmt='rgba', bufferfmt='ubyte')
    texture.flip_vertical()
    
    return texture


def generate_enemy_texture(size, color, enemy_type):
    """
    Генерация текстуры врага в зависимости от типа
    """
    from array import array
    
    center = size // 2
    pixels = [[0, 0, 0, 0] for _ in range(size * size)]
    
    if enemy_type in ['herbivore_slime']:
        # Простой круг с глазами (как слайм)
        return generate_slime_texture(size, color)
    
    elif enemy_type in ['skeleton_warrior']:
        # Скелет - белая фигура с "костями"
        _draw_humanoid_shape(pixels, size, color)
        
    elif enemy_type in ['fire_elemental', 'lava_golem']:
        # Огненные существа - с "пламенем"
        _draw_flame_shape(pixels, size, color)
        
    elif enemy_type in ['ice_mage']:
        # Маг - фигура в мантии
        _draw_mage_shape(pixels, size, color)
        
    elif enemy_type in ['shadow_assassin']:
        # Теневой убийца - тёмный силуэт
        _draw_shadow_shape(pixels, size, color)
        
    elif enemy_type in ['stone_golem']:
        # Голем - угловатая фигура
        _draw_golem_shape(pixels, size, color)
        
    elif enemy_type in ['spider']:
        # Паук - 8 ног
        _draw_spider_shape(pixels, size, color)
        
    elif enemy_type in ['snow_wolf']:
        # Волк - четвероногое
        _draw_wolf_shape(pixels, size, color)
        
    elif enemy_type in ['elite_guard', 'ruins_keeper']:
        # Элита/босс - большая фигура с аурой
        _draw_elite_shape(pixels, size, color)
        
    else:
        # По умолчанию - простой круг
        radius = center - 2
        for y in range(size):
            for x in range(size):
                dx = x - center
                dy = y - center
                if dx * dx + dy * dy <= radius * radius:
                    idx = y * size + x
                    pixels[idx] = [int(color[0]*255), int(color[1]*255), 
                                   int(color[2]*255), 255]
    
    # Конвертируем в байты
    flat_pixels = []
    for p in pixels:
        flat_pixels.extend(p)
    
    texture = Texture.create(size=(size, size), colorfmt='rgba')
    texture.blit_buffer(bytes(flat_pixels), colorfmt='rgba', bufferfmt='ubyte')
    texture.flip_vertical()
    
    return texture


def _draw_humanoid_shape(pixels, size, color):
    """Рисуем гуманоидную форму (скелет)"""
    center = size // 2
    
    # Голова
    head_radius = size // 6
    head_y = center + size // 4
    for dy in range(-head_radius, head_radius + 1):
        for dx in range(-head_radius, head_radius + 1):
            if dx * dx + dy * dy <= head_radius * head_radius:
                px, py = center + dx, head_y + dy
                if 0 <= px < size and 0 <= py < size:
                    idx = py * size + px
                    pixels[idx] = [int(color[0]*255), int(color[1]*255), 
                                   int(color[2]*255), 255]
    
    # Тело
    body_width = size // 4
    body_height = size // 3
    body_y = center - size // 8
    for dy in range(body_height):
        for dx in range(-body_width // 2, body_width // 2 + 1):
            px, py = center + dx, body_y + dy
            if 0 <= px < size and 0 <= py < size:
                idx = py * size + px
                pixels[idx] = [int(color[0]*255), int(color[1]*255), 
                               int(color[2]*255), 255]
    
    # Глаза (тёмные впадины)
    eye_offset = size // 10
    for eye_x in [center - eye_offset, center + eye_offset]:
        eye_y = head_y
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                px, py = eye_x + dx, eye_y + dy
                if 0 <= px < size and 0 <= py < size:
                    idx = py * size + px
                    pixels[idx] = [30, 30, 30, 255]


def _draw_flame_shape(pixels, size, color):
    """Рисуем огненную форму"""
    center = size // 2
    radius = center - 4
    
    # Основное тело
    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            # Немного деформируем для эффекта пламени
            dist = math.sqrt(dx * dx + dy * dy * 0.7)
            if dist <= radius:
                idx = y * size + x
                # Градиент от центра
                intensity = 1.0 - (dist / radius) * 0.5
                r = int(min(255, color[0] * 255 * intensity + 50))
                g = int(color[1] * 255 * intensity)
                b = int(color[2] * 255 * intensity * 0.5)
                pixels[idx] = [r, g, b, 255]
    
    # Языки пламени сверху
    for i in range(3):
        flame_x = center + (i - 1) * (size // 5)
        for y_off in range(size // 4):
            y = center + radius - y_off
            x = flame_x + random.randint(-2, 2)
            if 0 <= x < size and 0 <= y < size:
                idx = y * size + x
                pixels[idx] = [255, int(200 - y_off * 10), 0, 255]


def _draw_mage_shape(pixels, size, color):
    """Рисуем фигуру мага"""
    center = size // 2
    
    # Мантия (треугольник)
    robe_height = int(size * 0.7)
    robe_top = center + size // 4
    for y in range(robe_height):
        actual_y = robe_top - y
        width = int((y / robe_height) * (size * 0.6))
        for dx in range(-width // 2, width // 2 + 1):
            px = center + dx
            if 0 <= px < size and 0 <= actual_y < size:
                idx = actual_y * size + px
                pixels[idx] = [int(color[0]*255), int(color[1]*255), 
                               int(color[2]*255), 255]
    
    # Голова (капюшон)
    head_radius = size // 6
    head_y = robe_top + head_radius // 2
    for dy in range(-head_radius, head_radius + 1):
        for dx in range(-head_radius, head_radius + 1):
            if dx * dx + dy * dy <= head_radius * head_radius:
                px, py = center + dx, head_y + dy
                if 0 <= px < size and 0 <= py < size:
                    idx = py * size + px
                    # Немного темнее для капюшона
                    pixels[idx] = [int(color[0]*200), int(color[1]*200), 
                                   int(color[2]*200), 255]
    
    # Глаза (светящиеся)
    eye_y = head_y - 2
    for eye_x in [center - 4, center + 4]:
        for dy in range(-2, 2):
            for dx in range(-1, 2):
                px, py = eye_x + dx, eye_y + dy
                if 0 <= px < size and 0 <= py < size:
                    idx = py * size + px
                    pixels[idx] = [200, 220, 255, 255]


def _draw_shadow_shape(pixels, size, color):
    """Рисуем теневую фигуру"""
    center = size // 2
    
    # Размытая тёмная фигура
    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            dist = math.sqrt(dx * dx + dy * dy)
            radius = center - 2
            
            if dist <= radius:
                # Тень с неровными краями
                noise = random.random() * 0.3
                alpha = int((1.0 - dist / radius + noise) * 200)
                alpha = max(0, min(255, alpha))
                idx = y * size + x
                pixels[idx] = [int(color[0]*255), int(color[1]*255), 
                               int(color[2]*255), alpha]
    
    # Красные глаза
    eye_y = center + 5
    for eye_x in [center - 5, center + 5]:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if dx * dx + dy * dy <= 4:
                    px, py = eye_x + dx, eye_y + dy
                    if 0 <= px < size and 0 <= py < size:
                        idx = py * size + px
                        pixels[idx] = [255, 0, 0, 255]


def _draw_golem_shape(pixels, size, color):
    """Рисуем фигуру голема"""
    center = size // 2
    
    # Массивное квадратное тело
    body_size = int(size * 0.7)
    start = (size - body_size) // 2
    
    for y in range(body_size):
        for x in range(body_size):
            px = start + x
            py = start + y
            if 0 <= px < size and 0 <= py < size:
                idx = py * size + px
                # Добавляем текстуру камня
                brightness = 0.8 + random.random() * 0.2
                pixels[idx] = [int(color[0]*255*brightness), 
                               int(color[1]*255*brightness), 
                               int(color[2]*255*brightness), 255]
    
    # Глаза (жёлтые)
    eye_y = center + body_size // 4
    for eye_x in [center - body_size // 5, center + body_size // 5]:
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                px, py = eye_x + dx, eye_y + dy
                if 0 <= px < size and 0 <= py < size:
                    idx = py * size + px
                    pixels[idx] = [255, 200, 0, 255]


def _draw_spider_shape(pixels, size, color):
    """Рисуем паука"""
    center = size // 2
    body_radius = size // 5
    
    # Тело
    for dy in range(-body_radius, body_radius + 1):
        for dx in range(-body_radius, body_radius + 1):
            if dx * dx + dy * dy <= body_radius * body_radius:
                px, py = center + dx, center + dy
                if 0 <= px < size and 0 <= py < size:
                    idx = py * size + px
                    pixels[idx] = [int(color[0]*255), int(color[1]*255), 
                                   int(color[2]*255), 255]
    
    # 8 ног
    leg_length = size // 3
    for i in range(8):
        angle = (i / 8) * 2 * math.pi
        for dist in range(body_radius, body_radius + leg_length):
            x = int(center + math.cos(angle) * dist)
            y = int(center + math.sin(angle) * dist)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    px, py = x + dx, y + dy
                    if 0 <= px < size and 0 <= py < size:
                        idx = py * size + px
                        pixels[idx] = [int(color[0]*200), int(color[1]*200), 
                                       int(color[2]*200), 255]
    
    # Красные глаза
    for eye_x in [center - 3, center + 3]:
        eye_y = center + 3
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if dx * dx + dy * dy <= 4:
                    px, py = eye_x + dx, eye_y + dy
                    if 0 <= px < size and 0 <= py < size:
                        idx = py * size + px
                        pixels[idx] = [255, 0, 0, 255]


def _draw_wolf_shape(pixels, size, color):
    """Рисуем волка"""
    center = size // 2
    
    # Тело (овал)
    body_width = size // 2
    body_height = size // 3
    for y in range(size):
        for x in range(size):
            dx = (x - center) / (body_width / 2)
            dy = (y - center) / (body_height / 2)
            if dx * dx + dy * dy <= 1:
                idx = y * size + x
                pixels[idx] = [int(color[0]*255), int(color[1]*255), 
                               int(color[2]*255), 255]
    
    # Голова
    head_x = center + body_width // 3
    head_radius = size // 6
    for dy in range(-head_radius, head_radius + 1):
        for dx in range(-head_radius, head_radius + 1):
            if dx * dx + dy * dy <= head_radius * head_radius:
                px, py = head_x + dx, center + dy
                if 0 <= px < size and 0 <= py < size:
                    idx = py * size + px
                    pixels[idx] = [int(color[0]*255), int(color[1]*255), 
                                   int(color[2]*255), 255]
    
    # Глаза
    eye_y = center + 2
    for eye_x in [head_x - 3, head_x + 3]:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if dx * dx + dy * dy <= 4:
                    px, py = eye_x + dx, eye_y + dy
                    if 0 <= px < size and 0 <= py < size:
                        idx = py * size + px
                        pixels[idx] = [100, 150, 255, 255]


def _draw_elite_shape(pixels, size, color):
    """Рисуем элитного врага/босса"""
    center = size // 2
    radius = center - 4
    
    # Основа с аурой
    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist <= radius:
                idx = y * size + x
                # Градиент с блеском
                intensity = 1.0 - (dist / radius) * 0.3
                shimmer = 0.9 + 0.1 * math.sin(dx * 0.5 + dy * 0.5)
                r = int(color[0] * 255 * intensity * shimmer)
                g = int(color[1] * 255 * intensity * shimmer)
                b = int(color[2] * 255 * intensity * shimmer)
                pixels[idx] = [r, g, b, 255]
            elif dist <= radius + 4:
                # Светящаяся аура
                idx = y * size + x
                alpha = int((1.0 - (dist - radius) / 4) * 150)
                pixels[idx] = [int(color[0]*255), int(color[1]*255), 
                               int(color[2]*255), alpha]
    
    # Руны/символы
    for i in range(6):
        angle = (i / 6) * 2 * math.pi
        rune_x = int(center + math.cos(angle) * (radius * 0.6))
        rune_y = int(center + math.sin(angle) * (radius * 0.6))
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                px, py = rune_x + dx, rune_y + dy
                if 0 <= px < size and 0 <= py < size:
                    idx = py * size + px
                    pixels[idx] = [255, 255, 200, 255]


def load_texture_or_placeholder(path, size, color):
    """
    Пытается загрузить текстуру из файла, 
    если не удаётся - возвращает заглушку
    """
    if os.path.exists(path):
        try:
            img = CoreImage(path)
            return img.texture
        except Exception as e:
            print(f"Ошибка загрузки {path}: {e}")
    
    # Возвращаем заглушку
    return generate_circle_texture(size, color)


class SpatialHash:
    """
    Пространственный хеш для оптимизации коллизий
    """
    
    def __init__(self, cell_size=100):
        self.cell_size = cell_size
        self.cells = {}
    
    def _get_cell(self, x, y):
        """Получить ключ ячейки по координатам"""
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def _get_cells_for_rect(self, x, y, w, h):
        """Получить все ячейки, пересекающиеся с прямоугольником"""
        min_cell_x = int(x // self.cell_size)
        max_cell_x = int((x + w) // self.cell_size)
        min_cell_y = int(y // self.cell_size)
        max_cell_y = int((y + h) // self.cell_size)
        
        cells = []
        for cx in range(min_cell_x, max_cell_x + 1):
            for cy in range(min_cell_y, max_cell_y + 1):
                cells.append((cx, cy))
        return cells
    
    def clear(self):
        """Очистить все ячейки"""
        self.cells.clear()
    
    def insert(self, obj, x, y, w, h):
        """Вставить объект в хеш"""
        for cell in self._get_cells_for_rect(x, y, w, h):
            if cell not in self.cells:
                self.cells[cell] = set()
            self.cells[cell].add(obj)
    
    def query(self, x, y, w, h):
        """Найти все объекты, которые могут пересекаться с прямоугольником"""
        result = set()
        for cell in self._get_cells_for_rect(x, y, w, h):
            if cell in self.cells:
                result.update(self.cells[cell])
        return result
    
    def remove(self, obj, x, y, w, h):
        """Удалить объект из хеша"""
        for cell in self._get_cells_for_rect(x, y, w, h):
            if cell in self.cells and obj in self.cells[cell]:
                self.cells[cell].remove(obj)