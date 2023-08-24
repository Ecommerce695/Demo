from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from customer.models import UserProfile,UserAddress
from datetime import datetime
from customer.models import KnoxAuthtoken,Role,UserRole
from pytz import utc
from rest_framework.generics import CreateAPIView
from .models import Cart
from super_admin.models import images, variants,Product, collection, tags,CompanyProfile
from .serializers import CartSerializer,CartQuantitySerializer
import re,json, requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Ecomerce_project import settings

###############   Cart   #########

# class cart_api(CreateAPIView):
#     serializer_class = CartSerializer

#     @transaction.atomic
#     def post(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {"message" : "Invalid Access Token"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)

#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role = Role.objects.get(role='USER')
#         role1 = role.role_id
#         roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid():
#                         seri = serializer.validated_data['variant']
#                         if(Cart.objects.filter(user=userdata, variant=seri).exists()):
#                             cart = Cart.objects.get(user=userdata, variant=seri)
#                             variant = variants.objects.get(variant_id = seri)
#                             product = Product.objects.get(id=variant.id)
#                             img = images.objects.get(variant_id=seri)
#                             Cart.objects.filter(variant=variant.variant_id, user=userdata).update(quantity=cart.quantity+1,
#                                                                                             price=product.price,
#                                                                                             cart_value=(cart.quantity+1)*product.price,
#                                                                                             src =img.src,
#                                                                                             title = product.title,
#                                                                                             sku = variant.sku,
#                                                                                             color = variant.color,
#                                                                                             brand = product.brand,
#                                                                                             type = product.type,
#                                                                                             stock=product.stock-1,
#                                                                                             discount=product.discount)
#                             data = {"message":"Product Added Successful"}
#                             return Response(data, status=status.HTTP_200_OK)
#                         else:
#                             if(variants.objects.filter(variant_id=seri).exists()):
#                                 variant = variants.objects.get(variant_id=seri)
#                                 product = Product.objects.get(id=variant.id)
#                                 productquantity = product.stock
#                                 if productquantity==0:
#                                     data = {"message":'Out of stock'}
#                                     return Response(data, status=status.HTTP_404_NOT_FOUND)
#                                 else:
#                                     img = images.objects.get(variant_id=variant.variant_id)
#                                     t2 = Cart.objects.create(
#                                         user= usertable,
#                                         product = product,
#                                         quantity = 1,
#                                         price = product.price,
#                                         title = product.title,
#                                         cart_value = 1*product.price,
#                                         variant = variant,
#                                         sku = variant.sku,
#                                         size = variant.size,
#                                         color = variant.color,
#                                         src = img.src,
#                                         brand = product.brand,
#                                         type = product.type,
#                                         discount = product.discount,
#                                         stock = product.stock
#                                     )
#                                     t3 = Product.objects.filter(id=seri).update(stock=productquantity-1)
#                                     data = {"message":'Product Added Successful'}
#                                     return Response(data, status=status.HTTP_200_OK)
#                             else:
#                                 return Response({"message":"Product not found"}, status=status.HTTP_404_NOT_FOUND)
#                     else:
#                         return Response({"message":"Serializer is not valid"}, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data ={
#                     "warning" : "User not assigned to Role",
#                     "message" : "Activate your account"
#                 }
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
       

#     @transaction.atomic
#     def delete(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {"message" : "Invalid Access Token"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)

#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role = Role.objects.get(role='USER')
#         role1 = role.role_id
#         roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid():
#                         seri = serializer.validated_data['variant']
#                         if(Cart.objects.filter(user=userdata, variant=seri).exists()):
#                             cart1 = Cart.objects.get(user=userdata, variant=seri)
#                             variant = variants.objects.get(variant_id=seri)
#                             product = Product.objects.get(id=variant.id)
#                             Cart.objects.filter(user=userdata, variant=seri).delete() 
#                             Product.objects.filter(id=seri).update(stock=product.stock+cart1.quantity)
#                             data = {"message":'Removed successfully'}
#                             return Response(data, status=status.HTTP_200_OK)
#                         else:
#                             data1 = {"message":'Data not found in cart'}
#                             return Response(data1, status=status.HTTP_404_NOT_FOUND)
#                     else:
#                         return Response({"message":"Serializer is not valid"}, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data ={
#                     "warning" : "User not assigned to Role",
#                     "message" : "Activate your account"
#                 }
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)



#     @transaction.atomic
#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {"message" : "Invalid Access Token"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)

