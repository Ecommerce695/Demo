from django.db import models
import datetime
from django.contrib.auth.models import AbstractUser
import uuid   


class CustomerProfile(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_column='customer_id')
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    username = models.CharField(max_length=50,unique=True)
    mobile_number = models.PositiveBigIntegerField(blank=True, null=True)
    email = models.CharField(unique=True, max_length=40, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    date_joined =models.DateTimeField(default=datetime.datetime.now())
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        db_table = 'customer_profile'

class AddressType(models.Model):
    type = models.CharField(primary_key=True, max_length=20)
    description = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'address_type'

class Category(models.Model):
    id = models.AutoField(primary_key=True, null=False, db_column='category_id')
    category_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'category'

class Product(models.Model):
    id = models.AutoField(primary_key=True, db_column='product_id')
    vendor = models.ForeignKey('VendorProfile', models.DO_NOTHING, blank=True, null=True)
    category = models.ForeignKey(Category, models.DO_NOTHING, blank=True, null=True)
    product_name = models.CharField(max_length=40, blank=True, null=True)
    description = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    unit_price = models.FloatField(blank=True, null=True)


    class Meta:
        db_table = 'product'

    def __str__(self):
        return self.product_name


class Cart(models.Model):
    id = models.AutoField(primary_key=True,db_column='cart_id')
    customer = models.ForeignKey('CustomerProfile', models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey(Product,db_column='product_id',on_delete=models.CASCADE,blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'cart'



class CustomerAddress(models.Model):
    type = models.ForeignKey(AddressType, models.CASCADE, db_column='type', blank=True, null=True)
    customer = models.ForeignKey('CustomerProfile', models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=40, blank=True, null=True)
    mobile_number = models.PositiveBigIntegerField(blank=True, null=True)
    address = models.CharField(db_column='house_no/plot_no', max_length=30, blank=True, null=True)  # Field renamed to remove unsuitable characters.
    near_by = models.CharField(max_length=30, blank=True, null=True)
    street_no = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    postal_code = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'customer_address'



class PasswordReset(models.Model):
    email = models.ForeignKey(CustomerProfile, models.CASCADE, db_column='email', blank=True, null=True)
    token = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'password_reset'


class ProductLaptop(models.Model):
    product = models.ForeignKey(Product, models.CASCADE)
    series = models.CharField(max_length=50, blank=True, null=True)
    screen_size = models.CharField(max_length=50, blank=True, null=True)
    colour = models.CharField(max_length=50, blank=True, null=True)
    hard_disk = models.CharField(max_length=30, blank=True, null=True)
    cpu_model = models.CharField(max_length=80, blank=True, null=True)
    ram = models.CharField(max_length=30, blank=True, null=True)
    operating_system = models.CharField(max_length=50, blank=True, null=True)
    graphics_processor = models.CharField(max_length=50, blank=True, null=True)
    graphics_card_description = models.CharField(max_length=50, blank=True, null=True)
    cpu_speed = models.CharField(max_length=30, blank=True, null=True)
    weight = models.CharField(max_length=30, blank=True, null=True)
    release_date = models.DateField(auto_now=True)

    class Meta:
        db_table = 'product_laptop'


class ProductMobile(models.Model):
    product = models.ForeignKey(Product, models.DO_NOTHING)
    product_name = models.CharField(max_length=100, blank=True, null=True)
    model_number = models.CharField(max_length=50, blank=True, null=True)
    display_size = models.CharField(max_length=50, blank=True, null=True)
    processor = models.CharField(max_length=50, blank=True, null=True)
    front_camera = models.CharField(max_length=50, blank=True, null=True)
    rear_camera = models.CharField(max_length=50, blank=True, null=True)
    colour = models.CharField(max_length=50, blank=True, null=True)
    ram = models.CharField(max_length=20, blank=True, null=True)
    storage_rom = models.CharField(max_length=20, blank=True, null=True)
    battery_capicity = models.CharField(max_length=20, blank=True, null=True)
    os = models.CharField(max_length=20, blank=True, null=True)
    weight = models.CharField(max_length=20, blank=True, null=True)
    release_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'product_mobile'


class ProductSaleDetails(models.Model):
    id = models.AutoField(primary_key=True)
    vendor = models.ForeignKey('VendorProfile', models.CASCADE)
    product = models.ForeignKey(Product, models.CASCADE)
    description = models.CharField(max_length=250)
    price = models.FloatField(max_length=30, blank=True, null=True)
    discount_price = models.FloatField(max_length=30, blank=True, null=True)
    product_availability = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'product_sale_details'


class VendorProfile(models.Model):
    vendor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org_id = models.CharField(max_length=30, blank=True, null=True)
    username = models.CharField(unique=True, max_length=50)
    full_name = models.CharField(max_length=40, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    org_name = models.CharField(max_length=100, blank=True, null=True)
    email_id = models.EmailField(max_length=50, blank=True, null=True)
    phone_number = models.PositiveBigIntegerField(blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=40, blank=True, null=True)
    date_joined = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'vendor_profile'

    def __str__(self):
        return self.username


class Wishlist(models.Model):
    customer = models.ForeignKey(CustomerProfile, models.CASCADE, blank=True, null=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wishlist'
