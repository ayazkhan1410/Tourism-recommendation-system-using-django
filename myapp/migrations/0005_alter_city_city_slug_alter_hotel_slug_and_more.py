# Generated by Django 5.0.6 on 2024-05-22 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_remove_city_is_featured_destination'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='city_slug',
            field=models.SlugField(blank=True, max_length=150, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='slug',
            field=models.SlugField(blank=True, max_length=150, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='slug',
            field=models.SlugField(blank=True, max_length=150, null=True, unique=True),
        ),
    ]