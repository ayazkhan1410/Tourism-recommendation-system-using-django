# Generated by Django 5.0.6 on 2024-05-24 11:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_place_place_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='HotelRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('review', models.TextField(blank=True, null=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hotel_ratings', to='myapp.hotel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hotel_ratings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlaceRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('review', models.TextField()),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='place_ratings', to='myapp.place')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='place_ratings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
