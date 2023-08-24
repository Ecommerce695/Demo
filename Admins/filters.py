from rest_framework.generics import CreateAPIView
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from pytz import utc
from datetime import datetime,timezone,timedelta
from customer.models import UserProfile, UserRole, Role,KnoxAuthtoken
from .serializers import AdminProductsFilter, AdminVendorsFilter, AdminOrderFilter, AdminUsersFilter, AdminSalesFilter
from super_admin.models import Product ,variants,tags,images,collection,CompanyProfile
from order.models import OrderItemHistory
from payments.models import Payment_details_table,Transaction_table
import re
from rest_framework.views import APIView
from django.core.paginator import Paginator
from Ecomerce_project.settings import prperpage
from shipment.models import shipment

class GetAdminProductsIncludingFilters(APIView):
    serializer_class = AdminProductsFilter
    
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
        role3 = Role.objects.get(role='ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
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
                        
                        if d1<=d2:
                            product_list =Product.objects.filter(user_id=userdata,title__icontains=name,brand__icontains=brand,category__icontains=category,type__icontains=type1,price__range=[p1,p2],created_at__range=(d1,d2+timedelta(days=1))).values('id').order_by('-created_at','-id')
                            datalist =[]
                            if product_list.exists(): 
                                for i in product_list:
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
                                    "adminproducts_data":a,
                                    "total_pages":paginator.num_pages,
                                    "products_per_page":prperpage,
                                    "total_products":paginator.count
                                }
                                try:
                                    return Response(data1,status=status.HTTP_200_OK)
                                except:
                                    return Response({"message":"Page/value error"},status=status.HTTP_400_BAD_REQUEST)
                            paginator = Paginator(datalist,prperpage)
                            page = request.GET.get("page",pageno)
                            object_list = paginator.page(page)
                            a=list(object_list)

                            data1 = {
                                "adminproducts_data":a,
                                "total_pages":paginator.num_pages,
                                "products_per_page":prperpage,
                                "total_products":paginator.count
                            }
                            return Response(data1, status=status.HTTP_200_OK)
                        return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                    return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data={'message':"Current User is not Admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


class GetAllProductsIncludingFilters(CreateAPIView):
    serializer_class = AdminProductsFilter

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
        role3 = Role.objects.get(role='ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
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
                         
                        if d1<=d2:
                            product_list=Product.objects.filter(title__icontains=name,brand__icontains=brand,category__icontains=category,type__icontains=type1,price__range=[p1,p2],created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at','-id')
                            datalist =[]
                            if product_list.exists():
                                for i in product_list:
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
                                        "created_at":pro.created_at.date()
                                    }
                                    datalist.append(data)
                                    print(data)
                                paginator = Paginator(datalist,prperpage)
                                page = request.GET.get("page",pageno)
                                object_list = paginator.page(page)
                                a=list(object_list)
                                data1 = {
                                    "products_data":a,
                                    "total_pages":paginator.num_pages,
                                    "products_per_page":prperpage,
                                    "total_products":paginator.count
                                }
                                try:
                                    return Response(data1,status=status.HTTP_200_OK)
                                except:
                                    return Response({"message":"Page/value error"},status=status.HTTP_400_BAD_REQUEST)
                            paginator = Paginator(datalist,prperpage)
                            page = request.GET.get("page",pageno)
                            object_list = paginator.page(page)
                            a=list(object_list)
                            data1 = {
                                "products_data":a,
                                "total_pages":paginator.num_pages,
                                "products_per_page":prperpage,
                                "total_products":paginator.count
                            }
                            return Response(data1, status=status.HTTP_200_OK)
                        return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                    return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data={'message':"Current User is not Admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


class GetUsersListIncludingFilters(CreateAPIView):
    serializer_class = AdminUsersFilter

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
        r_admin = Role.objects.get(role='ADMIN')
        role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)
        if role.exists():
            r_user= Role.objects.get(role='USER')
            role_u=UserRole.objects.filter(role_id=r_user.role_id).values()
            if(UserProfile.objects.filter(id=user, is_active='True')):
                if role_u.exists():
                    if token1.expiry < datetime.now(utc):
                        KnoxAuthtoken.objects.filter(user=user).delete()
                        data = {"message":'Session Expired, Please login again'}
                        return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                    else: 
                        serializer = self.serializer_class(data=request.data)
                        if serializer.is_valid(raise_exception=True):
                            active=serializer.data['is_active']
                            # name=serializer.data['name']
                            email=serializer.data['email']
                            date1=serializer.data['from_date']
                            date2=serializer.data['to_date']
                            pageno=serializer.validated_data['pageno']
                            try:
                                if date1=='' and date2=='':
                                    d1= UserProfile.objects.earliest('date_joined').date_joined.date()
                                    d2=UserProfile.objects.latest('date_joined').date_joined.date()
                                elif date1=='':
                                    d1= UserProfile.objects.earliest('date_joined').date_joined.date()
                                    date22=datetime.strptime(date2, '%Y-%m-%d')
                                    d2=date22.date()
                                elif date2=='':
                                    date12=datetime.strptime(date1, '%Y-%m-%d')
                                    d1=date12.date()
                                    d2=UserProfile.objects.latest('date_joined').date_joined.date()
                                else:
                                    date12=datetime.strptime(date1, '%Y-%m-%d')
                                    date22=datetime.strptime(date2, '%Y-%m-%d')
                                    d1=date12.date()
                                    d2=date22.date()
                            except:
                                d1=datetime.now().date()
                                d2=datetime.now().date()
                            if active!='':
                                user_list=UserProfile.objects.filter(email__icontains=email,is_active__icontains=active,date_joined__range=(d1,d2+timedelta(days=1))).values().order_by('-date_joined','-id')
                            else:
                                user_list=UserProfile.objects.filter(email__icontains=email,date_joined__range=(d1,d2+timedelta(days=1))).values().order_by('-date_joined','-id')
                            if d1<=d2:
                                l=[]
                                if user_list.exists():
                                    datalist =[] 
                                    for j in user_list:
                                        if (UserRole.objects.filter(user_id=j['id'],role_id=3)):
                                            assigned_role = 'USER/VENDOR'
                                            usertable= UserProfile.objects.get(id = j['id'])
                                            count = datetime.now(timezone.utc)- usertable.last_login
                                            data = {
                                                "id" : usertable.id,
                                                "username":usertable.username,
                                                "mobile_number":usertable.mobile_number,
                                                "email":usertable.email,
                                                "first_name":usertable.first_name,
                                                "last_name":usertable.last_name,
                                                "is_active" : usertable.is_active,
                                                "last_Login" : count.days,
                                                "is_vendor" : usertable.is_vendor_com_user,
                                                "roles" : assigned_role,
                                                "date_joined":usertable.date_joined.date()
                                            }
                                            datalist.append(data)

                                        elif (UserRole.objects.filter(user_id=j['id'],role_id=4)):
                                            assigned_role = 'USER'
                                            usertable= UserProfile.objects.get(id = j['id'])

                                            count = datetime.now(timezone.utc)- usertable.last_login
                                            data = {
                                                "id" : usertable.id,
                                                "username":usertable.username,
                                                "mobile_number":usertable.mobile_number,
                                                "email":usertable.email,
                                                "first_name":usertable.first_name,
                                                "last_name":usertable.last_name,
                                                "is_active" : usertable.is_active,
                                                "last_Login" : count.days,
                                                "is_vendor" : usertable.is_vendor_com_user,
                                                "roles" : assigned_role,
                                                "date_joined":usertable.date_joined.date()
                                            }
                                            datalist.append(data)

                                    paginator = Paginator(datalist,prperpage)
                                    page = request.GET.get("page",pageno)
                                    object_list = paginator.page(page)
                                    a=list(object_list)
                                    data1 = {
                                        "users_data":a,
                                        "total_pages":paginator.num_pages,
                                        "products_per_page":prperpage,
                                        "total_products":paginator.count
                                    }
                                    try:
                                        return Response(data1,status=status.HTTP_200_OK)
                                    except:
                                        return Response({"message":"Page/value error"},status=status.HTTP_400_BAD_REQUEST)
                                paginator = Paginator(l,prperpage)
                                page = request.GET.get("page",pageno)
                                object_list = paginator.page(page)
                                a=list(object_list)
                                data1 = {
                                    "users_data":a,
                                    "total_pages":paginator.num_pages,
                                    "products_per_page":prperpage,
                                    "total_products":paginator.count
                                }
                                return Response(data1, status=status.HTTP_200_OK)
                            return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
                return Response({"message":"Userdata not found in Role"}, status=status.HTTP_404_NOT_FOUND)  
            else:
                data = {"message":'User is in In-Active, please Activate your account'}
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data={'message':"Current User is not Admin"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
    
class GetVendorsListIncludingFilters(CreateAPIView):
    serializer_class = AdminVendorsFilter

    def post(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        user = token1.user_id
        r_admin = Role.objects.get(role='ADMIN')
        role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)
        if role.exists():
            if(UserProfile.objects.filter(id=user, is_active='True')):
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else: 
                    serializer = self.serializer_class(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        active=serializer.data['is_active']
                        name=serializer.data['org_name']
                        tax_status=serializer.data['tax_status']
                        email=serializer.data['email']
                        date1=serializer.data['from_date']
                        date2=serializer.data['to_date']
                        pageno=serializer.validated_data['pageno']
                        try:
                            if date1=='' and date2=='':
                                d1= CompanyProfile.objects.earliest('date_joined').date_joined.date()
                                d2=CompanyProfile.objects.latest('date_joined').date_joined.date()
                            elif date1=='':
                                d1= CompanyProfile.objects.earliest('date_joined').date_joined.date()
                                date22=datetime.strptime(date2, '%Y-%m-%d')
                                d2=date22.date()
                            elif date2=='':
                                date12=datetime.strptime(date1, '%Y-%m-%d')
                                d1=date12.date()
                                d2=CompanyProfile.objects.latest('date_joined').date_joined.date()
                            else:
                                date12=datetime.strptime(date1, '%Y-%m-%d')
                                date22=datetime.strptime(date2, '%Y-%m-%d')
                                d1=date12.date()
                                d2=date22.date()
                        except:
                            d1=datetime.now().date()
                            d2=datetime.now().date()

                        if tax_status=='':
                            tax_s=''
                        else:
                            tax_s=tax_status

                        if active!='':
                            user_list=CompanyProfile.objects.filter(is_active__icontains=active,org_name__icontains=name,tax_status__icontains=tax_s,email__icontains=email,date_joined__range=(d1,d2+timedelta(days=1))).values().order_by('-date_joined')
                        else:
                            user_list=CompanyProfile.objects.filter(org_name__icontains=name,tax_status__icontains=tax_s,email__icontains=email,date_joined__range=(d1,d2+timedelta(days=1))).values().order_by('-date_joined')
                        
                        if d1<=d2:   
                            l=[]                
                            if user_list.exists():
                                datalist=[]
                                for j in user_list:
                                    if (UserRole.objects.filter(user_id=j['user_id'],role_id=3).exists()):
                                        assigned_role = 'VENDOR'
                                        v = CompanyProfile.objects.get(user=j['user_id'])
                                        data = {
                                        "org_name" : v.org_name,
                                        "mobile" : v.mobile,
                                        "email" : v.email,
                                        "tax_id" : v.tax_id,
                                        "tax_status": v.tax_status,
                                        "is_active" : v.is_active,
                                        "date_joined":v.date_joined.date(),
                                        "role":assigned_role,
                                        }
                                        datalist.append(data)
                                paginator = Paginator(datalist,prperpage)
                                page = request.GET.get("page",pageno)
                                object_list = paginator.page(page)
                                a=list(object_list)
                                data1 = {
                                    "vendors_data":a,
                                    "total_pages":paginator.num_pages,
                                    "products_per_page":prperpage,
                                    "total_products":paginator.count
                                }
                                try:
                                    return Response(data1,status=status.HTTP_200_OK)
                                except:
                                    return Response({"message":"page/value error"},status=status.HTTP_400_BAD_REQUEST)
                            paginator = Paginator(l,prperpage)
                            page = request.GET.get("page",pageno)
                            object_list = paginator.page(page)
                            a=list(object_list)
                            data1 = {
                                "vendors_data":a,
                                "total_pages":paginator.num_pages,
                                "products_per_page":prperpage,
                                "total_products":paginator.count
                            }
                            return Response(data1,status=status.HTTP_200_OK)
                        return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                    return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message":'User is in In-Active, please Activate your account'}
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
            
        return Response({'message':"Current User is not Admin"},status=status.HTTP_404_NOT_FOUND)

class GetAllOrdersListIncludingFilters(CreateAPIView):
    serializer_class = AdminOrderFilter

    def post(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        user = token1.user_id

        r_admin = Role.objects.get(role='ADMIN')
        role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

        if role.exists():
            if(token1.expiry < datetime.now(utc)):
                KnoxAuthtoken.objects.filter(user=user).delete()
                data = {"message":'Session Expired, Please login again'}
                return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
            else: 
                serializer = self.serializer_class(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    o_id=serializer.data['order_id']
                    p_status=serializer.data['payment_status']
                    o_status=serializer.data['order_status']
                    shipment_status=serializer.data['shipment_status']
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
                    if d1<=d2:
                        if p_status=='':
                            o = OrderItemHistory.objects.filter(alias__icontains=o_id, shipment_status__icontains=shipment_status, order_status__icontains=o_status,created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at','-id')
                            datalist=[]
                            for i in o:
                                orders = OrderItemHistory.objects.get(alias=i['alias'])
                                if orders.shipment_status=='':
                                    s_status='NA'
                                else:
                                    s_status=orders.shipment_status
                                
                                try:
                                    payment = Transaction_table.objects.get(orderitem=i['id'])
                                    state=payment.status
                                except:
                                    if orders.order_status=='INPROGRESS':
                                        state='ON HOLD'
                                    else:
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
                                "order_item_id" :orders.id,
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
                                "all_orders_data":a,
                                "total_pages":paginator.num_pages,
                                "products_per_page":prperpage,
                                "total_products":paginator.count
                            }
                            try:
                                return Response(data1,status=status.HTTP_200_OK)
                            except:
                                return Response({"message":"value error"},status=status.HTTP_400_BAD_REQUEST)
                        else:
                            tt = Transaction_table.objects.filter(status__iexact=p_status).values('orderitem')
                            datalist=[]
                            if tt.exists():
                                for t in tt:
                                    o = OrderItemHistory.objects.filter(id=int(t['orderitem']),alias__icontains=o_id,shipment_status__icontains=shipment_status, order_status__icontains=o_status,created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at','-id')
                                    for i in o:
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
                                            "order_item_id" :orders.id,
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
                                    "all_orders_data":a,
                                    "total_pages":paginator.num_pages,
                                    "products_per_page":prperpage,
                                    "total_products":paginator.count
                                }
                                try:
                                    return Response(data1,status=status.HTTP_200_OK)
                                except:
                                    return Response({"message":"value error"},status=status.HTTP_400_BAD_REQUEST)
                    return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"Userdata not found in Role"}, status=status.HTTP_404_NOT_FOUND)


class GetSalesListIncludingFilters(CreateAPIView):
    serializer_class = AdminSalesFilter

    def post(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        user = token1.user_id
        r_admin = Role.objects.get(role='ADMIN')
        role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)
        if role.exists():
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
                    if oid!='':
                        order_id=o_id[0]
                    else:
                        order_id=''
                    if d1<=d2:
                        l=[]
                        if (Transaction_table.objects.filter(status='PAID').exists()):
                            if i_id=='':
                                tx=Transaction_table.objects.filter(orderitem__icontains=order_id,alias__icontains=t_id,created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at')
                                datalist=[]
                                for k in tx:
                                    d = OrderItemHistory.objects.filter(id=k['orderitem'],shipment_status__icontains=d_status).values().order_by('-created_at')
                                    for i in d:
                                        try:
                                            ord = OrderItemHistory.objects.get(id=i['id'])
                                            txn=Transaction_table.objects.get(orderitem=i['id'],status='PAID')
                                            try:
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
                                            except:
                                                pass
                                        except:
                                            pass
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
                                try:
                                    return Response(data1,status=status.HTTP_200_OK)
                                except:
                                    return Response({"message":"value error"},status=status.HTTP_400_BAD_REQUEST)
                            else:
                                p=Payment_details_table.objects.filter(invoiceno__icontains=i_id).values()
                                l=[]
                                if p.exists():
                                    datalist=[]
                                    for i in p:
                                        ord=OrderItemHistory.objects.filter(id=i['orderitem']).values()
                                        for j in ord:
                                            tx=Transaction_table.objects.filter(orderitem=j['id'],alias__icontains=t_id,created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at')
                                            for i in tx:
                                                try:
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
                                                except:
                                                        pass
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
                                    try:
                                        return Response(data1,status=status.HTTP_200_OK)
                                    except:
                                        return Response({"message":"value error"},status=status.HTTP_400_BAD_REQUEST)
                                paginator = Paginator(l,prperpage)
                                page = request.GET.get("page",pageno)
                                object_list = paginator.page(page)
                                a=list(object_list)
                                data1 = {
                                    "sales_data":a,
                                    "total_pages":paginator.num_pages,
                                    "products_per_page":prperpage,
                                    "total_products":paginator.count
                                }
                                return Response(data1,status=status.HTTP_200_OK)
                        else:
                            paginator = Paginator(l,prperpage)
                            page = request.GET.get("page",pageno)
                            object_list = paginator.page(page)
                            a=list(object_list)
                            data1 = {
                                "sales_data":a,
                                "total_pages":paginator.num_pages,
                                "products_per_page":prperpage,
                                "total_products":paginator.count
                            }
                            return Response(data1,status=status.HTTP_200_OK)
                    return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"Userdata not found in Role"}, status=status.HTTP_404_NOT_FOUND)
    

class GetMyOrdersListIncludingFilters(CreateAPIView):
    serializer_class = AdminOrderFilter

    def post(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        user = token1.user_id
        r_admin = Role.objects.get(role='ADMIN')
        role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

        if role.exists():
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
                    if (Product.objects.filter(user_id=u.id).exists()):
                        if d1<=d2:
                            if p_status=='':
                                p=Product.objects.filter(user_id=u.id).values('id')
                                datalist=[]
                                for k in p:
                                    o = OrderItemHistory.objects.filter(product=k['id'],alias__icontains=o_id,shipment_status__icontains=shipment_status, order_status__icontains=o_status,created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at','-id')
                                    company= CompanyProfile.objects.get(user=user)
                                    
                                    for i in o:
                                        orders = OrderItemHistory.objects.get(alias=i['alias'])

                                        if orders.shipment_status=='':
                                            s_status='NA'
                                        else:
                                            s_status=orders.shipment_status

                                        try:
                                            payment = Transaction_table.objects.get(orderitem=i['id'])
                                            state=payment.status
                                        except:
                                            if orders.order_status=='INPROGRESS':
                                                state='ON HOLD'
                                            else:
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
                                            "order_item_id" :orders.id,
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
                                try:
                                    return Response(data1,status=status.HTTP_200_OK)
                                except:
                                    return Response({"message":"value error"},status=status.HTTP_400_BAD_REQUEST)
                            else:
                                tt = Transaction_table.objects.filter(status__iexact=p_status).values()
                                l=[]
                                if tt.exists():
                                    company= CompanyProfile.objects.get(user=user)
                                    p=Product.objects.filter(user_id=u.id).values('id')
                                    datalist=[]
                                    for k in p:
                                        for t in tt:
                                            o = OrderItemHistory.objects.filter(product=k['id'],id=int(t['orderitem']),alias__icontains=o_id,shipment_status__icontains=shipment_status, order_status__icontains=o_status,created_at__range=(d1,d2+timedelta(days=1))).values().order_by('-created_at','-id')
                                            for i in o:
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
                                                    "order_item_id" :orders.id,
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
                                    try:
                                        return Response(data1,status=status.HTTP_200_OK)
                                    except:
                                        return Response({"message":"value error"},status=status.HTTP_400_BAD_REQUEST)
                                paginator = Paginator(l,prperpage)
                                page = request.GET.get("page",pageno)
                                object_list = paginator.page(page)
                                a=list(object_list)
                                data1 = {
                                    "my_orders_data":a,
                                    "total_pages":paginator.num_pages,
                                    "products_per_page":prperpage,
                                    "total_products":paginator.count
                                }
                                return Response(data1,status=status.HTTP_200_OK)
                        return Response({"message":"From date should be less than To date"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                return Response({'message':"Value error"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"Userdata not found in Role"}, status=status.HTTP_404_NOT_FOUND)
