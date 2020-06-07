# Generated by Django 3.0.7 on 2020-06-07 10:48

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ("disty", "0005_access_source_ip"),
    ]

    operations = [
        migrations.AddField(
            model_name="access",
            name="timestamp",
            field=models.DateTimeField(
                default=datetime.datetime(2020, 6, 7, 10, 48, 40, 38632, tzinfo=utc),
                verbose_name="timestamp",
            ),
            preserve_default=False,
        ),
    ]
