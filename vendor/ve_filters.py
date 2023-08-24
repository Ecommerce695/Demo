from rest_framework.generics import CreateAPIView
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from pytz import utc
from datetime import datetime,timezone,timedelta
from customer.models import UserProfile, UserRole, Role,KnoxAuthtoken
from super_admin.models import Product ,variants,tags,images,collection,CompanyProfile
from order.models import OrderItemHistory
from payments.models import Payment_details_table,Transaction_table
import re
from django.core.paginator import Paginator
from Ecomerce_project.settings import prperpage
from shipment.models import shipment
from vendor.serializers import vend_prod_seri,vend_orde_seri,vend_sales_seri






class GetvendorProductsIncludingFilters(CreateAPIView):
    serializer_class = vend_prod_seri
    
    @transaction.atomic
    def post(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role3 = Role.objects.get(role='VENDOR')
        venrole = role3.role_id
        roles = UserRole.objects.filter(role_id=venrole).filter(user_id=userdata)
        if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.serializer_class(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        category = serializer.data['category']
                        name=serializer.data['name']
                        brand=serializer.data['brand']
                        type1=serializer.data['type']
                        p1=serializer.data['price_from']
                        p2=serializer.data['price_to']
                        date1=serializer.data['from_date']
                        date2=serializer.data['to_date']
                        pageno=serializer.validated_data['pageno']
                        try:
                            if date1=='' and date2=='':
                                d1= Product.objects.earliest('created_at').created_at.date()
                                d2=Product.objects.latest('created_at').created_at.date()
                            elif date1=='':
                                d1= Product.objects.earliest('created_at').created_at.date()
                                date22=datetime.strptime(date2, '%Y-%m-%d')
                                d2=date22.date()
                            elif date2=='':
                                date12=datetime.strptime(date1, '%Y-%m-%d')
                                d1=date12.date()
                                d2=Product.objects.latest('created_at').created_at.date()
                            else:
                                date12=datetime.strptime(date1, '%Y-%m-%d')
                                date22=datetime.strptime(date2, '%Y-%m-%d')
                                d1=date12.date()
                                d2=date22.date()
                        except:
                            d1=datetime.now().date()
                            d2=datetime.now().date()
                        product_list =Product.objects.filter(user=userdata,title__icontains=name,brand__icontains=brand,category__icontains=category,type__icontains=type1,price__range=[p1,p2],created_at__range=(d1,d2+timedelta(days=1))).values('id').order_by('-created_at','-id')
                        datalist =[]
                        if d1<=d2:
                            if product_list.exists(): 
                                for i in product_list:
                                    try:
                                        pro = Product.objects.get(id = i['id'])
                                        col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
                                        var = variants.objects.filter(id=i['id']).values()
                                        img = images.objects.filter(id=i['id']).values()
                                        t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
                                        vendor = CompanyProfile.objects.get(user=pro.user)
                                        data = {
                                            "id": pro.id,
                                            "title": pro.title,
                                            "description": pro.description, 
                                            "type": pro.type,
                                            "brand": pro.brand,
                                            "collection": col,
                                            "category": pro.category,
                                            "price": round(pro.price,2),
                                            "sale": pro.sale,
                                            "discount": pro.discount,
                                            "stock": pro.stock,
                                            "new": pro.new,
                                            "tags":t,
                                            "variants" : var,
                                            "images" : img,
                                            "sold_by" : vendor.org_name,
                                            "created_at":pro.created_at.date(),
                                            "is_deleted":pro.is_deleted
                                        }
                                        datalist.append(data)
                                        paginator = Paginator(datalist,prperpage)
                                        page = request.GET.get("page",pageno)
                                        object_list = paginator.page(page)
                                        a=list(object_list)

                                        data1 = {
                                            "vendorproducts_data":a,
                                            "total_pages":paginator.num_pages,
                                            "products_per_page":prperpage,
                                            "total_products":paginator.count
                                        }
                                    except:
                                        pass
                                try:
                                    return Response(data1,status=status.HTTP_200_OK)
                                except:
                                    return Response({"message":"Page/value error"},status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response([], status=status.HTTP_204_NO_CONTENT)
                        else:
                            return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data={'message':"Current User is not Vendor"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your Company account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        







class GetMyOrdersListIncludingFilters(CreateAPIView):
    serializer_class = vend_orde_seri

    @transaction.atomic
    def post(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        user = token1.user_id
        userda = UserProfile.objects.get(id=user)
        userdata = userda.id
        role3 = Role.objects.get(role='VENDOR')
        venrole = role3.role_id
        roles = UserRole.objects.filter(role_id=venrole).filter(user_id=userdata)
        if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
            if roles.exists():
                if(token1.expiry < datetime.now(utc)):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else: 
                    serializer = self.serializer_class(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        o_id=serializer.data['order_id']
                        p_status=serializer.data['payment_status']
                        shipment_status=serializer.data['shipment_status']
                        o_status=serializer.data['order_status']
                        date1=serializer.data['from_date']
                        date2=serializer.data['to_date']
                        pageno=serializer.validated_data['pageno']
                        try:
                            if date1=='' and date2=='':
                                d1= OrderItemHistory.objects.earliest('created_at').created_at.date()
                                d2=OrderItemHistory.objects.latest('created_at').created_at.date()
                                
                            elif date1=='':
                                d1= OrderItemHistory.objects.earliest('created_at').created_at.date()
                                date22=datetime.strptime(date2, '%Y-%m-%d')
                                d2=date22.date()
                                
                            elif date2=='':
                                date12=datetime.strptime(date1, '%Y-%m-%d')
                                d1=date12.date()
                                d2=OrderItemHistory.objects.latest('created_at').created_at.date()
                            else:
                                date12=datetime.strptime(date1, '%Y-%m-%d')
                                date22=datetime.strptime(date2, '%Y-%m-%d')
                                d1=date12.date()
                                d2=date22.date()
                        except:
                            d1=datetime.now().date()
                            d2=datetime.now().date()
                        u = UserProfile.objects.get(id=user)
                        if (Product.objects.filter(user=u.id).exists()):
                            if d1<=d2:
                                if p_status=='':
                                    p=Product.objects.filter(user_id=u.id).values('id')
                                    datalist=[]
                                    for k in p:
                                        o = OrderItemHistory.objects.filter(product=k['id'],alias__icontains=o_id,shipment_status__icontains=shipment_status, order_status__icontains=o_status,created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at','-id')
                                        for i in o:
                                            try:
                                                orders = OrderItemHistory.objects.get(alias=i['alias'])

                                                if orders.shipment_status=='':
                                                    s_status='NA'
                                                else:
                                                    s_status=orders.shipment_status

                                                try:
                                                    payment = Transaction_table.objects.get(orderitem=i['id'])
                                                    state=payment.status
                                                except:
                                                    state='FAILED'

                                                try:
                                                    src = images.objects.get(id = i['product'])
                                                    image=src.src
                                                except:
                                                    image=''

                                                try:
                                                    ship =shipment.objects.get(order_item_id=orders.id)
                                                    shipment_id=ship.shipment_id
                                                except:
                                                    shipment_id=''

                                                pro = Product.objects.get(id=orders.product)
                                                u = UserProfile.objects.get(username=pro.user)
                                                company = CompanyProfile.objects.get(user=u.id)

                                                if orders.shipment_status=='' and orders.order_status=='ORDER PLACED':
                                                    shipment_actions='SHIP NOW'
                                                elif orders.shipment_status=='NEW':
                                                    shipment_actions='PICKUP'
                                                elif orders.shipment_status=='PICKUP SCHEDULED' or orders.shipment_status=='PICKUP BOOKED' or orders.shipment_status=='OUT FOR PICKUP':
                                                    shipment_actions='DOWNLOAD MANIFEST/LABEL/INVOICE'
                                                elif orders.shipment_status=='IN TRANSIT' or orders.shipment_status=='PICKED UP' or orders.shipment_status=='PICKED':
                                                    shipment_actions='TRACK ORDER'
                                                elif orders.shipment_status=='DELIVERED':
                                                    shipment_actions='VIEW ORDER'
                                                elif orders.order_status=='CANCELLED':
                                                    shipment_actions='CANCELLED'
                                                elif orders.order_status=='RETURNED':
                                                    shipment_actions='RETURNED'
                                                elif orders.order_status=='INPROGRESS':
                                                    shipment_actions='INPROGRESS'
                                                else :
                                                    shipment_actions='NA'

                                                data = {
                                                    "order_id" :orders.alias,
                                                    "parent_order_id":orders.order,
                                                    "image" : image,
                                                    "payment_status" : state,
                                                    "order_status":orders.order_status,
                                                    "shipment_status": s_status,
                                                    "date": orders.created_at.date(),
                                                    "total" : round(orders.item_price,2),
                                                    "created_at":orders.created_at.date(),
                                                    "shipment_id":shipment_id,
                                                    "shipment_actions":shipment_actions,
                                                    "org_name":company.org_name
                                                }
                                                datalist.append(data)
                                                paginator = Paginator(datalist,prperpage)
                                                page = request.GET.get("page",pageno)
                                                object_list = paginator.page(page)
                                                a=list(object_list)
                                                data1 = {
                                                    "my_orders_data":a,
                                                    "total_pages":paginator.num_pages,
                                                    "products_per_page":prperpage,
                                                    "total_products":paginator.count
                                                }
                                            except:
                                                pass
                                    try:
                                        return Response(data1,status=status.HTTP_200_OK)
                                    except:
                                        return Response({"message":"pagination value error"},status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    tt = Transaction_table.objects.filter(status__iexact=p_status).values()
                                    if tt.exists():
                                        p=Product.objects.filter(user=u.id).values('id')
                                        datalist=[]
                                        for k in p:
                                            for t in tt:
                                                o = OrderItemHistory.objects.filter(product=k['id'],id=int(t['orderitem']),alias__icontains=o_id,shipment_status__icontains=shipment_status, order_status__icontains=o_status,created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at','-id')
                                                for i in o:
                                                    try:
                                                        orders = OrderItemHistory.objects.get(alias=i['alias'])
                                                        
                                                        if orders.shipment_status=='':
                                                            s_status='NA'
                                                        else:
                                                            s_status=orders.shipment_status

                                                        try:
                                                            payment = Transaction_table.objects.get(orderitem=i['id'])
                                                            state=payment.status
                                                        except:
                                                            state='FAILED'

                                                        try:
                                                            src = images.objects.get(id = i['product'])
                                                            image=src.src
                                                        except:
                                                            image=''
                                                            
                                                        try:
                                                            ship =shipment.objects.get(order_item_id=orders.id)
                                                            shipment_id=ship.shipment_id
                                                        except:
                                                            shipment_id=''
                                                        pro = Product.objects.get(id=orders.product)
                                                        u = UserProfile.objects.get(username=pro.user)
                                                        company = CompanyProfile.objects.get(user=u.id)

                                                        if orders.shipment_status=='' and orders.order_status=='ORDER PLACED':
                                                            shipment_actions='SHIP NOW'
                                                        elif orders.shipment_status=='NEW':
                                                            shipment_actions='PICKUP'
                                                        elif orders.shipment_status=='PICKUP SCHEDULED' or orders.shipment_status=='PICKUP BOOKED' or orders.shipment_status=='OUT FOR PICKUP':
                                                            shipment_actions='DOWNLOAD MANIFEST/LABEL/INVOICE'
                                                        elif orders.shipment_status=='IN TRANSIT' or orders.shipment_status=='PICKED UP' or orders.shipment_status=='PICKED':
                                                            shipment_actions='TRACK ORDER'
                                                        elif orders.shipment_status=='DELIVERED':
                                                            shipment_actions='VIEW ORDER'
                                                        elif orders.order_status=='CANCELLED':
                                                            shipment_actions='CANCELLED'
                                                        elif orders.order_status=='RETURNED':
                                                            shipment_actions='RETURNED'
                                                        elif orders.order_status=='INPROGRESS':
                                                            shipment_actions='INPROGRESS'
                                                        else :
                                                            shipment_actions='NA'

                                                        data = {
                                                            "order_id" :orders.alias,
                                                            "parent_order_id":orders.order,
                                                            "image" : image,
                                                            "payment_status" : state,
                                                            "order_status":orders.order_status,
                                                            "shipment_status": s_status,
                                                            "date": orders.created_at.date(),
                                                            "total" : round(orders.item_price,2),
                                                            "created_at":orders.created_at.date(),
                                                            "shipment_id":shipment_id,
                                                            "shipment_actions":shipment_actions,
                                                            "org_name":company.org_name
                                                        }
                                                        datalist.append(data)
                                                        paginator = Paginator(datalist,prperpage)
                                                        page = request.GET.get("page",pageno)
                                                        object_list = paginator.page(page)
                                                        a=list(object_list)
                                                        data1 = {
                                                            "my_orders_data":a,
                                                            "total_pages":paginator.num_pages,
                                                            "products_per_page":prperpage,
                                                            "total_products":paginator.count
                                                        }
                                                    except:
                                                        pass
                                        try:
                                            return Response(data1,status=status.HTTP_200_OK)
                                        except:
                                            return Response({"message":"pagnation value error"},status=status.HTTP_400_BAD_REQUEST)
                                    else:
                                        return Response({'message':"Payment status not found"},status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            return Response({'message':"Products not found for this user"},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data={'message':"Current User is not Vendor"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your Company account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)







class GetSalesListIncludingFilters(CreateAPIView):
    serializer_class = vend_sales_seri

    @transaction.atomic
    def post(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        user = token1.user_id
        usertb = UserProfile.objects.get(id=user)
        userdata = usertb.id
        role3 = Role.objects.get(role='VENDOR')
        venrole = role3.role_id
        roles = UserRole.objects.filter(role_id=venrole).filter(user_id=userdata)
        if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
            if roles.exists():
                if(token1.expiry < datetime.now(utc)):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else: 
                    serializer = self.serializer_class(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        oid=serializer.data['order_id']
                        o_id=re.findall('\d+',oid)
                        i_id=serializer.data['invoice_id']
                        t_id=serializer.data['transaction_id']
                        d_status=serializer.data['delivery_status']
                        date1=serializer.data['from_date']
                        date2=serializer.data['to_date']
                        pageno=serializer.validated_data['pageno']
                        try:
                            if date1=='' and date2=='':
                                d1= OrderItemHistory.objects.earliest('created_at').created_at.date()
                                d2=OrderItemHistory.objects.latest('created_at').created_at.date()
                            elif date1=='':
                                d1= OrderItemHistory.objects.earliest('created_at').created_at.date()
                                date22=datetime.strptime(date2, '%Y-%m-%d')
                                d2=date22.date()
                            elif date2=='':
                                date12=datetime.strptime(date1, '%Y-%m-%d')
                                d1=date12.date()
                                d2=OrderItemHistory.objects.latest('created_at').created_at.date()
                            else:
                                date12=datetime.strptime(date1, '%Y-%m-%d')
                                date22=datetime.strptime(date2, '%Y-%m-%d')
                                d1=date12.date()
                                d2=date22.date()
                        except:
                            d1=datetime.now().date()
                            d2=datetime.now().date()

                        prtabl = Product.objects.filter(user=userdata).values('id')

                        if oid!='':
                            order_id=o_id[0]
                        else:
                            order_id=''
                        if d1<=d2:
                            if (Transaction_table.objects.filter(status__icontains='PAID').exists()):
                                if i_id=='':
                                    tx=Transaction_table.objects.filter(orderitem__icontains=order_id,alias__icontains=t_id,created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at')
                                    datalist=[]
                                    for k in tx:
                                        try:
                                            d = OrderItemHistory.objects.filter(id=k['orderitem'],shipment_status__icontains=d_status,product__in=prtabl).values().order_by('-created_at')
                                            for i in d:
                                                ord = OrderItemHistory.objects.get(id=i['id'])
                                                txn=Transaction_table.objects.get(orderitem=i['id'],status='PAID')
                                                pay = Payment_details_table.objects.get(orderitem=i['id'])
                                                data={
                                                    "order_id" : ord.alias,
                                                    "transaction_id" : txn.alias,
                                                    "shipment_status" : ord.shipment_status,
                                                    "order_status":ord.order_status,
                                                    "payment_status":txn.status,
                                                    "invoice_id" : pay.invoiceno,
                                                    "amount" : round(pay.amount,2),
                                                    "created_at":txn.created_at.date()
                                                }
                                                datalist.append(data)
                                            paginator = Paginator(datalist,prperpage)
                                            page = request.GET.get("page",pageno)
                                            object_list = paginator.page(page)
                                            a=list(object_list)
                                            data1 = {
                                                "sales_data":a,
                                                "total_pages":paginator.num_pages,
                                                "products_per_page":prperpage,
                                                "total_products":paginator.count
                                            }
                                        except:
                                            pass
                                    try:
                                        return Response(data1,status=status.HTTP_200_OK)
                                    except:
                                        return Response({"message":"pagination value error"},status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    p=Payment_details_table.objects.filter(invoiceno__icontains=i_id).values()
                                    datalist=[]
                                    if p.exists():
                                        for i in p:
                                            try:
                                                ord=OrderItemHistory.objects.filter(id=i['orderitem'],product__in=prtabl).values()
                                                for j in ord:
                                                    tx=Transaction_table.objects.filter(orderitem=j['id'],alias__icontains=t_id,created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at')
                                                    for i in tx:
                                                            txn=Transaction_table.objects.get(id=i['id'],status='PAID')
                                                            ord = OrderItemHistory.objects.get(id=txn.orderitem)
                                                            pay = Payment_details_table.objects.get(orderitem=ord.id)
                                                            data={
                                                                "order_id" : ord.alias,
                                                                "transaction_id" : txn.alias,
                                                                "shipment_status" : ord.shipment_status,
                                                                "order_status":ord.order_status,
                                                                "payment_status":txn.status,
                                                                "invoice_id" : pay.invoiceno,
                                                                "amount" : round(pay.amount,2),
                                                                "created_at":txn.created_at.date()
                                                            }
                                                            datalist.append(data)
                                                    paginator = Paginator(datalist,prperpage)
                                                    page = request.GET.get("page",pageno)
                                                    object_list = paginator.page(page)
                                                    a=list(object_list)
                                                    data1 = {
                                                        "sales_data":a,
                                                        "total_pages":paginator.num_pages,
                                                        "products_per_page":prperpage,
                                                        "total_products":paginator.count
                                                    }
                                            except:
                                                pass
                                        try:
                                            return Response(data1,status=status.HTTP_200_OK)
                                        except:
                                            return Response({"message":"pagination value error"},status=status.HTTP_400_BAD_REQUEST)
                                    else:
                                        return Response([],status=status.HTTP_204_NO_CONTENT)
                            else:
                                return Response([],status=status.HTTP_204_NO_CONTENT)
                        else:
                            return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data={'message':"Current User is not Vendor"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your Company account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)