#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role = Role.objects.get(role='USER')
#         role1 = role.role_id
#         roles = UserRole.objects.filter(role_id=role1).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     data = Cart.objects.filter(user=userdata)
#                     if data.exists():
#                         product = Cart.objects.filter(user=userdata).values('product')
#                         datalist =[] 

#                         for i in product:
#                             pro = Product.objects.get(id = i['product'])
                           
#                             col = collection.objects.filter(id=i["product"]).values_list('collection',flat=True)
#                             var = variants.objects.filter(id=i["product"]).values()
#                             img = images.objects.filter(id=i["product"]).values()
#                             t = tags.objects.filter(id=i["product"]).values_list('tags',flat=True)
                            
#                             data = {
#                                 "id": pro.id,
#                                 "title": pro.title,
#                                 "description": pro.description, 
#                                 "type": pro.type,
#                                 "brand": pro.brand,
#                                 "collection": col,
#                                 "category": pro.category,
#                                 "price": pro.price,
#                                 "sale": pro.sale,
#                                 "discount": pro.discount,
#                                 "stock": pro.stock,
#                                 "new": pro.new,
#                                 "variants" : var,
#                                 "images" : img,
#                                 "tag":t
#                             }
#                             datalist.append(data)
#                         return Response(datalist, status=status.HTTP_200_OK)
#                     else:
#                         data = {"message":'Data not exists in cart'}
#                         return Response(data, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data ={
#                     "warning" : "User not assigned to Role",
#                     "message" : "Activate your account"
#                 }
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


# class cart_quantityadd(CreateAPIView):
#     serializer_class = CartSerializer

#     @transaction.atomic
#     def put(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {"message" : "Invalid Access Token"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)

#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role = Role.objects.get(role='USER')
#         role1 = role.role_id
#         roles = UserRole.objects.filter(role_id=role1).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data = request.data)
#                     if serializer.is_valid():
#                         seri = serializer.validated_data['variant']  
#                         if(Cart.objects.filter(user=userdata, variant=seri).exists()):
#                             if(variants.objects.filter(variant_id=seri).exists()):
#                                 variant = variants.objects.get(variant_id=seri)
#                                 product = Product.objects.get(id=variant.id)
#                                 productprice = product.price
#                                 productquantity = product.stock
#                                 if productquantity==0:
#                                     data = {"message":'Out of stock'}
#                                     return Response(data, status=status.HTTP_404_NOT_FOUND)
#                                 else:
#                                     img = images.objects.get(varinat_id=variant.variant_id)
#                                     carttable = Cart.objects.get(variant=seri, user=userdata)
#                                     cartquantity = carttable.quantity
#                                     cartprice = carttable.price
#                                     cartvalue = carttable.cart_value
#                                     Cart.objects.filter(variant=seri, user=userdata).update(quantity=cartquantity+1,
#                                                                                             price=cartprice,
#                                                                                             cart_value=cartvalue+productprice,
#                                                                                             src =img.src)
#                                     Product.objects.filter(id=seri).update(stock=productquantity-1)
#                                     data = {"message":'Added successfully'}
#                                     return Response(data, status=status.HTTP_200_OK)
#                             else:
#                                 return Response({"message":"Product not found"}, status=status.HTTP_406_NOT_ACCEPTABLE)
#                         else:
#                             data = {"message":'Data not exists in cart'}
#                             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
#                     else:
#                         data = {"message":'Serializer not valid'}
#                         return Response(data, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 data ={
#                     "warning" : "User not assigned to Role",
#                     "message" : "Activate your account"
#                 }
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)




# class cart_quantitydecrease(CreateAPIView):
#     serializer_class = CartSerializer
    
#     @transaction.atomic
#     def put(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {"message" : "Invalid Access Token"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)

