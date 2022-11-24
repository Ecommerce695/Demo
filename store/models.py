from django.db import models
import datetime
from django.contrib.auth.models import AbstractUser



class UserProfile(AbstractUser):
    id = models.AutoField(primary_key=True, db_column='user_id')
    first_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    username = models.CharField(max_length=200,unique=True)
    mobile_number = models.PositiveBigIntegerField(blank=True, null=True)
    email = models.EmailField(unique=True, max_length=40, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    date_joined =models.DateTimeField(default=datetime.datetime.now())
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_profile'
        ordering = ['id']


class Role(models.Model):
    role_id =models.AutoField(primary_key=True)
    role = models.CharField(unique=True, max_length=40,blank=True, null=True)
    role_desc = models.CharField(max_length=255, null=True)

    class Meta: 
        db_table = 'role'

class UserRole(models.Model):
    role_id = models.IntegerField( db_column='role_id')
    user_id = models.IntegerField(db_column='user_id')

    class Meta:
        db_table= 'user_role'
        unique_together = (('role_id', 'user_id'))

class KnoxAuthtoken(models.Model):
    digest = models.CharField(primary_key=True, max_length=128)
    created = models.DateTimeField()
    user = models.ForeignKey(UserProfile, models.CASCADE)
    expiry = models.DateTimeField(blank=True, null=True)
    token_key = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'knox_authtoken'

class AddressType(models.Model):
    type = models.CharField(primary_key=True, max_length=50)
    description = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = 'address_type'

class Category(models.Model):
    id = models.AutoField(primary_key=True, null=False, db_column='category_id')
    category_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'category'

    def __str__(self):
        return self.category_name


class UserAddress(models.Model):
    type = models.ForeignKey(AddressType, models.CASCADE, db_column='address_type', blank=True, null=True)
    user = models.ForeignKey('UserProfile', models.CASCADE, blank=True, null=True, db_column='user_id')
    name = models.CharField(max_length=200, blank=True, null=True)
    mobile_number = models.PositiveBigIntegerField(blank=True, null=True)
    address = models.CharField(db_column='house_no/plot_no', max_length=500, blank=True, null=True)  # Field renamed to remove unsuitable characters.
    near_by = models.CharField(max_length=100, blank=True, null=True)
    street_no = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'user_address'



class PasswordReset(models.Model):
    email = models.ForeignKey(UserProfile, models.CASCADE, db_column='email', blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'password_reset'


class OrgProfile(models.Model):
    id = models.AutoField(primary_key=True, db_column='org_id')
    user = models.ForeignKey(UserProfile, models.CASCADE, db_column='user_id', null=True)
    org_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    mobile = models.PositiveBigIntegerField(blank=True, null=True)
    tax_id = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=500, blank=True, null=True)
    state = models.CharField(max_length=500, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'org_profile'

    def __str__(self):
        return self.org_name

class Product(models.Model):
    id = models.AutoField(primary_key=True, db_column='product_id')
    user = models.ForeignKey(UserProfile, models.CASCADE, blank=True, null=True,db_column='user_id')
    category = models.ForeignKey(Category, models.CASCADE, blank=True, null=True)
    product_name = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    unit_price = models.FloatField(blank=True, null=True)
    dis_price = models.FloatField(blank=True, null=True, db_column='discount_price')
    available_qty = models.PositiveIntegerField(default=0,blank=True, null=True)

    class Meta:
        db_table = 'product'
        ordering = ['id']

    def __str__(self):
        return self.product_name


class ProductLaptop(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, db_column='product_id')
    brand = models.CharField(max_length=255, db_column='brand_name', null=True, blank=True)
    series = models.CharField(max_length=255, null=True, blank=True)
    device_spec = models.TextField(blank =True, null=True, db_column='device_specifications')
    display_spec = models.TextField(blank=True, null=True,db_column='display_specifications')
    storage_spec = models.TextField(blank=True, null=True,db_column='storage_specifications')
    other_spec = models.TextField(blank=True, null=True,db_column='other_specifications')
    release_date = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'product_laptop'

    

class Cart(models.Model):
    id = models.AutoField(primary_key=True,db_column='cart_id')
    user = models.ForeignKey('UserProfile', models.CASCADE, blank=True, null=True, db_column='user_id')
    product = models.ForeignKey(Product,db_column='product_id',on_delete=models.CASCADE,blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    cart_value = models.FloatField(blank=True,default=0, db_column='total_cart_value')
    created_at = models.DateTimeField(default=datetime.datetime.now())
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'user_cart'

class ProductMobile(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, db_column='product_id')
    model_number = models.CharField(max_length=200, blank=True, null=True)
    model_name = models.CharField(max_length=200, blank=True, null=True)
    storage_spec = models.TextField( blank=True, null=True,db_column='storage_specifications')
    battery_spec = models.TextField( blank=True, null=True,db_column='battery_specifications')
    device_spec = models.TextField( blank=True, null=True,db_column='device_specifications')
    camera_spec = models.TextField( blank=True, null=True,db_column='camera_specifications')
    other_spec = models.TextField( blank=True, null=True,db_column='other_specifications')
    release_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'product_mobile'



class Wishlist(models.Model):
    user = models.ForeignKey(UserProfile, models.CASCADE, blank=True, null=True, db_column='user_id')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_wishlist'


class Search_History(models.Model):
    id = models.AutoField(primary_key=True,db_column = 'search_id')
    user = models.ForeignKey(UserProfile,on_delete = models.CASCADE, db_column='user_id')
    search_item = models.CharField(max_length = 100, null= True, blank=True)
    created_at = models.DateTimeField(default = datetime.datetime.now())

    class Meta:
        db_table = 'search_history'

class Reviews(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='user_id',  null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    comments = models.TextField()
    rating = models.FloatField()
    images = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'product_reviews'

