from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from datetime import datetime
from django.db import transaction
from rest_framework.generics import CreateAPIView
from pytz import utc
from customer.models import KnoxAuthtoken, UserProfile, UserRole, Role, UserAddress
from super_admin.models import Product,variants, CompanyProfile,images
from payments.models import Transaction_table
from order.models import Order,OrderItemHistory
import requests, json
from .models import shipment
from Ecomerce_project.settings import SHIPMENT_TOKEN
from rest_framework import status


class CreateReturnAPI(CreateAPIView):

    @transaction.atomic()
    def post(self,request,token,oid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
        try:
            o = shipment.objects.get(shipment_order_id=oid)
        except:
            data = {"message" : "Invalid Order Id"}
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

            response1 = requests.request("GET", url, headers=headers, data=payload)
            j = response1.json()
            if response1.status_code==200 or response1.status==200:
                url = "https://apiv2.shiprocket.in/v1/external/orders/create/return"

                payload = json.dumps({
                "order_id": j['data']['id'],
                "order_date": j['data']['order_date'],
                "channel_id": j['data']['shipments']['channel_id'],
                "pickup_customer_name": j['data']['customer_name'],
                # "pickup_last_name": '',
                "pickup_address": j['data']['customer_address'],
                "pickup_address_2": j['data']['customer_address_2'],
                "pickup_city": j['data']['customer_city'],
                "pickup_state": j['data']['customer_state'],
                "pickup_country": j['data']['customer_country'],
                "pickup_pincode": j['data']['customer_pincode'],
                "pickup_email": j['data']['customer_email'],
                "pickup_phone": j['data']['customer_phone'],

                "shipping_customer_name": j['data']['pickup_address']['name'],
                "shipping_address": j['data']['pickup_address']['address'],
                "shipping_city":j['data']['pickup_address']['city'],
                "shipping_country": j['data']['pickup_address']['country'],
                "shipping_pincode": j['data']['pickup_address']['pin_code'],
                "shipping_state": j['data']['pickup_address']['state'],
                "shipping_email": j['data']['pickup_address']['email'],
                # "shipping_isd_code": "91",
                "shipping_phone": j['data']['pickup_address']['phone'],
                "order_items": [
                    {
                    "sku": j['data']['products'][0]['sku'],
                    "name": j['data']['products'][0]['name'],
                    "units": j['data']['others']['order_items'][0]['units'],
                    "selling_price": j['data']['products'][0]['selling_price'],
                    "discount": j['data']['products'][0]['discount'],
                    "hsn": j['data']['products'][0]['hsn'],
                    "brand": j['data']['products'][0]['brand'],
                    # "qc_size": "43"
                    }
                ],
                "payment_method": j['data']['payment_method'],
                # "total_discount": "0",
                "sub_total": j['data']['net_total'],
                "length": j['data']['shipments']['length'],
                "breadth": j['data']['shipments']['breadth'],
                "height": j['data']['shipments']['height'],
                "weight": j['data']['products'][0]['weight']
                })
                headers = {
                'Content-Type': 'application/json',
                'Authorization': SHIPMENT_TOKEN
                }

                response = requests.request("POST", url, headers=headers, data=payload)
                data=response.json()
                if response.status_code==200 or response.status==200:
                    shipment.objects.filter(shipment_order_id=o.shipment_order_id).update(return_shipment_id=data['shipment_id'],return_shipment_order_id=data['order_id'])
                    OrderItemHistory.objects.filter(id=o.order_item_id).update(shipment_status=data['status'])
                    data={
                        "message":"Return Request Successful",
                        "shipment":response.json()
                    }
                    return Response(data,status=status.HTTP_201_CREATED)
                elif response.status_code==400:
                    data={
                        "message":"Failed To Create Return Request",
                        "error" : "Can't Return Product after Cancelling Request"
                    }
                    return Response(data,status=status.HTTP_429_TOO_MANY_REQUESTS)
                else:
                    return Response(response.json())
            else:
                return Response(response1.json())
        else:
            data={
                "message" :"Unauthorized to Ship Order",
                "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
                "status":status.HTTP_401_UNAUTHORIZED
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

class GenerateReturnAWB(CreateAPIView):

    @transaction.atomic()
    def get(self,request,token,oid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
        try:
            o = shipment.objects.get(shipment_order_id=oid)
        except:
            data = {"message" : "Invalid Order Id"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
            #Check If order has been shipped already and not cancelled by admin/vendor 
            url = "https://apiv2.shiprocket.in/v1/external/courier/assign/awb"

            payload = json.dumps({
            "shipment_id": o.return_shipment_id,
            "courier_id": "",
            "status": "",
            "is_return": 1
            })
            headers = {
            'Content-Type': 'application/json',
            'Authorization': SHIPMENT_TOKEN
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            r = response.json()
            if response.status_code == 200:
                print(r['response']['data']['awb_code'])
                shipment.objects.filter(shipment_order_id=o.shipment_order_id).update(return_awb_code=r['response']['data']['awb_code'])
                return Response(r)
            else:
                data={
                    "message":"Failed To Get Return Awb From Shiprocket API",
                    "error":response.json()
                }
                return Response(data)
        else:
            data={
                "message" :"Unauthorized to Ship Order",
                "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
                "status":status.HTTP_401_UNAUTHORIZED
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)