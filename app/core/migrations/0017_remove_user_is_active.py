# Generated by Django 4.2.7 on 2023-12-07 19:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_remove_user_is_staff'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_active',
        ),
    ]
