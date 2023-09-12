# Generated by Django 4.1.4 on 2023-09-08 09:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='brand',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='color',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='discount',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='price',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='size',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='sku',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='src',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='stock',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='title',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='type',
        ),
        migrations.AlterField(
            model_name='cart',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 8, 14, 49, 19, 441181)),
        ),
    ]