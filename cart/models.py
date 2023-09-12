from django.db import models
from super_admin.models import Product, variants
from customer.models import UserProfile
import datetime
# Create your models here.
    

class Cart(models.Model):
    id = models.AutoField(primary_key=True,db_column='cart_id')
    user = models.ForeignKey(UserProfile, models.CASCADE, blank=True, null=True, db_column='user_id')
    product = models.ForeignKey(Product,db_column='product_id',on_delete=models.CASCADE,blank=True, null=True)
    variant = models.PositiveIntegerField(null=True)
    quantity = models.IntegerField(blank=True, null=True)
    cart_value = models.FloatField(blank=True,default=0, db_column='total_cart_value')
    created_at = models.DateTimeField(default=datetime.datetime.now())
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_cart'
