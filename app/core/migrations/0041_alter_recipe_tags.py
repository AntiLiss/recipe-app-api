# Generated by Django 4.2.9 on 2024-01-02 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_alter_recipe_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='core.tag'),
        ),
    ]