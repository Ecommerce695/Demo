from django.db import transaction
# from django.contrib import messages
from .serializers import RegisterSerializer, UserprofileSerializer,ResetPasswordSerializer
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
from .serializers import RegisterSerializer
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password


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


# Logout Request of User
@api_view(["GET"])
def signoff(request):
    logout(request)
    return Response('User Logged out successfully')


# To Fetch/Update/Delete Particular User details by Passing PK
@transaction.atomic
@api_view(['GET','PUT','DELETE'])
def user_detail_api(request, pk):
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

@transaction.atomic
@api_view(['POST'])
#@login_required(login_url="login/")
def wish_list_api(request,id,pid):
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
<<<<<<< HEAD


@transaction.atomic
@api_view(['POST'])
def add_to_cart_api(request,id,pid,qty=1):
    user = CustomerProfile.objects.get(pk=id)
    product  = Product.objects.get(pk=pid)
    if request.method == 'POST':
        if product.quantity >= qty:
            if Cart.objects.filter(product=pid, customer=id):
                return HttpResponse("Alredy this product exists in your cart")
            else :
                added = Cart.objects.create(
                    customer = user,
                    product = product,
                    quantity = qty,
                    price = product.unit_price,
                    cart_value = product.unit_price * qty

                
                )
                prod = Product.objects.filter(id=pid).update(available_qty = product.quantity - qty)
                added.save()
                print(user)
                print(product)
                print(product.unit_price)
                print(product.quantity)
                print(prod)
                return HttpResponse("Added to Cart")
        else : 
            return HttpResponse("Cart Quantity is more that Product Quantity")
    else : 
        return HttpResponse("Failed to Add Product")



# @transaction.atomic
# @api_view(['PUT'])
# def reset_password_api(request,id):
#     try:
#         user = CustomerProfile.objects.get(pk=id)
#     except user.DoesNotExist:
#         return HttpResponse(status=404)

#     if request.method == 'PUT':
#         data = JSONParser().parse(request)
#         serializer = ResetPasswordSerializer(user, data=data)

#         if serializer.is_valid():            
#             serializer.save()
#             user.set_password(serializer.data.get('password'))
#             user.save()
#             return Response(serializer.data)    
#         return Response('S',{'message':True})


@transaction.atomic
@api_view(['PUT'])
def reset(request,pk):
    if request.method == 'PUT':
        change_password = request.POST['password']
        pwd = make_password(change_password)
        CustomerProfile.objects.filter(id = pk).update(password = pwd)
        # print(pas_reset)
        return HttpResponse('Sucess')
        


#Orders Function
# @transaction.atomic
# @api_view(['POST'])
# def purchase(request,id,pid):
#     if request.method =='POST':
#         user = CustomerProfile.objects.get(pk = id)
#         pro= Product.objects.get(pk= pid)

#         user_order = Orders.objects.create(user_id = user, product_id =pro)
#         user_order.save()
#         return HttpResponse("Sucessful")

#     else:
#         return HttpResponse("Login required") 


# @transaction.atomic
# @csrf_exempt
# def product_view(request):
    
#     if request.method == 'POST':
#         pro = Product.objects.last()
#         # category= request.POST['category']
#         # sub_cat = request.POST['sub_cat']
#         category = Category.objects.get('pk')
#         prod = Product.objects.create(category= category)
#         update = Product.objects.update(product_id = request.category[:2]+"-"+request.sub_cat[:2]+pro)
#         print(update)
#         prod.save()

#         response = {
#             prod.category,
#             prod.sub_cat,
#             update.product_id
#         }        

#         return HttpResponse(response)
#     return HttpResponse('Failed')

# @api_view(['GET'])
# @transaction.atomic
# @csrf_exempt
# def my_orders(request,id):

#     if request.method == 'GET':
#         user = CustomerProfile.objects.get(pk=id)        
#         order = Orders.objects.filter(user_id = user)

#         data = list(order.values())
#         print(order)

#         print(data)
#         # returning it
#         return JsonResponse(data, safe=False)
    
# @transaction.atomic
# @csrf_exempt
# def search_bar(request,cat):

#     if request.method =='GET':
#         category = Category.objects.filter(name = cat)
#         response = {
#             category
#         }
#         return HttpResponse(response)

# @transaction.atomic
# @csrf_exempt
# def cart_view(request):
#     if request.method == 'POST':

# @transaction.atomic
# @csrf_exempt
# def fetch(request, id):
#     if request.method  == 'GET':
#         user  = User_profile.objects.get(pk=id)
#         email = user.email
#         return HttpResponse(email)




        
=======
>>>>>>> f8038fe51dc52d035b4cffa96319ed57c652b950
