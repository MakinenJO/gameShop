# Generated by Django 3.0.2 on 2020-02-10 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('play_game', '0003_auto_20200209_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamepurchase',
            name='purchase_id',
            field=models.CharField(default=None, max_length=64, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gamepurchase',
            name='purchase_ref',
            field=models.CharField(default=None, max_length=64, unique=True),
            preserve_default=False,
        ),
    ]
