# Generated by Django 4.1.4 on 2023-08-10 09:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(db_column='cart_id', primary_key=True, serialize=False)),
                ('variant', models.PositiveIntegerField(null=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('sku', models.CharField(max_length=1000, null=True)),
                ('size', models.CharField(max_length=100, null=True)),
                ('color', models.CharField(max_length=100, null=True)),
                ('src', models.CharField(max_length=1000, null=True)),
                ('brand', models.CharField(max_length=100, null=True)),
                ('type', models.CharField(max_length=100, null=True)),
                ('discount', models.PositiveIntegerField()),
                ('stock', models.PositiveIntegerField()),
                ('cart_value', models.FloatField(blank=True, db_column='total_cart_value', default=0)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2023, 8, 10, 15, 23, 1, 685246))),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'user_cart',
            },
        ),
    ]
