from rest_framework import serializers
from rest_framework import  status
from super_admin.models import CompanyProfile, Product, ProductMobile, ProductLaptop,variants


###########  Vendor_org_register  #########

class VendorOrgRegistration(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['org_name','email','mobile','tax_id','description','address','city','state','pincode','country']


class VendorOrgupdate(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['org_name','description','address','city','state','pincode','country']


class vecomapanyemailserializer(serializers.Serializer):
    email = serializers.EmailField()


class vecomapanymobileserializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['mobile']



class vecomapanytaxidserializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['tax_id']

class vendorActivateAccountSerializer(serializers.Serializer):
    otp = serializers.IntegerField()



class vendorResetActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Check for email in DB
        if not CompanyProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError({"message":"This Email is Not Registered"})
        else:
            return value



class VendorActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CompanyProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError("This Email is Not Registered")
        else:
            return value


class ProductSerilaizer(serializers.Serializer):

    PRODUCT_STATUS_PUBLISH = 'Publish'
    PRODUCT_STATUS_DRAFT = 'Draft'
    STATUS_CHOICES =[
        (PRODUCT_STATUS_PUBLISH,'Publish'),
        (PRODUCT_STATUS_DRAFT,'Draft')
    ]
    
    PRODUCT_TYPE_GADGET = 'Gadgets'
    PRODUCT_TYPE_ACCESSORIES = 'Accessories'
    PRODUCT_TYPE_ELECTRONICS = 'Electronics'
    TYPE_CHOICES =[
        (PRODUCT_TYPE_GADGET, 'Gadgets'),
        (PRODUCT_TYPE_ACCESSORIES, 'Accessories'),
        (PRODUCT_TYPE_ELECTRONICS, 'Electronics')
    ]

    title = serializers.CharField()
    description = serializers.CharField()
    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    brand = serializers.CharField()
    sale = serializers.BooleanField()
    new = serializers.BooleanField()
    category = serializers.CharField()
    dimensions = serializers.CharField()
    weight = serializers.FloatField()
    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    charge_checked = serializers.BooleanField()
    warranty = serializers.BooleanField()
    warranty_file= serializers.FileField(default='')
    warranty_months = serializers.IntegerField(default=0)
    collection = serializers.CharField()
    price = serializers.IntegerField()
    discount = serializers.IntegerField(default=0)
    quantity = serializers.IntegerField()
    sku = serializers.CharField(default='')
    color = serializers.CharField()
    variant_images = serializers.ListField()
    
  
class ProductDetailsUpdate(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields =('title','description','type','brand','sale','new','category','dimensions','weight','status','is_wattanty','warranty_path','warranty_months')
        extra_kwargs = {
            "warranty_path" : {
                "required" : False
            }
        }

class VariantDetailsUpdate(serializers.ModelSerializer):
    class Meta:
        model = variants
        fields =('price','discount','quantity','sku','color')
        # extra_kwargs = {
        #     "warranty_path" : {
        #         "required" : False
        #     }
        # }
        
# class VariantDetailUpdate(serializers.Serializer):


class product_variant(serializers.Serializer):
    price = serializers.IntegerField()
    discount = serializers.IntegerField()
    quantity = serializers.IntegerField()
    sku = serializers.CharField(default='')
    color = serializers.CharField()
    images = serializers.ListField()

    collection = serializers.CharField()
    size = serializers.CharField(default='')
    color = serializers.CharField()
    path = serializers.ImageField()


class MobileSpecification(serializers.ModelSerializer):
    class Meta:
        model = ProductMobile
        fields = ['model_number','model_name','storage_spec','battery_spec','device_spec','camera_spec','other_spec']


class LaptopSpecification(serializers.ModelSerializer):
    class Meta:
        model = ProductLaptop
        fields = ['brand','series','storage_spec','display_spec','device_spec','other_spec']


class CategoryBasedProductPagination(serializers.Serializer):
    category = serializers.CharField(default='')
    pageno = serializers.CharField(default=1)


class seri_colour(serializers.Serializer):
    colour = serializers.CharField()
    pageno = serializers.CharField(default=1)


class ven_search(serializers.Serializer):
    search_item = serializers.CharField()


class price_seri(serializers.Serializer):
    min_price = serializers.IntegerField()
    max_price = serializers.IntegerField()


class date_seri(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()



class vend_prod_seri(serializers.Serializer):
    name=serializers.CharField(default='')
    category = serializers.CharField(default='')
    brand=serializers.CharField(default='')
    type=serializers.CharField(default='')
    price_from=serializers.IntegerField(default=0)
    price_to=serializers.IntegerField(default=1000000000)
    from_date=serializers.CharField(default='')
    to_date=serializers.CharField(default='')
    pageno = serializers.IntegerField(default=1)



class vend_orde_seri(serializers.Serializer):
    order_id=serializers.CharField(default='')
    payment_status=serializers.CharField(default='')
    order_status=serializers.CharField(default='')
    shipment_status = serializers.CharField(default='')
    from_date=serializers.CharField(default='')
    to_date=serializers.CharField(default='')
    pageno = serializers.IntegerField(default=1)


class vend_sales_seri(serializers.Serializer):
    order_id=serializers.CharField(default='')
    transaction_id=serializers.CharField(default='')
    invoice_id=serializers.CharField(default='')
    delivery_status=serializers.CharField(default='')
    from_date=serializers.CharField(default='')
    to_date=serializers.CharField(default='')
    pageno = serializers.IntegerField(default=1)