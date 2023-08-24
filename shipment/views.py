from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from datetime import datetime
from django.db import transaction
from rest_framework.generics import CreateAPIView
from pytz import utc
from customer.models import KnoxAuthtoken, UserProfile, UserRole, Role, UserAddress
from super_admin.models import Product,variants, CompanyProfile,images
from cart.models import Cart
from payments.models import Transaction_table
from order.models import Order,OrderItemHistory
import requests, json
from .models import shipment
from Ecomerce_project.settings import SHIPMENT_TOKEN
from rest_framework import status

class CreateShipmentForOrder(CreateAPIView):

    @transaction.atomic()
    def post(self,request,token,oid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            o = Order.objects.get(id=oid)
        except:
            data = {"message" : "Invalid Order Id"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        if (UserRole.objects.filter(user_id=usertable.id).exclude(role_id=4)).exists():
            add = UserAddress.objects.get(id=o.delivery)
            order_items = OrderItemHistory.objects.filter(order=oid).values().all()
            if order_items.exists():
                for ord in order_items:
                    tx=Transaction_table.objects.filter(order=ord['order'],status='PAID').values()
                    if tx.exists():

                        order_list=[]
                        list=[]
                        orders_list=[]
                        for i in order_items:
                            item= OrderItemHistory.objects.get(id=i["id"])
                            users = UserProfile.objects.get(id=item.user)
                            if (shipment.objects.filter(order_item_id=item.id).exists()):
                                return Response({"message":"Order Already exists in Shipment"},status=status.HTTP_208_ALREADY_REPORTED)
                            else:
                                pro = Product.objects.get(id=item.product)
                                variant = variants.objects.get(id=pro.id)
                                item_price = item.item_price/item.quantity
                                # unit_price = item_price-(item_price*0.18)
                                shipment_order_items = (
                                    {
                                        "product_id": item.product,
                                        "name": pro.title,
                                        "sku": variant.sku,
                                        "units": item.quantity,
                                        "tax": 18,
                                        "status": 1,
                                        "discount": 0,
                                        "selling_price": item_price,
                                        "hsn": 441122,
                                        "brand": pro.brand,
                                        "color": variant.color,
                                        "size": variant.size,
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
                                        "shipping_charges": max(l),
                                        "giftwrap_charges": 0,
                                        "transaction_charges": 0,
                                        "total_discount": 0,
                                        "sub_total": item.item_price,  
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
                                data=(json.loads(response.text))
                                orders_list.append(data)
                                if response.status_code==200:
                                    s=shipment.objects.create(order_item_id=item.id,shipment_order_id=data['order_id'],shipment_id=data['shipment_id'],
                                                            order_date=item.created_at,order_amount=item.item_price,pickup_address=company_name.id,
                                                            shipping_address=add.id,user=usertable)
                                    shipment.objects.filter(id=s.id).update(alias='SHIP-'+str(s.id))
                                    OrderItemHistory.objects.filter(id=item.id).update(shipment_status=data['status'])
                                    pass
                                else: 
                                    return Response(response.json())
                        return Response(orders_list)
                    return Response({"message":"Cant Proceed Shipment for Unsuccessful Order"})
        else:
            data={
                "message" :"Unauthorized to Ship Order",
                "error":"Admin,SuperAdmin or Vendor is accepted to Start Shipment Process",
                "status":status.HTTP_401_UNAUTHORIZED
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED) 
               
class GetOrderDetails(CreateAPIView):

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
            data = {"message" : "Invalid Shipment Order Id"}
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
    

class PickupRequest(CreateAPIView):

    @transaction.atomic()
    def post(self,request,token,sid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            o = shipment.objects.get(shipment_id=sid)
        except:
            data = {"message" : "Invalid Shipment ID"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        url = "https://apiv2.shiprocket.in/v1/external/courier/generate/pickup"

        payload = json.dumps({
        "shipment_id": [o.shipment_id]
        })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': SHIPMENT_TOKEN
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        return Response(response.json())
    

class GenerateAWB(CreateAPIView):

    @transaction.atomic()
    def post(self,request,token,sid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            o = shipment.objects.get(shipment_id=sid)
        except:
            data = {"message" : "Invalid Shipment ID"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        url = "https://apiv2.shiprocket.in/v1/external/courier/assign/awb"

        payload = json.dumps({
        "shipment_id": o.shipment_id
        })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': SHIPMENT_TOKEN
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return Response(response.json())


class GetPickupLocations(CreateAPIView):

    @transaction.atomic()
    def get(self, request):
        url = "https://apiv2.shiprocket.in/v1/external/settings/company/pickup"

        payload={}
        headers = {
        'Authorization': SHIPMENT_TOKEN
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        return Response(response.json())

class ChangePickupLocation(CreateAPIView):

    @transaction.atomic()
    def patch(self, request, oid, pl):
        try:
            o = shipment.objects.get(shipment_order_id=oid)
        except:
            data = {"message" : "Invalid Order Id"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
        if (CompanyProfile.objects.filter(org_name=pl).exists()):
            p = pl
        elif pl=='Primary': 
            p="Primary"
        else:
            return Response({"message":"Address not found"}, status=status.HTTP_401_UNAUTHORIZED)
        
        url = "https://apiv2.shiprocket.in/v1/external/orders/address/pickup"

        payload = json.dumps({
        "order_id": [
            o.shipment_order_id
        ],
        "pickup_location": p
        })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': SHIPMENT_TOKEN
        }

        response = requests.request("PATCH", url, headers=headers, data=payload)
        # print(response.text)
        return Response(response.json())
    

class ChangeDeliveryLocation(CreateAPIView):

    @transaction.atomic()
    def post(self, request,token, oid, aid):
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
        try:
            address = UserAddress.objects.get(id=aid)
        except:
            data = {"message" : "Invalid Address Id"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
        url = "https://apiv2.shiprocket.in/v1/external/orders/address/update"

        payload = json.dumps({
        "order_id": o.shipment_order_id,
        "shipping_customer_name": address.name,
        "shipping_phone": address.mobile,
        "shipping_address": address.address,
        "shipping_address_2": address.address,
        "shipping_city": address.city,
        "shipping_state": address.state,
        "shipping_country": address.country,
        "shipping_pincode": address.pincode
        })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': SHIPMENT_TOKEN
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)
        return Response({"message":"Updated Successfully"},status=status.HTTP_200_OK)
    

class CancelOrder(CreateAPIView):

    @transaction.atomic()
    def post(self, request,token, oid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        if OrderItemHistory.objects.filter(id=oid,order_status='ORDER PLACED').exclude(shipment_status__in=('CANCELLATION REQUESTED','CANCELED')).exists():
            # try:
            #     o = shipment.objects.get(shipment_order_id=oid)
            #     print(o.s)
            # except:
            #     pass
            try:
                o = shipment.objects.get(order_item_id=oid)
                url = "https://apiv2.shiprocket.in/v1/external/orders/cancel"

                payload = json.dumps({
                "ids": [o.shipment_order_id]
                })
                headers = {
                'Content-Type': 'application/json',
                'Authorization': SHIPMENT_TOKEN
                }

                response = requests.request("POST", url, headers=headers, data=payload)
                # print(response.text)
                OrderItemHistory.objects.filter(id=oid).update(order_status='CANCELLED',shipment_status='CANCELED')
                Transaction_table.objects.filter(orderitem=oid).update(status='REFUND INPROGRESS')
                data={
                    'message':"Successfully Cancelled",
                    "shipment":response.json()
                }
                return Response(data)
            except:
                OrderItemHistory.objects.filter(id=oid).update(order_status='CANCELLED',shipment_status='CANCELED')
                Transaction_table.objects.filter(orderitem=oid).update(status='REFUND INPROGRESS')
                return Response({'message':"Successfully Cancelled"},status=status.HTTP_200_OK)
        

        elif OrderItemHistory.objects.filter(id=oid,shipment_status__in=('CANCELLATION REQUESTED','CANCELED')):
            return Response({'message':"Order Already Cancelled"},status=status.HTTP_429_TOO_MANY_REQUESTS)
        else:
            data={"message":"Order Item ID Not Found"}
            return Response(data,status=status.HTTP_404_NOT_FOUND)
    
class GetallOrders(CreateAPIView):

    @transaction.atomic()
    def get(self, request):
        url = "https://apiv2.shiprocket.in/v1/external/orders"

        payload={}
        headers = {
        'Content-Type': 'application/json',
        'Authorization': SHIPMENT_TOKEN
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        return Response(response.json())


    
class ListReturnOrders(CreateAPIView):

    @transaction.atomic()
    def get(self,request):
        url = "https://apiv2.shiprocket.in/v1/external/orders/processing/return"

        payload={}
        headers = {
        'Content-Type': 'application/json',
        'Authorization': SHIPMENT_TOKEN
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        return Response(response.json())

class AllShipmentDetails(CreateAPIView):

    @transaction.atomic()
    def get(self,request):
        url = "https://apiv2.shiprocket.in/v1/external/shipments"

        payload={}
        headers = {
        'Content-Type': 'application/json',
        'Authorization': SHIPMENT_TOKEN
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        return Response(response.json())
    
class SingleShipmentDetails(CreateAPIView):

    @transaction.atomic()
    def get(self,request,sid):
        url = "https://apiv2.shiprocket.in/v1/external/shipments/"+str(sid)
        payload={}
        headers = {
        'Content-Type': 'application/json',
        'Authorization': SHIPMENT_TOKEN
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        return Response(response.json())
    

class ExportAddress(CreateAPIView):
    def post(self,request):
        address = CompanyProfile.objects.all().values()
        if address.exists():
            for i in address:
                company_name=CompanyProfile.objects.get(id=i['id'])

                url = "https://apiv2.shiprocket.in/v1/external/settings/company/addpickup"

                payload = json.dumps({
                "pickup_location": company_name.org_name,
                "name": company_name.org_name,
                "email": company_name.email,
                "phone": company_name.mobile,
                "address": company_name.address,
                "address_2": '',
                "city": company_name.city,
                "state": company_name.state,
                "country": company_name.country,
                "pin_code": company_name.pincode,
                "gstin" : company_name.tax_id.upper()
                })
                headers = {
                'Content-Type': 'application/json',
                'Authorization': SHIPMENT_TOKEN
                }
                data1=requests.request("POST", url, headers=headers, data=payload)
                print(data1.text)
                print()
            return Response("Success")
        return Response([],status=status.HTTP_204_NO_CONTENT)
            
class CouriersList(CreateAPIView):
    def get(self, request):
        url = "https://apiv2.shiprocket.in/v1/external/courier/courierListWithCounts"
        payload={}
        headers = {
        'Content-Type': 'application/json',
        'Authorization': SHIPMENT_TOKEN
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        return Response(response.json())
    
class DomesticCourierServiceability(CreateAPIView):
    def get(self,request):
        url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"

        payload=json.dumps({
            "pickup_postcode":360490, 
            "delivery_postcode":516439,
            "cod":"0",  # 1 for COD and 0 for Prepaid orders.
            "weight":"0.5",
            "declared_value":300000
        })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': SHIPMENT_TOKEN
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data=response.json()
        print(data)
        if response.status_code==200:
            
            i=1
            date_list=[]
            charger_list=[]
            for i in range(len(data['data']['available_courier_companies'])):
                date = data['data']['available_courier_companies'][i]['etd']
                shipping_chargers = data['data']['available_courier_companies'][i]["freight_charge"]
                i=i+1
                date_list.append(date)
                charger_list.append(shipping_chargers)
            values={
                "city":data['data']['available_courier_companies'][0]['city'],
                "max_days" : max(date_list),
                "min_days" : min(date_list),
                "Min_shipping_charge":min(charger_list),
                "Max_shipping_chargers":max(charger_list)
            }
            
            return Response(values)
        # return Response(response.json())
