# Generated by Django 3.0.7 on 2020-06-10 20:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('disty', '0003_auto_20200610_2028'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expiry', models.DateTimeField(verbose_name='expiry at')),
                ('url', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(verbose_name='created at')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
