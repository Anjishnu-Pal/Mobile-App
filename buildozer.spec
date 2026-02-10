[app]
title = SensorMonitor
package.name = sensormonitor
package.domain = com.sensormonitor

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy

orientations = portrait,landscape
fullscreen = 0

# NFC Permissions for NHS 3152 communication
android.permissions = INTERNET,NFC,ACCESS_FINE_LOCATION,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# NFC Features
 # android.features = android.hardware.nfc

# No native code compilation
android.add_src = native_sensor

# JNI setup
android.ndk = 25b
android.api = 31
android.minapi = 21

# Services
p4a.bootstrap = sdl2

# Skip cython compilation
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
requirements = python3,kivy

# Enable debug mode for development
android.debug_skeleton = yes
