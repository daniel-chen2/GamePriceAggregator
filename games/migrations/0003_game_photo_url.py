# Generated by Django 3.0.4 on 2020-03-24 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_auto_20200324_1133'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='photo_url',
            field=models.TextField(default=None, null=True),
        ),
    ]