#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role = Role.objects.get(role='USER')
#         role1 = role.role_id
#         roles = UserRole.objects.filter(role_id=role1).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data = request.data)
#                     if serializer.is_valid():
#                         seri = serializer.validated_data['variant']
#                         if(Cart.objects.filter(user=userdata, variant=seri).exists()):
#                             if(variants.objects.filter(id=seri).exists()):
#                                 variant = variants.objects.get(variant_id=seri)
#                                 product = Product.objects.get(id=variant.id)
#                                 productprice = product.price
#                                 productqnty = product.stock
#                                 carttable = Cart.objects.get(variant=seri, user=userdata)
#                                 cartquantity = carttable.quantity
#                                 cartprice = carttable.price
#                                 cartvalue = carttable.cart_value
#                                 img = images.objects.get(id = product.id)
#                                 Cart.objects.filter(product=seri, user=userdata).update(quantity=cartquantity-1, price=cartprice, cart_value=cartvalue-productprice,src =img.src)
#                                 Product.objects.filter(id=seri).update(stock=productqnty+1)
#                                 cart1 = Cart.objects.get(variant=seri, user=userdata)
#                                 cartcheck = cart1.quantity
#                                 if cartcheck >= 1:
#                                     data = {"message":'decreased Successfully'}
#                                     return Response(data, status=status.HTTP_200_OK)
#                                 else:
#                                     cd = Cart.objects.filter(variant=seri, user=userdata).delete()
#                                     data = {"message":'Deleted Successfully'}
#                                     return Response(data, status=status.HTTP_200_OK)
#                             else:
#                                 return Response({"message":"Product not found"}, status=status.HTTP_406_NOT_ACCEPTABLE)
#                         else:
#                             data = {"message":'Data not exists in cart'}
#                             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
#                     else:
#                         data = {"message":'Serializer not valid'}
#                         return Response(data, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 data ={
#                     "warning" : "User not assigned to Role",
#                     "message" : "Activate your account"
#                 }
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


###############   Cart   #########

class cart_api(CreateAPIView):
    serializer_class = CartSerializer

    @transaction.atomic
    def post(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        seri = serializer.validated_data['id']
                        if(Cart.objects.filter(user=userdata, product=seri).exists()):
                            cart = Cart.objects.get(user=userdata, product=seri)
                            product = Product.objects.get(id=seri)
                            prices = product.price-(product.price*product.discount/100)
                            qty = cart.quantity+1
                            total = prices*qty
                            Cart.objects.filter(product=seri, user=userdata).update(quantity=qty, 
                            price=product.price, discount=product.discount,title=product.title,
                            cart_value=total)
                            Product.objects.filter(id=seri).update(stock=product.quantity-1)
                            data = {"message":'Added to cart'}
                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            if(Product.objects.filter(id=seri).exists()):
                                product = Product.objects.get(id=seri)
                                productquantity = product.stock
                                if productquantity==0:
                                    data = {"message":'Out of stock'}
                                    return Response(data, status=status.HTTP_404_NOT_FOUND)
                                else:
                                    var = variants.objects.get(id=product.id)
                                    img = images.objects.get(id=product.id)
                                    prices = product.price-(product.price*product.discount/100)
                                    Cart.objects.create(product=product, user=usertable, quantity=1, price=product.price,discount=product.discount, cart_value=prices,title=product.title,variant=var.variant_id, sku=var.sku,size=var.size,color=var.color,src=img.src,brand=product.brand,type=product.type,stock=product.stock)
                                    Product.objects.filter(id=seri).update(stock=productquantity-1)
                                    data = {"message":'Added to cart'}
                                    return Response(data, status=status.HTTP_200_OK)
                            else:
                                return Response({"message":"Product not found"}, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"message":"Serializer is not valid"}, status=status.HTTP_404_NOT_FOUND)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
       

    @transaction.atomic
    def get(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    data = Cart.objects.filter(user=userdata)
                    if data.exists():
                        product = Cart.objects.filter(user=userdata).values('product')
                        datalist =[] 
                        for i in product:
                            pro = Product.objects.get(id = i['product'])
                            c = Cart.objects.get(user=userdata,product=i["product"])
                            col = collection.objects.filter(id=i["product"]).values_list('collection',flat=True)
                            var = variants.objects.filter(id=i["product"]).values()
                            img = images.objects.filter(id=i["product"]).values()
                            t = tags.objects.filter(id=i["product"]).values_list('tags',flat=True)

                            company = CompanyProfile.objects.get(user=pro.user)
                            if (UserAddress.objects.filter(user=userdata).exists()):
                                user_add = UserAddress.objects.get(user=userdata,is_default=True)

                                url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"

                                payload=json.dumps({
                                    "pickup_postcode":company.pincode, # Pickup Location
                                    "delivery_postcode":user_add.pincode,  # Delivery Location
                                    "cod":"0",  # 1 for COD and 0 for Prepaid orders
                                    "weight":pro.weight # Product Weight in Kgs
                                })
                                headers = {
                                'Content-Type': 'application/json',
                                'Authorization': settings.SHIPMENT_TOKEN
                                }

                                response = requests.request("GET", url, headers=headers, data=payload)
                                data=response.json()

                                if response.status_code==200:
                                    i=1
                                    date_list=[]
                                    date_list.clear()                
                                    charger_list=[]
                                    for i in range(len(data['data']['available_courier_companies'])):
                                        date = data['data']['available_courier_companies'][i]['etd']
                                        shipping_chargers = data['data']['available_courier_companies'][i]["freight_charge"]
                                        i=i+1
                                        date_list.append(date)
                                        charger_list.append(shipping_chargers)
                                    data = {
                                        "id": pro.id,
                                        "title": pro.title,
                                        "description": pro.description, 
                                        "type": pro.type,
                                        "brand": pro.brand,
                                        "collection": col,
                                        "category": pro.category,
                                        "price": pro.price,
                                        "sale": pro.sale,
                                        "discount": pro.discount,
                                        "quantity": int(c.quantity),
                                        "new": pro.new,
                                        "variants" : var,
                                        "images" : img,
                                        "tag":t,
                                        "estimated_delivery_date": max(date_list),
                                        "shipping_chargers":max(charger_list),
                                        "is_deleted":pro.is_deleted
                                    }
                                    datalist.append(data)
                                elif data['status_code']!=200:
                                    data = {
                                        "id": pro.id,
                                        "title": pro.title,
                                        "description": pro.description, 
                                        "type": pro.type,
                                        "brand": pro.brand,
                                        "collection": col,
                                        "category": pro.category,
                                        "price": pro.price,
                                        "sale": pro.sale,
                                        "discount": pro.discount,
                                        "quantity": int(c.quantity),
                                        "new": pro.new,
                                        "variants" : var,
                                        "images" : img,
                                        "tag":t,
                                        "is_deleted":pro.is_deleted
                                    }
                                    datalist.append(data)
                            else:
                                data = {
                                    "id": pro.id,
                                    "title": pro.title,
                                    "description": pro.description, 
                                    "type": pro.type,
                                    "brand": pro.brand,
                                    "collection": col,
                                    "category": pro.category,
                                    "price": pro.price,
                                    "sale": pro.sale,
                                    "discount": pro.discount,
                                    "quantity": int(c.quantity),
                                    "new": pro.new,
                                    "variants" : var,
                                    "images" : img,
                                    "tag":t,
                                    "is_deleted":pro.is_deleted
                                }
                                datalist.append(data)
                            
                        return Response(datalist, status=status.HTTP_200_OK)
                    else:
                        return Response([], status=status.HTTP_204_NO_CONTENT)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)



