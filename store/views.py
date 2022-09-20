from django.shortcuts import render,redirect
from django.contrib import auth
from django.db import transaction
# from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .serializers import UserprofileSerializer
from .models import Cart, Category, Order, Product, Sub_Category, User_profile, Vendor_Products, Wishlist
from django.core.mail import send_mail
from Ecomerce_project.settings import EMAIL_HOST_USER
from django.views.decorators.csrf import csrf_exempt
import random
from rest_framework.response import Response
from rest_framework import response
from django.http import JsonResponse
#create_refresh_token
from .authentication import create_access_token, create_refresh_token 
from rest_framework.exceptions import APIException
from rest_framework.decorators import api_view
from django.http import HttpResponse
from rest_framework.parsers import JSONParser
from knox.auth import AuthToken

# Creating Register Page and Storing Data into DataBase
@csrf_exempt
@transaction.atomic
@api_view(['POST'])    # Uncomment this to See in API view
def signup(request):
    if request.method == "POST":

        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        mobile = request.POST['mobile'] 
        password = request.POST['password']
        
        password = make_password(password)
        user = User_profile.objects.create(username=username, email=email,first_name=first_name, last_name=last_name,mobile = mobile,password=password)
        generated_otp = random.randint(1000,9999)

        subject = 'OTP Verification is Pending'
        message = "Hello " + user.username +"," + " \n\n Welcome to Eshop  \n\n  " + f'Your One-Time Password { generated_otp}'
        recepient = user.email
        send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently = False)

        if generated_otp == int(input("Enter OTP")):
            user.save()
        else: 
            int(input("Enter Valid OTP"))
        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

            
        response = {
            "username" : user.username,
            "email" : user.email,
            "password" : user.password,
            "Access Token" : access_token,
            "Refresh Token" : refresh_token,
            "token" : AuthToken.objects.create(user)[1]
        }
        
        return JsonResponse(response)

    else:
        # return render(request,'Auth/signup.html')
        return Response("Failed")

# Login Page 
@csrf_exempt
@transaction.atomic
@api_view(['POST'])   # Uncomment this to See in API view
def login(request):
    if request.method == 'POST':
        
        user = auth.authenticate(username = request.POST['username'], password = request.POST['password'])

        # if user is not None:
        #     auth.login(request,user)
        if not user:
            raise APIException('Invalid Details')

        if not user.check_password(request.POST['password']):
            raise APIException('Invalid Credentials')


        access_token = create_access_token(user.id)
        # refresh_token = create_refresh_token(user.id)

        # response = response.set_cookie(key='refeshToken' , value=refresh_token, httponly=True)

        response = {
            "id" : user.id,
            "username" : user.username,
            "email" : user.email,
            "password" : user.password,
            "A_Token" : access_token
        }

        return JsonResponse(response)
            
    else:
        return JsonResponse({
            "Invalid Details..."
        })



def logout(request):
    auth.logout(request)
    return redirect('home')

# This API will fetch all the User Details in the Database
@csrf_exempt
@api_view(['GET'])
def details(request):
    if request.method =='GET':
        # Creating a Object 
        user = User_profile.objects.all() 
        # Converting it into QuerySet 
        data = list(user.values())
        # returning it
        return JsonResponse(data,safe=False)

# To fetch Particular User details by Passing ID
@api_view(['GET','PUT','DELETE'])
@csrf_exempt
def user_detail(request, pk):
    try:
        user = User_profile.objects.get(pk=pk)
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


# Adding Selected / Favorite Products to Wishlist Module

@transaction.atomic
@api_view(['POST'])
#@login_required(login_url="login/")
@csrf_exempt
def wish_list(request,id,pid):
    if request.method =='POST':
        user = User_profile.objects.get(pk = id)
        pro= Vendor_Products.objects.get(pk= pid)

        if Wishlist.objects.filter(product = pro, user=user):
            return HttpResponse("Already Exists")
        else:
            wish_list = Wishlist.objects.create(user = user, product =pro)
            wish_list.save()
            return HttpResponse("Sucessful")

    else:
        return HttpResponse("Login required")   

#Orders Function
@transaction.atomic
@api_view(['POST'])
@csrf_exempt
def my_order(request,id,pid):
    if request.method =='POST':
        user = User_profile.objects.get(pk = id)
        pro= Product.objects.get(pk= pid)

        if Order.objects.filter(product_id = pro, user_id=user):
            return HttpResponse("Already Exists")
        else:
            user_order = Order.objects.create(user_id = user, product_id =pro)
            user_order.save()
            return HttpResponse("Sucessful")

    else:
        return HttpResponse("Login required") 


@transaction.atomic
@csrf_exempt
def product_view(request):
    
    if request.method == 'POST':
        pro = Product.objects.last()
        # category= request.POST['category']
        # sub_cat = request.POST['sub_cat']
        category = Category.objects.get('pk')
        sub_cat = Sub_Category.objects.get('pk')
        prod = Product.objects.create(category= category, sub_cat = sub_cat)
        update = Product.objects.update(product_id = request.category[:2]+"-"+request.sub_cat[:2]+pro)
        print(update)
        prod.save()

        response = {
            prod.category,
            prod.sub_cat,
            update.product_id
        }        

        return HttpResponse(response)
    return HttpResponse('Failed')

@api_view(['GET'])
@transaction.atomic
@csrf_exempt
def purchase(request,id):

    if request.method == 'GET':
        user = User_profile.objects.get(pk=id)        
        order = Order.objects.filter(user_id = user)

        data = list(order.values())
        print(order)

        print(data)
        # returning it
        return JsonResponse(data, safe=False)
    
@transaction.atomic
@csrf_exempt
def search_bar(request,cat):

    if request.method =='GET':
        category = Category.objects.filter(name = cat)
        response = {
            category
        }
        return HttpResponse(response)

# @transaction.atomic
# @csrf_exempt
# def cart_view(request):
#     if request.method == 'POST':

