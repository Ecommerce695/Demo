from django.db import models
import datetime
from datetime import timedelta

#------------ New Tables for Order and Payment

expired_at = datetime.datetime.now()+timedelta(minutes=30)
class Transaction_table(models.Model):
    id = models.AutoField(primary_key=True,db_column='transaction_id')
    transaction = models.CharField(max_length=100,db_column='session_id',null=True,blank=True)
    status = models.CharField(max_length=100,db_column='payment_status',null=True,blank=True)
    user = models.PositiveIntegerField(db_column='user_id', null=True)
    order = models.PositiveIntegerField(db_column='order_id', null=True)
    orderitem = models.PositiveIntegerField(db_column='order_item_id', null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    updated_at = models.DateTimeField(auto_now=True)
    expired_at = models.DateTimeField(default=expired_at)
    alias=models.CharField(max_length=20,unique=True, null=True)
    customer = models.CharField(max_length=100,db_column='stripe_customer_id',null=True,blank=True)

    class Meta:
        db_table = 'transaction'





class Payment_details_table(models.Model):
    id = models.AutoField(primary_key=True,db_column='payment_id')
    payment = models.CharField(max_length=100,db_column='stripe_payment_intent_id',null=True,blank=True)
    paymenttype = models.CharField(max_length=100,db_column='payment_type',null=True,blank=True)
    amount = models.FloatField(db_column='transaction_amount',null=True,blank=True)
    invoice = models.CharField(max_length=100,db_column='invoice_id',null=True,blank=True)
    currency = models.CharField(max_length=100,db_column='currency_type',null=True,blank=True)
    orderitem = models.PositiveIntegerField(db_column='order_item_id', null=True)
    status = models.CharField(max_length=100,db_column='payment_status',null=True,blank=True)
    charge_id = models.CharField(max_length=100,db_column='stripe_charge_id',null=True,blank=True)
    paymentmethodid = models.CharField(max_length=100,db_column='stripe_paymentmethod_id',null=True,blank=True)
    transaction_id = models.CharField(max_length=100,db_column='stripe_transaction_id',null=True,blank=True)
    reciept = models.CharField(max_length=100,db_column='stripe_reciept_id',null=True,blank=True)
    invoiceno = models.CharField(max_length=100,db_column='stripe_invoice_number',null=True,blank=True)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    updated_at = models.DateTimeField(auto_now=True)
    alias=models.CharField(max_length=20,unique=True, null=True)

    class Meta:
        db_table = 'payment_details'
