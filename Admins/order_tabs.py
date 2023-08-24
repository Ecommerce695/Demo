# from rest_framework.generics import CreateAPIView
# from django.db import transaction
# from rest_framework.response import Response
# from rest_framework import status
# from pytz import utc
# from datetime import datetime,timedelta
# from customer.models import UserProfile, UserRole,KnoxAuthtoken
# from .serializers import AdminOrderTabFilter
# from super_admin.models import Product ,variants,tags,images,collection,CompanyProfile
# from order.models import OrderItemHistory
# from payments.models import Payment_details_table,Transaction_table
# import re
# from rest_framework.views import APIView


# class GetInProgressOrdersListIncludingFilters(CreateAPIView):
#     serializer_class = AdminOrderTabFilter

#     def post(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         role=UserRole.objects.filter(user_id=user).exclude(role_id=4)
#         if role.exists():
#             if(token1.expiry < datetime.now(utc)):
#                 KnoxAuthtoken.objects.filter(user=user).delete()
#                 data = {"message":'Session Expired, Please login again'}
#                 return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#             else: 
#                 serializer = self.serializer_class(data=request.data)
#                 if serializer.is_valid(raise_exception=True):
#                     o_id=serializer.data['order_id']
#                     date1=serializer.data['from_date']
#                     date2=serializer.data['to_date']
                    
#                     try:
#                         if date1=='' and date2=='':
#                             d1= OrderItemHistory.objects.earliest('created_at').created_at.date()
#                             d2=OrderItemHistory.objects.latest('created_at').created_at.date()
                            
#                         elif date1=='':
#                             d1= OrderItemHistory.objects.earliest('created_at').created_at.date()
#                             date22=datetime.strptime(date2, '%Y-%m-%d')
#                             d2=date22.date()
                            
#                         elif date2=='':
#                             date12=datetime.strptime(date1, '%Y-%m-%d')
#                             d1=date12.date()
#                             d2=OrderItemHistory.objects.latest('created_at').created_at.date()
#                         else:
#                             date12=datetime.strptime(date1, '%Y-%m-%d')
#                             date22=datetime.strptime(date2, '%Y-%m-%d')
#                             d1=date12.date()
#                             d2=date22.date()
#                     except:
#                         d1=datetime.now().date()
#                         d2=datetime.now().date()
#                     if d1<=d2:
#                         o = OrderItemHistory.objects.filter(alias__icontains=o_id,shipment_status__icontains='',created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at','-id')
#                         list=[]
#                         for i in o:
#                             orders = OrderItemHistory.objects.get(alias=i['alias'])
#                             delivery_state='INPROGRESS'
#                             try:
#                                 payment = Transaction_table.objects.get(orderitem=i['id'])
#                                 state=payment.status
#                             except:
#                                 state='Failed'
#                             try:
#                                 src = images.objects.get(id = i['product'])
#                                 image=src.src
#                             except:
#                                 image=''

#                             data = {
#                             "order_id" :orders.alias,
#                             "parent_order_id":orders.order,
#                             "image" : image,
#                             "payment_status" : state,
#                             "delivery_status": delivery_state,
#                             "date": orders.created_at.date(),
#                             "total" : round(orders.item_price,2),
#                             "created_at":orders.created_at.date()
#                             }
#                             list.append(data)
#                         return Response(list, status=status.HTTP_200_OK)
#                     return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
#                 return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
#         data={
#             "error":"Admin,SuperAdmin or Vendor is accepted",
#             "status":status.HTTP_401_UNAUTHORIZED
#             }
#         return Response(data, status=status.HTTP_401_UNAUTHORIZED)
    

# class GetNewOrdersListIncludingFilters(CreateAPIView):
#     serializer_class = AdminOrderTabFilter

#     def post(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         role=UserRole.objects.filter(user_id=user).exclude(role_id=4)
#         if role.exists():
#             if(token1.expiry < datetime.now(utc)):
#                 KnoxAuthtoken.objects.filter(user=user).delete()
#                 data = {"message":'Session Expired, Please login again'}
#                 return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#             else: 
#                 serializer = self.serializer_class(data=request.data)
#                 if serializer.is_valid(raise_exception=True):
#                     o_id=serializer.data['order_id']
#                     date1=serializer.data['from_date']
#                     date2=serializer.data['to_date']
                    
