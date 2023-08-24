from rest_framework import serializers
from rest_framework import  status
from super_admin.models import CompanyProfile, Product, ProductMobile, ProductLaptop


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


class vendor_products(serializers.Serializer):

    category = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    type = serializers.CharField()
    brand = serializers.CharField()
    price = serializers.FloatField()
    sale = serializers.BooleanField()
    discount = serializers.IntegerField(default=0)
    quantity = serializers.IntegerField()
    new = serializers.BooleanField()
    collection = serializers.CharField()
    size = serializers.CharField(default='')
    color = serializers.CharField()
    path = serializers.ImageField()
    dimensions = serializers.CharField(default='0.5X0.5X0.5')
    weight = serializers.FloatField(default='0.5')
    pageno = serializers.CharField(default=1)



class vend_products(serializers.Serializer):
    pageno = serializers.CharField(default=1)

class vendor_products_update(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['category','title','description','price','discount','dimensions','weight']



class product_variant(serializers.Serializer):
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