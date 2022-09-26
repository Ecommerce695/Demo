from rest_framework import serializers
from store.models import CustomerProfile, Wishlist
from rest_framework import serializers , validators
from django.contrib.auth.hashers import make_password


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ('username', 'password', 'email', 'first_name','last_name','mobile_number')

        extra_kwargs = {
            "password" : {"write_only" : True},
            "email" : {
                "required" : True,
                "allow_blank" : False,
                "validators" : [
                    validators.UniqueValidator(
                        CustomerProfile.objects.all(), "Email Id already Exists"
                    )
                ]
            },
            "mobile" : {
                "required" : True,
                "allow_blank" : False,
                "validators" : [
                    validators.UniqueValidator(
                        CustomerProfile.objects.all(), "Mobile Number already Exists"
                    )
                ]
            }
            
        }

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        email = validated_data.get('email')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        mobile = validated_data.get('mobile_number')

        user = CustomerProfile.objects.create(
            username = username,
            password = make_password(password),
            email = email,
            first_name = first_name,
            last_name = last_name,
            mobile_number = mobile
        )

        user.save()
        return user


class UserprofileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['first_name','last_name','email','mobile_number']


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['customer', 'product_id', 'price']

        