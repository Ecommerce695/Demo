# Generated by Django 4.1.4 on 2023-09-07 09:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlist',
            name='brand',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='category',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='color',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='discount',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='price',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='size',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='sku',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='src',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='title',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='type',
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 7, 15, 24, 42, 791540)),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 9, 15, 24, 42, 791540)),
        ),
        migrations.AlterField(
            model_name='reset_password',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 7, 15, 24, 42, 789568)),
        ),
        migrations.AlterField(
            model_name='saveforlater',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 7, 15, 24, 42, 804527)),
        ),
        migrations.AlterField(
            model_name='search_history',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 7, 15, 24, 42, 799530)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 7, 15, 24, 42, 768547)),
        ),
        migrations.AlterField(
            model_name='wishlist',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 7, 15, 24, 42, 796530)),
        ),
    ]
