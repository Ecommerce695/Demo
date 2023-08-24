from django.db import models
from super_admin.models import Product, variants
from customer.models import UserProfile
import datetime
# Create your models here.
    

class Cart(models.Model):
    id = models.AutoField(primary_key=True,db_column='cart_id')
    user = models.ForeignKey(UserProfile, models.CASCADE, blank=True, null=True, db_column='user_id')
    product = models.ForeignKey(Product,db_column='product_id',on_delete=models.CASCADE,blank=True, null=True)
    # variant = models.ForeignKey(variants, on_delete=models.CASCADE,  null=True)
    variant = models.PositiveIntegerField(null=True)
    quantity = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=False)
    sku = models.CharField(max_length=1000,null=True)
    size = models.CharField(max_length=100, null=True)
    color = models.CharField(max_length=100, null=True)
    src = models.CharField(max_length=1000, null=True)
    brand =models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=100, null=True)
    discount = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    cart_value = models.FloatField(blank=True,default=0, db_column='total_cart_value')
    created_at = models.DateTimeField(default=datetime.datetime.now())
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_cart'
