from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from datetime import datetime
from django.db import transaction
from rest_framework.generics import CreateAPIView
from pytz import utc
from customer.models import KnoxAuthtoken, UserProfile, UserRole, Role, UserAddress
from super_admin.models import Product,variants, CompanyProfile,images
from payments.models import Transaction_table,Payment_details_table
from order.models import Order,OrderItemHistory
import requests, json
from .models import shipment
from Ecomerce_project.settings import SHIPMENT_TOKEN
from rest_framework import status
from .serializers import PicupScheduleSerializer

class CreateShipmentForEachOrder(CreateAPIView):

    @transaction.atomic()
    def get(self,request,token,oid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            o = OrderItemHistory.objects.get(id=oid)
        except:
            data = {"message" : "Invalid OrderItem Id"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
            order_items = OrderItemHistory.objects.filter(id=oid).values().all()
           
            if(Transaction_table.objects.filter(orderitem=oid,status='PAID')).exists():
                order_list=[]
                list=[]
                orders_list=[]
                
                for i in order_items:
                    item= OrderItemHistory.objects.get(id=i["id"])
                    users = UserProfile.objects.get(id=item.user)
                    od = Order.objects.get(id=item.order)
                    add = UserAddress.objects.get(id=od.delivery)

                    if (shipment.objects.filter(order_item_id=item.id).exists()):
                        return Response({"message":"Order Already exists in Shipment"},status=status.HTTP_208_ALREADY_REPORTED)
                    else:
                        pro = Product.objects.get(id=item.product)
                        variant = variants.objects.get(id=pro.id)
                        item_price = item.item_price/item.quantity
                        prices = Payment_details_table.objects.get(orderitem=item.id)
                        # unit_price = item_price-(item_price*0.18)
                        shipment_order_items = (
                            {
                                "product_id": item.product,
                                "name": pro.title,
                                "sku": variant.sku,
                                "units": item.quantity,
                                "tax": 18, #18*item.quantity,
                                "status": 1,
                                "discount": 0,
                                "selling_price": item.item_price, #item_price+item.quantity,
                                "hsn": '',
                                "brand": pro.brand,
                                "color": variant.color,
                                "weight": pro.weight,
                                "dimensions": pro.dimensions,
                                "category" :pro.category
                            }
                        )
                        list.append(shipment_order_items)
                        order_list.append(i["id"])
                        p = Product.objects.get(id=item.product)
                        company_name = CompanyProfile.objects.get(user=p.user)
                        url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"

                        payload=json.dumps({
                            "pickup_postcode":company_name.pincode, # Pickup Location
                            "delivery_postcode":add.pincode,  # Delivery Location
                            "cod":"0",  # 1 for COD and 0 for Prepaid orders
                            "weight":pro.weight # Product Weight in Kgs
                        })
                        headers = {
                        'Content-Type': 'application/json',
                        'Authorization': SHIPMENT_TOKEN
                        }
                        response = requests.request("GET", url, headers=headers, data=payload)
                        data=response.json()
                        if (data['status']==200):
                            l =[]
                            for i in range(len(data['data']['available_courier_companies'])):
                                shipping_chargers = data['data']['available_courier_companies'][i]["freight_charge"]
                                i=i+1
                                l.append(shipping_chargers)
                            url = "https://apiv2.shiprocket.in/v1/external/orders/create/adhoc"
                            payload = json.dumps(
                                    {
                                    "order_id": item.alias,
                                    "order_date": str(datetime.now()),
                                    "pickup_location": company_name.org_name,
                                    "channel_id": "",
                                    "comment": "Testing from Project",
                                    "company_name":"xShop by xAmplify",
                                    "order_type":"ESSENTIALS",
                                    "international_shipment" : False,
                                    "billing_customer_name": add.name,
                                    "billing_last_name": add.name,
                                    "billing_address": add.address,
                                    "billing_address_2": add.landmark,
                                    "billing_city": add.city,
                                    "billing_pincode": add.pincode,
                                    "billing_state": add.state,
                                    "billing_country": add.country,
                                    "billing_email": users.email,
                                    "billing_phone": add.mobile,
                                    "shipping_is_billing": True,
                                    "shipping_customer_name": "",
                                    "shipping_last_name": "",
                                    "shipping_address": "",
                                    "shipping_address_2": "",
                                    "shipping_city": "",
                                    "shipping_pincode": "",
                                    "shipping_country": "",
                                    "shipping_state": "",
                                    "shipping_email": "",
                                    "shipping_phone": "",
                                    "order_items": [shipment_order_items],
                                    "payment_method": "Prepaid",
                                    "shipping_charges": item.shipment_charge,
                                    "giftwrap_charges": 0,
                                    "transaction_charges": prices.amount*0.08,
                                    "total_discount": 0,
                                    "sub_total": prices.amount,  
                                    "length": pro.dimensions.split('X')[0],
                                    "breadth":pro.dimensions.split('X')[1],
                                    "height": pro.dimensions.split('X')[2],
                                    "weight": pro.weight
                                    }
                                )
                            headers = {
                            'Content-Type': 'application/json',
                            'Authorization': SHIPMENT_TOKEN
                            }
                            response = requests.request("POST", url, headers=headers, data=payload)
                            data=response.json()
                            orders_list.append(data)
                            if data["status"]==200 or response.status_code==200:
                                u = UserProfile.objects.get(id=o.user)
                                s=shipment.objects.create(order_item_id=item.id,shipment_order_id=data['order_id'],shipment_id=data['shipment_id'],
                                                        order_date=item.created_at,order_amount=item.item_price,pickup_address=company_name.id,
                                                        shipping_address=add.id,user=u)
                                shipment.objects.filter(shipment_id=s.shipment_id).update(alias='SHIP-'+str(s.shipment_id))
                                OrderItemHistory.objects.filter(id=item.id).update(shipment_status=data['status'])
                                pass
                            else: 
                                return Response(response.json())
                        elif data['status']==404:
                            return Response({'message':"Delivery postcode not serviceable"},status=status.HTTP_404_NOT_FOUND)
                        elif response.status_code==401 or data['status_code']==401:
                            data={'message': 'Token has expired', 'status_code': 401}
                            return Response(data,status=status.HTTP_401_UNAUTHORIZED)
                        elif data['status_code']!=200 or response.status_code!=200:
                            return Response(data)   
                r ={
                    "message" : "Successfully Shipped",
                    "data" : orders_list
                }
                return Response(r,status=status.HTTP_201_CREATED)
            return Response({"message":"Cant Proceed Shipment for Unsuccessful Order"})
        else:
            data={
                "message" :"Unauthorized to Ship Order",
                "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
                "status":status.HTTP_401_UNAUTHORIZED
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED) 


class GenerateAWB_Pickup(CreateAPIView):
    serializer_class = PicupScheduleSerializer

    @transaction.atomic()
    def post(self,request,token,shipmentid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            o = shipment.objects.get(shipment_id=shipmentid)
        except:
            data = {"message" : "Invalid Shipment ID"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
            if(UserProfile.objects.filter(id=usertable.id, is_active='True')):
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else: 
                    serializer = self.serializer_class(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        pickup_date=serializer.data['pickup_date']
                        if pickup_date=='':
                            d= datetime.now().date()
                            date=datetime.strptime(str(d), '%Y-%m-%d').date()
                        else:
                            date=datetime.strptime(str(pickup_date), '%Y-%m-%d').date()
                        
                        try:
                            url1 = "https://apiv2.shiprocket.in/v1/external/courier/assign/awb"
                            payload1 = json.dumps({
                            "shipment_id": o.shipment_id
                            })
                            headers1 = {
                            'Content-Type': 'application/json',
                            'Authorization': SHIPMENT_TOKEN
                            }
                            response1 = requests.request("POST", url1, headers=headers1, data=payload1)
                            if (response1.status_code==200 and response1.json()['awb_assign_status']==1):
                                shipment.objects.filter(shipment_id=o.shipment_id).update(awb_code=response1.json()['response']['data']['awb_code'])
                                
                                url2 = "https://apiv2.shiprocket.in/v1/external/courier/generate/pickup"
                                payload2 = json.dumps({
                                "shipment_id": [o.shipment_id],
                                "pickup_date":[str(date)]
                                })
                                headers2 = {
                                'Content-Type': 'application/json',
                                'Authorization': SHIPMENT_TOKEN
                                }
                                response2 = requests.request("POST", url2, headers=headers2, data=payload2)
                                if response2.json()['Status']==False:
                                    return Response({'message':"Invalid date format. Valid format is YYYY-MM-DD"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                elif response2.json()['Status']==True:
                                    url3 = "https://apiv2.shiprocket.in/v1/external/orders/show/"+str(o.shipment_order_id)
                                    payload3={}
                                    headers3 = {
                                    'Content-Type': 'application/json',
                                    'Authorization': SHIPMENT_TOKEN
                                    }
                                    response3 = requests.request("GET", url3, headers=headers3, data=payload3)
                                    data=response3.json()
                                    if response3.status_code==200:
                                        OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['data']['status'])
                                        data={
                                            "message":"Successfully Generated Pickup",
                                            "shipment":response2.json()
                                        }
                                        return Response(data,status=status.HTTP_202_ACCEPTED)
                                    else:
                                        return Response(response3.json())
                                    
                            elif (response1.status_code==200 and response1.json()['awb_assign_status']==0):
                                shipment.objects.filter(order_item_id=o.order_item_id).update(awb_code=data['data']['shipments']['awb'])
                                
                                url2 = "https://apiv2.shiprocket.in/v1/external/courier/generate/pickup"
                                payload2 = json.dumps({
                                "shipment_id": [o.shipment_id],
                                "pickup_date":[str(date)]
                                })
                                headers2 = {
                                'Content-Type': 'application/json',
                                'Authorization': SHIPMENT_TOKEN
                                }
                                response2 = requests.request("POST", url2, headers=headers2, data=payload2)
                                if response2.json()['Status']==False:
                                    return Response({'message':"Invalid date format. Valid format is YYYY-MM-DD"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                elif response2.json()['Status']==True:
                                    url3 = "https://apiv2.shiprocket.in/v1/external/orders/show/"+str(o.shipment_order_id)
                                    payload3={}
                                    headers3 = {
                                    'Content-Type': 'application/json',
                                    'Authorization': SHIPMENT_TOKEN
                                    }
                                    response3 = requests.request("GET", url3, headers=headers3, data=payload3)
                                    data=response3.json()
                                    
                                    if response3.status_code==200:
                                        OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['data']['status'])
                                        data={
                                            "message":"Successfully Generated Pickup",
                                            "shipment":response2.json()
                                        }
                                        return Response(data,status=status.HTTP_202_ACCEPTED)
                                    else:
                                        return Response(response3.json())
                            elif (response1.status_code==400):
                                return Response({'message': 'Oops! Cannot reassign courier for this shipment.', 'status_code': 400})
                            elif (response1.status_code==401 or data['status_code']==401):
                                data={'message': 'Token has expired', 'status_code': 401}
                                return Response(data,status=status.HTTP_401_UNAUTHORIZED)
                        except:
                            return Response(response1.json())
                    else:
                        return Response(serializer.error_messages,status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({'message':"Actiavte your Account"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            data={
                "message" :"Unauthorized to Ship Order",
                "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
                "status":status.HTTP_401_UNAUTHORIZED
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)


class ShipmentTracking(CreateAPIView):
    def get(self, request, token,shipmentid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            ship = shipment.objects.get(shipment_id=shipmentid)
        except:
            return Response({"message":"Invalid Shipment ID"})
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
            order_item=OrderItemHistory.objects.get(id=ship.order_item_id)
            # url = "https://apiv2.shiprocket.in/v1/external/courier/track/shipment/"+str(ship.shipment_id)

            # payload={}
            # headers = {
            # 'Content-Type': 'application/json',
            # 'Authorization': SHIPMENT_TOKEN
            # }

            # response = requests.request("GET", url, headers=headers, data=payload)
            # return Response(response.json())
            if (order_item.order_status=='ORDER PLACED' and ship.awb_code!=''):
                url = "https://apiv2.shiprocket.in/v1/external/courier/track/awb/"+str(ship.awb_code)
                payload={}
                headers = {
                'Content-Type': 'application/json',
                'Authorization': SHIPMENT_TOKEN
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                data=response.json()
                if response.status_code==200 or data['status']==200:
                    try:
                        OrderItemHistory.objects.filter(id=ship.order_item_id).update(shipment_status=data['tracking_data']['shipment_track'][0]['current_status'].upper())
                        return Response(response.json())
                    except:
                        data={
                            "message":" There is no activities found",
                            "shipment":response.json()
                        }
                        return Response(data,status=status.HTTP_200_OK)
                else:
                    return Response(response.json())
            elif (order_item.order_status=='ORDER PLACED' and ship.awb_code==''):
                url = "https://apiv2.shiprocket.in/v1/external/courier/track/shipment/"+str(ship.shipment_id)
                payload={}
                headers = {
                'Content-Type': 'application/json',
                'Authorization': SHIPMENT_TOKEN
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                data=response.json()
                if response.status_code==200 or data['status']==200:
                    try:
                        OrderItemHistory.objects.filter(id=ship.order_item_id).update(shipment_status=data['tracking_data']['shipment_track'][0]['current_status'].upper())
                        return Response(response.json())
                    except:
                        data={
                            "message":" There is no activities found",
                            "shipment":response.json()
                        }
                        return Response(data,status=status.HTTP_200_OK)
                else:
                    return Response(response.json())
            elif (order_item.order_status=='RETURN PLACED' and ship.return_awb_code!=''):
                url = "https://apiv2.shiprocket.in/v1/external/courier/track/awb/"+str(ship.return_awb_code)
                payload={}
                headers = {
                'Content-Type': 'application/json',
                'Authorization': SHIPMENT_TOKEN
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                data=response.json()
                if response.status_code==200 or data['status']==200:
                    try:
                        OrderItemHistory.objects.filter(id=ship.order_item_id).update(shipment_status=data['tracking_data']['shipment_track'][0]['current_status'].upper())
                        return Response(response.json())
                    except:
                        data={
                            "message":" There is no activities found",
                            "shipment":response.json()
                        }
                        return Response(data,status=status.HTTP_200_OK)
                else:
                    return Response(response.json())
            elif (order_item.order_status=='RETURN PLACED' and ship.return_awb_code==''):
                url = "https://apiv2.shiprocket.in/v1/external/courier/track/shipment/"+str(ship.return_shipment_id)
                payload={}
                headers = {
                'Content-Type': 'application/json',
                'Authorization': SHIPMENT_TOKEN
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                data=response.json()
                if response.status_code==200 or data['status']==200:
                    try:
                        OrderItemHistory.objects.filter(id=ship.order_item_id).update(shipment_status=data['tracking_data']['shipment_track'][0]['current_status'].upper())
                        return Response(response.json())
                    except:
                        data={
                            "message":" There is no activities found",
                            "shipment":response.json()
                        }
                        return Response(data,status=status.HTTP_200_OK)
                else:
                    return Response(response.json())
        else:
            data={
                "message" :"Unauthorized to Ship Order",
                "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
                "status":status.HTTP_401_UNAUTHORIZED
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
    
class OrderStatusView(CreateAPIView):

    @transaction.atomic()
    def get(self,request,token,oid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            order_item = OrderItemHistory.objects.get(id =oid)
        except:
            data = {"message" : "Order Item Doesn't Exist"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            o = shipment.objects.get(order_item_id=order_item.id)
        except:
            data = {"message" : "Shipment Not Assigned Yet"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
            url = "https://apiv2.shiprocket.in/v1/external/orders/show/"+str(o.shipment_order_id)
            payload={}
            headers = {
            'Content-Type': 'application/json',
            'Authorization': SHIPMENT_TOKEN
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            data=response.json()
            if response.status_code==200:
                OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['data']['status'])
                return Response(data,status=status.HTTP_200_OK)
            else:
                return Response(response.text,status=status.HTTP_401_UNAUTHORIZED)
        else:
            data={
                "message" :"Unauthorized to Ship Order",
                "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
                "status":status.HTTP_401_UNAUTHORIZED
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED) 
    
class GenerateManifest(CreateAPIView):

    @transaction.atomic()
    def get(self,request,token,shipmentid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            ship = shipment.objects.get(shipment_id=shipmentid)
        except:
            return Response({"message":"Invalid Shipment ID"})
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():

            url = "https://apiv2.shiprocket.in/v1/external/manifests/generate"

            payload = json.dumps({
            "shipment_id": [
                ship.shipment_id
            ]
            })
            headers = {
            'Content-Type': 'application/json',
            'Authorization': SHIPMENT_TOKEN
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code==200:
                return Response(response.json())
            elif response.status_code==400:
                url1 = "https://apiv2.shiprocket.in/v1/external/manifests/print"

                payload1 = json.dumps({
                "order_ids": [
                    ship.shipment_order_id
                ]
                })
                headers1 = {
                'Content-Type': 'application/json',
                'Authorization': SHIPMENT_TOKEN
                }

                response1 = requests.request("POST", url1, headers=headers1, data=payload1)
                if response1.status_code==200:
                    return Response(response1.json())
                else:
                    return Response(response1.json())
            else:
                return Response(response.json())
        else:
            data={
                "message" :"Unauthorized to Ship Order",
                "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
                "status":status.HTTP_401_UNAUTHORIZED
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
# class PrintManifest(CreateAPIView):

#     @transaction.atomic()
#     def get(self,request,token,shipmentid):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {"message" : "Invalid Access Token"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         try:
#             ship = shipment.objects.get(shipment_id=shipmentid)
#         except:
#             return Response({"message":"Invalid Shipment ID"})
#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
#             url = "https://apiv2.shiprocket.in/v1/external/manifests/print"

#             payload = json.dumps({
#             "order_ids": [
#                 ship.shipment_order_id
#             ]
#             })
#             headers = {
#             'Content-Type': 'application/json',
#             'Authorization': SHIPMENT_TOKEN
#             }

#             response = requests.request("POST", url, headers=headers, data=payload)
#             return Response(response.json())
#         else:
#             data={
#                 "message" :"Unauthorized to Ship Order",
#                 "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
#                 "status":status.HTTP_401_UNAUTHORIZED
#             }
#             return Response(data, status=status.HTTP_401_UNAUTHORIZED)
    
class GenerateLabel(CreateAPIView):

    @transaction.atomic()
    def get(self,request,token,shipmentid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            ship = shipment.objects.get(shipment_id=shipmentid)
        except:
            return Response({"message":"Invalid Shipment ID"})
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
            url = "https://apiv2.shiprocket.in/v1/external/courier/generate/label"

            payload = json.dumps({
            "shipment_id": [
                ship.shipment_id
            ]
            })
            headers = {
            'Content-Type': 'application/json',
            'Authorization': SHIPMENT_TOKEN
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            return Response(response.json())
        else:
            data={
                "message" :"Unauthorized to Ship Order",
                "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
                "status":status.HTTP_401_UNAUTHORIZED
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

class GenerateInvoice(CreateAPIView):

    @transaction.atomic()
    def get(self,request,token,shipmentid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            ship = shipment.objects.get(shipment_id=shipmentid)
        except:
            return Response({"message":"Invalid Shipment ID"})
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
            url = "https://apiv2.shiprocket.in/v1/external/orders/print/invoice"

            payload = json.dumps({
            "ids": [
                ship.shipment_order_id
            ]
            })
            headers = {
            'Content-Type': 'application/json',
            'Authorization': SHIPMENT_TOKEN
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            return Response(response.json())
        else:
            data={
                "message" :"Unauthorized to Ship Order",
                "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
                "status":status.HTTP_401_UNAUTHORIZED
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)


class RefreshOrderStatusView(CreateAPIView):

    @transaction.atomic()
    def get(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
        orders = OrderItemHistory.objects.filter(order_status__in=('RETURN PLACED','ORDER PLACED')).values('id').order_by('-created_at')
        user = token1.user_id
        usertable = UserProfile.objects.get (id=user)
        
        if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
            for i in orders:
                try:
                    order_item = OrderItemHistory.objects.get(id =i['id'])
                    o = shipment.objects.get(order_item_id=order_item.id)

                    if (order_item.order_status=='ORDER PLACED' and o.awb_code!=''):
                        url = "https://apiv2.shiprocket.in/v1/external/courier/track/awb/"+str(o.awb_code)
                        payload={}
                        headers = {
                        'Content-Type': 'application/json',
                        'Authorization': SHIPMENT_TOKEN
                        }

                        response = requests.request("GET", url, headers=headers, data=payload)
                        data=response.json()
                        if response.status_code==200 or data['status']==200:
                            try:
                                OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['tracking_data']['shipment_track'][0]['current_status'].upper())
                            except:
                                url3 = "https://apiv2.shiprocket.in/v1/external/orders/show/"+str(o.shipment_order_id)
                                payload3={}
                                headers3 = {
                                'Content-Type': 'application/json',
                                'Authorization': SHIPMENT_TOKEN
                                }
                                response3 = requests.request("GET", url3, headers=headers3, data=payload3)
                                data=response3.json()
                                if response3.status_code==200:
                                    OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['data']['status'])
                                else:
                                    pass
                        else:
                            pass
                    elif (order_item.order_status=='ORDER PLACED' and o.awb_code==''):
                        url = "https://apiv2.shiprocket.in/v1/external/courier/track/shipment/"+str(o.shipment_id)
                        payload={}
                        headers = {
                        'Content-Type': 'application/json',
                        'Authorization': SHIPMENT_TOKEN
                        }

                        response = requests.request("GET", url, headers=headers, data=payload)
                        data=response.json()
                        if response.status_code==200 or data['status']==200:
                            try:
                                OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['tracking_data']['shipment_track'][0]['current_status'].upper())
                            except:
                                url3 = "https://apiv2.shiprocket.in/v1/external/orders/show/"+str(o.shipment_order_id)
                                payload3={}
                                headers3 = {
                                'Content-Type': 'application/json',
                                'Authorization': SHIPMENT_TOKEN
                                }
                                response3 = requests.request("GET", url3, headers=headers3, data=payload3)
                                data=response3.json()
                                if response3.status_code==200:
                                    OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['data']['status'])
                                else:
                                    pass
                        else:
                            pass
                    elif (order_item.order_status=='RETURN PLACED' and o.return_awb_code!=''):
                        url = "https://apiv2.shiprocket.in/v1/external/courier/track/awb/"+str(o.return_awb_code)
                        payload={}
                        headers = {
                        'Content-Type': 'application/json',
                        'Authorization': SHIPMENT_TOKEN
                        }

                        response = requests.request("GET", url, headers=headers, data=payload)
                        data=response.json()
                        if response.status_code==200 or data['status']==200:
                            try:
                                OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['tracking_data']['shipment_track'][0]['current_status'].upper())
                            except:
                                url3 = "https://apiv2.shiprocket.in/v1/external/orders/show/"+str(o.shipment_order_id)
                                payload3={}
                                headers3 = {
                                'Content-Type': 'application/json',
                                'Authorization': SHIPMENT_TOKEN
                                }
                                response3 = requests.request("GET", url3, headers=headers3, data=payload3)
                                data=response3.json()
                                if response3.status_code==200:
                                    OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['data']['status'])
                                else:
                                    pass
                        else:
                            pass
                    elif (order_item.order_status=='RETURN PLACED' and o.return_awb_code==''):
                        url = "https://apiv2.shiprocket.in/v1/external/courier/track/shipment/"+str(o.return_shipment_id)
                        payload={}
                        headers = {
                        'Content-Type': 'application/json',
                        'Authorization': SHIPMENT_TOKEN
                        }

                        response = requests.request("GET", url, headers=headers, data=payload)
                        data=response.json()
                        if response.status_code==200 or data['status']==200:
                            try:
                                OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['tracking_data']['shipment_track'][0]['current_status'].upper())
                            except:
                                url3 = "https://apiv2.shiprocket.in/v1/external/orders/show/"+str(o.shipment_order_id)
                                payload3={}
                                headers3 = {
                                'Content-Type': 'application/json',
                                'Authorization': SHIPMENT_TOKEN
                                }
                                response3 = requests.request("GET", url3, headers=headers3, data=payload3)
                                data=response3.json()
                                if response3.status_code==200:
                                    OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['data']['status'])
                                else:
                                    pass
                        else:
                            pass
                    else:
                        url3 = "https://apiv2.shiprocket.in/v1/external/orders/show/"+str(o.shipment_order_id)
                        payload3={}
                        headers3 = {
                        'Content-Type': 'application/json',
                        'Authorization': SHIPMENT_TOKEN
                        }
                        response3 = requests.request("GET", url3, headers=headers3, data=payload3)
                        data=response3.json()
                        if response3.status_code==200:
                            OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['data']['status'])
                        else:
                            pass
                except:
                    pass
            return Response({"message":"Success"},status=status.HTTP_200_OK)
        else:
            data={
                "message" :"Unauthorized to Ship Order",
                "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
                "status":status.HTTP_401_UNAUTHORIZED
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

class CancelShipment(CreateAPIView):

    @transaction.atomic()
    def get(self,request,token,shipmentid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            s = shipment.objects.get(shipment_id=shipmentid)
        except:
            return Response({"message":"Invalid Shipment ID"})
        user = token1.user_id
        usertable = UserProfile.objects.get (id=user)
        
        if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
            url = "https://apiv2.shiprocket.in/v1/external/orders/cancel/shipment/awbs"

            payload = json.dumps({
            "awbs": [s.awb_code]
            })
            headers = {
            'Content-Type': 'application/json',
            'Authorization': SHIPMENT_TOKEN
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            # Shipment Cancel API Response Messages
            # -------------------------------------------------

            # 200 {'message': 'Shipment(s) are in processing tab !'}
            # {'message': 'Shipment(s) are in processing tab !'}

            # 200 {'message': 'Bulk Shipment(s) cancellation is in progress. Please wait for 24 hours.'}
            # {'message': 'Bulk Shipment(s) cancellation is in progress. Please wait for 24 hours.'}
            if response.status_code==200 or response.status==200:
                if s.awb_code!='':
                    shipment.objects.filter(awb_code=s.awb_code).update(awb_code='')
                    OrderItemHistory.objects.filter(id=s.order_item_id).update(shipment_status='NEW')
                    data={
                        "message":"Shipment Cancellation Successful",
                        "shipment":response.json()
                    }
                    return Response(data,status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({"message":"Can't Cancel Shipment before Generating Pickup"},status=status.HTTP_400_BAD_REQUEST)
            elif response.status_code==401 or data['status_code']==401:
                data={'message': 'Token has expired', 'status_code': 401}
                return Response(data,status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(response.json(),status=status.HTTP_404_NOT_FOUND)
        else:
            data={
                "message" :"Unauthorized to Ship Order",
                "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
                "status":status.HTTP_401_UNAUTHORIZED
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        
# class CreateReturnAPI(CreateAPIView):

#     @transaction.atomic()
#     def post(self,request,token,oid):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {"message" : "Invalid Access Token"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
        
#         try:
#             o = shipment.objects.get(shipment_order_id=oid)
#         except:
#             data = {"message" : "Invalid Order Id"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)

#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
#             url = "https://apiv2.shiprocket.in/v1/external/orders/show/"+str(o.shipment_order_id)
#             payload={}
#             headers = {
#             'Content-Type': 'application/json',
#             'Authorization': SHIPMENT_TOKEN
#             }

#             response1 = requests.request("GET", url, headers=headers, data=payload)
#             j = response1.json()
#             if response1.status_code==200 or response1.status==200:
#                 url = "https://apiv2.shiprocket.in/v1/external/orders/create/return"

#                 payload = json.dumps({
#                 "order_id": j['data']['id'],
#                 "order_date": j['data']['order_date'],
#                 "channel_id": j['data']['shipments']['channel_id'],
#                 "pickup_customer_name": j['data']['customer_name'],
#                 # "pickup_last_name": '',
#                 "pickup_address": j['data']['customer_address'],
#                 "pickup_address_2": j['data']['customer_address_2'],
#                 "pickup_city": j['data']['customer_city'],
#                 "pickup_state": j['data']['customer_state'],
#                 "pickup_country": j['data']['customer_country'],
#                 "pickup_pincode": j['data']['customer_pincode'],
#                 "pickup_email": j['data']['customer_email'],
#                 "pickup_phone": j['data']['customer_phone'],

#                 "shipping_customer_name": j['data']['pickup_address']['name'],
#                 "shipping_address": j['data']['pickup_address']['address'],
#                 "shipping_city":j['data']['pickup_address']['city'],
#                 "shipping_country": j['data']['pickup_address']['country'],
#                 "shipping_pincode": j['data']['pickup_address']['pin_code'],
#                 "shipping_state": j['data']['pickup_address']['state'],
#                 "shipping_email": j['data']['pickup_address']['email'],
#                 # "shipping_isd_code": "91",
#                 "shipping_phone": j['data']['pickup_address']['phone'],
#                 "order_items": [
#                     {
#                     "sku": j['data']['products'][0]['sku'],
#                     "name": j['data']['products'][0]['name'],
#                     "units": j['data']['others']['order_items'][0]['units'],
#                     "selling_price": j['data']['products'][0]['selling_price'],
#                     "discount": j['data']['products'][0]['discount'],
#                     "hsn": j['data']['products'][0]['hsn'],
#                     "brand": j['data']['products'][0]['brand'],
#                     # "qc_size": "43"
#                     }
#                 ],
#                 "payment_method": j['data']['payment_method'],
#                 # "total_discount": "0",
#                 "sub_total": j['data']['net_total'],
#                 "length": j['data']['shipments']['length'],
#                 "breadth": j['data']['shipments']['breadth'],
#                 "height": j['data']['shipments']['height'],
#                 "weight": j['data']['products'][0]['weight']
#                 })
#                 headers = {
#                 'Content-Type': 'application/json',
#                 'Authorization': SHIPMENT_TOKEN
#                 }

#                 response = requests.request("POST", url, headers=headers, data=payload)
#                 data=response.json()
#                 if response.status_code==200 or response.status==200:
#                     shipment.objects.filter(shipment_order_id=o.shipment_order_id).update(return_shipment_id=data['shipment_id'],return_shipment_order_id=data['order_id'])
#                     OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['status'])
#                     data={
#                         "message":"Return Request Successful",
#                         "shipment":response.json()
#                     }
#                     return Response(data,status=status.HTTP_201_CREATED)
#                 elif response.status_code==400:
#                     data={
#                         "message":"Failed To Create Return Request",
#                         "error" : "Can't Return Product after Cancelling Request"
#                     }
#                     return Response(data,status=status.HTTP_429_TOO_MANY_REQUESTS)
#                 else:
#                     return Response(response.json())
#             else:
#                 return Response(response1.json())
#         else:
#             data={
#                 "message" :"Unauthorized to Ship Order",
#                 "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
#                 "status":status.HTTP_401_UNAUTHORIZED
#             }
#             return Response(data, status=status.HTTP_401_UNAUTHORIZED)

# class GenerateReturnAWB(CreateAPIView):

#     @transaction.atomic()
#     def get(self,request,token,oid):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {"message" : "Invalid Access Token"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
        
#         try:
#             o = shipment.objects.get(shipment_order_id=oid)
#         except:
#             data = {"message" : "Invalid Order Id"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)

#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
#             #Check If order has been shipped already and not cancelled by admin/vendor 
#             url = "https://apiv2.shiprocket.in/v1/external/courier/assign/awb"

#             payload = json.dumps({
#             "shipment_id": o.return_shipment_id,
#             "courier_id": "",
#             "status": "",
#             "is_return": 1
#             })
#             headers = {
#             'Content-Type': 'application/json',
#             'Authorization': SHIPMENT_TOKEN
#             }

#             response = requests.request("POST", url, headers=headers, data=payload)
#             r = response.json()
#             if response.status_code == 200:
#                 # print(r['response']['data']['awb_code'])
#                 shipment.objects.filter(shipment_order_id=o.shipment_order_id).update(return_awb_code=r['response']['data']['awb_code'])
#                 return Response(r)
#             else:
#                 data={
#                     "message":"Failed To Get Return Awb From Shiprocket API",
#                     "error":response.json()
#                 }
#                 return Response(data)
#         else:
#             data={
#                 "message" :"Unauthorized to Ship Order",
#                 "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
#                 "status":status.HTTP_401_UNAUTHORIZED
#             }
#             return Response(data, status=status.HTTP_401_UNAUTHORIZED)