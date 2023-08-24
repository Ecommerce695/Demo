
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from datetime import datetime
from rest_framework.decorators import api_view
from django.db import transaction
from rest_framework.generics import CreateAPIView
from pytz import utc
from order.serializers import ordercancelserializer,orderserializer,ser_useraddress, pr_seri
from customer.models import KnoxAuthtoken, UserProfile, UserRole, Role, UserAddress, Wishlist, AddressType
from super_admin.models import Product, images, variants, tags, collection
from cart.models import Cart
from payments.models import Transaction_table, Payment_details_table
from order.models import (Order, OrderCancelled,OrderItemHistory,OrderReturn,viewhistory,OrderItemRefund,OrderDeliverySuccess)
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
import requests
import json
from Ecomerce_project.settings import SHIPMENT_TOKEN
from super_admin.models import CompanyProfile






#################   Single product order api   ###############################

class singleproductorder(CreateAPIView):
    serializer_class = orderserializer

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
        roles = UserRole.objects.filter(role_id=role1).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        dp = serializer.validated_data['product_id']
                        ser_dq = serializer.validated_data['quantity']
                        if(Product.objects.filter(id=dp).exists()):
                            prtb = Product.objects.get(id=dp)
                            dis_price = prtb.price-(prtb.price*prtb.discount/100)
                            # if product is out of stock: not able to do buy now.
                            if(ser_dq>0):
                                if prtb.stock >= ser_dq:
                                    viewhistory.objects.filter(user=userdata).all().delete()
                                    view_tb = viewhistory.objects.create(product=prtb.id,user=userdata,quantity=ser_dq,price=round(dis_price,2),totalvalue=round(dis_price*ser_dq,2))
                                    prodtb = Product.objects.get(id=dp)
                                    vrtb = variants.objects.get(id=dp)
                                    imgtb = images.objects.get(id=dp)
                                    Cart.objects.filter(user=userdata,product=dp).all().delete()
                                    Cart.objects.create(user=usertable,product=prodtb,variant=vrtb.variant_id,quantity=ser_dq,price=prodtb.price,title=prodtb.title,sku=vrtb.sku,size=vrtb.size,color=vrtb.color,src=imgtb.src,brand=prodtb.brand,type=prodtb.type,discount=prodtb.discount,stock=prodtb.stock,cart_value=dis_price*ser_dq)
                                    Product.objects.filter(id=dp).update(stock=prtb.stock-ser_dq)
                                    view_table = viewhistory.objects.filter(user=userdata,product=dp).values('totalvalue')
                                    totalvalue = view_table.aggregate(Sum('totalvalue')).get('totalvalue__sum')
                                    datalist = []
                                    data = {
                                            "product_id":view_tb.product,
                                            "product_name":prodtb.title,
                                            "price":view_tb.price,
                                            "quantity":view_tb.quantity,
                                            "total_product_value":view_tb.totalvalue
                                        }
                                    datalist.append(data)
                                    data1 = {
                                        "order_details":datalist,
                                        "total_order_amount":round(totalvalue,2)
                                    }
                                    return Response(data1,status=status.HTTP_200_OK)
                                else:
                                    return Response({"message":"Out of quantity"},status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({"message":"Negative quantity value not allowed"},status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({"message":"Product not exists"},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"message":"Serializer is not valid"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        





#################  Order through cart  #################

@csrf_exempt
@transaction.atomic
@api_view(["GET"])
def ordercart(request,token):
    if request.method == 'GET':
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
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Cart.objects.filter(user=userdata).exists()):
                        viewhistory.objects.filter(user=userdata).all().delete()
                        h = Cart.objects.filter(user=userdata).values('product','price','discount','quantity','cart_value')  
                        h1 = h.aggregate(Sum('cart_value')).get('cart_value__sum')
                        datalist = []
                        for i in h:
                            prodtb = Product.objects.get(id=i['product'])
                            dis_price = i['price']-(i['price']*i['discount']/100)
                            view_tb = viewhistory.objects.create(product=i['product'],user=userdata,quantity=i['quantity'],price=round(dis_price,2),totalvalue=round(dis_price*i['quantity'],2))
                            data = {
                                "product_id":view_tb.product,
                                "product_name":prodtb.title,
                                "price":view_tb.price,
                                "quantity":view_tb.quantity,
                                "total_product_value":view_tb.totalvalue
                            }
                            datalist.append(data)
                            data1 = {
                                "order_details":datalist,
                                "total_order_amount":round(h1,2)
                            }   
                        return Response(data1, status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Data not found in cart for this user"},status=status.HTTP_404_NOT_FOUND)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_400_BAD_REQUEST)
    




###############   User Address    #########################
class address_api(CreateAPIView):
    serializer_class = ser_useraddress

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
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        usadress = serializer.validated_data['address_id']
                        try:
                           UserAddress.objects.get(user=userdata,id=usadress)
                        except:
                            return Response({"message":"User has no address on this address_id"},status=status.HTTP_404_NOT_FOUND)
                        
                        if(viewhistory.objects.filter(user=userdata).exists()):                    
                            viewtb=viewhistory.objects.filter(user=userdata).values('product','totalvalue','quantity','price')
                            total = viewtb.aggregate(Sum('totalvalue')).get('totalvalue__sum')
                            datalist1 = []
                            datalist11 = []
                            for n in viewtb:
                                prid = n['product']
                                uadr=UserAddress.objects.get(id=usadress,user=userdata)
                                prtab=Product.objects.get(id=prid)
                                cmptb=CompanyProfile.objects.get(user=prtab.user)
                                if cmptb.country == 'INDIA' and uadr.country == 'UNITED STATES':
                                    return Response({"message":"Delivery not available for US"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                elif uadr.country == 'INDIA' and cmptb.country == 'UNITED STATES':
                                    return Response({"message":"Delivery not available for INDIA"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                elif(uadr.country != cmptb.country):
                                    return Response({"message":"Delivery not available for other countries"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                else:
                                    url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"
                                    payload=json.dumps({
                                        "pickup_postcode":int(cmptb.pincode),
                                        "delivery_postcode":int(uadr.pincode), 
                                        "cod":"0", 
                                        "weight":prtab.weight
                                    })
                                    headers = {
                                        'Content-Type': 'application/json',
                                        'Authorization': SHIPMENT_TOKEN
                                    }
                                    response = requests.request("GET", url, headers=headers, data=payload)
                                    data=response.json()
                                    if response.status_code==401 or data['status']==401:
                                        return Response({"message":"Shipment token expired"},status=status.HTTP_408_REQUEST_TIMEOUT)
                                    else:
                                        if response.status_code and data['status']==200:
                                            i=1
                                            date1 = data['data']['available_courier_companies'][i]['etd']
                                            data2 = {
                                                "product_id":prtab.id,
                                                "product_name":prtab.title,
                                                "price":n['price'],
                                                "quantity":n['quantity'],
                                                "total_product_value":n['totalvalue'],
                                                "estimated_delivery_date":date1,
                                                "message":"Address validated and delivery posiible"
                                            }
                                            datalist1.append(data2)
                                            viewhistory.objects.filter(user=userdata,product=prtab.id).update(address=usadress,is_delivered='True')
                                        elif response.status_code==404 or data['status']==404 or response.status_code==422 or data['status']==422:
                                            data1 = {
                                                "product_id":prtab.id,
                                                "product_name":prtab.title,
                                                "price":n['price'],
                                                "quantity":n['quantity'],
                                                "total_product_value":n['totalvalue'],
                                                "message":"Delivery not available to this address"
                                            }
                                            datalist11.append(data1)
                                            viewhistory.objects.filter(user=userdata,product=prtab.id).update(is_delivered='False')
                            data = {
                                "Delivered_products":datalist1,
                                "Undelivered_products":datalist11,
                                "total_order_amount":total
                            }
                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            return Response({"message":"Please select the products before selecting the address"},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"message":"Please provide address id"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        



####### Remove undelivered products for delivery address   #######################

class pr_remove(CreateAPIView):
    serializer_class=pr_seri

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
        roles = UserRole.objects.filter(role_id=role1).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        product_id = serializer.validated_data['product_id']
                        if(viewhistory.objects.filter(product=product_id, user=userdata).exists()):
                            viewhistory.objects.filter(product=product_id,user=userdata).delete()
                            Cart.objects.filter(product=product_id,user=userdata).delete()
                            return Response({"message":"Product removed successfully"},status=status.HTTP_200_OK)
                        else:
                            return Response({"message":"Product not selected to order"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({"message":"Value Error"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)



    

######################   order cancel   ########################

class OrderCancelApi(CreateAPIView):
    serializer_class = ordercancelserializer

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
        roles = UserRole.objects.filter(role_id=role1).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        spid = serializer.validated_data['orderitemid']
                        srea = serializer.validated_data['reason']
                        if(OrderItemHistory.objects.filter(id=spid,order_status='CANCELLED').exists()):
                            return Response({"message":"order for this order_item is already cancelled"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        elif(OrderItemHistory.objects.filter(id=spid,order_status='RETURNED').exists()):
                            return Response({"message":"order for this order_item is already returned"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            if((OrderItemHistory.objects.filter(id=spid, user=userdata).filter(order_status__iexact='ORDER PLACED') and 
                                Transaction_table.objects.filter(orderitem=spid, status__iexact='PAID')).exists()):
                                if(OrderItemHistory.objects.filter(id=spid,shipment_status='DELIVERED').exists()):
                                    return Response({"message":"Please return the order, not allowed to cancel"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                else:
                                    otab = OrderItemHistory.objects.get(id=spid)
                                    orprice = otab.item_price*otab.quantity  
                                    padetails=Payment_details_table.objects.get(orderitem=spid)  
                                    try:
                                        redetails=stripe.Refund.create(payment_intent=padetails.payment, amount=int(orprice))
                                        payintretr=stripe.PaymentIntent.retrieve(redetails['payment_intent'])
                                        oritref=OrderItemRefund.objects.create(orderitemid=otab,status=redetails['status'],refund=redetails['id'],
                                                                    transaction_id=redetails['balance_transaction'],recieptno=redetails['receipt_number'],
                                                                    refund_amount=orprice,currency=redetails['currency'])
                                        OrderItemRefund.objects.filter(id=oritref.id).update(alias='ORDREF-'+str(oritref.id))
                                        Transaction_table.objects.filter(orderitem=spid).update(status='REFUNDED',updated_at=datetime.now())
                                        OrderItemHistory.objects.filter(user=userdata,id=spid).update(order_status='CANCELLED',updated_at=datetime.now())
                                        OrderCancelled.objects.create(order_item=otab,order_price=orprice,reason_for_cancel=srea,payment_type=payintretr['payment_method_types'])
                                        ###### check with the product shipment
                                        d = Product.objects.get(id=otab.product)
                                        Product.objects.filter(id=d.id).update(stock=d.stock+otab.quantity)
                                        data1 = {
                                            "product_id":otab.product,
                                            "order_amount":orprice,
                                            "order_status":"ORDER CANCELLED",
                                            "payment_status":'REFUNDED',
                                            "transaction_id":oritref.transaction_id
                                        }
                                        return Response(data1,status=status.HTTP_200_OK)
                                    except Exception as e:
                                        return Response(e,status=status.HTTP_406_NOT_ACCEPTABLE)
                            else:
                                return Response({"message":"Order is not placed for this order_item to cancel"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({"message":"Serializer is not valid"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


            

##################################  order returned   ###########################

class OrderReturnAPI(CreateAPIView):
    serializer_class = ordercancelserializer

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
        roles = UserRole.objects.filter(role_id=role1).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        spid = serializer.validated_data['orderitemid']
                        srea = serializer.validated_data['reason']
                        if(OrderItemHistory.objects.filter(id=spid,order_status='CANCELLED').exists()):
                            return Response({"message":"order for this order_item is already cancelled"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        elif(OrderItemHistory.objects.filter(id=spid,order_status='RETURNED').exists()):
                            return Response({"message":"order for this order_item is already returned"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            if(OrderItemHistory.objects.filter(id=spid, user=userdata).filter(order_status='ORDER PLACED') and 
                               Transaction_table.objects.filter(orderitem=spid, status__iexact='PAID').exists()):
                                if(OrderItemHistory.objects.filter(id=spid, user=userdata).filter(shipment_status__iexact='DELIVERED')):
                                    otab = OrderItemHistory.objects.get(id=spid)
                                    orprice = otab.item_price*otab.quantity
                                    padetails=Payment_details_table.objects.get(orderitem=spid)  
                                    try:
                                        redetails=stripe.Refund.create(payment_intent=padetails.payment, amount=int(orprice))
                                        payintretr=stripe.PaymentIntent.retrieve(redetails['payment_intent'])
                                        oritref=OrderItemRefund.objects.create(orderitemid=otab,status=redetails['status'],refund=redetails['id'],
                                                                    transaction_id=redetails['balance_transaction'],recieptno=redetails['receipt_number'],
                                                                    refund_amount=orprice,currency=redetails['currency'])
                                        OrderItemRefund.objects.filter(id=oritref.id).update(alias='ORDREF-'+str(oritref.id))
                                        Transaction_table.objects.filter(orderitem=spid).update(status='REFUNDED',updated_at=datetime.now())
                                        OrderItemHistory.objects.filter(user=userdata,id=spid).update(order_status='RETURNED',updated_at=datetime.now())
                                        OrderReturn.objects.create(order_item=otab,order_price=orprice,reason_for_return=srea,payment_type=payintretr['payment_method_types'])
                                        ### delivered order status details are deleted from orderdeliverysuccess table
                                        OrderDeliverySuccess.objects.filter(order_item=spid).delete()
                                        ###### check with the product shipment
                                        d = Product.objects.get(id=otab.product)
                                        Product.objects.filter(id=d.id).update(stock=d.stock+otab.quantity)
                                        data1 = {
                                            "product_id":otab.product,
                                            "order_amount":orprice,
                                            "order_status":"ORDER RETURNED",
                                            "payment_status":'REFUNDED',
                                            "transaction_id":oritref.transaction_id
                                        }
                                        return Response(data1,status=status.HTTP_200_OK)
                                    except Exception as e:
                                        return Response(e,status=status.HTTP_406_NOT_ACCEPTABLE)
                                else:
                                    return Response({"message":"Please cancel the order, not allowed to return"},status=status.HTTP_406_NOT_ACCEPTABLE)
                            else:
                                return Response({"message":"Order is not placed for this order_item to return"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({"message":"Serializer is not valid"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)