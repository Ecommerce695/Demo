from .models import User_profile
from rest_framework import serializers

class UserprofileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_profile
        fields = ['first_name','last_name','email','mobile']

# class User_addressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = user_address
#         fields = ['address','city','state','country','zip','mobile','address_type']

        
        