class cart_quantity(CreateAPIView):
    serializer_class = CartQuantitySerializer

    @transaction.atomic
    def put(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data = request.data)
                    if serializer.is_valid():
                        seri = serializer.validated_data['id'] 
                        qty = serializer.validated_data['quantity'] 
                        if (Product.objects.filter(id=seri).exists()):
                            if(Cart.objects.filter(user=userdata, product=seri).exists()):
                                cart = Cart.objects.get(product=seri, user=userdata)
                                
                                if(Product.objects.filter(id=seri).exists()):
                                    product = Product.objects.get(id=seri)
                                    prices = product.price-(product.price*product.discount/100)
                                    productquantity = product.stock
                                    carttable = Cart.objects.get(product=seri, user=userdata)
                                    cartquantity = carttable.quantity
                                    cartprice = carttable.price
                                    cartvalue = carttable.cart_value
                                    
                                    if qty<0:
                                        if cartquantity==1:
                                            Cart.objects.filter(product=seri, user=userdata).delete()
                                            Product.objects.filter(id=seri).update(stock=productquantity+1)
                                            data = {"message":'Removed successfully'}  
                                            return Response(data, status=status.HTTP_200_OK)
                                        else:
                                            Cart.objects.filter(product=seri, user=userdata, variant=cart.variant).update(quantity=cartquantity-1, price=cartprice, cart_value=cartvalue-prices, title=product.title)
                                            Product.objects.filter(id=seri).update(stock=productquantity+(-1))
                                            data = {"message":'Removed successfully'}  
                                            return Response(data, status=status.HTTP_200_OK)  
                                    elif qty>0:
                                        if product.stock<=0:
                                            data = {"message":'Out of stock'}
                                            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE) 
                                        else:
                                            Cart.objects.filter(product=seri, user=userdata, variant=cart.variant).update(quantity=cartquantity+1, price=product.price, cart_value=cart.cart_value+prices, title=product.title)
                                            Product.objects.filter(id=seri).update(stock=productquantity-1)
                                            data = {"message":'Added successfully'}
                                            return Response(data, status=status.HTTP_200_OK)
                                    elif productquantity==0 :
                                        data = {"message":'Out of stock'}
                                        return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)     
                                else:
                                    return Response({"message":"Product not found"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                            else:
                                if(qty<=0):
                                    return Response({"message":"Please add product to cart before decrease quantity"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                else:
                                    pro =  Product.objects.get(id=seri)
                                    var = variants.objects.get(id=pro.id)
                                    img = images.objects.get(id=pro.id)
                                    prices = pro.price-(pro.price*pro.discount/100)
                                    Cart.objects.create(product=pro, user=usertable, quantity=1, price=pro.price,discount=pro.discount, cart_value=prices*1,title=pro.title,variant=var.variant_id, sku=var.sku,size=var.size,color=var.color,src=img.src,brand=pro.brand,type=pro.type,stock=pro.stock)
                                    Product.objects.filter(id=seri).update(stock=pro.stock-1)
                                    data = {"message":'Added to cart'}
                                    return Response(data, status=status.HTTP_200_OK)
                        else:
                            data = {"message":'Product not found'}
                            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        data = {"message":'Serializer not valid'}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)



# class CartDelete():
@csrf_exempt
@transaction.atomic
def cartdelete(request,token,pid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if request.method=='DELETE':
            if(UserProfile.objects.filter(id=userdata, is_active='True')):
                if roles.exists():
                    if token1.expiry < datetime.now(utc):
                        KnoxAuthtoken.objects.filter(user=user).delete()
                        data = {"message":'Session Expired, Please login again'}
                        return JsonResponse(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                    else:
                        if(Cart.objects.filter(user=userdata, product=pid).exists()):
                            cart1 = Cart.objects.get(user=userdata, product=pid)
                            cartquantity = cart1.quantity
                            product = Product.objects.get(id=pid)
                            productquantity = product.stock
                            Cart.objects.filter(user=userdata, product=pid).delete() 
                            Product.objects.filter(id=pid).update(stock=productquantity+cartquantity)
                            data = {"message":'Removed successfully'}
                            return JsonResponse(data, status=status.HTTP_200_OK)
                        else:
                            data1 = {"message":'Data not found in cart'}
                            return JsonResponse(data1, status=status.HTTP_404_NOT_FOUND)
                else:
                    data ={
                        "warning" : "User not assigned to Role",
                        "message" : "Activate your account"
                    }
                    return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data = {"message":'User is in In-Active, please Activate your account'}
                return JsonResponse(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        return JsonResponse({"message":"Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)





# class cart_quantitydecrease(CreateAPIView):
#     serializer_class = CartSerializer
    
#     @transaction.atomic
#     def put(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {"message" : "Invalid Access Token"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)

#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role = Role.objects.get(role='USER')
#         role1 = role.role_id
#         roles = UserRole.objects.filter(role_id=role1).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data = request.data)
#                     if serializer.is_valid():
#                         seri = serializer.validated_data['id']
#                         if(Cart.objects.filter(user=userdata, product=seri).exists()):
#                             if(Product.objects.filter(id=seri).exists()):
#                                 product = Product.objects.get(id=seri)
#                                 productprice = product.price
#                                 productqnty = product.stock
#                                 carttable = Cart.objects.get(product=seri, user=userdata)
#                                 cartquantity = carttable.quantity
#                                 cartprice = carttable.price
#                                 cartvalue = carttable.cart_value
#                                 Cart.objects.filter(product=seri, user=userdata).update(quantity=cartquantity-1, price=cartprice, cart_value=cartvalue-productprice,title=product.title)
#                                 Product.objects.filter(id=seri).update(stock=productqnty+1)
#                                 cart1 = Cart.objects.get(product=seri, user=userdata)
#                                 cartcheck = cart1.quantity
#                                 if cartcheck >= 1:
#                                     data = {"message":'decreased Successfully'}
#                                     return Response(data, status=status.HTTP_200_OK)
#                                 else:
#                                     cd = Cart.objects.filter(product=seri, user=userdata).delete()
#                                     data = {"message":'Deleted Successfully'}
#                                     return Response(data, status=status.HTTP_200_OK)
#                             else:
#                                 return Response({"message":"Product not found"}, status=status.HTTP_406_NOT_ACCEPTABLE)
#                         else:
#                             data = {"message":'Data not exists in cart'}
#                             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
#                     else:
#                         data = {"message":'Serializer not valid'}
#                         return Response(data, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 data ={
#                     "warning" : "User not assigned to Role",
#                     "message" : "Activate your account"
#                 }
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
