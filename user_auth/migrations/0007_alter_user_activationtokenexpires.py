# Generated by Django 5.0.8 on 2024-09-13 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0006_user_activationtoken_user_activationtokenexpires_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='activationTokenExpires',
            field=models.TimeField(blank=True, null=True),
        ),
    ]