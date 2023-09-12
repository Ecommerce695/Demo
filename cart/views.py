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
                        serivariant = serializer.validated_data['variant']
                        if(Cart.objects.filter(user=userdata, product=seri,variant=serivariant).exists()):
                            cart = Cart.objects.get(user=userdata, product=seri,variant=serivariant)
                            product = variants.objects.get(id=seri,variant_id=serivariant)
                            qty = cart.quantity+1
                            total = product.selling_price*qty
                            Cart.objects.filter(product=seri,variant=serivariant, user=userdata).update(
                                quantity=qty, 
                                cart_value=total,
                                updated_at=datetime.now())
                            variants.objects.filter(id=seri,variant_id=serivariant).update(stock=product.quantity-1)
                            data = {"message":'Added to cart'}
                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            if(variants.objects.filter(id=seri,variant_id=serivariant).exists()):
                                variant=variants.objects.get(id=seri,variant_id=serivariant)
                                p= Product.objects.get(id=variant.id)
                                productquantity = variant.stock
                                if productquantity==0:
                                    data = {"message":'Out of stock'}
                                    return Response(data, status=status.HTTP_404_NOT_FOUND)
                                else:
                                    sellingprice = variant.selling_price
                                    Cart.objects.create(
                                        product=p,
                                        user=usertable,
                                        variant=variant.variant_id,
                                        quantity=1,
                                        cart_value=sellingprice)
                                    variants.objects.filter(id=seri,variant_id=serivariant).update(stock=productquantity-1)
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
                        cart_data = Cart.objects.filter(user=userdata).values()
                        datalist =[] 
                        for i in cart_data:
                            v= variants.objects.get(variant_id=i["variant"])
                            pro = Product.objects.get(id = v.id)
                            col = collection.objects.filter(id=pro.id).values_list('collection',flat=True)
                            var = variants.objects.filter(id=pro.id,variant_id=v.variant_id).values()
                            img = images.objects.filter(id=v.id,variant_id=v.variant_id).values()
                            t = tags.objects.filter(id=pro.id).values_list('tags',flat=True)
                            company = CompanyProfile.objects.get(user=pro.user)

                            if (UserAddress.objects.filter(user=userdata,is_default=True).exists()):
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
                                    if pro.is_charged==False:
                                        data = {
                                            "id": pro.id,
                                            "title": pro.title,
                                            "description": pro.description, 
                                            "type": pro.type,
                                            "brand": pro.brand,
                                            "collection": col,
                                            "sale": pro.sale,
                                            "new": pro.new,
                                            # "user_id": userdata,
                                            "category_id": pro.category_id,
                                            "category": pro.category,
                                            "rating": pro.rating,
                                            "is_active": pro.is_active,
                                            "alias": pro.alias,
                                            "dimensions": pro.dimensions,
                                            "weight": pro.weight,
                                            "status": pro.status,
                                            "is_charged": pro.is_charged,
                                            # "shipping_charges": pro.shipping_charges,
                                            # "other_charges": pro.other_charges,
                                            "is_wattanty": pro.is_wattanty,
                                            "warranty_months": pro.warranty_months,
                                            "warranty_src": pro.warranty_src,
                                            "warranty_path": pro.warranty_path.name,
                                            "created_at": pro.created_at.date(),
                                            "updated_at" : pro.updated_at.date(),
                                            "new": pro.new,
                                            "tags":t,
                                            "variants" : var,
                                            "images" : img,
                                            "sold_by" : company.org_name,
                                            "weight": pro.weight,
                                            "dimensions":pro.dimensions,
                                            "estimated_delivery_date": max(date_list),
                                            "shipping_chargers":max(charger_list),
                                        }
                                        datalist.append(data)
                                    elif pro.is_charged==True:
                                        data = {
                                            "id": pro.id,
                                            "title": pro.title,
                                            "description": pro.description, 
                                            "type": pro.type,
                                            "brand": pro.brand,
                                            "collection": col,
                                            "sale": pro.sale,
                                            "new": pro.new,
                                            # "user_id": userdata,
                                            "category_id": pro.category_id,
                                            "category": pro.category,
                                            "rating": pro.rating,
                                            "is_active": pro.is_active,
                                            "alias": pro.alias,
                                            "dimensions": pro.dimensions,
                                            "weight": pro.weight,
                                            "status": pro.status,
                                            "is_charged": pro.is_charged,
                                            # "shipping_charges": pro.shipping_charges,
                                            # "other_charges": pro.other_charges,
                                            "is_wattanty": pro.is_wattanty,
                                            "warranty_months": pro.warranty_months,
                                            "warranty_src": pro.warranty_src,
                                            "warranty_path": pro.warranty_path.name,
                                            "created_at": pro.created_at.date(),
                                            "updated_at" : pro.updated_at.date(),
                                            "new": pro.new,
                                            "tags":t,
                                            "variants" : var,
                                            "images" : img,
                                            "sold_by" : company.org_name,
                                            "weight": pro.weight,
                                            "dimensions":pro.dimensions,
                                            "estimated_delivery_date": max(date_list),
                                            "shipping_chargers":0
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
                                        "sale": pro.sale,
                                        "new": pro.new,
                                        # "user_id": userdata,
                                        "category_id": pro.category_id,
                                        "category": pro.category,
                                        "rating": pro.rating,
                                        "is_active": pro.is_active,
                                        "alias": pro.alias,
                                        "dimensions": pro.dimensions,
                                        "weight": pro.weight,
                                        "status": pro.status,
                                        "is_charged": pro.is_charged,
                                        "shipping_charges": pro.shipping_charges,
                                        "other_charges": pro.other_charges,
                                        "is_wattanty": pro.is_wattanty,
                                        "warranty_months": pro.warranty_months,
                                        "warranty_src": pro.warranty_src,
                                        "warranty_path": pro.warranty_path.name,
                                        "created_at": pro.created_at.date(),
                                        "updated_at" : pro.updated_at.date(),
                                        "new": pro.new,
                                        "tags":t,
                                        "variants" : var,
                                        "images" : img,
                                        "sold_by" : company.org_name,
                                        "weight": pro.weight,
                                        "dimensions":pro.dimensions,
                                        # "estimated_delivery_date": max(date_list),
                                        # "shipping_chargers":max(charger_list),
                                    }
                            else:
                                data = {
                                    "id": pro.id,
                                    "title": pro.title,
                                    "description": pro.description, 
                                    "type": pro.type,
                                    "brand": pro.brand,
                                    "collection": col,
                                    "sale": pro.sale,
                                    "new": pro.new,
                                    # "user_id": userdata,
                                    "category_id": pro.category_id,
                                    "category": pro.category,
                                    "rating": pro.rating,
                                    "is_active": pro.is_active,
                                    "alias": pro.alias,
                                    "dimensions": pro.dimensions,
                                    "weight": pro.weight,
                                    "status": pro.status,
                                    "is_charged": pro.is_charged,
                                    "shipping_charges": pro.shipping_charges,
                                    "other_charges": pro.other_charges,
                                    "is_wattanty": pro.is_wattanty,
                                    "warranty_months": pro.warranty_months,
                                    "warranty_src": pro.warranty_src,
                                    "warranty_path": pro.warranty_path.name,
                                    "created_at": pro.created_at.date(),
                                    "updated_at" : pro.updated_at.date(),
                                    "new": pro.new,
                                    "tags":t,
                                    "variants" : var,
                                    "images" : img,
                                    "sold_by" : company.org_name,
                                    "weight": pro.weight,
                                    "dimensions":pro.dimensions,
                                    "estimated_delivery_date": max(date_list),
                                    "shipping_chargers":max(charger_list),
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
                        serivariant = serializer.validated_data['variant'] 
                        qty = serializer.validated_data['quantity'] 
                        if (variants.objects.filter(id=seri,variant_id=serivariant).exists()):
                            if(Cart.objects.filter(user=userdata, product=seri,variant=serivariant).exists()):
                                cart = Cart.objects.get(product=seri,variant=serivariant,user=userdata)
                                
                                var = variants.objects.get(variant_id=serivariant,id=seri)
                                # product = Product.objects.get(id=seri)
                                prices = var.selling_price
                                productquantity = var.stock
                                carttable = Cart.objects.get(product=seri, user=userdata,variant=serivariant)
                                cartquantity = carttable.quantity
                                cartvalue = carttable.cart_value
                                    
                                if qty<0:
                                    if cartquantity==1:
                                        Cart.objects.filter(product=seri,variant=serivariant, user=userdata).delete()
                                        variants.objects.filter(id=seri,variant_id=serivariant).update(stock=productquantity+1)
                                        data = {"message":'Removed successfully'}  
                                        return Response(data, status=status.HTTP_200_OK)
                                    else:
                                        Cart.objects.filter(product=seri, user=userdata, variant=cart.variant).update(quantity=cartquantity-1, cart_value=cartvalue-prices)
                                        variants.objects.filter(id=seri,variant_id=serivariant).update(stock=productquantity+(1))
                                        data = {"message":'Removed successfully'}  
                                        return Response(data, status=status.HTTP_200_OK)  
                                elif qty>0:
                                    if var.stock<=0:
                                        data = {"message":'Out of stock'}
                                        return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE) 
                                    else:
                                        Cart.objects.filter(product=seri, user=userdata, variant=cart.variant).update(quantity=cartquantity+1, cart_value=cart.cart_value+prices)
                                        variants.objects.filter(id=seri,variant_id=serivariant).update(stock=productquantity-1)
                                        data = {"message":'Added successfully'}
                                        return Response(data, status=status.HTTP_200_OK)
                                elif productquantity==0 :
                                    data = {"message":'Out of stock'}
                                    return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)     
                            else:
                                if(qty<=0):
                                    return Response({"message":"Please add product to cart before decrease quantity"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                else:
                                    var = variants.objects.get(id=seri,variant_id=serivariant)
                                    pro =  Product.objects.get(id=seri)
                                    prices = var.selling_price
                                    Cart.objects.create(
                                        product=pro, 
                                        user=usertable, 
                                        quantity=1, 
                                        cart_value=prices*1,
                                        variant=var.variant_id)
                                    variants.objects.filter(id=seri,variant_id=serivariant).update(stock=var.stock-1)
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
def cartdelete(request,token,pid,vid):
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
                        if(Cart.objects.filter(user=userdata, product=pid,variant=vid).exists()):
                            cart1 = Cart.objects.get(user=userdata, product=pid,variant=vid)
                            cartquantity = cart1.quantity
                            var=variants.objects.get(id=pid,variant_id=vid)
                            productquantity = var.stock
                            Cart.objects.filter(user=userdata, product=pid,variant=vid).delete() 
                            variants.objects.filter(id=pid,variant_id=vid).update(stock=productquantity+cartquantity)
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
