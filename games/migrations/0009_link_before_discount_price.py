# Generated by Django 2.2.9 on 2020-03-25 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0008_auto_20200325_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='before_discount_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]