# Generated by Django 3.0.4 on 2020-03-30 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0017_store_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='code',
            field=models.CharField(max_length=3),
        ),
    ]