#                     try:
#                         if date1=='' and date2=='':
#                             d1= OrderItemHistory.objects.earliest('created_at').created_at.date()
#                             d2=OrderItemHistory.objects.latest('created_at').created_at.date()
                            
#                         elif date1=='':
#                             d1= OrderItemHistory.objects.earliest('created_at').created_at.date()
#                             date22=datetime.strptime(date2, '%Y-%m-%d')
#                             d2=date22.date()
                            
#                         elif date2=='':
#                             date12=datetime.strptime(date1, '%Y-%m-%d')
#                             d1=date12.date()
#                             d2=OrderItemHistory.objects.latest('created_at').created_at.date()
#                         else:
#                             date12=datetime.strptime(date1, '%Y-%m-%d')
#                             date22=datetime.strptime(date2, '%Y-%m-%d')
#                             d1=date12.date()
#                             d2=date22.date()
#                     except:
#                         d1=datetime.now().date()
#                         d2=datetime.now().date()
#                     if d1<=d2:
#                         o = OrderItemHistory.objects.filter(alias__icontains=o_id,shipment_status__icontains='NEW',created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at','-id')
#                         list=[]
#                         for i in o:
#                             orders = OrderItemHistory.objects.get(alias=i['alias'])
#                             try:
#                                 payment = Transaction_table.objects.get(orderitem=i['id'])
#                                 state=payment.status
#                             except:
#                                 state='failed'
#                             try:
#                                 src = images.objects.get(id = i['product'])
#                                 image=src.src
#                             except:
#                                 image=''

#                             data = {
#                             "order_id" :orders.alias,
#                             "parent_order_id":orders.order,
#                             "image" : image,
#                             "payment_status" : state,
#                             "delivery_status": orders.shipment_status,
#                             "date": orders.created_at.date(),
#                             "total" : round(orders.item_price,2),
#                             "created_at":orders.created_at.date()
#                             }
#                             list.append(data)
#                         return Response(list, status=status.HTTP_200_OK)
#                     return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
#                 return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
#         data={
#             "error":"Admin,SuperAdmin or Vendor is accepted",
#             "status":status.HTTP_401_UNAUTHORIZED
#             }
#         return Response(data, status=status.HTTP_401_UNAUTHORIZED)
                         

# class GetPickedOrdersListIncludingFilters(CreateAPIView):
#     serializer_class = AdminOrderTabFilter

#     def post(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         role=UserRole.objects.filter(user_id=user).exclude(role_id=4)
#         if role.exists():
#             if(token1.expiry < datetime.now(utc)):
#                 KnoxAuthtoken.objects.filter(user=user).delete()
#                 data = {"message":'Session Expired, Please login again'}
#                 return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#             else: 
#                 serializer = self.serializer_class(data=request.data)
#                 if serializer.is_valid(raise_exception=True):
#                     o_id=serializer.data['order_id']
#                     date1=serializer.data['from_date']
#                     date2=serializer.data['to_date']
                    
#                     try:
#                         if date1=='' and date2=='':
#                             d1= OrderItemHistory.objects.earliest('created_at').created_at.date()
#                             d2=OrderItemHistory.objects.latest('created_at').created_at.date()
                            
#                         elif date1=='':
#                             d1= OrderItemHistory.objects.earliest('created_at').created_at.date()
#                             date22=datetime.strptime(date2, '%Y-%m-%d')
#                             d2=date22.date()
                            
#                         elif date2=='':
#                             date12=datetime.strptime(date1, '%Y-%m-%d')
#                             d1=date12.date()
#                             d2=OrderItemHistory.objects.latest('created_at').created_at.date()
#                         else:
#                             date12=datetime.strptime(date1, '%Y-%m-%d')
#                             date22=datetime.strptime(date2, '%Y-%m-%d')
#                             d1=date12.date()
#                             d2=date22.date()
#                     except:
#                         d1=datetime.now().date()
#                         d2=datetime.now().date()
#                     if d1<=d2:
#                         o = OrderItemHistory.objects.filter(alias__icontains=o_id,shipment_status__icontains='PICKUP',created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at','-id')
#                         list=[]
#                         for i in o:
#                             orders = OrderItemHistory.objects.get(alias=i['alias'])
#                             try:
#                                 payment = Transaction_table.objects.get(orderitem=i['id'])
#                                 state=payment.status
#                             except:
#                                 state='failed'
#                             try:
#                                 src = images.objects.get(id = i['product'])
#                                 image=src.src
#                             except:
#                                 image=''

