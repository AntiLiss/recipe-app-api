# Generated by Django 4.2.8 on 2023-12-27 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_ingredient_recipe_ingredients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(to='core.ingredient'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='core.tag'),
        ),
    ]
