import datetime
from unicodedata import decimal
from django.db import models
from django.contrib.auth.models import AbstractUser

# Extending User Model as User_Profile and Some more fields 
class User_profile(AbstractUser):
    id = models.AutoField(primary_key=True,db_column='user_id')  
    username = models.CharField(max_length=100,unique=True) 
    first_name=models.CharField(max_length=250) 
    last_name=models.CharField(max_length=250)
    email=models.EmailField(max_length=250, unique=True) 
    mobile=models.CharField(max_length=15)
    age=models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    created_date =models.DateTimeField(default=datetime.datetime.now())
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        db_table = 'et_user_profile'

    # str function in a django model returns a string 
    # that is exactly rendered as the display name of instances for that model.
    def __str__(self):
        self.username

class Vendor_Profile(models.Model):
    id = models.AutoField(primary_key=True,db_column='vendor_id')
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    mobile = models.PositiveBigIntegerField()
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    password = models.CharField(max_length=50)
    created_date =models.DateTimeField(default=datetime.datetime.now())
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)

    class Meta:
        db_table = 'et_vendor_profile'

    # def __str__(self):
    #     return "%s"%self.username


class Vendor_Products(models.Model):
    user = models.ForeignKey(Vendor_Profile, on_delete=models.CASCADE, db_column='vendor_id',default=999)
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.FloatField()
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'et_vendor_products'

    def __str__(self):
        return "%s"%self.name



class Wishlist(models.Model):
    user = models.ForeignKey(User_profile, on_delete=models.CASCADE, db_column='user_id',null=False)
    product = models.ForeignKey(Vendor_Products, on_delete=models.CASCADE, db_column='product_id',null=False)
    created_at = models.DateField(auto_now=True)

    class Meta:
        db_table = 'et_wishlist'


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'et_category'

    def __str__(self):
        return "%s"%self.name

class Sub_Category(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = 'et_sub_category'

    def __str__(self):
        return "%s"%self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True, db_column='product_id')
    name = models.CharField(max_length=30, default='Product Name')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    sub_category = models.ForeignKey(Sub_Category, on_delete=models.CASCADE, default=1)
    quantity = models.PositiveSmallIntegerField(default=0)
    price = models.FloatField(max_length=10, default=0)
    description = models.TextField(null=True, default='')

    class Meta:
        db_table = 'et_products'

    def __str__(self):
        return "%s"%self.name


class Order(models.Model):
    user_id = models.ForeignKey(User_profile, on_delete=models.CASCADE,blank=False, null=False)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'et_order'

    def __str__(self):
        return "%s"%self.pk


class Cart(models.Model):
    user_id = models.ForeignKey(User_profile,on_delete=models.CASCADE, blank=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    qunatity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s"%self.pk

    class Meta:
        db_table = 'et_cart'