#                             data = {
#                             "order_id" :orders.alias,
#                             "parent_order_id":orders.order,
#                             "image" : image,
#                             "payment_status" : state,
#                             "delivery_status": orders.shipment_status,
#                             "date": orders.created_at.date(),
#                             "total" : round(orders.item_price,2),
#                             "created_at":orders.created_at.date()
#                             }
#                             list.append(data)
#                         return Response(list, status=status.HTTP_200_OK)
#                     return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
#                 return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
#         data={
#             "error":"Admin,SuperAdmin or Vendor is accepted",
#             "status":status.HTTP_401_UNAUTHORIZED
#             }
#         return Response(data, status=status.HTTP_401_UNAUTHORIZED)
                         
# class GetCancelOrdersListIncludingFilters(CreateAPIView):
#     serializer_class = AdminOrderTabFilter

#     def post(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         role=UserRole.objects.filter(user_id=user).exclude(role_id=4)
#         if role.exists():
#             if(token1.expiry < datetime.now(utc)):
#                 KnoxAuthtoken.objects.filter(user=user).delete()
#                 data = {"message":'Session Expired, Please login again'}
#                 return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#             else: 
#                 serializer = self.serializer_class(data=request.data)
#                 if serializer.is_valid(raise_exception=True):
#                     o_id=serializer.data['order_id']
#                     date1=serializer.data['from_date']
#                     date2=serializer.data['to_date']
                    
#                     try:
#                         if date1=='' and date2=='':
#                             d1= OrderItemHistory.objects.earliest('created_at').created_at.date()
#                             d2=OrderItemHistory.objects.latest('created_at').created_at.date()
                            
#                         elif date1=='':
#                             d1= OrderItemHistory.objects.earliest('created_at').created_at.date()
#                             date22=datetime.strptime(date2, '%Y-%m-%d')
#                             d2=date22.date()
                            
#                         elif date2=='':
#                             date12=datetime.strptime(date1, '%Y-%m-%d')
#                             d1=date12.date()
#                             d2=OrderItemHistory.objects.latest('created_at').created_at.date()
#                         else:
#                             date12=datetime.strptime(date1, '%Y-%m-%d')
#                             date22=datetime.strptime(date2, '%Y-%m-%d')
#                             d1=date12.date()
#                             d2=date22.date()
#                     except:
#                         d1=datetime.now().date()
#                         d2=datetime.now().date()
#                     if d1<=d2:
#                         o = OrderItemHistory.objects.filter(alias__icontains=o_id,shipment_status__icontains='CANCEL',created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at','-id')
#                         list=[]
#                         for i in o:
#                             orders = OrderItemHistory.objects.get(alias=i['alias'])
#                             try:
#                                 payment = Transaction_table.objects.get(orderitem=i['id'])
#                                 state=payment.status
#                             except:
#                                 state='failed'
#                             try:
#                                 src = images.objects.get(id = i['product'])
#                                 image=src.src
#                             except:
#                                 image=''

#                             data = {
#                             "order_id" :orders.alias,
#                             "parent_order_id":orders.order,
#                             "image" : image,
#                             "payment_status" : state,
#                             "delivery_status": orders.shipment_status,
#                             "date": orders.created_at.date(),
#                             "total" : round(orders.item_price,2),
#                             "created_at":orders.created_at.date()
#                             }
#                             list.append(data)
#                         return Response(list, status=status.HTTP_200_OK)
#                     return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
#                 return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
#         data={
#             "error":"Admin,SuperAdmin or Vendor is accepted",
#             "status":status.HTTP_401_UNAUTHORIZED
#             }
#         return Response(data, status=status.HTTP_401_UNAUTHORIZED)
                         