# Generated by Django 5.0.6 on 2024-05-24 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_placefeatureimages'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='place_address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
