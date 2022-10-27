#! /usr/bin/env python

from django.db import transaction
from .serializers import RegisterSerializer, UserprofileSerializer
from .models import AddressType, Category, CustomerAddress,Reviews, CustomerProfile, Product, Wishlist, Cart, Search_bar_history
from .models import KnoxAuthtoken
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
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.db.models import Q



# User Registration API
@transaction.atomic
@api_view(['POST'])
def register_api(request):
    serializer = RegisterSerializer(data = request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    user.save()

    return Response (
        {
            'user_info' :{
                'id' : user.id,
                'username' : user.username,
                'email' : user.email,
                'password' : user.password,
                'mobile' : user.mobile_number
            }
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
def logout_api(request):
    logout(request)
    return Response('User Logged out successfully')

                            #*****************USER PROFILE ********************************

# To Fetch/Update/Delete Particular User details by Passing PrimaryKey
@transaction.atomic
@api_view(['GET','PUT','DELETE'])
def user_detail_api(request, token):
    try:
        # user = CustomerProfile.objects.get(pk=id)
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        user = CustomerProfile.objects.get(id=a)
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

# Update/Change Password 
@transaction.atomic
@api_view(['PUT'])
def reset_pwd_api(request,token):
    try:
        # user = CustomerProfile.objects.get(pk=id)
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        use = CustomerProfile.objects.get(id=a)
        user = use.id
    except user.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method == 'PUT':

        change_password = request.POST['password']
        pwd = make_password(change_password)
        CustomerProfile.objects.filter(id = user).update(password = pwd)
        cust = CustomerProfile.objects.filter(id = user)
        data = list(cust.values('first_name', 'last_name','username'))
        return JsonResponse(data, safe=False)
        
# # Modifing First Name 
# @transaction.atomic
# @api_view(['PUT'])
# def fname_update_api(request, id):
#     if request.method =='PUT':
#         first_name = request.POST['first_name']
#         CustomerProfile.objects.filter(id=id).update(first_name = first_name)
#         return HttpResponse("Modified First Name")

# #Modifing Last Name 
# @transaction.atomic
# @api_view(['PUT'])
# def lname_update_api(request, id):
#     if request.method =='PUT':
#         last_name = request.POST['last_name']
#         CustomerProfile.objects.filter(id=id).update(last_name = last_name)
#         return HttpResponse("Modified Last Name")

# #Modifing Email
# @transaction.atomic
# @api_view(['PUT'])
# def email_update_api(request,id):
#     if request.method == 'PUT':
#         update_email = request.POST['email']
    
#         CustomerProfile.objects.filter(id=id).update(email = update_email)
#         return HttpResponse("Modified Email")


# Moving Fav Product to WishList
@transaction.atomic
@api_view(['POST'])
def wish_list_api(request,token,pid):
    try:
        # user = CustomerProfile.objects.get(pk=id)
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        use = CustomerProfile.objects.get(id=a)
        user = use.id
    except user.DoesNotExist:
        return HttpResponse(status=404)

    if request.method =='POST':
        user = CustomerProfile.objects.get(pk = user)
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

# User ADD Address API
@transaction.atomic
@api_view(['POST'])
def add_address_api(request,token):
    try:
        # user = CustomerProfile.objects.get(pk=id)
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        use = CustomerProfile.objects.get(id=a)
        user = use.id
    except user.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'POST':
        name = use.username
        mobile = request.POST['mobile_number']
        address = request.POST['address']
        near_by = request.POST['near_by']
        street_no = request.POST['street_no']
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']
        zip = request.POST['postal_code']
        address = CustomerAddress.objects.create(
            customer = use, 
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

            # **** Delete Address API*********

@transaction.atomic
@api_view(['DELETE'])
def delete_address_api(request, token,aid):
    try:
        # user = CustomerProfile.objects.get(pk=id)
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        use = CustomerProfile.objects.get(id=a)
        user = use.id
    except user.DoesNotExist:
        return HttpResponse(status=404)

    if request.method =='DELETE':
        CustomerAddress.objects.filter(customer = user).filter(pk = aid).delete()
        return HttpResponse("Deleted Successfully")
    else:
        return HttpResponse('Customer Address Not Found')


#*************************CART Module API******************************

# ADDING PRODUCT TO CART FOR FIRST TIME
@transaction.atomic
@api_view(['POST'])
def add_to_cart_api(request,token,pid,qty=1):
    try:
        # user = CustomerProfile.objects.get(pk=id)
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        use = CustomerProfile.objects.get(id=a)
        user = use.id
    except user.DoesNotExist:
        return HttpResponse(status=404)
    
    product  = Product.objects.get(pk=pid)
    
    if request.method == 'POST':
        if product.available_qty >= qty:
            if Cart.objects.filter(product=pid, customer=user):
                return HttpResponse("Alredy this product exists in your cart")
            else :
                Cart.objects.create(
                    customer = use,
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
def delete_from_cart_api(request,token,pid):
    if request.method == 'DELETE':
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        use = CustomerProfile.objects.get(id=a)
        user = use.id

        capid = Cart.objects.get(product=pid)
        cartqnty = capid.quantity

        prid = Product.objects.get(pk=pid)
        productid = prid.id
        product_avl_quantity = prid.available_qty
        try:
            Cart.objects.filter(product=productid, customer=user).delete()
            Product.objects.filter(id=productid).update(available_qty=product_avl_quantity+cartqnty)
            return HttpResponse('Your product successfully Removed from the cart')
        except:
            return HttpResponse('Product does not exists')


# ADDING EXTRA QUANTITYT TO EXSISTING PRODUCT
@transaction.atomic
@api_view(['PUT'])
def cart_quantity_add_api(request,token,pid,qty=1):
    if request.method == 'PUT':
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        use = CustomerProfile.objects.get(id=a)
        user = use.id
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
def cart_quantity_remove_api(request,token,pid,qty=1):
    if request.method == 'PUT':
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        use = CustomerProfile.objects.get(id=a)
        user = use.id

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

# Fetch User Cart Details
@transaction.atomic
@api_view(['GET'])
def cart_details_api(request, token):
    if request.method == 'GET':
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        use = CustomerProfile.objects.get(id=a)
        user = use.id

        cart = Cart.objects.filter(customer = user)
        data = list(cart.values())
        return JsonResponse(data, safe=False)



        #   ****************  PRODUCT API ******************************

#Displays List Of Products
@transaction.atomic
@api_view(['GET'])
def products(request):
    if request.method == 'GET':
        product = Product.objects.all()
        data = list(product.values())
        return JsonResponse(data, safe=False)


                # *******Filters Product with Search Name Filter*******

@transaction.atomic
@api_view(['POST'])
def searchbar(request,token):
    if request.method == 'POST':
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        use = CustomerProfile.objects.get(id=a)

        name = request.POST['name']
        search = Search_bar_history.objects.create(customer = use, search_item = name)
        search.save()
        items  = Product.objects.filter(Q(product_name__startswith = name)| Q(product_name__icontains= name))

        if items.exists():
            data = list(items.values('id','product_name', 'unit_price','dis_price'))
        else:
            categorysearch = Category.objects.get(category_name=name)
            category_id = categorysearch.id
            products = Product.objects.filter(category = category_id)
            data = list(products.values('id','product_name', 'unit_price','dis_price'))
        return JsonResponse(data,safe=False)
    else:
        return HttpResponse("Method Not Allowed")


            ##  ***********Mobile Wise Products Filter API***********************

@transaction.atomic
@api_view(['GET'])
def mobile_category_api(request):
    if request.method == 'GET':
        category = Category.objects.get(category_name = 'Mobiles')
        category_id = category.id
        product = Product.objects.filter(category = category_id)
        data = list(product.values('id','product_name', 'unit_price','dis_price'))
        return JsonResponse(data,safe=False)


            ##  ***********Laptop Wise Products Filter API***********************

@transaction.atomic
@api_view(['GET'])
def laptop_category_api(request):
    if request.method == 'GET':
        category = Category.objects.get(category_name = 'Laptops')
        category_id = category.id
        product = Product.objects.filter(category = category_id)
        data = list(product.values('id','product_name', 'unit_price','dis_price'))
        return JsonResponse(data,safe=False)


            ##  ***********Gadgets Wise Products Filter API***********************

@transaction.atomic
@api_view(['GET'])
def gadget_category_api(request):
    if request.method == 'GET':
        category = Category.objects.get(category_name = 'Gadgets')
        category_id = category.id
        product = Product.objects.filter(category = category_id)
        data = list(product.values('id','product_name', 'unit_price','dis_price'))
        return JsonResponse(data,safe=False)


            #  ****************Recommended Products API*********************
@transaction.atomic()
@api_view(['GET'])
def recommendation_api(request,token):
    if request.method == 'GET':
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        use = CustomerProfile.objects.get(id=a)
        user = use.id

        recmmd = Search_bar_history.objects.filter(customer= user).order_by('-created_at')[:5]
        data = list(recmmd.values())
        return JsonResponse(data,safe=False)

            # ******** Latest Products**********

@transaction.atomic()
@api_view(['GET'])
def latest_product_api(request):
    if request.method =='GET':
        product = Product.objects.all().order_by('-id')[:5]
        data = list(product.values('id','product_name', 'unit_price','dis_price'))
        return JsonResponse(data,safe=False)


            # *********** Price Filter API ***********

@transaction.atomic
@api_view(['GET'])
def price_filter_api(request):
    price_from = request.GET.get('price_from', None)
    price_to = request.GET.get('price_to', None)

    if price_from and price_to:
        product = Product.objects.filter(unit_price__range=(price_from, price_to))
        data = list(product.values('id', 'product_name', 'unit_price'))
        return JsonResponse(data, safe=False)
    else:
        products = Product.objects.all()
        data = list(products.values('id', 'product_name', 'unit_price'))
        return JsonResponse(data, safe=False)


@transaction.atomic
@api_view(['GET'])
def category_name_wise_product_filter_api(request, name):
    if request.method == 'GET':
        categories = Category.objects.get(category_name__iexact = name)
        categoryid = categories.id

        products = Product.objects.filter(category = categoryid)
        productslist = list(products.values('product_name'))
        return JsonResponse(productslist, safe=False)


#####  REVIEW FOR PRODUCT PURCHASED
from django.db.models import Avg

@transaction.atomic
@api_view(['POST'])

def review(request,token,pid):
    try:
        # user = CustomerProfile.objects.get(pk=id)
        u_token = KnoxAuthtoken.objects.get(token_key = token)
        a = u_token.user_id
        use = CustomerProfile.objects.get(id=a)
        user = use.id
    except user.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'POST':
        rating = request.POST['rating']
        comments = request.POST['comments']
        
        productid = Product.objects.get(id=pid)

        review = Reviews.objects.filter(customer=user, product=pid)
        if review.exists():
            return HttpResponse("Review exists")
        if int(rating) <= 5:
            Reviews.objects.create(customer=use, product=productid, rating=rating, comments=comments)
            query = Reviews.objects.filter(product=pid).values_list('rating')
            queryavg = query.aggregate(Avg('rating')).get('rating__avg')
            # Product.objects.filter(id=pid).update(avg_rating=queryavg)
            return HttpResponse('Success')
        else:
            return HttpResponse('Error')    
    else:
        return HttpResponse('Error')


##### GET TOP RATED PRODUCTS
@transaction.atomic
@api_view(['GET'])
def topratedproducts(request):
    if request.method =='GET':
        # userid = CustomerProfile.objects.filter(id = uid)
        products = Product.objects.filter(avg_rating__gte = 4).values()
        return Response(products)
