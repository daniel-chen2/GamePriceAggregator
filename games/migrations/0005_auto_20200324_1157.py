# Generated by Django 3.0.4 on 2020-03-24 03:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0004_remove_game_photo_1'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.Game'),
        ),
    ]
