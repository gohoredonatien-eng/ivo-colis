[app]
title = IVO COLIS EXPRESS
package.name = ivocolis
package.domain = com.ivo.colis

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
version.regex = __version__ = ['"]([^'"]*)['"]
orientation = portrait

[buildozer]
log_level = 2

# Liste des requirements pour ton app VIP
requirements = python3,kivy,openpyxl,sqlite3

# Permissions importantes
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license_agreement = True

# Icone (optionnel)
# icon.filename = %(source.dir)s/icon.png

[app:android]
# Pour ouvrir WhatsApp
android.manifest.intent_filters = 

[buildozer:android]
# Si tu veux un APK release
# p4a.branch = master
