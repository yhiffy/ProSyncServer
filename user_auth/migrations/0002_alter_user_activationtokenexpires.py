# Generated by Django 5.0.8 on 2024-09-13 04:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='activationTokenExpires',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 13, 4, 46, 51, 52380, tzinfo=datetime.timezone.utc)),
        ),
    ]