[app]
title = Учёт Рабочих
package.name = workertracker
package.domain = org.khujand.apps
source.dir = .
source.include_exts = py,kv,json
version = 1.0.0
requirements = python3==3.10.14,kivy==2.2.1,kivymd==1.1.1,pillow
orientation = portrait
fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.ndk_api = 21
android.archs = arm64-v8a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
