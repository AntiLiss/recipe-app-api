# Generated by Django 4.2.9 on 2024-01-02 18:19

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, default='sdfsdf', upload_to=core.models.generate_recipe_image_path),
            preserve_default=False,
        ),
    ]
