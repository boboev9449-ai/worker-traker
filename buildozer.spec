[app]

# ── Основные параметры ──────────────────────────────────────────
title = Учёт Рабочих
package.name = workertracker
package.domain = org.khujand.apps
source.dir = .
source.include_exts = py,kv,json,png,jpg,atlas,ttf

version = 1.0.0

# ── Зависимости ─────────────────────────────────────────────────
# Основные: kivy + kivymd
requirements = python3,kivy==2.2.1,kivymd==1.1.1,sdl2_ttf==2.0.18,pillow

# ── Иконка и заставка (опционально) ────────────────────────────
# Создайте icon.png (512x512) и раскомментируйте:
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

# ── Ориентация ──────────────────────────────────────────────────
orientation = portrait

# ── Полноэкранный режим ─────────────────────────────────────────
fullscreen = 0

# ── Android настройки ───────────────────────────────────────────
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.ndk_api = 21

# Архитектуры (arm64-v8a — современные телефоны)
android.archs = arm64-v8a, armeabi-v7a

# ── Gradle зависимости (для Material Design) ────────────────────
android.gradle_dependencies = com.google.android.material:material:1.6.0

# ── Разное ──────────────────────────────────────────────────────
android.allow_backup = True
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
