"""
КОНФИГУРАЦИЯ ИГРЫ
Все константы, настройки врагов, способностей и мира
"""

from kivy.utils import platform

# ============================================
# НАСТРОЙКИ ЭКРАНА И ПРОИЗВОДИТЕЛЬНОСТИ
# ============================================

# Определяем платформу
IS_MOBILE = platform in ('android', 'ios')

# Размеры окна (для десктопа)
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# FPS
TARGET_FPS = 60
DELTA_TIME = 1.0 / TARGET_FPS

# ============================================
# НАСТРОЙКИ МИРА
# ============================================

# Размер мира в пикселях
WORLD_WIDTH = 3000
WORLD_HEIGHT = 3000

# Размер тайла
TILE_SIZE = 64

# Размер чанка для оптимизации (в тайлах)
CHUNK_SIZE = 8

# ============================================
# БИОМЫ
# ============================================

# Типы биомов
BIOME_FIELDS = 'fields'           # Зелёные поля (стартовая зона)
BIOME_DARK_FOREST = 'dark_forest' # Тёмный лес
BIOME_FIRE_LANDS = 'fire_lands'   # Огненные земли
BIOME_ICE_WASTES = 'ice_wastes'   # Ледяные пустоши
BIOME_RUINS = 'ruins'             # Руины (центр карты)

# Цвета биомов (для отрисовки)
BIOME_COLORS = {
    BIOME_FIELDS: (0.3, 0.7, 0.2, 1),       # Зелёный
    BIOME_DARK_FOREST: (0.15, 0.25, 0.15, 1), # Тёмно-зелёный
    BIOME_FIRE_LANDS: (0.5, 0.2, 0.1, 1),   # Красно-коричневый
    BIOME_ICE_WASTES: (0.7, 0.85, 0.95, 1), # Светло-голубой
    BIOME_RUINS: (0.25, 0.25, 0.3, 1),      # Серый
}

# Распределение биомов (центр = руины, остальное по секторам)
# Структура мира:
#   [Лёд]    [Лес]    [Лёд]
#   [Лес]    [РУИНЫ]  [Огонь]
#   [Поля]   [Поля]   [Огонь]

# ============================================
# НАСТРОЙКИ ИГРОКА (СЛАЙМА)
# ============================================

PLAYER_START_HP = 100
PLAYER_START_DAMAGE = 10
PLAYER_START_SPEED = 200  # пикселей в секунду
PLAYER_SIZE = 40          # размер спрайта в пикселях
PLAYER_ATTACK_RANGE = 50  # дальность базовой атаки
PLAYER_ATTACK_COOLDOWN = 0.5  # секунд между атаками

# Множители за поглощение
ABSORPTION_HP_GAIN = 1.0      # 100% HP врага добавляется к игроку
ABSORPTION_DAMAGE_GAIN = 0.5  # 50% урона врага
ABSORPTION_SPEED_GAIN = 0.03  # +3% скорости за каждое поглощение
ABSORPTION_SIZE_GAIN = 0.08   # +8% размера за каждое поглощение

MAX_SPEED_BONUS = 1.5         # Максимум +150% к скорости
MAX_SIZE_BONUS = 2.0          # Максимум +200% к размеру

MAX_ABILITIES = 6             # Максимум активных способностей

# ============================================
# ВРАГИ
# ============================================

# Типы поведения врагов
AI_PASSIVE = 'passive'           # Бродит случайно, убегает при атаке
AI_TERRITORIAL = 'territorial'   # Атакует при приближении
AI_AGGRESSIVE = 'aggressive'     # Активно ищет и преследует
AI_STATIONARY = 'stationary'     # Не двигается, стреляет
AI_PACK = 'pack'                 # Стайное поведение

# Радиусы обнаружения
DETECTION_RANGE_TERRITORIAL = 150
DETECTION_RANGE_AGGRESSIVE = 300
DETECTION_RANGE_STATIONARY = 250

# Время респавна врагов (секунды)
RESPAWN_TIME = 90

# Время, за которое нужно поглотить тело
BODY_DECAY_TIME = 10

