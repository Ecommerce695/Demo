from django.db import models
import datetime
from django.contrib.auth.models import AbstractUser
from super_admin.models import Product, variants

class UserProfile(AbstractUser):
    id = models.AutoField(primary_key=True, db_column='user_id')
    first_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    username = models.CharField(max_length=200,unique=True)
    mobile_number = models.PositiveBigIntegerField(unique=True, null=True)
    email = models.EmailField(unique=True, max_length=40, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    date_joined =models.DateTimeField(default=datetime.datetime.now())
    last_login = models.DateTimeField(auto_now=True)
    alias=models.CharField(max_length=20,unique=True, null=True)
    is_active = models.BooleanField(default=False)
    is_vendor_com_user = models.BooleanField(default=False)

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
    user = models.ForeignKey(UserProfile, models.CASCADE, null=True, blank=True, db_column='user_id')
    expiry = models.DateTimeField(blank=True, null=True)
    token_key = models.CharField(max_length=8, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'knox_authtoken'

class AddressType(models.Model):
    type = models.CharField(primary_key=True, max_length=50)
    description = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = 'address_type'


class UserAddress(models.Model):
    type = models.ForeignKey(AddressType, models.CASCADE, db_column='address_type', blank=True, null=True)
    # type = models.CharField(max_length=200, db_column='address_type', null=True, blank=True)
    user = models.ForeignKey(UserProfile, models.CASCADE, blank=True, null=True, db_column='user_id')
    name = models.CharField(max_length=200, blank=True, null=True)
    mobile = models.PositiveBigIntegerField(blank=True, null=True)
    address = models.CharField(db_column='house_no/plot_no', max_length=500, blank=True, null=True)
    landmark = models.CharField(max_length=100, blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True,db_column='pincode')
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_address'



# Rest Password Model
class Reset_Password(models.Model):
    user = models.IntegerField(db_column='user_id', null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.CharField(max_length = 50, blank=True, null=True)
    key = models.CharField(max_length=32, blank=True, null=False, db_column='key')
    created_at = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = 'reset_password'


custom_expiry_date = datetime.datetime.now()+datetime.timedelta(days=2)
class Account_Activation(models.Model):
    user = models.IntegerField(db_column='user_id', null=True)
    key = models.CharField(max_length=100, blank=True, null=True)
    otp = models.PositiveIntegerField()
    agent = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    expiry_date = models.DateTimeField(default=custom_expiry_date)
    email = models.CharField(max_length=50, null=True,blank=True,default='')

    class Meta:
        db_table = 'account_activation'

class avg_rating(models.Model):
    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    rating = models.FloatField(max_length=50)

    class Meta:
        db_table = 'avg_rating'



class Wishlist(models.Model):
    user = models.ForeignKey(UserProfile, models.CASCADE, blank=True, null=True, db_column='user_id')
    product = models.ForeignKey('super_admin.Product', on_delete=models.CASCADE,db_column='product_id')
    variant = models.PositiveIntegerField(null=True)
    title = models.CharField(max_length=1000, null=True)
    category = models.CharField(max_length=100, null=True)
    brand = models.CharField(max_length=100, null=True)
    sku = models.CharField(max_length=1000,null=True)
    size = models.CharField(max_length=100, null=True)
    color = models.CharField(max_length=100, null=True)
    src = models.CharField(max_length=1000, null=True)
    discount = models.PositiveIntegerField()
    type = models.CharField(max_length=1000, null=True)
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
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='user_id',  null=True, blank=True)
    product = models.ForeignKey('super_admin.Product', on_delete=models.CASCADE, db_column='product_id',null=True, blank=True)
    src = models.CharField(max_length=100, null=True)
    comments = models.TextField()
    rating = models.FloatField()
    images = models.ImageField(db_column='path', null=True, blank=True, upload_to='product/images/')
    oritemid = models.PositiveIntegerField(db_column='order_item_id',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'user_product_reviews'

class SaveForLater(models.Model):
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    variant = models.PositiveIntegerField(null=True)
    sku = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(UserProfile, on_delete= models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'save_for_later'