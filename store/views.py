from email.headerregistry import Address
from django.shortcuts import render,redirect
from django.db import transaction
# from django.contrib import messages
from .serializers import RegisterSerializer, UserprofileSerializer
from .models import AddressType, CustomerAddress, CustomerProfile, Product, Wishlist, Cart
from rest_framework.response import Response
from django.http import JsonResponse
#create_refresh_token
# from .authentication import create_access_token, create_refresh_token 
# from rest_framework.exceptions import APIException
from rest_framework.decorators import api_view
from django.http import HttpResponse
from rest_framework.parsers import JSONParser
from knox.auth import AuthToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.auth import AuthToken
from store.models import CustomerProfile
from .serializers import RegisterSerializer
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth import logout

# User Registration API
@transaction.atomic
@api_view(['POST'])
def register_api(request):
    serializer = RegisterSerializer(data = request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    user.save()
    
    _, token = AuthToken.objects.create(user)

    return Response (
        {
            'user_info' :{
                'id' : user.id,
                'username' : user.username,
                'email' : user.email,
                'password' : user.password,
                'mobile' : user.mobile_number
            },
            'token' : token
        }
    )

# User Login API
@transaction.atomic
@api_view(['POST'])
def login_api(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']

    _, token = AuthToken.objects.create(user)

    return Response (
        {
            'user_info' :{
                'id' : user.id,
                'username' : user.username,
                'email' : user.email,
                "mobile" : user.mobile_number
            },
            'token' : token
        }
    )


# User Logout API
@api_view(['POST'])
def signoff(request):
    logout(request)


# To Fetch/Update/Delete Particular User details by Passing PK
@transaction.atomic
@api_view(['GET','PUT','DELETE'])
def user_detail(request, pk):
    try:
        user = CustomerProfile.objects.get(pk=pk)
    except user.DoesNotExist:
        return HttpResponse(status=404)
  
    if request.method == 'GET':
        serializer = UserprofileSerializer(user)
        return JsonResponse(serializer.data)
  
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = UserprofileSerializer(user, data=data)
  
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
  
    elif request.method == 'DELETE':
        user.delete()
        return HttpResponse(status=204)


# Adding Selective Products to Wishlist Module
import json

@transaction.atomic
@api_view(['POST'])
#@login_required(login_url="login/")
def wish_list(request,id,pid):
    if request.method =='POST':
        user = CustomerProfile.objects.get(pk = id)
        pro= Product.objects.get(pk= pid)

        price = pro.unit_price

        if Wishlist.objects.filter(product_id = pro, customer=user):
            return HttpResponse("Product already Exists")
        else:
            wishlist = Wishlist.objects.create(product_id = pro, customer=user, price = price )
            response = {
                wishlist.product_id,
                wishlist.customer,
                wishlist.price
            }

            return HttpResponse("Sucessfull" , {"data" : response})

    else:
        return HttpResponse("Login required")   


@transaction.atomic
@api_view(['POST'])
def address_api(request,id):
    user = CustomerProfile.objects.get(pk=id)
    if request.method == 'POST':
        name = user.username
        mobile = request.POST['mobile_number']
        address = request.POST['address']
        near_by = request.POST['near_by']
        street_no = request.POST['street_no']
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']
        zip = request.POST['postal_code']
        address = CustomerAddress.objects.create(
            customer = user, 
            type = AddressType.objects.last(),
            name = name,
            mobile_number = mobile,
            address = address,
            near_by = near_by,
            street_no = street_no,
            city = city,
            state = state,
            country = country,
            postal_code = zip

        )

        return HttpResponse('Sucessfull')
