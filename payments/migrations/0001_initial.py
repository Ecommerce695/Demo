# Generated by Django 4.1.4 on 2023-08-10 09:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Payment_details_table',
            fields=[
                ('id', models.AutoField(db_column='payment_id', primary_key=True, serialize=False)),
                ('payment', models.CharField(blank=True, db_column='stripe_payment_intent_id', max_length=100, null=True)),
                ('paymenttype', models.CharField(blank=True, db_column='payment_type', max_length=100, null=True)),
                ('amount', models.FloatField(blank=True, db_column='transaction_amount', null=True)),
                ('invoice', models.CharField(blank=True, db_column='invoice_id', max_length=100, null=True)),
                ('currency', models.CharField(blank=True, db_column='currency_type', max_length=100, null=True)),
                ('orderitem', models.PositiveIntegerField(db_column='order_item_id', null=True)),
                ('status', models.CharField(blank=True, db_column='payment_status', max_length=100, null=True)),
                ('charge_id', models.CharField(blank=True, db_column='stripe_charge_id', max_length=100, null=True)),
                ('paymentmethodid', models.CharField(blank=True, db_column='stripe_paymentmethod_id', max_length=100, null=True)),
                ('transaction_id', models.CharField(blank=True, db_column='stripe_transaction_id', max_length=100, null=True)),
                ('reciept', models.CharField(blank=True, db_column='stripe_reciept_id', max_length=100, null=True)),
                ('invoiceno', models.CharField(blank=True, db_column='stripe_invoice_number', max_length=100, null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2023, 8, 10, 15, 23, 1, 689262))),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('alias', models.CharField(max_length=20, null=True, unique=True)),
            ],
            options={
                'db_table': 'payment_details',
            },
        ),
        migrations.CreateModel(
            name='Transaction_table',
            fields=[
                ('id', models.AutoField(db_column='transaction_id', primary_key=True, serialize=False)),
                ('transaction', models.CharField(blank=True, db_column='session_id', max_length=100, null=True)),
                ('status', models.CharField(blank=True, db_column='payment_status', max_length=100, null=True)),
                ('user', models.PositiveIntegerField(db_column='user_id', null=True)),
                ('order', models.PositiveIntegerField(db_column='order_id', null=True)),
                ('orderitem', models.PositiveIntegerField(db_column='order_item_id', null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2023, 8, 10, 15, 23, 1, 688265))),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expired_at', models.DateTimeField(default=datetime.datetime(2023, 8, 10, 15, 53, 1, 687266))),
                ('alias', models.CharField(max_length=20, null=True, unique=True)),
                ('customer', models.CharField(blank=True, db_column='stripe_customer_id', max_length=100, null=True)),
            ],
            options={
                'db_table': 'transaction',
            },
        ),
    ]
