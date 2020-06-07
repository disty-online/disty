import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "disty_online.settings")
import django

django.setup()

from disty.models import Role, User


admin_role = Role(role_name="admin")
admin_role.save()
internal_role = Role(role_name="internal")
internal_role.save()


pingo = User(name="Pingo", role=admin_role, password="mickey")
pingo.save()
logan = User(name="Logan", role=internal_role, password="wolverine")
logan.save()
