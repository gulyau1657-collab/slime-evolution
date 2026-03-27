[app]

# Название приложения
title = Slime Evolution

# Имя пакета
package.name = slimeevolution

# Домен пакета (используется для полного имени пакета)
package.domain = org.game

# Исходный код
source.dir = .

# Включаемые расширения файлов
source.include_exts = py,png,jpg,kv,atlas,json

# Папки для включения
source.include_patterns = assets/*,src/*,saves/*

# Исключаемые папки
source.exclude_dirs = tests,bin,venv,__pycache__,.git

# Версия приложения
version = 1.0.0

# Требования (зависимости)
requirements = python3,kivy

# Точка входа
entrypoint = main.py

# Иконка приложения (опционально)
# icon.filename = %(source.dir)s/assets/icon.png

# Заставка (опционально)  
# presplash.filename = %(source.dir)s/assets/presplash.png

# Ориентация экрана: landscape, portrait, all
orientation = landscape

# Полноэкранный режим
fullscreen = 1

# Минимальная версия Android API
android.minapi = 21

# Целевая версия Android API
android.api = 31

# NDK версия
android.ndk = 25b

# Архитектуры для сборки
android.archs = arm64-v8a,armeabi-v7a

# Разрешения Android
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Gradle зависимости (если нужны)
# android.gradle_dependencies =

# Принять лицензии SDK автоматически
android.accept_sdk_license = True

# Режим сборки: debug или release
# android.release_artifact = aab
# android.debug_artifact = apk

# Logcat фильтры для отладки
android.logcat_filters = *:S python:D

# Копировать библиотеки вместо ссылок
android.copy_libs = 1

# Включить AndroidX
android.enable_androidx = True

[buildozer]

# Уровень логирования: 0 = ошибки, 1 = инфо, 2 = отладка
log_level = 2

# Предупреждения как ошибки
warn_on_root = 1

# Папка для сборки
build_dir = ./.buildozer

# Папка для артефактов
bin_dir = ./bin