from dis import disco
from django.db import transaction
from .serializers import RegisterSerializer, UserprofileSerializer,ResetPasswordSerializer
from .models import AddressType, Category, CustomerAddress, CustomerProfile, Product, Wishlist, Cart
from rest_framework.response import Response
from django.http import JsonResponse
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


# To Fetch/Update/Delete Particular User details by Passing PrimaryKey
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

# Reset/Change Password 
@transaction.atomic
@api_view(['PUT'])
def reset(request,pk):
    if request.method == 'PUT':
        change_password = request.POST['password']
        pwd = make_password(change_password)
        CustomerProfile.objects.filter(id = pk).update(password = pwd)
        # print(pas_reset)
        return HttpResponse('Sucess')
        


# Adding Selective Products of User to Wishlist
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

# USER  ADDRESSESS
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

# ADDING PRODUCT TO CART FOR FIRST TIME
@transaction.atomic
@api_view(['POST'])
def add_to_cart_api(request,id,pid,qty=1):
    user = CustomerProfile.objects.get(pk=id)
    product  = Product.objects.get(pk=pid)
    if request.method == 'POST':
        # if product.quantity >= qty:
        if product.available_qty >= qty:
            if Cart.objects.filter(product=pid, customer=id):
                return HttpResponse("Alredy this product exists in your cart")
            else :
                Cart.objects.create(
                    customer = user,
                    product = product,
                    quantity = qty,
                    price = product.unit_price,
                    cart_value = product.unit_price * qty
                )
                Product.objects.filter(id=pid).update(available_qty =product.available_qty - qty)
                return HttpResponse("Added to Cart")
        else : 
            return HttpResponse("Cart Quantity is more that Product Quantity")
    else : 
        return HttpResponse("Failed to Add Product")

# REMOVING THE PRODUCT FROM USER CART
@transaction.atomic
@api_view(['DELETE'])
def delete_from_cart(request,id,pid):
    if request.method == 'DELETE':
        uid = CustomerProfile.objects.get(pk=id)
        userid = uid.id
        capid = Cart.objects.get(product=pid)
        cartqnty = capid.quantity
        prid = Product.objects.get(pk=pid)
        productid = prid.id
        product_avl_quantity = prid.available_qty
        try:
            Cart.objects.filter(product=productid, customer=userid).delete()
            Product.objects.filter(id=productid).update(available_qty=product_avl_quantity+cartqnty)
            return HttpResponse('Your product successfully Removed from the cart')
        except:
            return HttpResponse('Product does not exists')

from django.db.models.functions import Round 


# ADDING EXTRA QUANTITYT TO EXSISTING PRODUCT
@transaction.atomic
@api_view(['PUT'])
def cart_quantity_add_api(request,id,pid,qty=1):
    if request.method == 'PUT':
        user = CustomerProfile.objects.get(pk = id)
        product = Product.objects.get(pk = pid)

        cart = Cart.objects.get(product = pid)
        if qty <= cart.quantity and cart.quantity >0:
            Cart.objects.filter(customer = user).filter(product = pid).update(
                quantity = cart.quantity + qty, 
                cart_value = cart.cart_value + product.unit_price
                )
            Product.objects.filter(id = pid).update(available_qty = product.available_qty - qty)
            return HttpResponse("Quantity Addded Sucessfull")
        else : 
            return HttpResponse("No Sufficient Qty")
    else :
        return HttpResponse("Invalid Method") 


# REMOVING EXTRA QUANTITYT TO EXSISTING PRODUCT
@transaction.atomic
@api_view(['PUT'])
def cart_quantity_remove_api(request,id,pid,qty=1):
    if request.method == 'PUT':
        user = CustomerProfile.objects.get(pk = id)
        product = Product.objects.get(pk = pid)

        cart = Cart.objects.get(product = pid)
        if cart.quantity >=qty:
            Cart.objects.filter(customer = user).filter(product = pid).update(
                quantity = cart.quantity - qty, 
                cart_value = cart.cart_value - product.unit_price
                )
            Product.objects.filter(id = pid).update(available_qty = product.available_qty + qty)
            return HttpResponse("Quantity Removed Sucessfull")
        elif cart.quantity == 0 and cart.quantity < 1:
            Cart.objects.filter(product = pid).filter(customer= user).delete()
            return HttpResponse("Product Removed From Cart Sucessfully")
    else :
        return HttpResponse("Invalid Request Method") 

