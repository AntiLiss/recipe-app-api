# Generated by Django 4.2.8 on 2023-12-16 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_alter_recipe_time_minutes_alter_user_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='time_minutes',
            field=models.DecimalField(decimal_places=1, max_digits=5),
        ),
    ]
