# Generated by Django 4.2.8 on 2023-12-21 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='days',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]