# Конфигурация всех типов врагов
ENEMY_TYPES = {
    'herbivore_slime': {
        'name': 'Травоядный слайм',
        'hp': 30,
        'damage': 5,
        'speed': 180,
        'size': 32,
        'ai': AI_PASSIVE,
        'biome': BIOME_FIELDS,
        'color': (0.4, 0.9, 0.4, 1),  # Светло-зелёный
        'abilities': ['slippery_skin', 'regeneration'],
        'exp': 10,
    },
    'skeleton_warrior': {
        'name': 'Скелет-воин',
        'hp': 50,
        'damage': 10,
        'speed': 140,
        'size': 36,
        'ai': AI_TERRITORIAL,
        'biome': BIOME_FIELDS,
        'color': (0.9, 0.9, 0.85, 1),  # Белый/кость
        'abilities': ['bone_throw', 'bone_shield', 'sword_strike'],
        'exp': 25,
    },
    'fire_elemental': {
        'name': 'Огненный элементаль',
        'hp': 70,
        'damage': 15,
        'speed': 150,
        'size': 38,
        'ai': AI_AGGRESSIVE,
        'biome': BIOME_FIRE_LANDS,
        'color': (1.0, 0.4, 0.1, 1),  # Оранжево-красный
        'abilities': ['fireball', 'fire_trail', 'fire_dash', 'burning_aura'],
        'exp': 40,
    },
    'ice_mage': {
        'name': 'Ледяной маг',
        'hp': 60,
        'damage': 12,
        'speed': 100,
        'size': 36,
        'ai': AI_TERRITORIAL,
        'biome': BIOME_ICE_WASTES,
        'color': (0.5, 0.7, 1.0, 1),  # Голубой
        'abilities': ['ice_arrow', 'freeze_area', 'ice_wall', 'cold_aura'],
        'exp': 35,
    },
    'shadow_assassin': {
        'name': 'Теневой убийца',
        'hp': 40,
        'damage': 25,
        'speed': 220,
        'size': 34,
        'ai': AI_AGGRESSIVE,
        'biome': BIOME_DARK_FOREST,
        'color': (0.2, 0.15, 0.25, 1),  # Тёмно-фиолетовый
        'abilities': ['teleport_behind', 'critical_strike', 'invisibility', 'shadow_dash'],
        'exp': 45,
    },
    'stone_golem': {
        'name': 'Каменный голем',
        'hp': 150,
        'damage': 8,
        'speed': 60,
        'size': 52,
        'ai': AI_TERRITORIAL,
        'biome': BIOME_FIELDS,
        'color': (0.5, 0.5, 0.5, 1),  # Серый
        'abilities': ['earthquake', 'stone_skin', 'golem_regen'],
        'exp': 50,
    },
    'spider': {
        'name': 'Паук',
        'hp': 35,
        'damage': 8,
        'speed': 170,
        'size': 28,
        'ai': AI_PACK,
        'biome': BIOME_DARK_FOREST,
        'color': (0.1, 0.1, 0.1, 1),  # Чёрный
        'abilities': ['web_shot', 'poison_bite', 'summon_spiderlings'],
        'exp': 20,
        'pack_size': (3, 5),  # Размер стаи (мин, макс)
    },
    'snow_wolf': {
        'name': 'Снежный волк',
        'hp': 55,
        'damage': 14,
        'speed': 200,
        'size': 38,
        'ai': AI_AGGRESSIVE,
        'biome': BIOME_ICE_WASTES,
        'color': (0.95, 0.95, 1.0, 1),  # Белый
        'abilities': ['ice_bite', 'howl', 'wolf_dash'],
        'exp': 35,
    },
    'lava_golem': {
        'name': 'Лавовый голем',
        'hp': 200,
        'damage': 20,
        'speed': 70,
        'size': 56,
        'ai': AI_TERRITORIAL,
        'biome': BIOME_FIRE_LANDS,
        'color': (0.8, 0.2, 0.0, 1),  # Тёмно-красный
        'abilities': ['lava_spit', 'fire_wave', 'lava_armor'],
        'exp': 70,
    },
    'elite_guard': {
        'name': 'Элитный страж',
        'hp': 300,
        'damage': 30,
        'speed': 120,
        'size': 48,
        'ai': AI_STATIONARY,
        'biome': BIOME_RUINS,
        'color': (0.9, 0.75, 0.3, 1),  # Золотой
        'abilities': ['laser_beam', 'summon_shields', 'guard_teleport', 'energy_burst'],
        'exp': 100,
    },
    'ruins_keeper': {
        'name': 'Хранитель Руин',
        'hp': 1000,
        'damage': 50,
        'speed': 100,
        'size': 80,
        'ai': AI_AGGRESSIVE,
        'biome': BIOME_RUINS,
        'color': (0.6, 0.1, 0.6, 1),  # Фиолетовый
        'abilities': ['all'],  # Все способности
        'exp': 500,
        'is_boss': True,
    },
}

