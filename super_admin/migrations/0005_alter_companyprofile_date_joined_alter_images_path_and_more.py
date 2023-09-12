# Generated by Django 4.1.4 on 2023-09-01 09:21

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('super_admin', '0004_alter_companyprofile_date_joined_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyprofile',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 1, 14, 51, 10, 785783)),
        ),
        migrations.AlterField(
            model_name='images',
            name='path',
            field=models.ImageField(blank=True, db_column='path', null=True, upload_to='variants/images/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]),
        ),
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 1, 14, 51, 10, 793783)),
        ),
        migrations.AlterField(
            model_name='product',
            name='warranty_path',
            field=models.FileField(null=True, upload_to='product/warranty/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
        migrations.AlterField(
            model_name='productlaptop',
            name='release_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 1, 14, 51, 10, 797968)),
        ),
    ]