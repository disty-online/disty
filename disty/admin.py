from django.contrib import admin

# Register your models here.
from .models import File, DownloadUrl, Access, UploadUrl

admin.site.site_header = "Disty"


class FileAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at", "checksum")


class AccessAdmin(admin.ModelAdmin):
    list_display = ("url", "file", "timestamp", "source_ip", "user_agent")


class UrlAdmin(admin.ModelAdmin):
    list_display = ("url", "owner", "file", "created_at", "expiry")


admin.site.register(File, FileAdmin)
admin.site.register(DownloadUrl, UrlAdmin)
admin.site.register(Access, AccessAdmin)
admin.site.register(UploadUrl)
