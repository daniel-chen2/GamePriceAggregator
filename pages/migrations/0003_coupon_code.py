# Generated by Django 3.0.4 on 2020-04-29 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_bundle_coupon_free_game'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='code',
            field=models.TextField(blank=True),
        ),
    ]
