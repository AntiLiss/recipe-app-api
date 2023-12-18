# Generated by Django 4.2.8 on 2023-12-17 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_alter_recipe_time_minutes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='time_minutes',
            field=models.DecimalField(decimal_places=1, max_digits=4),
        ),
    ]
