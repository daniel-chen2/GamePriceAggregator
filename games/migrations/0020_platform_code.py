# Generated by Django 3.0.4 on 2020-03-30 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0019_auto_20200330_2219'),
    ]

    operations = [
        migrations.AddField(
            model_name='platform',
            name='code',
            field=models.CharField(default='ps4', max_length=5),
        ),
    ]
