# Generated by Django 3.0.4 on 2020-03-24 03:33

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='platforms',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='rawg_id',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
