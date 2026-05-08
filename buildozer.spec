[app]
title = Учёт Рабочих
package.name = workertracker
package.domain = org.khujand.apps
source.dir = .
source.include_exts = py,json
version = 2.0.0

# Без KivyMD — только чистый Kivy
requirements = python3==3.10.14,kivy==2.3.0,pillow,android

orientation = portrait
fullscreen = 0

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 35
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.sdk = 35
android.archs = arm64-v8a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
