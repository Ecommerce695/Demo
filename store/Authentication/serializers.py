from store.models import User_profile
from rest_framework import serializers , validators
from django.contrib.auth.hashers import make_password


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_profile
        fields = ('username', 'password', 'email', 'first_name','last_name','mobile')

        extra_kwargs = {
            "password" : {"write_only" : True},
            "email" : {
                "required" : True,
                "allow_blank" : False,
                "validators" : [
                    validators.UniqueValidator(
                        User_profile.objects.all(), "Email Id already Exists"
                    )
                ]
            },
            "mobile" : {
                "required" : True,
                "allow_blank" : False,
                "validators" : [
                    validators.UniqueValidator(
                        User_profile.objects.all(), "Mobile Number already Exists"
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
        mobile = validated_data.get('mobile')

        user = User_profile.objects.create(
            username = username,
            password = make_password(password),
            email = email,
            first_name = first_name,
            last_name = last_name,
            mobile = mobile
        )

        user.save()
        return user
