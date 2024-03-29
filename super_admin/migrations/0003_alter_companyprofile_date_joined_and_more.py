# Generated by Django 4.1.4 on 2023-08-29 11:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('super_admin', '0002_alter_companyprofile_date_joined_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyprofile',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 29, 17, 2, 24, 62277)),
        ),
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 29, 17, 2, 24, 67273)),
        ),
        migrations.AlterField(
            model_name='product',
            name='warranty_path',
            field=models.FileField(null=True, upload_to='product/warranty/'),
        ),
        migrations.AlterField(
            model_name='productlaptop',
            name='release_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 29, 17, 2, 24, 83265)),
        ),
    ]
