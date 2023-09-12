from rest_framework import serializers, validators
from rest_framework import serializers
from customer.models import UserProfile
from super_admin.models import CompanyProfile,Product,ProductLaptop,ProductMobile,Category,variants


class AdminRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'password', 'email', 'first_name','last_name','mobile_number')
        extra_kwargs = {
            "password" : {"write_only" : True},
            "email" : {
                "required" : True,
                "allow_blank" : False,
                "validators" : [
                    validators.UniqueValidator(
                        UserProfile.objects.all(), "Email Id already Exists"
                    )
                ]
            },
            "mobile" : {
                "required" : True,
                "validators" : [
                    validators.UniqueValidator(
                        UserProfile.objects.all(), "Mobile Number already Exists"
                    )
                ]
            }
        }
    def create(self,validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        email = validated_data.get('email').lower()
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        mobile = validated_data.get('mobile_number')

        user = UserProfile.objects.create_user(
            username = username,
            password = password,
            email = email,
            mobile_number = mobile,
            first_name=first_name,
            last_name=last_name,
            is_staff = False,
            is_superuser = False,
            is_active = True
        )
        user.save()
        return user

class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    if username != '' or password != '':
        pass
    else:
        raise serializers.ValidationError({"message" : "Enter Username or Password"})


class Admin_org_serializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['org_name','email','mobile','tax_id','description','address','city','state','pincode','country']


class AdminOrgupdate(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['org_name','description','address','city','state','pincode','country']


class comapanyemailserializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['email']


class comapanymobileserializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['mobile']



class comapanytaxidserializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['tax_id']



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

class drop_mobile(serializers.ModelSerializer):
    class Meta:
        model = ProductMobile
        fields = ['model_number','model_name','storage_spec','battery_spec','device_spec','camera_spec','other_spec']


class drop_laptop(serializers.ModelSerializer):
    class Meta:
        model = ProductLaptop
        fields = ['brand','series','storage_spec','display_spec','device_spec','other_spec']


class admin_category(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']

class admin_variant(serializers.Serializer):
    collection = serializers.CharField()
    size = serializers.CharField(default='')
    color = serializers.CharField()
    path = serializers.ImageField()


class DateFilter(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    
class ProductNameFilter(serializers.Serializer):
    name = serializers.CharField()
    
class ProductCategoryFilter(serializers.Serializer):
    category = serializers.CharField()
    
class ProductPriceFilter(serializers.Serializer):
    from_price = serializers.IntegerField()
    to_price = serializers.IntegerField()
    
class ProductColorFilter(serializers.Serializer):
    color = serializers.CharField()
    
class ProductTypeFilter(serializers.Serializer):
    type = serializers.CharField()
    
class ProductAvailabeFilter(serializers.Serializer):
    is_available = serializers.BooleanField()
    
class ProductDiscountFilter(serializers.Serializer):
    discount = serializers.IntegerField()

class OrderIdFilter(serializers.Serializer):
    id = serializers.IntegerField()

class OrderPaymentStatusFilter(serializers.Serializer):
    status = serializers.CharField()

class OrderStatusFilter(serializers.Serializer):
    status = serializers.CharField()


class SalesOrderIDFilter(serializers.Serializer):
    id= serializers.IntegerField()

class SalesTxnIDFilter(serializers.Serializer):
    id = serializers.IntegerField()

class SalesInvoiceIDFilter(serializers.Serializer):
    id = serializers.CharField()

class SalesDeliveryStatusFilter(serializers.Serializer):
    status = serializers.CharField()

class AdminProductsFilter(serializers.Serializer):
    name=serializers.CharField(default='')
    category = serializers.CharField(default='')
    brand=serializers.CharField(default='')
    type=serializers.CharField(default='')
    price_from=serializers.IntegerField(default=0)
    price_to=serializers.IntegerField(default=1000000000)
    from_date=serializers.CharField(default='')
    to_date=serializers.CharField(default='')
    pageno = serializers.IntegerField(default=1)

class AdminUsersFilter(serializers.Serializer):
    is_active=serializers.CharField(default='')
    email=serializers.EmailField(default='')
    from_date=serializers.CharField(default='')
    to_date=serializers.CharField(default='')
    pageno = serializers.IntegerField(default=1)

class AdminVendorsFilter(serializers.Serializer):
    is_active=serializers.CharField(default='')
    org_name=serializers.CharField(default='')
    tax_status=serializers.CharField(default='')
    email=serializers.EmailField(default='')
    from_date=serializers.CharField(default='')
    to_date=serializers.CharField(default='')
    pageno = serializers.IntegerField(default=1)

class AdminOrderFilter(serializers.Serializer):
    order_id=serializers.CharField(default='')
    payment_status=serializers.CharField(default='')
    order_status=serializers.CharField(default='')
    shipment_status = serializers.CharField(default='')
    from_date=serializers.CharField(default='')
    to_date=serializers.CharField(default='')
    pageno = serializers.IntegerField(default=1)

class AdminSalesFilter(serializers.Serializer):
    order_id=serializers.CharField(default='')
    transaction_id=serializers.CharField(default='')
    invoice_id=serializers.CharField(default='')
    delivery_status=serializers.CharField(default='')
    from_date=serializers.CharField(default='')
    to_date=serializers.CharField(default='')
    pageno = serializers.IntegerField(default=1)

# class AdminOrderTabFilter(serializers.Serializer):
#     order_id=serializers.CharField(default='')
#     from_date=serializers.CharField(default='')
#     to_date=serializers.CharField(default='')
class OrderSerializer(serializers.Serializer):
    orderitem=serializers.IntegerField()