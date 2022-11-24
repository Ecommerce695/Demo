from rest_framework import serializers
from store.models import UserAddress, UserProfile, Role, UserRole
from rest_framework import serializers , validators
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.http import HttpResponse




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
                "allow_blank" : False,
                "validators" : [
                    validators.UniqueValidator(
                        UserProfile.objects.all(), "Mobile Number already Exists"
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

        user = UserProfile.objects.create_user(
            username = username,
            password = password,
            email = email,
            first_name = first_name,
            last_name = last_name,
            mobile_number = mobile
        )

        user.save()
        return user


class UserprofileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name','last_name','email','mobile_number']

class UserAddress(serializers.ModelSerializer):
    user = serializers.CharField(source = 'UserProfile.id')

    class Meta:
        model = UserAddress
        fields = ('type','user','name', 'mobile_number','address',
                    'near_by','street_no','city','state','country','postal_code')




class ResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['password']

        extra_kwargs = {
            "password" : {"write_only" : True}
        }

    def create(self, validated_data):
        password = validated_data.get('password')

        user = UserProfile.objects.update_user(
            password = password
        )

        user.save()
        return user

        



######################################################################################


##### Super_Admin register ######
class SuperAdminregisterserializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'password', 'email', 'mobile_number')

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
            }
        }


    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        email = validated_data.get('email')
        mobile_number = validated_data.get('mobile_number')

        user = UserProfile.objects.create_user(
            username = username,
            password = password,
            email = email,
            mobile_number = mobile_number,
            is_staff = False,
            is_superuser = False
        )
        user.save()
        user1 = user.id
        roles = Role.objects.get(role='SUPER_ADMIN')
        roles1 = roles.role_id
        user1 = UserRole.objects.create(role_id = roles1, user_id = user1)
        return user



##### Super_admin login #####
class SuperAdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        role = Role.objects.get(role='SUPER_ADMIN')
        role1 = role.role_id
        if user and user.is_active:
            user1 = user.id
            if(UserRole.objects.filter(role_id=role1).filter(user_id=user1)):
                return user
            else:
                raise serializers.ValidationError('Incorrect Credentials')
        raise serializers.ValidationError('Incorrect Credentials Passed.')



##### Admin register ######
class Adminregisterserializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'password', 'email', 'mobile_number')

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
            }
        }


    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        email = validated_data.get('email')
        mobile_number = validated_data.get('mobile_number')

        user = UserProfile.objects.create_user(
            username = username,
            password = password,
            email = email,
            mobile_number = mobile_number,
            is_staff = False,
            is_superuser = False
        )
        user.save()
        user1 = user.id
        roles = Role.objects.get(role='ADMIN')
        roles1 = roles.role_id
        user1 = UserRole.objects.create(role_id = roles1, user_id = user1)
        return user



##### Admin login #####
class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        role = Role.objects.get(role='ADMIN')
        role1 = role.role_id
        if user and user.is_active:
            user1 = user.id
            if(UserRole.objects.filter(role_id=role1).filter(user_id=user1)):
                return user
            else:
                raise serializers.ValidationError('Incorrect Credentials')
        raise serializers.ValidationError('Incorrect Credentials Passed.')
