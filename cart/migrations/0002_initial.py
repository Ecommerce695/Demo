# Generated by Django 4.1.4 on 2023-08-10 09:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cart', '0001_initial'),
        ('super_admin', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='product',
            field=models.ForeignKey(blank=True, db_column='product_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='super_admin.product'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(blank=True, db_column='user_id', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
