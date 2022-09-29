# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AddressType(models.Model):
    type = models.CharField(primary_key=True, max_length=20)
    description = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'address_type'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user = models.OneToOneField('CustomerProfile', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'authtoken_token'


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    quantity = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    customer = models.ForeignKey('CustomerProfile', models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey('Product', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cart'


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'category'


class CustomerAddress(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=40, blank=True, null=True)
    mobile_number = models.BigIntegerField(blank=True, null=True)
    house_no_plot_no = models.CharField(db_column='house_no/plot_no', max_length=30, blank=True, null=True)  # Field renamed to remove unsuitable characters.
    near_by = models.CharField(max_length=30, blank=True, null=True)
    street_no = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    postal_code = models.IntegerField(blank=True, null=True)
    customer = models.ForeignKey('CustomerProfile', models.DO_NOTHING, blank=True, null=True)
    type = models.ForeignKey(AddressType, models.DO_NOTHING, db_column='type', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer_address'


class CustomerProfile(models.Model):
    customer_id = models.UUIDField(primary_key=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    username = models.CharField(unique=True, max_length=50)
    mobile_number = models.BigIntegerField(blank=True, null=True)
    email = models.CharField(unique=True, max_length=40, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateTimeField()
    last_login = models.DateTimeField()
    is_active = models.BooleanField()
    is_staff = models.BooleanField()
    is_superuser = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'customer_profile'


class CustomerProfileGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    customerprofile = models.ForeignKey(CustomerProfile, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'customer_profile_groups'
        unique_together = (('customerprofile', 'group'),)


class CustomerProfileUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    customerprofile = models.ForeignKey(CustomerProfile, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'customer_profile_user_permissions'
        unique_together = (('customerprofile', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(CustomerProfile, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class KnoxAuthtoken(models.Model):
    digest = models.CharField(primary_key=True, max_length=128)
    created = models.DateTimeField()
    user = models.ForeignKey(CustomerProfile, models.DO_NOTHING)
    expiry = models.DateTimeField(blank=True, null=True)
    token_key = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'knox_authtoken'


class OrderItems(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Orders', models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey('Product', models.DO_NOTHING, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_items'


class OrderStatus(models.Model):
    order_status_code = models.AutoField(primary_key=True)
    description = models.CharField(max_length=230, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_status'


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(CustomerProfile, models.DO_NOTHING, blank=True, null=True)
    order_status_code = models.ForeignKey(OrderStatus, models.DO_NOTHING, db_column='order_status_code', blank=True, null=True)
    tracking_id = models.IntegerField(blank=True, null=True)
    payment_id = models.IntegerField(blank=True, null=True)
    order_value = models.IntegerField(blank=True, null=True)
    customer_email = models.CharField(max_length=30, blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    billing_address = models.CharField(max_length=50, blank=True, null=True)
    shipping_address = models.CharField(max_length=50, blank=True, null=True)
    cancel_policy = models.CharField(max_length=40, blank=True, null=True)
    is_order_placed = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'


class PasswordReset(models.Model):
    id = models.BigAutoField(primary_key=True)
    token = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField()
    email = models.ForeignKey(CustomerProfile, models.DO_NOTHING, db_column='email', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'password_reset'


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=40, blank=True, null=True)
    description = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    unit_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, models.DO_NOTHING, blank=True, null=True)
    vendor = models.ForeignKey('VendorProfile', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product'


class ProductLaptop(models.Model):
    id = models.BigAutoField(primary_key=True)
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
    release_date = models.DateField()
    product = models.ForeignKey(Product, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_laptop'


class ProductMobile(models.Model):
    id = models.BigAutoField(primary_key=True)
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
    release_date = models.DateField()
    product = models.ForeignKey(Product, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_mobile'


class ProductSaleDetails(models.Model):
    description = models.CharField(max_length=250)
    price = models.FloatField(blank=True, null=True)
    discount_price = models.FloatField(blank=True, null=True)
    product_availability = models.IntegerField(blank=True, null=True)
    product = models.ForeignKey(Product, models.DO_NOTHING)
    vendor = models.ForeignKey('VendorProfile', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_sale_details'


class VendorProfile(models.Model):
    vendor_id = models.UUIDField(primary_key=True)
    org_id = models.CharField(max_length=30, blank=True, null=True)
    username = models.CharField(unique=True, max_length=50)
    full_name = models.CharField(max_length=40, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    org_name = models.CharField(max_length=100, blank=True, null=True)
    email_id = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.BigIntegerField(blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=40, blank=True, null=True)
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'vendor_profile'


class Wishlist(models.Model):
    id = models.BigAutoField(primary_key=True)
    price = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    customer = models.ForeignKey(CustomerProfile, models.DO_NOTHING, blank=True, null=True)
    product_id = models.ForeignKey(Product, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'wishlist'


class YetToShip(models.Model):
    order = models.ForeignKey(Orders, models.DO_NOTHING, blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    ship_to_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'yet_to_ship'
