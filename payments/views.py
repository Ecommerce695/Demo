from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.db import transaction
from django.conf import settings
from payments.models import Transaction_table,Payment_details_table
from order.models import Order,OrderItemHistory,viewhistory
from cart.models import Cart
from customer.models import UserProfile,KnoxAuthtoken,Role,UserRole, UserAddress
from super_admin.models import Product, images, CompanyProfile
from rest_framework import status
from rest_framework.response import Response
import stripe
from django.core.mail import send_mail
from pytz import utc
from rest_framework.generics import CreateAPIView
from payments.serializers import checkoutseri
from django.db.models import Sum, Avg
from datetime import time, timedelta, datetime
from Ecomerce_project.settings import SHIPMENT_TOKEN
import json
import requests
import pytz
from Ecomerce_project.settings import STRIPE_SECRET_KEY, STRIPE_SECRET_US_KEY

# Create your views here.
#####################   using API     ##################################


@api_view(['GET'])
@csrf_exempt
@transaction.atomic
def checkoutapi(request,token):
    if request.method == 'GET':
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        uid = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1).filter(user_id=uid)
        if(UserProfile.objects.filter(id=uid, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(viewhistory.objects.filter(user=uid).exists()):                        
                        view_tb = viewhistory.objects.filter(user=uid).values('product','price','quantity','address','totalvalue')
                        for m in view_tb:
                            m1 = m['product']
                            m2 = m['address']
                            if(viewhistory.objects.filter(user=uid,product=m1).filter(address__isnull=True,is_delivered='False').exists()):
                                return Response({"message":"Delivery address not selected"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            orsum = view_tb.aggregate(Sum('totalvalue')).get('totalvalue__sum')
                            ortb = Order.objects.create(user=uid,order_price=round(orsum,2),payment_type='')
                            datalist = []
                            
                            uadr=UserAddress.objects.get(id=m2)
                            prtab=Product.objects.get(id=m1)
                            cmptb=CompanyProfile.objects.get(user=prtab.user)

                            if uadr.country != cmptb.country:
                                return Response({"message":"Delivery not available for other countries"},status=status.HTTP_406_NOT_ACCEPTABLE)
                            else:
                                if uadr.country and cmptb.country =='INDIA':
                                    currency = 'inr'
                                    stripe.api_key = STRIPE_SECRET_KEY
                                    a = stripe.TaxRate.create(
                                        display_name="other_taxes",
                                        inclusive=False,   #### due to not included in overall amount(to be added)
                                        percentage=8.0,
                                        country="IN",
                                        description="Other taxes for application",
                                    )
                                    a1 = a['id']
                                    for i1 in view_tb:
                                        oritemtb = OrderItemHistory.objects.create(order=ortb.id,user=uid,product=i1['product'],quantity=i1['quantity'],item_price=i1['price'],alias='Null',order_status='INPROGRESS',created_at=datetime.now(),updated_at=datetime.now())
                                        OrderItemHistory.objects.filter(id=oritemtb.id).update(alias='ORD-'+str(oritemtb.id))
                                        try:
                                            prtb = Product.objects.get(id=i1['product'])
                                            strprice = prtb.strprice
                                        except:
                                            return Response({"message":"Product not exists in db"},status=status.HTTP_404_NOT_FOUND)
                                        data = {
                                            "price":strprice,
                                            "quantity":oritemtb.quantity,
                                            "tax_rates":[a1],
                                        }
                                        datalist.append(data)

                                        uadr1=UserAddress.objects.get(id=i1['address'])
                                        prtab1=Product.objects.get(id=i1['product'])
                                        cmptb1=CompanyProfile.objects.get(user=prtab1.user)

                                        url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"
                                        payload=json.dumps({
                                            "pickup_postcode":int(cmptb1.pincode),
                                            "delivery_postcode":int(uadr1.pincode), 
                                            "cod":"0", 
                                            "weight":prtab1.weight
                                        })
                                        headers = {
                                            'Content-Type': 'application/json',
                                            'Authorization': SHIPMENT_TOKEN
                                        }
                                        response = requests.request("GET", url, headers=headers, data=payload)
                                        data=response.json()
                                        if response.status_code==401 or data['status']==401:
                                            return Response({"message":"Shipment token expired"},status=status.HTTP_408_REQUEST_TIMEOUT)
                                        elif response.status_code==422 or response.status_code==404 or data['status']==404 or data['status']==422:
                                            return Response({"message":"Delivery not available to that address"},status=status.HTTP_400_BAD_REQUEST)
                                        else:
                                            if response.status_code and data['status']==200:
                                                i=1
                                                charger_list=[]
                                                for i in range(len(data['data']['available_courier_companies'])):
                                                    shipping_chargers = data['data']['available_courier_companies'][i]["freight_charge"]
                                                    i=i+1
                                                    charger_list.append(shipping_chargers)
                                                val1 = max(charger_list)
                                        OrderItemHistory.objects.filter(id=oritemtb.id).update(shipment_charge=float(round(val1)))
                                    Order.objects.filter(id=ortb.id).update(billing=i1['address'],delivery=i1['address'])
                                
                                    or1=OrderItemHistory.objects.filter(order=ortb.id).values('id','shipment_charge')
                                    orshs = or1.aggregate(Avg('shipment_charge')).get('shipment_charge__avg')
                                    char1 = round(orshs,2)

                                    shitb = stripe.ShippingRate.create(
                                        display_name="Delivery Charge",type="fixed_amount",
                                        fixed_amount={"amount": int(char1)*100, "currency": currency},
                                        )
                                    
                                    try:
                                        session = stripe.checkout.Session.create(
                                            shipping_options=[{"shipping_rate": shitb['id']}],
                                            invoice_creation={
                                                "enabled": True,
                                                "invoice_data": {
                                                    "description": "Invoice for Order",
                                                    "metadata": {"order": ortb.id},
                                                    "rendering_options": {"amount_tax_display": "include_inclusive_tax"},
                                                    "footer": "Auto generated Invoice. No need signatures.",
                                                },      
                                            },
                                            line_items = datalist,
                                            currency = currency,
                                            mode='payment',
                                            customer = stripe.Customer.create(
                                                email=usertable.email,phone=usertable.mobile_number, name=usertable.username,
                                                address={
                                                    "city":uadr.city,
                                                    "country":uadr.country,
                                                    "line1":uadr.address,
                                                    "line2":uadr.landmark,
                                                    "postal_code":uadr.pincode,
                                                    "state":uadr.state,
                                                }
                                            ), 
                                            payment_method_types=['card'],
                                            success_url='http://54.67.88.195/shop/checkout/success',
                                            cancel_url='http://54.67.88.195/shop/checkout/paymentfailed',
                                            consent_collection={
                                                'terms_of_service': 'required',
                                            },
                                            expires_at=datetime.now()+timedelta(minutes=30),
                                        )
                                        oritm = OrderItemHistory.objects.filter(order=ortb.id).values('order','id')
                                        for i2 in oritm:
                                            t=Transaction_table.objects.create(transaction=session.id,user=uid,order=i2['order'],status='ON HOLD',orderitem=i2['id'],customer=session['customer'],
                                                                            created_at=datetime.now(),expired_at=datetime.now()+timedelta(minutes=30),updated_at=datetime.now())
                                            Transaction_table.objects.filter(id=t.id).update(alias='TXN-'+str(t.id))
                                            data2 = {
                                                "id":session.id,
                                                "url":session.url,
                                                "status":session.payment_status
                                            }
                                        return Response(data2,status=status.HTTP_200_OK)
                                    except:
                                        return Response({"message":"These products not allowed to order/checkout error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                
                                elif uadr.country and cmptb.country == 'UNITED STATES':
                                    currency = "usd"
                                    stripe.api_key = STRIPE_SECRET_US_KEY
                                    a = stripe.TaxRate.create(
                                        display_name="other_taxes",
                                        inclusive=False,   #### due to not included in overall amount(to be added)
                                        percentage=8.0,
                                        country="US",
                                        description="Other taxes for application",
                                    )
                                    a1 = a['id']
                                    for i1 in view_tb:
                                        oritemtb = OrderItemHistory.objects.create(order=ortb.id,user=uid,product=i1['product'],quantity=i1['quantity'],item_price=i1['price'],alias='Null',order_status='INPROGRESS',created_at=datetime.now(),updated_at=datetime.now())
                                        OrderItemHistory.objects.filter(id=oritemtb.id).update(alias='ORD-'+str(oritemtb.id))
                                        try:
                                            prtb = Product.objects.get(id=i1['product'])
                                            strprice = prtb.strprice
                                        except:
                                            return Response({"message":"Product not exists in db"},status=status.HTTP_404_NOT_FOUND)
                                        data = {
                                            "price":strprice,
                                            "quantity":oritemtb.quantity,
                                            "tax_rates":[a1],
                                            }
                                        datalist.append(data)

                                        uadr1=UserAddress.objects.get(id=i1['address'])
                                        prtab1=Product.objects.get(id=i1['product'])
                                        cmptb1=CompanyProfile.objects.get(user=prtab1.user)

                                        url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"
                                        payload=json.dumps({
                                            "pickup_postcode":int(cmptb1.pincode),
                                            "delivery_postcode":int(uadr1.pincode), 
                                            "cod":"0", 
                                            "weight":prtab1.weight
                                        })
                                        headers = {
                                            'Content-Type': 'application/json',
                                            'Authorization': SHIPMENT_TOKEN
                                        }
                                        response = requests.request("GET", url, headers=headers, data=payload)
                                        data=response.json()
                                        if response.status_code==401 or data['status']==401:
                                            return Response({"message":"Shipment token expired"},status=status.HTTP_408_REQUEST_TIMEOUT)
                                        elif response.status_code==422 or response.status_code==404 or data['status']==404 or data['status']==422:
                                            return Response({"message":"Delivery not available to that address"},status=status.HTTP_400_BAD_REQUEST)
                                        else:
                                            if response.status_code and data['status']==200:
                                                i=1
                                                charger_list=[]
                                                for i in range(len(data['data']['available_courier_companies'])):
                                                    shipping_chargers = data['data']['available_courier_companies'][i]["freight_charge"]
                                                    i=i+1
                                                    charger_list.append(shipping_chargers)
                                                val1 = max(charger_list)
                                        OrderItemHistory.objects.filter(id=oritemtb.id).update(shipment_charge=float(round(val1)))
                                    Order.objects.filter(id=ortb.id).update(billing=i1['address'],delivery=i1['address'])
                                
                                    or1=OrderItemHistory.objects.filter(order=ortb.id).values('id','shipment_charge')
                                    orshs = or1.aggregate(Avg('shipment_charge')).get('shipment_charge__avg')
                                    char1 = round(orshs,2)

                                    shitb = stripe.ShippingRate.create(
                                        display_name="Delivery Charge",type="fixed_amount",
                                        fixed_amount={"amount": int(char1), "currency": currency},
                                    )

                                    try:
                                        session = stripe.checkout.Session.create(
                                            shipping_options=[{"shipping_rate": shitb['id']}],
                                            invoice_creation={
                                                "enabled": True,
                                                "invoice_data": {
                                                    "description": "Invoice for Order",
                                                    "rendering_options": {"amount_tax_display": "include_inclusive_tax"},
                                                    "footer": "Auto generated Invoice. No need signatures.",
                                                    "rendering_options":{
                                                        "amount_tax_display":"exclude_tax",
                                                    },
                                                },
                                            },
                                            line_items=datalist,
                                            currency = currency,
                                            mode='payment',
                                            customer = stripe.Customer.create(
                                                email=usertable.email,phone=usertable.mobile_number, name=usertable.username,
                                                address={
                                                    "city":uadr.city,
                                                    "country":uadr.country,
                                                    "line1":uadr.address,
                                                    "line2":uadr.landmark,
                                                    "postal_code":uadr.pincode,
                                                    "state":uadr.state
                                                }), 
                                            payment_method_types=['card'],
                                            success_url='http://54.67.88.195/shop/checkout/success',
                                            cancel_url='http://54.67.88.195/shop/checkout/paymentfailed',
                                            consent_collection={
                                                'terms_of_service': 'required',
                                            },
                                            expires_at=datetime.now()+timedelta(minutes=30),
                                        )
                                        oritm = OrderItemHistory.objects.filter(order=ortb.id).values('order','id')
                                        for i2 in oritm:
                                            t=Transaction_table.objects.create(transaction=session.id,user=uid,order=i2['order'],status='ON HOLD',orderitem=i2['id'],customer=session['customer'],
                                                                            created_at=datetime.now(),expired_at=datetime.now()+timedelta(minutes=30),updated_at=datetime.now())
                                            Transaction_table.objects.filter(id=t.id).update(alias='TXN-'+str(t.id))
                                            data = {
                                                "id":session.id,
                                                "url":session.url,
                                                "status":session.payment_status
                                            }
                                        return Response(data,status=status.HTTP_200_OK)
                                    except:
                                        return Response({"message":"These products not allowed to order/checkout error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                else:
                                    return Response({"message":"Country not allowed to pay"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({"message":"Not allowed"},status=status.HTTP_406_NOT_ACCEPTABLE)
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
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)





@csrf_exempt
@api_view(["GET"])
@transaction.atomic
def newdatart(request,token,session):
    if request.method == 'GET':
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        uid = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1).filter(user_id=uid)
        if(UserProfile.objects.filter(id=uid, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    try:
                        Transaction_table.objects.filter(transaction__in=session).exists()
                    except:
                        return Response({"message":"Invalid session id"},status=status.HTTP_404_NOT_FOUND)
                    
                    if(Transaction_table.objects.filter(transaction=session,user=uid)):
                        trtb = Transaction_table.objects.filter(transaction=session, user=uid).values('order')
                        for h in trtb:
                            orid1=h['order']
                        ortbadre=Order.objects.get(id=orid1)
                        usad=UserAddress.objects.get(id=ortbadre.delivery)
                        if usad.country == 'INDIA':
                            stripe.api_key = STRIPE_SECRET_KEY
                            pidr = stripe.checkout.Session.retrieve(session)
                            oritem = Transaction_table.objects.filter(transaction=session,user=uid).values('orderitem')
                            if(Payment_details_table.objects.filter(orderitem__in=oritem).exists()):
                                return Response({"message":"Payment already done for this order"},status=status.HTTP_400_BAD_REQUEST)
                            else:
                                for i in oritem:
                                    b = i['orderitem']
                                ortbl = OrderItemHistory.objects.filter(id=b).values('order')
                                orprice = Order.objects.filter(id__in=ortbl).values('order_price','delivery')
                                for j in orprice:
                                    oradre = j['delivery']
                                if pidr['payment_status'] == 'paid':
                                    pirtr = stripe.PaymentIntent.retrieve(pidr['payment_intent'])
                                    trret = stripe.Charge.retrieve(pirtr['latest_charge'])
                                    strin = stripe.Invoice.retrieve(pidr['invoice'])
                                    oritpr = OrderItemHistory.objects.filter(order__in=ortbl).values('item_price','quantity','id','product')
                                    for amount in oritpr:
                                        itpr = amount['item_price']*amount['quantity']
                                        paytabl = Payment_details_table.objects.create(payment=pidr['payment_intent'],status='PAID',amount=round(itpr,2),paymenttype=pidr['payment_method_types'],invoice=pidr['invoice'],
                                                                                    currency=pidr['currency'],alias='',orderitem=amount['id'],reciept=strin['receipt_number'],invoiceno=strin['number'],
                                                                                    charge_id=pirtr['latest_charge'],paymentmethodid=pirtr['payment_method'],transaction_id=trret['balance_transaction'],
                                                                                    created_at=datetime.now(),updated_at=datetime.now())
                                        Payment_details_table.objects.filter(id=paytabl.id).update(alias='PYMT-'+str(paytabl.id))
                                        OrderItemHistory.objects.filter(user=uid,order__in=ortbl).update(order_status='ORDER PLACED',updated_at=datetime.now())
                                        Transaction_table.objects.filter(orderitem__in=oritem).update(status='PAID',updated_at=datetime.now())
                                        Order.objects.filter(id__in=ortbl).update(payment_type=pidr['payment_method_types'])
                                        Cart.objects.filter(user=uid,product=amount['product']).all().delete()
                                        viewhistory.objects.filter(user=uid,product=amount['product']).all().delete()

                                    ordata=OrderItemHistory.objects.filter(order__in=ortbl).values('id','alias','product','order','quantity','order_status','item_price','shipment_status','created_at','delivery_date')
                                    datalist = []
                                    for m in ordata:
                                        ordertabl = Order.objects.get(id=m['order'])
                                        prtb = Product.objects.get(id=m['product'])
                                        payt = Payment_details_table.objects.get(orderitem=m['id'])
                                        adre = UserAddress.objects.filter(id=oradre).values().all()
                                        img = images.objects.get(id=prtb.id)
                                        data = {
                                                "product_id":m['product'],
                                                "product_name":prtb.title,
                                                "image":img.src,
                                                "order_id":m['alias'],
                                                "order_quantity":m['quantity'],
                                                "order_price":m['item_price']*m['quantity'],
                                                "order_status":m['order_status'],
                                                "shipment_status":m['shipment_status'],
                                            }
                                        datalist.append(data)
                                        data1 = {
                                            "Order_data":datalist,
                                            "address":adre,
                                            "subtotal":pidr['amount_subtotal']/100,
                                            "shipping_charge":pidr['shipping_cost']['amount_total']/100,
                                            "processing_fee":pidr['total_details']['amount_tax']/100,
                                            "Total_order_amount":pidr['amount_total']/100,
                                            "order_date":ordertabl.created_at.date(),
                                            "payment_method":payt.paymenttype,
                                            "transaction_id":payt.transaction_id
                                        }
                                    return Response(data1,status=status.HTTP_200_OK)
                                else:
                                    Transaction_table.objects.filter(transaction=session,user=uid).update(status='ON HOLD',updated_at=datetime.now())
                                    OrderItemHistory.objects.filter(user=uid,order__in=ortbl).update(order_status='INPROGRESS',updated_at=datetime.now())
                                    return Response({"message":"Payment not done, Please do payment until order in hold"},status=status.HTTP_402_PAYMENT_REQUIRED)
                        elif(usad.country == 'UNITED STATES'):
                            stripe.api_key = STRIPE_SECRET_US_KEY
                            pidr = stripe.checkout.Session.retrieve(session)
                            oritem = Transaction_table.objects.filter(transaction=session,user=uid).values('orderitem')
                            if(Payment_details_table.objects.filter(orderitem__in=oritem).exists()):
                                return Response({"message":"Payment already done for this order"},status=status.HTTP_400_BAD_REQUEST)
                            else:
                                for i in oritem:
                                    b = i['orderitem']
                                ortbl = OrderItemHistory.objects.filter(id=b).values('order')
                                orprice = Order.objects.filter(id__in=ortbl).values('order_price','delivery')
                                for j in orprice:
                                    oradre = j['delivery']
                                if pidr['payment_status'] == 'paid':
                                    pirtr = stripe.PaymentIntent.retrieve(pidr['payment_intent'])
                                    trret = stripe.Charge.retrieve(pirtr['latest_charge'])
                                    strin = stripe.Invoice.retrieve(pidr['invoice'])
                                    oritpr = OrderItemHistory.objects.filter(order__in=ortbl).values('item_price','quantity','id','product')
                                    for amount in oritpr:
                                        itpr = amount['item_price']*amount['quantity']
                                        paytabl = Payment_details_table.objects.create(payment=pidr['payment_intent'],status='PAID',amount=round(itpr,2),paymenttype=pidr['payment_method_types'],invoice=pidr['invoice'],
                                                                                    currency=pidr['currency'],alias='',orderitem=amount['id'],reciept=strin['receipt_number'],invoiceno=strin['number'],
                                                                                    charge_id=pirtr['latest_charge'],paymentmethodid=pirtr['payment_method'],transaction_id=trret['balance_transaction'],
                                                                                    created_at=datetime.now(),updated_at=datetime.now())
                                        Payment_details_table.objects.filter(id=paytabl.id).update(alias='PYMT-'+str(paytabl.id))
                                        OrderItemHistory.objects.filter(user=uid,order__in=ortbl).update(order_status='ORDER PLACED',updated_at=datetime.now())
                                        Transaction_table.objects.filter(orderitem__in=oritem).update(status='PAID',updated_at=datetime.now())
                                        Order.objects.filter(id__in=ortbl).update(payment_type=pidr['payment_method_types'])
                                        Cart.objects.filter(user=uid,product=amount['product']).all().delete()
                                        viewhistory.objects.filter(user=uid,product=amount['product']).all().delete()

                                    ordata=OrderItemHistory.objects.filter(order__in=ortbl).values('id','alias','product','order','quantity','order_status','item_price','shipment_status','created_at','delivery_date')
                                    datalist = []
                                    for m in ordata:
                                        ordertabl = Order.objects.get(id=m['order'])
                                        prtb = Product.objects.get(id=m['product'])
                                        payt = Payment_details_table.objects.get(orderitem=m['id'])
                                        adre = UserAddress.objects.filter(id=oradre).values().all()
                                        img = images.objects.get(id=prtb.id)
                                        data = {
                                                "product_id":m['product'],
                                                "product_name":prtb.title,
                                                "image":img.src,
                                                "order_id":m['alias'],
                                                "order_quantity":m['quantity'],
                                                "order_price":m['item_price']*m['quantity'],
                                                "order_status":m['order_status'],
                                                "shipment_status":m['shipment_status'],
                                            }
                                        datalist.append(data)
                                        data1 = {
                                            "Order_data":datalist,
                                            "address":adre,
                                            "subtotal":pidr['amount_subtotal'],
                                            "shipping_charge":pidr['shipping_cost']['amount_total'],
                                            "processing_fee":pidr['total_details']['amount_tax'],
                                            "Total_order_amount":pidr['amount_total'],
                                            "order_date":ordertabl.created_at.date(),
                                            "payment_method":payt.paymenttype,
                                            "transaction_id":payt.transaction_id
                                        }
                                    return Response(data1,status=status.HTTP_200_OK)
                                else:
                                    Transaction_table.objects.filter(transaction=session,user=uid).update(status='ON HOLD',updated_at=datetime.now())
                                    OrderItemHistory.objects.filter(user=uid,order__in=ortbl).update(order_status='INPROGRESS',updated_at=datetime.now())
                                    return Response({"message":"Payment not done, Please do payment until order in hold"},status=status.HTTP_402_PAYMENT_REQUIRED)
                        else:
                            return Response({"message":"Country not exist"},status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"message":"Please do checkout the order"},status=status.HTTP_402_PAYMENT_REQUIRED)
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
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)



@csrf_exempt
@api_view(["GET"])
@transaction.atomic
def retrypayment(request,token):
    if request.method == 'GET':
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        uid = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1).filter(user_id=uid)
        if(UserProfile.objects.filter(id=uid, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    trtb = Transaction_table.objects.filter(user=uid).last()
                    if(Transaction_table.objects.filter(user=uid).filter(transaction=trtb.transaction).filter(status='PAID')):
                        return Response({"message":"Payment already done"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        a = Transaction_table.objects.filter(user=uid,transaction=trtb.transaction).values('orderitem')
                        for i in a:
                            time_zone = pytz.timezone('UTC')
                            a = time_zone.localize(datetime.now())
                            b = a.astimezone(pytz.utc)
                            if(trtb.expired_at < b):
                                Transaction_table.objects.filter(user=uid,transaction=trtb.transaction).update(status='UNPAID',updated_at=datetime.now())
                                OrderItemHistory.objects.filter(user=uid,id=i['orderitem']).update(order_status='FAILED',updated_at=datetime.now())
                                link='https://checkout.stripe.com/c/pay/'+trtb.transaction+'#fidkdWxOYHwnPyd1blpxYHZxWjA0SzQxfXFWR1Fzc0R9TUBNdlFGbl1jMHJAV0RXXGBRX312NzNtSGp8dkxObF8xME00QGRDXWtiXWxDPXJNTmJ0VFBnQHBkZn00dEgyZF1uQUE1R1BoUjVhNTVXN3JTdTV%2FXScpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl'
                                data = {
                                    "id":trtb.transaction,
                                    "url":link
                                    }
                            else:
                                Transaction_table.objects.filter(user=uid,transaction=trtb.transaction).update(status='ON HOLD',updated_at=datetime.now())
                                OrderItemHistory.objects.filter(user=uid,id=i['orderitem']).update(order_status='INPROGRESS',updated_at=datetime.now())
                                link='https://checkout.stripe.com/c/pay/'+trtb.transaction+'#fidkdWxOYHwnPyd1blpxYHZxWjA0SzQxfXFWR1Fzc0R9TUBNdlFGbl1jMHJAV0RXXGBRX312NzNtSGp8dkxObF8xME00QGRDXWtiXWxDPXJNTmJ0VFBnQHBkZn00dEgyZF1uQUE1R1BoUjVhNTVXN3JTdTV%2FXScpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl'
                                data = {
                                    "id":trtb.transaction,
                                    "url":link
                                    }
                        return Response(data,status=status.HTTP_200_OK)
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
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    




@csrf_exempt
@transaction.atomic
@api_view(['GET'])
def tax_api(request,token):
    if request.method == 'GET':
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        uid = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1).filter(user_id=uid)
        if(UserProfile.objects.filter(id=uid, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    stripe.api_key = STRIPE_SECRET_KEY
                    a = stripe.TaxRate.create(
                        display_name="other_taxes",
                        inclusive=False,   #### due to not included in overall amount(to be added)
                        percentage=8.0,
                        country="IN",
                        # state="AP",
                        # jurisdiction="US - CA",
                        description="Other taxes for application",
                    )
                    print(a)
                    stripe.api_key = STRIPE_SECRET_US_KEY
                    a1 = stripe.TaxRate.create(
                        display_name="other_taxes",
                        inclusive=False,   #### due to not included in overall amount(to be added)
                        percentage=8.0,
                        country="US",
                        # state="AP",
                        # jurisdiction="US - CA",
                        description="Other taxes for application",
                    )
                    print(a1)
                    data = {
                        "Indian tax id":a['id'],
                        "US tax id":a1['id']
                    }
                    return Response(data,status=status.HTTP_200_OK)
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
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
                