from rest_framework import serializers
from customer.models import UserProfile, UserAddress
from super_admin.models import Category,Product
from rest_framework import serializers, validators

class RegisterSerializer(serializers.ModelSerializer):
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
            is_superuser = False
        )
        user.save()
        return user
        

class ActivateAccountSerializer(serializers.Serializer):
    otp = serializers.IntegerField()

class ResetActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    if username != '' or password != '':
        pass
    else:
        raise serializers.ValidationError({"message" : "Enter Username or Password"})

class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()

# Below Serializer to Update Email 
class Useremailserializer(serializers.Serializer):
    email = serializers.EmailField()


# Below Serializer to Update Username 
class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username']


# Below Serializer to Update Mobile Number 
class Usermobileserializer(serializers.Serializer):
    mobile_number = serializers.IntegerField()


class Userotpactivateserializer(serializers.Serializer):
    otp = serializers.IntegerField()

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Check for email in DB
        if not UserProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError({"message":"This Email is Not Registered"})
        else:
            return value
            


class ConfirmPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length = 255)
    confirmPassword = serializers.CharField(max_length =255)

    def validate(self, data):
        password = data['password']
        confirmPassword = data['confirmPassword']

        if password != confirmPassword:
            raise serializers.ValidationError({"message":"Password Fields didn't Match"})
        else: 
            return data

class UpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

class UserAddressSerializer(serializers.Serializer):
    type = serializers.CharField()
    name = serializers.CharField()
    mobile = serializers.IntegerField()
    address = serializers.CharField()
    landmark = serializers.CharField()
    area = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    country = serializers.CharField()
    pincode = serializers.IntegerField()
    is_default = serializers.BooleanField()

class UpdateAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ('type','name','mobile','address','landmark','area','city','state','country','pincode','is_default')
        extra_kwargs = {
            "is_default" : {"required" : False}
            }


class useraddressdelete(serializers.Serializer):
    type = serializers.CharField()
                    


class WishlistSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    variant = serializers.IntegerField()
    pageno = serializers.CharField(default=1)

class PaginationSerializer(serializers.Serializer):
    pageno = serializers.CharField(default=1)

class SearchSerializer(serializers.Serializer):
    search_item = serializers.CharField()
    pageno = serializers.CharField(default=1)


class ca_products(serializers.Serializer):
    category = serializers.CharField()

class reviewserializer(serializers.Serializer):
    orderitem_id = serializers.IntegerField()
    comments = serializers.CharField()
    rating = serializers.FloatField()
    images = serializers.FileField()


class productsserializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['_all_']


# class CategoryBasedProductsSerializer(serializers.Serializer):

#     CATEGORY_CHOICES = (
#         ('Mobiles', 'Mobiles'),
#         ('Laptops', 'Laptops'),
#         ('Gadgets','Gadgets')
#     )

#     category = serializers.ChoiceField(choices=CATEGORY_CHOICES)

#     def validate_category(self, category):
#         if not Category.objects.filter(category_name__iexact = category).exists():
#             raise serializers.ValidationError({"message":"Product Does't exists"})
#         else:
#             return category


class previlage(serializers.Serializer):
    userid  = serializers.IntegerField()


class roleadding(serializers.Serializer):
    userid  = serializers.IntegerField()
    userrole = serializers.CharField()

class ProductSerializer(serializers.Serializer):
    pincode = serializers.CharField(default='')

class CategoryBasedProductPagination(serializers.Serializer):
    category = serializers.CharField(default='')
    pageno = serializers.CharField(default=1)

class GetEstDeliveryDate(serializers.Serializer):
    product_id= serializers.IntegerField()
    pincode = serializers.IntegerField()

class OrderSerializer(serializers.Serializer):
    orderitem=serializers.IntegerField()