# Начальная популяция врагов в каждом биоме
ENEMY_SPAWN_CONFIG = {
    BIOME_FIELDS: [
        ('herbivore_slime', 20),
        ('skeleton_warrior', 15),
        ('stone_golem', 3),
    ],
    BIOME_DARK_FOREST: [
        ('shadow_assassin', 10),
        ('spider', 12),
    ],
    BIOME_FIRE_LANDS: [
        ('fire_elemental', 8),
        ('lava_golem', 5),
    ],
    BIOME_ICE_WASTES: [
        ('ice_mage', 10),
        ('snow_wolf', 8),
    ],
    BIOME_RUINS: [
        ('elite_guard', 5),
        ('ruins_keeper', 1),
    ],
}

# ============================================
# СПОСОБНОСТИ
# ============================================

# Типы способностей
ABILITY_ACTIVE = 'active'
ABILITY_PASSIVE = 'passive'

# Конфигурация способностей
ABILITIES = {
    # === СЛАЙМ ===
    'slippery_skin': {
        'name': 'Скользкая кожа',
        'type': ABILITY_PASSIVE,
        'description': 'Шанс уклонения +10%',
        'effect': {'dodge_chance': 0.1},
        'icon_color': (0.5, 1.0, 0.5, 1),
    },
    'regeneration': {
        'name': 'Регенерация',
        'type': ABILITY_PASSIVE,
        'description': 'Восстановление 2 HP/сек',
        'effect': {'hp_regen': 2},
        'icon_color': (0.3, 0.9, 0.3, 1),
    },
    
    # === СКЕЛЕТ ===
    'bone_throw': {
        'name': 'Бросок кости',
        'type': ABILITY_ACTIVE,
        'description': 'Дальняя атака костью',
        'cooldown': 2.0,
        'damage': 15,
        'range': 300,
        'projectile_speed': 400,
        'icon_color': (0.9, 0.9, 0.8, 1),
    },
    'bone_shield': {
        'name': 'Костяной щит',
        'type': ABILITY_ACTIVE,
        'description': '+20 защиты на 5 сек',
        'cooldown': 10.0,
        'duration': 5.0,
        'effect': {'defense': 20},
        'icon_color': (0.8, 0.8, 0.7, 1),
    },
    'sword_strike': {
        'name': 'Удар мечом',
        'type': ABILITY_ACTIVE,
        'description': 'Мощный удар мечом',
        'cooldown': 1.5,
        'damage': 20,
        'range': 60,
        'icon_color': (0.7, 0.7, 0.7, 1),
    },
    
    # === ОГНЕННЫЙ ЭЛЕМЕНТАЛЬ ===
    'fireball': {
        'name': 'Огненный шар',
        'type': ABILITY_ACTIVE,
        'description': 'Метает огненный шар',
        'cooldown': 1.5,
        'damage': 25,
        'range': 350,
        'projectile_speed': 350,
        'aoe_radius': 50,
        'icon_color': (1.0, 0.5, 0.0, 1),
    },
    'fire_trail': {
        'name': 'Огненный след',
        'type': ABILITY_ACTIVE,
        'description': 'Оставляет огненный след',
        'cooldown': 8.0,
        'duration': 4.0,
        'damage_per_sec': 10,
        'icon_color': (1.0, 0.3, 0.0, 1),
    },
    'fire_dash': {
        'name': 'Огненный рывок',
        'type': ABILITY_ACTIVE,
        'description': 'Быстрый рывок с уроном',
        'cooldown': 5.0,
        'damage': 15,
        'distance': 200,
        'icon_color': (1.0, 0.6, 0.1, 1),
    },
    'burning_aura': {
        'name': 'Горящая аура',
        'type': ABILITY_PASSIVE,
        'description': 'Урон врагам вблизи',
        'effect': {'aura_damage': 5, 'aura_radius': 80},
        'icon_color': (1.0, 0.4, 0.0, 1),
    },
    
    # === ЛЕДЯНОЙ МАГ ===
    'ice_arrow': {
        'name': 'Ледяная стрела',
        'type': ABILITY_ACTIVE,
        'description': 'Стрела льда, замедляет',
        'cooldown': 1.8,
        'damage': 18,
        'range': 300,
        'projectile_speed': 380,
        'slow_effect': 0.5,
        'slow_duration': 2.0,
        'icon_color': (0.6, 0.8, 1.0, 1),
    },
    'freeze_area': {
        'name': 'Заморозка',
        'type': ABILITY_ACTIVE,
        'description': 'Замораживает врагов вокруг',
        'cooldown': 12.0,
        'duration': 3.0,
        'radius': 120,
        'icon_color': (0.4, 0.6, 1.0, 1),
    },
    'ice_wall': {
        'name': 'Ледяная стена',
        'type': ABILITY_ACTIVE,
        'description': 'Создаёт стену льда',
        'cooldown': 15.0,
        'duration': 6.0,
        'wall_hp': 100,
        'icon_color': (0.5, 0.7, 1.0, 1),
    },
    'cold_aura': {
        'name': 'Холодная аура',
        'type': ABILITY_PASSIVE,
        'description': 'Замедляет врагов рядом',
        'effect': {'slow_aura': 0.3, 'slow_radius': 100},
        'icon_color': (0.7, 0.85, 1.0, 1),
    },
    
    # === ТЕНЕВОЙ УБИЙЦА ===
    'teleport_behind': {
        'name': 'Телепорт',
        'type': ABILITY_ACTIVE,
        'description': 'Телепорт за спину врага',
        'cooldown': 6.0,
        'range': 250,
        'icon_color': (0.3, 0.2, 0.4, 1),
    },
    'critical_strike': {
        'name': 'Крит. удар',
        'type': ABILITY_ACTIVE,
        'description': 'Удар с х3 уроном',
        'cooldown': 8.0,
        'damage_multiplier': 3.0,
        'range': 50,
        'icon_color': (0.4, 0.1, 0.3, 1),
    },
    'invisibility': {
        'name': 'Невидимость',
        'type': ABILITY_ACTIVE,
        'description': '5 сек невидимости',
        'cooldown': 20.0,
        'duration': 5.0,
        'icon_color': (0.2, 0.15, 0.25, 1),
    },
    'shadow_dash': {
        'name': 'Теневой рывок',
        'type': ABILITY_ACTIVE,
        'description': 'Быстрый рывок в тени',
        'cooldown': 4.0,
        'distance': 180,
        'icon_color': (0.25, 0.2, 0.3, 1),
    },
    
    # === КАМЕННЫЙ ГОЛЕМ ===
    'earthquake': {
        'name': 'Землетрясение',
        'type': ABILITY_ACTIVE,
        'description': 'АоЕ урон вокруг',
        'cooldown': 10.0,
        'damage': 30,
        'radius': 150,
        'icon_color': (0.6, 0.5, 0.4, 1),
    },
    'stone_skin': {
        'name': 'Каменная кожа',
        'type': ABILITY_ACTIVE,
        'description': '-50% урона на 8 сек',
        'cooldown': 20.0,
        'duration': 8.0,
        'damage_reduction': 0.5,
        'icon_color': (0.5, 0.5, 0.5, 1),
    },
    'golem_regen': {
        'name': 'Регенерация голема',
        'type': ABILITY_PASSIVE,
        'description': '+5 HP/сек',
        'effect': {'hp_regen': 5},
        'icon_color': (0.55, 0.55, 0.5, 1),
    },
    
    # === ПАУК ===
    'web_shot': {
        'name': 'Паутина',
        'type': ABILITY_ACTIVE,
        'description': 'Замедляет цель',
        'cooldown': 4.0,
        'range': 200,
        'slow_effect': 0.7,
        'slow_duration': 3.0,
        'icon_color': (0.8, 0.8, 0.8, 1),
    },
    'poison_bite': {
        'name': 'Ядовитый укус',
        'type': ABILITY_ACTIVE,
        'description': 'Урон со временем',
        'cooldown': 5.0,
        'damage': 5,
        'dot_damage': 3,
        'dot_duration': 5.0,
        'range': 40,
        'icon_color': (0.4, 0.8, 0.2, 1),
    },
    'summon_spiderlings': {
        'name': 'Призыв паучков',
        'type': ABILITY_ACTIVE,
        'description': 'Призывает 2 паучка',
        'cooldown': 15.0,
        'summon_count': 2,
        'icon_color': (0.2, 0.2, 0.2, 1),
    },
    
    # === СНЕЖНЫЙ ВОЛК ===
    'ice_bite': {
        'name': 'Ледяной укус',
        'type': ABILITY_ACTIVE,
        'description': 'Урон + замедление',
        'cooldown': 3.0,
        'damage': 20,
        'slow_effect': 0.4,
        'slow_duration': 2.0,
        'range': 50,
        'icon_color': (0.9, 0.95, 1.0, 1),
    },
    'howl': {
        'name': 'Вой',
        'type': ABILITY_ACTIVE,
        'description': 'Призывает волка',
        'cooldown': 25.0,
        'summon_count': 1,
        'icon_color': (0.85, 0.9, 1.0, 1),
    },
    'wolf_dash': {
        'name': 'Рывок волка',
        'type': ABILITY_ACTIVE,
        'description': 'Быстрый рывок',
        'cooldown': 4.0,
        'distance': 200,
        'damage': 12,
        'icon_color': (0.9, 0.9, 0.95, 1),
    },
    
    # === ЛАВОВЫЙ ГОЛЕМ ===
    'lava_spit': {
        'name': 'Лавовый плевок',
        'type': ABILITY_ACTIVE,
        'description': 'Дальняя атака лавой',
        'cooldown': 2.5,
        'damage': 25,
        'range': 280,
        'projectile_speed': 300,
        'icon_color': (1.0, 0.3, 0.0, 1),
    },
    'fire_wave': {
        'name': 'Огненная волна',
        'type': ABILITY_ACTIVE,
        'description': 'АоЕ волна огня',
        'cooldown': 12.0,
        'damage': 35,
        'radius': 180,
        'icon_color': (1.0, 0.4, 0.1, 1),
    },
    'lava_armor': {
        'name': 'Лавовая броня',
        'type': ABILITY_PASSIVE,
        'description': 'Иммунитет к огню',
        'effect': {'fire_immune': True},
        'icon_color': (0.8, 0.2, 0.0, 1),
    },
    
    # === ЭЛИТНЫЙ СТРАЖ ===
    'laser_beam': {
        'name': 'Лазерный луч',
        'type': ABILITY_ACTIVE,
        'description': 'Мощный лазер',
        'cooldown': 3.0,
        'damage': 40,
        'range': 400,
        'beam_width': 20,
        'icon_color': (1.0, 0.9, 0.3, 1),
    },
    'summon_shields': {
        'name': 'Призыв щитов',
        'type': ABILITY_ACTIVE,
        'description': 'Создаёт защитные щиты',
        'cooldown': 18.0,
        'shield_hp': 80,
        'shield_count': 3,
        'icon_color': (0.9, 0.8, 0.4, 1),
    },
    'guard_teleport': {
        'name': 'Телепортация',
        'type': ABILITY_ACTIVE,
        'description': 'Телепорт к цели',
        'cooldown': 8.0,
        'range': 350,
        'icon_color': (0.85, 0.7, 0.3, 1),
    },
    'energy_burst': {
        'name': 'Энергетический взрыв',
        'type': ABILITY_ACTIVE,
        'description': 'Мощный взрыв энергии',
        'cooldown': 15.0,
        'damage': 50,
        'radius': 200,
        'icon_color': (1.0, 0.85, 0.4, 1),
    },
}

