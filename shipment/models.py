from django.db import models
import datetime
from Ecomerce_project import settings

class shipment(models.Model):
    shipment_id = models.PositiveBigIntegerField(primary_key=True)
    order_item_id = models.PositiveIntegerField(null=True)
    shipment_order_id = models.PositiveBigIntegerField(null=True)
    return_shipment_id= models.PositiveBigIntegerField(null=True)
    awb_code=models.CharField(max_length=100,default='')
    return_awb_code = models.CharField(max_length=100,default='')
    return_shipment_order_id = models.PositiveBigIntegerField(null=True)
    order_amount = models.FloatField()
    pickup_address = models.PositiveIntegerField()
    shipping_address = models.PositiveIntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, db_column='user_id', null=True)
    order_date = models.DateTimeField()
    alias=models.CharField(max_length=20,unique=True, null=True)
    created_at=models.DateTimeField(default=datetime.datetime.now())
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'shipment'



