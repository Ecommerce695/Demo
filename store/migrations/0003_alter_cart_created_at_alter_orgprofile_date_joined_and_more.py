# Generated by Django 4.0.6 on 2022-11-22 11:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_cart_created_at_alter_orgprofile_date_joined_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 22, 16, 31, 34, 873084)),
        ),
        migrations.AlterField(
            model_name='orgprofile',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 22, 16, 31, 34, 869097)),
        ),
        migrations.AlterField(
            model_name='passwordreset',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 22, 16, 31, 34, 868085)),
        ),
        migrations.AlterField(
            model_name='productlaptop',
            name='release_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 22, 16, 31, 34, 872085)),
        ),
        migrations.AlterField(
            model_name='search_history',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 22, 16, 31, 34, 877084)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 22, 16, 31, 34, 858093)),
        ),
        migrations.AlterField(
            model_name='wishlist',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 22, 16, 31, 34, 875142)),
        ),
        migrations.AlterUniqueTogether(
            name='userrole',
            unique_together={('role_id', 'user_id')},
        ),
    ]
