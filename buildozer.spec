[app]

# (str) Title of your application
title = Heterdaad

# (str) Package name (MUST be lowercase, no spaces or special characters!)
package.name = heterdaad

# (str) Package domain (needed for android packaging)
package.domain = org.precisiontech

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (this ensures both main.py and storage.py are packaged!)
source.includes = py

# (str) Application versioning
version = 0.1

# (list) Application requirements
# Note: python3 without specific patch version prevents build errors in python-for-android
requirements = python3,kivy==2.3.1,requests,plyer,pyjnius

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions required for network requests
android.permissions = INTERNET

# (int) Target Android API
android.api = 34

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 26b

# (str) Android SDK directory to use (leave empty for autodetect)
android.sdk = 

# (str) Android NDK directory to use (leave empty for autodetect)
android.ndk_path = 

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
