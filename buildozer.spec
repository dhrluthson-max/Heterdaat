# =============================================================================
# Buildozer Specification File for Heterdaad (Android 15/16 + 16KB Page Size)
# =============================================================================

[app]
title = Heterdaad
package.name = heterdaad
package.domain = org.veiligheid
source.dir = .
source.include_exts = py,kv,png,jpg,atlas
source.exclude_dirs = safeapp-stable, safeapp-env, bin, .buildozer, venv, temp
version = 0.1

# ----------------- Requirements -----------------
requirements = python3,kivy==2.3.1,plyer,requests,pillow,cryptography==41.0.7

orientation = portrait
fullscreen = 0

# ----------------- Android Basis & Rechten -----------------
android.minapi = 24
android.permissions = VIBRATE, POST_NOTIFICATIONS, INTERNET

# =============================================================================
# 16 KB Page-Size & Android 15/16 Modern NDK Engine
# =============================================================================
p4a.branch = develop
android.api = 36
android.accept_sdk_license = True

# Ultramoderne NDK die de juiste ELF-uitlijning afdwingt voor Android 15/16
android.ndk = 29
android.ndk_api = 24

# Beperk architectuur tot 64-bit arm (Cruciaal om 4KB/16KB runtime conflicten te voorkomen)
android.archs = arm64-v8a

# Linker-vlaggen die 16 KB ELF-uitlijning afdwingen voor alle gedeelde (.so) bibliotheken
android.ext_platform_ldflags = -Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384

# =============================================================================
# Universele CI/CD Java & Gradle Omgeving (Mac + GitHub Actions Linux)
# =============================================================================
android.gradle_env = JAVA_HOME=$JAVA_HOME

[buildozer]
log_level = 2
warn_on_root = 1
