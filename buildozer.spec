[app]
title = AlzParking
package.name = alzparking
package.domain = org.alzparking
source.dir = Frontend
source.include_exts = py,png,jpg,kv,json
version = 0.1
requirements = python3,kivy==2.3.0,certifi
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
