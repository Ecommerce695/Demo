from django.db import models
import datetime

# Create your models here.
class Order(models.Model):

    id = models.AutoField(primary_key=True, db_column='order_id')
    user = models.IntegerField(db_column='user_id')
    order_price = models.FloatField()
    billing = models.PositiveIntegerField(db_column='billing_address',null=True,blank=True)
    delivery = models.PositiveIntegerField(db_column='delivery_address',null=True,blank=True)
    payment_type = models.CharField(max_length=100, default='',db_column='type_of_payment')
    created_at = models.DateTimeField(default=datetime.datetime.now())
    
    class Meta:
        db_table = 'orders'

class OrderItemHistory(models.Model):
   
    data = datetime.datetime.now()+datetime.timedelta(days=5)

    id  = models.AutoField(primary_key=True, db_column='order_item_id')
    order = models.IntegerField(db_column='order_id')
    user = models.IntegerField(db_column='user_id')
    product = models.IntegerField(db_column='product_id')
    variant = models.IntegerField(db_column='variant_id',null=True)
    alias=models.CharField(max_length=100, unique=True, default='')
    quantity = models.PositiveIntegerField()
    order_status = models.CharField(max_length=50, default='')
    item_price = models.FloatField()
    shipment_charge = models.FloatField(db_column='shipment_charge',default=0)
    shipment_status = models.CharField(max_length=50, default='')
    created_at = models.DateTimeField(default=datetime.datetime.now())
    updated_at = models.DateTimeField(auto_now=True)
    delivery_date = models.DateTimeField(default=data)
    
    class Meta:
        db_table = 'order_item_history'

class OrderDeliverySuccess(models.Model):
    id = models.AutoField(primary_key=True)
    order_item = models.ForeignKey('OrderItemHistory', models.CASCADE, db_column='order_item_id')
    order_price = models.FloatField()
    delivered_date = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'order_delivery_success'

class OrderCancelled(models.Model):
    id = models.AutoField(primary_key=True)
    order_item = models.ForeignKey('OrderItemHistory', models.CASCADE, db_column='order_item_id')
    order_price = models.FloatField()
    payment_type = models.CharField(max_length=100, default='')
    reason_for_cancel = models.TextField()
    cancel_date = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'order_cancelled'

class OrderReturn(models.Model):
    id = models.AutoField(primary_key=True)
    order_item = models.ForeignKey('OrderItemHistory', models.CASCADE, db_column='order_item_id')
    order_price = models.FloatField()
    payment_type = models.CharField(max_length=100, default='')
    reason_for_return = models.TextField()
    return_date = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'order_return'


class OrderItemRefund(models.Model):
    id = models.AutoField(primary_key=True)
    orderitemid = models.ForeignKey('OrderItemHistory', models.CASCADE, db_column='order_item_id',null=True,blank=True)
    refund = models.CharField(max_length=100,db_column='stripe_refund_id',null=True,blank=True)
    status = models.CharField(max_length=100, db_column='refund_status',default='')
    transaction_id = models.CharField(max_length=100,db_column='stripe_transaction_id',null=True,blank=True)
    refund_amount = models.FloatField()
    currency = models.CharField(max_length=100,db_column='currency_type',null=True,blank=True)
    recieptno = models.CharField(max_length=100,db_column='stripe_reciept_no',null=True,blank=True)
    created_at  = models.DateTimeField(default=datetime.datetime.now())
    alias=models.CharField(max_length=20,unique=True, null=True)

    class Meta:
        db_table = 'order_refund'



class viewhistory(models.Model):
    id = models.AutoField(primary_key=True,db_column='id')
    product = models.PositiveIntegerField(db_column='product_id')
    variant = models.PositiveIntegerField(db_column='variant_id', null=True)
    user = models.PositiveIntegerField(db_column='user_id')
    quantity = models.PositiveIntegerField(db_column='quantity')
    totalvalue = models.FloatField(db_column='total_value',null=True,blank=True)
    price = models.FloatField(db_column='price',null=True,blank=True)
    address = models.PositiveIntegerField(db_column='address_id',blank=True,null=True)
    is_delivered = models.BooleanField(default='False')

    class Meta:
        db_table = 'pre_checkout_history'