# ============================================
# UI И ЦВЕТА
# ============================================

# Цвета интерфейса
COLOR_HP_BAR = (0.8, 0.2, 0.2, 1)
COLOR_HP_BAR_BG = (0.3, 0.1, 0.1, 1)
COLOR_ABILITY_READY = (0.2, 0.8, 0.2, 1)
COLOR_ABILITY_COOLDOWN = (0.5, 0.5, 0.5, 0.7)
COLOR_TEXT = (1, 1, 1, 1)
COLOR_NOTIFICATION = (1, 0.9, 0.3, 1)

# Размеры UI элементов
HP_BAR_WIDTH = 200
HP_BAR_HEIGHT = 20
ABILITY_SLOT_SIZE = 50
MINIMAP_SIZE = 150

# ============================================
# УПРАВЛЕНИЕ
# ============================================

# Размер виртуального джойстика
JOYSTICK_SIZE = 120
JOYSTICK_DEAD_ZONE = 0.15

# Размер кнопок атаки/способностей
ACTION_BUTTON_SIZE = 70

# ============================================
# ЧАСТИЦЫ
# ============================================

# Настройки системы частиц
MAX_PARTICLES = 200
PARTICLE_LIFETIME = 1.0

# ============================================
# СОХРАНЕНИЯ
# ============================================

SAVE_FOLDER = 'saves'
SAVE_FILE = 'save_game.json'
AUTOSAVE_INTERVAL = 60  # секунд

# ============================================
# ОТЛАДКА
# ============================================

DEBUG_MODE = False
SHOW_COLLISION_BOXES = False
SHOW_FPS = True