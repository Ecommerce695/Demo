from django.db import models
import datetime
from Ecomerce_project import settings

class Category(models.Model):

    id = models.AutoField(primary_key=True, null=False, db_column='category_id')
    category_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'category'

    def __str__(self):
        return self.category_name
    

class CompanyProfile(models.Model):

    TAX_STATUS_PENDING = 'Pending'
    TAX_STATUS_COMPLETED = 'Verified'
    TAX_STATUS_FAILED = 'Failed'
    TAX_CHOICES =[
        (TAX_STATUS_PENDING,'Pending'),
        (TAX_STATUS_COMPLETED,'Verified'),
        (TAX_STATUS_FAILED,'Failed')
    ]
    id = models.AutoField(primary_key=True, db_column='id')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, db_column='user_id', null=True)
    org_name = models.CharField(max_length=255, db_column='company_name', null=True)
    email = models.EmailField(unique=True,max_length=255, blank=True, null=True)
    mobile = models.PositiveBigIntegerField(unique=True,blank=True, null=True)
    tax_id = models.CharField(unique=True,max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True, db_column='company_description')
    address = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=500, blank=True, null=True)
    state = models.CharField(max_length=500, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateTimeField(default=datetime.datetime.now())
    tax_status = models.CharField(max_length=10, choices=TAX_CHOICES, default=TAX_STATUS_PENDING)    #<--Newly added field
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'company_profile'
        ordering = ['id']

class Product(models.Model):
    PRODUCT_STATUS_PUBLISH = 'Publish'
    PRODUCT_STATUS_DRAFT = 'Draft'
    STATUS_CHOICES =[
        (PRODUCT_STATUS_PUBLISH,'Publish'),
        (PRODUCT_STATUS_DRAFT,'Draft')
    ]
    id = models.AutoField(primary_key=True, db_column='product_id')
    title = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, default='')
    brand = models.CharField(max_length=100, default='')
    sale = models.BooleanField(default=False)
    new = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, blank=True, null=True,db_column='user_id')
    category_id = models.PositiveIntegerField(blank=True, null=True)
    category = models.CharField(max_length=100, default='')
    rating = models.FloatField(db_column='avg_rating',null=True,blank=True)
    is_active = models.BooleanField(default=False)
    alias=models.CharField(max_length=20,unique=True, null=True)
    dimensions = models.CharField(max_length=20, default="0.5X0.5X0.5",help_text = "Please use the following format: L X B X H and values should be greater than 0.5 cm")
    weight = models.FloatField(default=0.05,help_text = "The minimum chargeable weight is 0.5 Kg")
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default=PRODUCT_STATUS_DRAFT)
    is_charged = models.BooleanField(db_column='is_charged',default=False)
    shipping_charges = models.PositiveIntegerField(default=0)
    other_charges = models.PositiveIntegerField(default=0)
    is_wattanty = models.BooleanField(default=False)
    warranty_months = models.PositiveIntegerField(default=0)
    warranty_src = models.CharField(max_length=1000,null=True)
    warranty_path= models.ImageField(null=True, blank=True, upload_to='product/warranty/')
    created_at = models.DateTimeField(default=datetime.datetime.now())
    updated_at = models.DateTimeField(auto_now=True)

    # strproduct = models.CharField(max_length=50,db_column='stripe_product_id',default='')
    # strprice = models.CharField(max_length=50,db_column='stripe_price_id',default='')


    class Meta:
        db_table = 'product'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if self.id:
            self.alias = "PRO-" + str(self.id)
        super().save(*args, **kwargs)

class collection(models.Model):
    COLLECTION_ON_SALE = 'on sale'
    COLLECTION_NEW_PRODUCT = 'new product'
    COLLECTION_BEST_SELLER= 'best seller'
    COLLECTION_FEATURED = 'featured product'
    COLLECTION_CHOICES =[
        (COLLECTION_ON_SALE , 'on sale'),
        (COLLECTION_NEW_PRODUCT , 'new product'),
        (COLLECTION_BEST_SELLER, 'best seller'),
        (COLLECTION_FEATURED , 'featured product')
    ]
    id = models.PositiveIntegerField(db_column='product_id')
    collection_id = models.AutoField(primary_key=True)
    collection = models.CharField(max_length=20,choices=COLLECTION_CHOICES,default='')

    class Meta:
        db_table = 'collection'
        ordering = ['id']

class tags(models.Model):
    id = models.PositiveIntegerField(db_column='product_id')
    tag_id = models.AutoField(primary_key=True)
    tags = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'tags'
        ordering = ['id']

class variants(models.Model):
    variant_id = models.AutoField(primary_key=True)
    id = models.PositiveIntegerField(db_column='product_id')
    price = models.PositiveBigIntegerField(default=0)
    gst= models.PositiveIntegerField(default=18)
    selling_price = models.PositiveBigIntegerField(default=0)
    discount = models.PositiveIntegerField(blank=True)
    quantity = models.PositiveIntegerField(default=0, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0,blank=True, null=True)
    sku = models.CharField(max_length=1000,null=True)
    # size = models.CharField(max_length=100, default='')
    color = models.CharField(max_length=100, default='')
    image_id = models.IntegerField(null=True)

    class Meta:
        db_table = 'variants'

# class ProductWarranty(models.Model):
#     product = models.IntegerField(null=False,unique=True)
#     file = models.FileField(upload_to ='uploads/')
#     # warranty_timeline = models.DateField()
#     created_at = models.DateTimeField(default=datetime.datetime.now())


class images(models.Model):
    image_id = models.AutoField(primary_key=True)
    id = models.IntegerField(db_column='product_id')
    alt = models.CharField(max_length=100, null=True)
    src = models.CharField(max_length=1000, null=True)
    variant_id = models.PositiveIntegerField(null=True)
    path = models.ImageField(db_column='path', null=True, blank=True, upload_to='variants/images/')

    class Meta:
        db_table = 'images'


class ProductLaptop(models.Model):
    product = models.ForeignKey('Product', models.CASCADE, db_column='product_id',blank=True, null=True)
    brand = models.CharField(max_length=255, db_column='brand_name', null=True, blank=True)
    series = models.CharField(max_length=255, null=True, blank=True)
    device_spec = models.TextField(blank =True, null=True, db_column='device_specifications')
    display_spec = models.TextField(blank=True, null=True,db_column='display_specifications')
    storage_spec = models.TextField(blank=True, null=True,db_column='storage_specifications')
    other_spec = models.TextField(blank=True, null=True,db_column='other_specifications')
    release_date = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'product_laptop'


class ProductMobile(models.Model):
    product = models.ForeignKey('Product', models.CASCADE, db_column='product_id',blank=True, null=True)
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
