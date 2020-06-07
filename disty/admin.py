from django.contrib import admin

# Register your models here.
from .models import Role, User, File, Url, Access

admin.site.register(Role)
admin.site.register(User)
admin.site.register(File)
admin.site.register(Url)
admin.site.register(Access)
