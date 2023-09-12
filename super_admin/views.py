from rest_framework.generics import CreateAPIView
from .serializers import (SARegisterSerializer,SA_org_serializer,superadminOrgupdate,comapanyemailserializer,
                          comapanymobileserializer,comapanytaxidserializer,
                          drop_mobile,drop_laptop,sa_category,OrderSerializer)
from customer.models import Role, UserRole,UserProfile,KnoxAuthtoken,UserAddress
from .models import CompanyProfile,Category,collection,images,tags,variants,Product,ProductLaptop,ProductMobile
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from pytz import utc
from datetime import datetime
from django.utils.crypto import get_random_string
import random, json, requests,re
from Ecomerce_project.settings import SHIPMENT_TOKEN
from order.models import OrderItemHistory,Order
from shipment.models import shipment


class SARegisterView(CreateAPIView):
    serializer_class= SARegisterSerializer

    @transaction.atomic()
    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        role = Role.objects.get(role='SUPER_ADMIN')
        r_id = role.role_id
        if(UserRole.objects.filter(role_id = r_id).exists()):
            return Response({"messgae" : "There can be only One Super Admin"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                serializerdata = serializer.data['email']
                org = UserProfile.objects.get(email = serializerdata)
                aliass = get_random_string(length=10)
                if (UserProfile.objects.filter(alias=aliass).exists()):
                    aliass = get_random_string(length=10)
                    UserProfile.objects.filter(email=serializer.data['email']).update(alias=aliass)
                else:
                    UserProfile.objects.filter(email=serializer.data['email']).update(alias=aliass)
                userid = org.id
                UserRole.objects.create(role_id = r_id, user_id = userid)
                return Response({"Success" : "Super Admin Account Created successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" :serializer.errors},status=status.HTTP_409_CONFLICT)

##########  Super admin org_register   ########

class SuperAdminOrganizationRegister(CreateAPIView):
    serializer_class = SA_org_serializer

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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if (token1.expiry < datetime.now(utc)):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                elif(CompanyProfile.objects.filter(user=userdata)):
                    data = {"message":'SuperAdmin Details Already Exists'}
                    return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        dataemail = serializer.validated_data['email']
                        datamobile = serializer.validated_data['mobile']
                        taxdata = serializer.validated_data['tax_id']
                        orgdata = serializer.validated_data['org_name']
                        orgaddress = serializer.validated_data['address']
                        orgcity = serializer.validated_data['city']
                        orgstate = serializer.validated_data['state']
                        orgcountry = serializer.validated_data['country']
                        orgpincode = serializer.validated_data['pincode']
                        pattern = re.compile("^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}")
                        if len(taxdata)==15 and pattern.match(taxdata) :
                            # url = "https://apiv2.shiprocket.in/v1/external/settings/company/addpickup"

                            # payload = json.dumps({
                            # "pickup_location": orgdata,
                            # "name": orgdata,
                            # "email": dataemail,
                            # "phone": datamobile,
                            # "address": orgaddress,
                            # "address_2": "",
                            # "city": orgcity,
                            # "state": orgstate,
                            # "country": orgcountry,
                            # "pin_code": orgpincode,
                            # "gstin" : taxdata.upper()
                            # })
                            # headers = {
                            # 'Content-Type': 'application/json',
                            # 'Authorization': SHIPMENT_TOKEN
                            # }

                            # r=requests.request("POST", url, headers=headers, data=payload)
                            # if r.status_code==200:
                            serializer.save()
                            CompanyProfile.objects.filter(email=dataemail, mobile=datamobile,
                            org_name=orgdata).update(user=usertable, is_active='True', tax_id = taxdata.upper(), tax_status ='Verified')
                            data = {"message" : "SuperAdmin Organization Details Successfully Added"}
                            return Response(data, status=status.HTTP_200_OK)
                            # else:
                            #     return Response(r.json())
                        return Response({"message":"Invalid GSTIN Number"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        data = {"message" : "Incorrect/Null Please Check the Fileds"}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data={"message" : "Current User is not SuperAdmin"}
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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    table = CompanyProfile.objects.filter(user=userdata)
                    if table.exists():
                        data = list(table.values('org_name','email','mobile','tax_id','description','address','city','state','pincode','country'))
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        data = {"message" : "Details Not Found"}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data={"message" : "Current User is not SuperAdmin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)


################################    Super admin org update   ###########################
class SuperAdminOrganizationDetailsUpdate(CreateAPIView):
    serializer_class = superadminOrgupdate

    @transaction.atomic
    def put(self,request,token):
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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(CompanyProfile.objects.filter(user=userdata)):
                        serializer = self.get_serializer(usertable, data=request.data)
                        if serializer.is_valid(raise_exception=True):
                            orgname = serializer.validated_data['org_name']
                            description = serializer.validated_data['description']
                            address = serializer.validated_data['address']
                            city = serializer.validated_data['city']
                            state = serializer.validated_data['state']
                            pincode = serializer.validated_data['pincode']
                            country = serializer.validated_data['country']

                            table = CompanyProfile.objects.filter(user=userdata).update(org_name=orgname, 
                            description=description, address=address,
                            city=city, state=state, pincode=pincode, country=country)
                            data = {"message":'Details Updated successfully'}
                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            data = {"message":'Incorrect Input fields'}
                            return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data = {"message":"Details Not Found"}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data={"message" : "Current User is not SuperAdmin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


    @transaction.atomic
    def delete(self,request,token):
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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    table = CompanyProfile.objects.filter(user=userdata)
                    if table.exists():
                        CompanyProfile.objects.filter(user = userdata).update(is_active=False)
                        data = {'message' : "Account Deactivated Successfully"}
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        data = {'message':"Details Not Found"}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data={'message' : "Current User is not SuperAdmin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


##################   Company email update ######################
class EmailUpdate(CreateAPIView):
    serializer_class = comapanyemailserializer

    @transaction.atomic
    def put(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        roles = Role.objects.get(role='SUPER_ADMIN')
        adminrole = roles.role_id
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        companytable = CompanyProfile.objects.filter(user=userdata, is_active='True')
        if(UserRole.objects.filter(role_id=adminrole, user_id=userdata)):
            if companytable.exists():
                if(token1.expiry < datetime.now(utc)):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(usertable, data=request.data)
                    if serializer.is_valid():
                        serializerdata = serializer.validated_data['email']
                        CompanyProfile.objects.filter(user=userdata).update(email=serializerdata)
                        return Response({"message":"email updated successfully"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Invalid Input field"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message":"Company details not exists for this user"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":"Current User is not SuperAdmin"}, status=status.HTTP_406_NOT_ACCEPTABLE)


##################   Company mobile update ######################
class MobileUpdate(CreateAPIView):
    serializer_class = comapanymobileserializer

    @transaction.atomic
    def put(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        roles = Role.objects.get(role='SUPER_ADMIN')
        adminrole = roles.role_id
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        companytable = CompanyProfile.objects.filter(user=userdata, is_active='True')
        if(UserRole.objects.filter(role_id=adminrole, user_id=userdata)):
            if companytable.exists():
                if(token1.expiry < datetime.now(utc)):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(usertable, data=request.data)
                    if serializer.is_valid():
                        serializerdata = serializer.validated_data['mobile']
                        #####   validations want to do for email while updating
                        CompanyProfile.objects.filter(user=userdata).update(mobile=serializerdata)
                        return Response({"message":"mobile updated successfully"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Invalid Input field"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message":"Company details not exists for this user"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":"Current User is not Super Admin"}, status=status.HTTP_406_NOT_ACCEPTABLE)


##################   Company tax_id update ######################
class TaxIdUpdate(CreateAPIView):
    serializer_class = comapanytaxidserializer

    @transaction.atomic
    def put(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        roles = Role.objects.get(role='SUPER_ADMIN')
        adminrole = roles.role_id
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        companytable = CompanyProfile.objects.filter(user=userdata, is_active='True')
        if(UserRole.objects.filter(role_id=adminrole, user_id=userdata)):
            if companytable.exists():
                if(token1.expiry < datetime.now(utc)):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(usertable, data=request.data)
                    if serializer.is_valid():
                        serializerdata = serializer.validated_data['tax_id']
                        pattern = re.compile("^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}")
                        if len(serializerdata)==15 and pattern.match(serializerdata):  
                            CompanyProfile.objects.filter(user=userdata).update(tax_id=serializerdata.upper())
                            return Response({"message":"tax_id updated successfully"}, status=status.HTTP_200_OK)
                        return Response({"message":"Invalid GSTIN Number"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({"message":"Invalid Input field"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message":"Company details not exists for this user"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":"Current User is not Super Admin"}, status=status.HTTP_406_NOT_ACCEPTABLE)


##################  Super admin Products  ###############   

# class SuperAdminProductsView(CreateAPIView):
#     serializer_class = sa_products

#     @transaction.atomic
#     def post(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role3 = Role.objects.get(role='SUPER_ADMIN')
#         sarole = role3.role_id
#         roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)

#         try:
#             cp = CompanyProfile.objects.get(user=userdata)
#         except:
#             return Response({"message":"Not registered with Company Profile"})
        
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):

#                         protitle = serializer.validated_data['title']
#                         prodescription = serializer.validated_data['description']
#                         protype = serializer.validated_data['type']
#                         probrand = serializer.validated_data['brand'] 
#                         pronew = serializer.validated_data['new']
#                         prosale =  serializer.validated_data['sale']
#                         procategory = serializer.validated_data['category']
#                         prodimension = serializer.validated_data['dimensions']
#                         proweight = serializer.validated_data['weight']
#                         prowarranty = serializer.validated_data['warranty']
#                         prowarrantyfile = serializer.validated_data['warranty_file']
#                         prowarrantymonths = serializer.validated_data['warranty_months']
#                         prostatus = serializer.validated_data['status']
#                         charged = serializer.validated_data['charge_checked']
#                         procollection = serializer.validated_data['collection']
#                         variant_price = serializer.validated_data['price']
#                         variant_discount = serializer.validated_data['discount']
#                         variant_quantity = serializer.validated_data['quantity']
#                         variant_color = serializer.validated_data['color']
#                         variant_src = serializer.validated_data['variant_images']
#                         varinat_sku = serializer.validated_data['sku']

#                         if variant_discount >100 or variant_discount<0:
#                             return Response({'message':"Invalid discount percentage","error":"Percentage should be >=0 (or) <=100"},status=status.HTTP_400_BAD_REQUEST)
                        
#                         if varinat_sku=='':
#                             skuval = 'SKU'+variant_color.upper()
#                         else:
#                             skuval = varinat_sku

#                         if prodimension =='':
#                             return Response({"messgae":"Please use the following format: L X B X H"})
#                         if proweight<0.1:
#                             return Response({"message":"The minimum chargeable weight is 0.1 Kg"})

#                         delivery = [380006,382345,282001,676305,600001,643253,797001,751003,180001,587315,560063,
#                                     110001,110020,500001,500058,600001,600082,515001,515311,403001,403405,560001,
#                                     800001,800016,226001,226017,302001,302017,400001,400065,700001,700046,560015,522020]
#                         # date_list=[]
#                         charger_list=[]
#                         for j in range(len(delivery)):
#                             try:
#                                 url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"

#                                 payload=json.dumps({
#                                     "pickup_postcode":cp.pincode, 
#                                     "delivery_postcode":delivery[j],
#                                     "cod":"0",  # 1 for COD and 0 for Prepaid orders.
#                                     "weight":proweight,
#                                     # "declared_value":10000
#                                 })
#                                 headers = {
#                                 'Content-Type': 'application/json',
#                                 'Authorization': SHIPMENT_TOKEN
#                                 }

#                                 response = requests.request("GET", url, headers=headers, data=payload)
#                                 data=response.json()
#                                 if response.status_code==200:            
#                                     for i in range(len(data['data']['available_courier_companies'])):
#                                         # date = data['data']['available_courier_companies'][i]['etd']
#                                         shipping_chargers = data['data']['available_courier_companies'][i]["freight_charge"]
#                                         i=i+1
#                                         # date_list.append(date)
#                                         charger_list.append(shipping_chargers)
#                             except:
#                                 pass
#                         if(Category.objects.filter(category_name__iexact=procategory)):
#                             tablecategory = Category.objects.get(category_name__iexact=procategory)
#                             if procategory.upper() in ('MOBILES','LAPTOPS','WATCHES'):
#                                 gst_percentage=18

#                             dimension_pattern = r'^\d+(\.\d+)?X\d+(\.\d+)?X\d+(\.\d+)?$'
#                             if re.match(dimension_pattern, prodimension):
#                                 if prowarrantyfile=='':
#                                     warranty_doc=''
#                                 else:
#                                     warranty_doc= 'http://127.0.0.1:8000/media/product/warranty/' + str(prowarrantyfile)
                                
#                                 dis_percentage =variant_discount/100
#                                 dis_price = variant_price*dis_percentage
#                                 final_price=(variant_price - dis_price)
#                                 charges = round((final_price)*0.15)
#                                 sellingPrice = final_price + charges + max(charger_list)
#                                 shipping = round(max(charger_list))

#                                 product = Product.objects.create(
#                                     title=protitle,
#                                     description=prodescription,
#                                     type = protype,
#                                     brand=probrand,
#                                     new=pronew,
#                                     sale=prosale,
#                                     user=usertable, 
#                                     category_id=tablecategory.id, 
#                                     category = tablecategory.category_name,
#                                     dimensions=prodimension,
#                                     weight=proweight,
#                                     status=prostatus,
#                                     warranty_src=warranty_doc,
#                                     warranty_path=prowarrantyfile,
#                                     warranty_months = prowarrantymonths,
#                                     is_charged = charged,
#                                     is_wattanty=prowarranty
#                                 )
                                
#                                 if charged==True and product.is_charged==True:
#                                     variant = variants.objects.create(id=product.id,price = variant_price,
#                                         gst = gst_percentage,
#                                         discount=variant_discount,
#                                         selling_price = round(sellingPrice),
#                                         sku=skuval,
#                                         color=variant_color,
#                                         quantity = variant_quantity,
#                                         stock=variant_quantity
#                                     )
#                                     Product.objects.filter(id=product.id).update(is_charged = charged,shipping_charges=round(shipping*2),other_charges=round(charges))
#                                 else:
#                                     Product.objects.filter(id=product.id).update(is_charged = charged,shipping_charges=0,other_charges=0)
#                                     variant = variants.objects.create(
#                                         id=product.id,
#                                         price = variant_price,
#                                         gst = gst_percentage,
#                                         discount=variant_discount,
#                                         selling_price = final_price,
#                                         sku=skuval,
#                                         color=variant_color,
#                                         quantity = variant_quantity,
#                                         stock=variant_quantity)
                                
#                                 for image in variant_src:
#                                     variant_image = 'http://127.0.0.1:8000/media/product/variants/' + str(image)
#                                     i=images.objects.create(id=product.id,alt=variant.color,path=image,src=variant_image,variant_id=variant.variant_id)

#                                 variants.objects.filter(variant_id=i.variant_id).update(image_id=i.image_id)
                                
#                                 col = collection.objects.create(id=product.id,collection=procollection)
#                                 tag = tags.objects.create(id=product.id,tags=probrand)
#                                 # tag = tags.objects.create(id=protable.id,tags=prosize)
#                                 tag = tags.objects.create(id=product.id,tags=variant_color)

#                                 if pronew ==True:
#                                     tags.objects.create(id=product.id,tags='new')

#                                 product.save()
#                                 data = {"message":'Product Added successfully'}
#                                 return Response(data, status=status.HTTP_200_OK)
#                             else:
#                                 return Response({'message':"Please use the following format: L X B X H"},status=status.HTTP_400_BAD_REQUEST)
#                         else:
#                             data = {'message': "Category Not Found"}
#                             return Response(data, status=status.HTTP_400_BAD_REQUEST)
#                     else:
#                         data = {'message': "Details Not Found"}
#                         return Response(data, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 data={'message' : "Current User is not Super Admin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


#     @transaction.atomic
#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role3 = Role.objects.get(role='SUPER_ADMIN')
#         sarole = role3.role_id
#         roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     table = Product.objects.filter(user=userdata)
#                     if table.exists():
#                         prodata = table.values('id')
#                         datalist =[] 

#                         for i in prodata:
#                             pro = Product.objects.get(id = i['id'])
#                             col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
#                             var = variants.objects.filter(id=i['id']).values()
#                             img = images.objects.filter(id=i['id']).values()
#                             t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
#                             sold_by = CompanyProfile.objects.get(user=pro.user)

#                             data = {
#                                 "id": pro.id,
#                                 "title": pro.title,
#                                 "description": pro.description, 
#                                 "type": pro.type,
#                                 "brand": pro.brand,
#                                 "collection": col,
#                                 "category": pro.category,
#                                 # "price": round(pro.price,2),
#                                 "sale": pro.sale,
#                                 # "discount": pro.discount,
#                                 # "stock": pro.stock,
#                                 "new": pro.new,
#                                 "tags":t,
#                                 "variants" : var,
#                                 "images" : img,
#                                 "weight": pro.weight,
#                                 "dimensions":pro.dimensions,
#                                 "sold_by" :sold_by.org_name
#                             }
#                             datalist.append(data)
#                         return Response(datalist, status=status.HTTP_200_OK)
#                     else:
#                         data = {"message":'Details Not Found'}
#                         return Response(data, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data={'message':"Current User is not Super Admin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)



# class AddProductVariant(CreateAPIView):
#     serializer_class = product_variant

#     @transaction.atomic
#     def post(self,request,token,pid):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role3 = Role.objects.get(role='SUPER_ADMIN')
#         sarole = role3.role_id
#         roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     if(Product.objects.filter(user=userdata, id=pid)):
#                         serializer = self.get_serializer(data=request.data)
#                         if serializer.is_valid(raise_exception=True):
#                             procollection = serializer.validated_data['collection']
#                             prosize = serializer.validated_data['size']
#                             procolor = serializer.validated_data['color']
#                             propath = serializer.validated_data['path']
#                             val = random.randint(1000,9999)
#                             strval = 'SKU'+str(val)

#                             custom_url = 'http://50.18.24.167/media/product/images/' + str(propath)
#                             pro = Product.objects.get(id=pid)
#                             var = variants.objects.create(id=pro.id,sku=strval,size=prosize,color=procolor)
                            
#                             i=images.objects.create(id=pro.id,alt=var.color,path=propath,src=custom_url,variant_id=var.variant_id)
#                             variants.objects.filter(variant_id=i.variant_id).update(image_id=i.image_id)
                            
#                             col = collection.objects.create(id=pro.id,collection=procollection)

#                             tag = tags.objects.create(id=pro.id,tags=prosize)
#                             tag = tags.objects.create(id=pro.id,tags=procolor)

#                             return Response({"message":"Successfully Added New Varinat"}, status=status.HTTP_201_CREATED)
#                         else :
#                             return Response({"message":"Missing value"},status=status.HTTP_204_NO_CONTENT)
#                     else:
#                         return Response({"message":"This Product Does not exists"},status=status.HTTP_404_NOT_FOUND)     



# ###############   Super admin products update, delete  ##############

# class ProductDetailsUpdate(CreateAPIView):
#     serializer_class = sa_products_update

#     @transaction.atomic
#     def put(self,request,token,pid):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role3 = Role.objects.get(role='SUPER_ADMIN')
#         sarole = role3.role_id
#         roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     if(Product.objects.filter(user=userdata, id=pid)):
#                         serializer = self.get_serializer(usertable, data=request.data)
#                         if serializer.is_valid(raise_exception=True):
#                             user = serializer.save()
#                             category = serializer.validated_data['category']
#                             productname = serializer.validated_data['title']
#                             description = serializer.validated_data['description']
#                             # unitprice = serializer.data['price']
#                             # discount = serializer.data['discount']
#                             dimension = serializer.validated_data['dimensions']
#                             weight = serializer.validated_data['weight']
#                             image = serializer.validated_data['path']


#                             if(Category.objects.filter(category_name__iexact=category)):
#                                 cat = Category.objects.get(category_name__iexact=category)
#                                 # if unitprice >= discount:
#                                 if image=='' or image==None:
#                                     Product.objects.filter(id=pid, user=userdata).update(
#                                         category = cat.id,
#                                         title=productname, 
#                                         description=description,
#                                         dimensions=dimension,
#                                         weight=weight)
#                                 else:
#                                     Product.objects.filter(id=pid, user=userdata).update(
#                                         category = cat.id,
#                                         title=productname, 
#                                         description=description,
#                                         dimensions=dimension,
#                                         weight=weight)
#                                     p=Product.objects.get(id=pid, user=userdata)
#                                     p.path = image
#                                     p.save()
#                                 data = {"message":'Product Details Updated successfully'}
#                                 return Response(data, status=status.HTTP_200_OK)
#                                 # else:
#                                 #     return Response({"message" : "Discount Price should be greater than Unit Price"}, status=status.HTTP_406_NOT_ACCEPTABLE)
#                             else:
#                                 data = {'message': "Category Not Found"}
#                                 return Response(data, status=status.HTTP_400_BAD_REQUEST)
#                         else:
#                             data = {'message' :"Incorrect Input Fields" }
#                             return Response(data, status=status.HTTP_400_BAD_REQUEST)
#                     else:
#                         data = {'message' : "Details Not Found"}
#                         return Response(data, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data={'message' : "Current User is not SuperAdmin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


#     @transaction.atomic
#     def delete(self,request,token,pid):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role3 = Role.objects.get(role='SUPER_ADMIN')
#         sarole = role3.role_id
#         roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     table = Product.objects.filter(user=userdata, id=pid)
#                     if table.exists():
#                         Product.object.filter(user=userdata, id=pid).update(is_deleted=True)
#                         data = {"message":'Product Removed Successfully'}
#                         return Response(data, status=status.HTTP_200_OK)
#                     else:
#                         data = {'message' : "Details Not Found"}
#                         return Response(data, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {'message' : "Current User is not SuperAdmin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
 

############  Drop down apis for product_category  #########

class MobileSpecificationView(CreateAPIView):    
    serializer_class  = drop_mobile

    @transaction.atomic
    def post(self,request,token,pid):
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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Category.objects.filter(category_name__iexact='Mobiles').exists()):
                        tablecategory = Category.objects.get(category_name__iexact='Mobiles')
                        categoryid = tablecategory.id
                        tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                        if tableproduct.exists():
                            serializer = self.get_serializer(data=request.data)
                            if serializer.is_valid(raise_exception=True):
                                if(ProductMobile.objects.filter(product=pid).exists()):
                                    return Response({"Product specification exists"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                else:
                                    table1 = Product.objects.get(id=pid)
                                    modelno = serializer.validated_data['model_number']
                                    modelname = serializer.validated_data['model_name']
                                    storage = serializer.validated_data['storage_spec']
                                    battery = serializer.validated_data['battery_spec']
                                    device = serializer.validated_data['device_spec']
                                    camera = serializer.validated_data['camera_spec']
                                    other = serializer.validated_data['other_spec']
                                    table = ProductMobile.objects.create(model_number=modelno, model_name=modelname,
                                    storage_spec=storage, battery_spec=battery, device_spec=device, camera_spec=camera,
                                    other_spec=other,product=table1)
                                    table.save()
                                    data = {"message":"Product Specifications Added successfully"}
                                    return Response(data, status=status.HTTP_200_OK)
                            else:
                                data = {'message' : "Incorrect Input Fields"}
                                return Response(data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            data = {'message':"Details Not Found"}
                            return Response(data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"Category not found"},status=status.HTTP_404_NOT_FOUND)
            else:
                data={'Current User is not SuperAdmin'}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


    @transaction.atomic
    def put(self,request,token,pid):
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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Category.objects.filter(category_name__iexact='Mobiles').exists()):
                        tablecategory = Category.objects.get(category_name__iexact='Mobiles')
                        categoryid = tablecategory.id
                        tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                        tablecheck = ProductMobile.objects.filter(product=pid)
                        if (tableproduct and tablecheck).exists():
                            tbproduct = Product.objects.get(id=pid)
                            serializer = self.get_serializer(tbproduct, data=request.data)
                            if serializer.is_valid(raise_exception=True):
                                user = serializer.save()
                                modelno = serializer.data['model_number']
                                modelname = serializer.data['model_name']
                                storage = serializer.data['storage_spec']
                                battery = serializer.data['battery_spec']
                                device = serializer.data['device_spec']
                                camera = serializer.data['camera_spec']
                                other = serializer.data['other_spec']
                                table = ProductMobile.objects.filter(product=pid).update(model_number=modelno, model_name=modelname,
                                storage_spec=storage, battery_spec=battery, device_spec=device, camera_spec=camera,
                                other_spec=other)
                                data = {"message":'Details Updated successfully'}
                                return Response(data, status=status.HTTP_200_OK)
                            else:
                                data = {'Incorrect Input Fields'}
                                return Response(status=status.HTTP_400_BAD_REQUEST)
                        else:
                            data = {'Details Not Found'}
                            return Response(data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"Category not found"},status=status.HTTP_404_NOT_FOUND)
            else:
                data={'message' : 'Current User is not SuperAdmin'}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

    @transaction.atomic
    def delete(self,request,token,pid):
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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Category.objects.filter(category_name__iexact='Mobiles').exists()):
                        tablecategory = Category.objects.get(category_name__iexact='Mobiles')
                        categoryid = tablecategory.id
                        tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                        table = ProductMobile.objects.filter(product=pid)
                        if (table and tableproduct).exists():
                            table.delete()
                            data = {"message":'Deleted successfully'}
                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            data = {'message' : "Details Not Found"}
                            return Response(data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"Category not found"},status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : 'Current User is not SuperAdmin'}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

    @transaction.atomic
    def get(self,request,token,pid):
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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Category.objects.filter(category_name__iexact='Mobiles').exists()):
                        tablecategory = Category.objects.get(category_name__iexact='Mobiles')
                        categoryid = tablecategory.id
                        tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                        table = ProductMobile.objects.filter(product=pid)
                        if (table and tableproduct).exists():
                            data = list(table.values())
                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            data = {"message":'Details Not Found'}
                            return Response(data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"Category not found"},status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : "Current User is not SuperAdmin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)



class LaptopSpecificationView(CreateAPIView):
    serializer_class  = drop_laptop

    @transaction.atomic
    def post(self,request,token,pid):
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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Category.objects.filter(category_name__iexact='Laptops').exists()):
                        tablecategory = Category.objects.get(category_name__iexact='Laptops')
                        categoryid = tablecategory.id
                        tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                        if tableproduct.exists():
                            serializer = self.get_serializer(data=request.data)
                            if serializer.is_valid(raise_exception=True):
                                if(ProductLaptop.objects.filter(product=pid).exists()):
                                    return Response({"Product specification exists"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                else:
                                    table1 = Product.objects.get(id=pid)
                                    brand = serializer.validated_data['brand']
                                    series = serializer.validated_data['series']
                                    storage = serializer.validated_data['storage_spec']
                                    display = serializer.validated_data['display_spec']
                                    device = serializer.validated_data['device_spec']
                                    other = serializer.validated_data['other_spec']
                                    table = ProductLaptop.objects.create(brand=brand, series=series, storage_spec=storage,
                                    display_spec=display, device_spec=device, other_spec=other,product=table1)
                                    data = {"message":"Product Specifications Added successfully"}
                                    return Response(data, status=status.HTTP_200_OK)
                            else:
                                data = {'message' : "Incorrect Input fields"}
                                return Response(data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            data = {"message":'Details Not Found'}
                            return Response(data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"Category not found"},status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : "Current User is not SuperAdmin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


    @transaction.atomic
    def put(self,request,token,pid):
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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Category.objects.filter(category_name__iexact='Laptops').exists()):
                        tablecategory = Category.objects.get(category_name__iexact='Laptops')
                        categoryid = tablecategory.id
                        tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                        tablecheck = ProductLaptop.objects.filter(product=pid)
                        if (tableproduct and tablecheck).exists():
                            tbproduct = Product.objects.get(id=pid)
                            serializer = self.get_serializer(tbproduct, data=request.data)
                            if serializer.is_valid(raise_exception=True):
                                user = serializer.save()
                                brand = serializer.data['brand']
                                series = serializer.data['series']
                                storage = serializer.data['storage_spec']
                                display = serializer.data['display_spec']
                                device = serializer.data['device_spec']
                                other = serializer.data['other_spec']
                                table = ProductLaptop.objects.filter(product=pid).update(brand=brand, series=series, storage_spec=storage,
                                display_spec=display, device_spec=device, other_spec=other)
                                data = {"message":'Details Updated successfully'}
                                return Response(data, status=status.HTTP_200_OK)
                            else:
                                data = {'message' : "Incorrect Input Fields"}
                                return Response(data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            data = {'message' : 'Details Not Found'}
                            return Response(data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"Category not found"},status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : 'Current User is not SuperAdmin'}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

                
    @transaction.atomic
    def delete(self,request,token,pid):
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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Category.objects.filter(category_name__iexact='Laptops').exists()):
                        tablecategory = Category.objects.get(category_name__iexact='Laptops')
                        categoryid = tablecategory.id
                        tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                        table = ProductLaptop.objects.filter(product=pid)
                        if (table and tableproduct).exists():
                            table.delete()
                            data = {"message":'Deleted successfully'}
                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            data = {'message' : "Details Not Found"}
                            return Response(data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"Category not found"},status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : "Current User is not SuperAdmin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

    @transaction.atomic
    def get(self,request,token,pid):
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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Category.objects.filter(category_name__iexact='Laptops').exists()):
                        tablecategory = Category.objects.get(category_name__iexact='Laptops')
                        categoryid = tablecategory.id
                        tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                        table = ProductLaptop.objects.filter(product=pid)
                        if (table and tableproduct).exists():
                            data = list(table.values())
                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            data = {'message' : "Details Not Found"}
                            return Response(data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"Category not found"},status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : 'Current User is not SuperAdmin'}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)



###################   Super_admin adding category   ###################

class AddCategoryView(CreateAPIView):
    serializer_class = sa_category

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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        serializerdata = serializer.validated_data['category_name']
                        if(Category.objects.filter(category_name__iexact=serializerdata).exists()):
                            return Response({"message":"Category Exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            Category.objects.create(category_name=serializerdata.capitalize())
                            return Response({"message":"Category created successfully, please add specifications"},status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Seralizer is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {'message' : "Current User is not Super_admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


    @transaction.atomic
    def delete(self,request,token):
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
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        serializerdata = serializer.validated_data['category_name']
                        if(Category.objects.filter(category_name__iexact=serializerdata).exists()):
                            Category.objects.filter(category_name__iexact=serializerdata).delete()
                            return Response({"message":"Category Removed successfully"},status=status.HTTP_200_OK)
                        else:
                            return Response({"message":"Category not found"},status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"message":"Seralizer is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {'message' : "Current User is not Super_admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        
class SuperAdminDashboardDetails(CreateAPIView):
    def get(self, request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        user = token1.user_id
        r_admin = Role.objects.get(role='SUPER_ADMIN')
        role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)
        if role.exists():
            if(token1.expiry < datetime.now(utc)):
                KnoxAuthtoken.objects.filter(user=user).delete()
                data = {"message":'Session Expired, Please login again'}
                return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
            else: 
                cp=CompanyProfile.objects.get(user=user)
                p=Product.objects.filter(user=cp.user).values()
                total_list=[]
                pending_list=[]
                for i in p:
                    total_orders = OrderItemHistory.objects.filter(product=i['id']).count()
                    total_list.append(total_orders)
                    pending_orders = OrderItemHistory.objects.filter(product=i['id'],order_status='Pending').count()
                    pending_list.append(pending_orders)
                return Response({
                            "total_orders":sum(total_list),
                            "pending_order":sum(pending_list)
                            })
        return Response({"message":"Userdata not found in Role"}, status=status.HTTP_404_NOT_FOUND)
    
class SuperAdminOrderDetailPageAPI(CreateAPIView):
    serializer_class = OrderSerializer

    @transaction.atomic
    def post(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        uid = usertable.id
        role = Role.objects.get(role='SUPER_ADMIN')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1).filter(user_id=uid)
        if(UserProfile.objects.filter(id=uid, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    # orderitem
                    serializer = self.serializer_class(data = request.data)
                    if serializer.is_valid(raise_exception=True):
                        item_id = serializer.validated_data['orderitem']

                        if OrderItemHistory.objects.filter(id=item_id).exists():
                            ord = OrderItemHistory.objects.get(id=item_id)
                            o = Order.objects.get(id=ord.order)
                            product = Product.objects.get(id=ord.product)
                            company = CompanyProfile.objects.get(user=product.user)
                            customer = UserAddress.objects.get(id=o.delivery)
                            us = UserProfile.objects.get(id=uid)
                            img = images.objects.get(id=product.id)
                            variant= variants.objects.get(id=product.id)

                            total_price=ord.item_price*ord.quantity
                            try:
                                ship = shipment.objects.get(order_item_id=ord.id)
                                url = "https://apiv2.shiprocket.in/v1/external/orders/show/"+str(ship.shipment_order_id)
                                payload={}
                                headers = {
                                'Content-Type': 'application/json',
                                'Authorization': SHIPMENT_TOKEN
                                }

                                order_response = requests.request("GET", url, headers=headers, data=payload)
                                order_data=order_response.json()
                                if order_response.status_code==200:
                                    
                                    date_object = datetime.strptime(order_response.json()['data']['shipments']['etd'], "%b %d, %Y")

                                    url = "https://apiv2.shiprocket.in/v1/external/courier/track/shipment/"+str(ship.shipment_id)
                                    payload={}
                                    headers = {
                                    'Content-Type': 'application/json',
                                    'Authorization': SHIPMENT_TOKEN
                                    }

                                    response_shipment = requests.request("GET", url, headers=headers, data=payload)
                                    data=response_shipment.json()
                                
                                    lists=[]
                                    if response_shipment.status_code==200 and data['tracking_data']['track_status']==1:
                                        OrderItemHistory.objects.filter(id=ship.order_item_id).update(shipment_status=order_response.json()['data']['status'])
                                        shipment_track_activities = {
                                            "track":data['tracking_data']['shipment_track_activities'],
                                            "url":data['tracking_data']['track_url']
                                        }
                                        lists.append(shipment_track_activities)
                                    elif response_shipment.status_code==200 and data['tracking_data']['track_status']==0:
                                        message=[]
                                        lists.append(message)
                                    elif response_shipment.status_code==401 or data['status_code']==401:
                                        message=[]
                                        lists.append(message)
                                    else:
                                        message=[]
                                        lists.append(message)

                                    data={
                                        "order_details" :{
                                            "parent_order_id":ord.order,
                                            "order_id":ord.id,
                                            "order_alias" :ord.alias,
                                            "order_status":ord.order_status,
                                            "shipment_status":ord.shipment_status,
                                            "created_at":ord.created_at,
                                            'updated_at':ord.updated_at,
                                            "product_id": product.id,
                                            "title":product.title,
                                            "image":img.src,
                                            "category":product.category,
                                            "brand":product.brand,
                                            "sku":variant.sku,
                                            "quantity":ord.quantity,
                                            "seller" : company.org_name,
                                            "unit_price" : round(ord.item_price,2),
                                            "total" : round(total_price,2),
                                            "shipping_charges":ord.shipment_charge,
                                            "processing_fee": round((ord.item_price*ord.quantity)*(8/100),2),
                                            "order_total" : round(total_price + ord.shipment_charge + total_price*0.08,2)
                                        },
                                        "customer_details":{
                                            "name" : customer.name,
                                            'mobile' : customer.mobile,
                                            "email": us.email,
                                            "address":customer.address,
                                            "city":customer.city,
                                            "state":customer.state,
                                            "country":customer.country,
                                            "pincode":customer.pincode
                                        },
                                        "pickup_address":{
                                            "company_name":company.org_name,
                                            "email":company.email,
                                            "phone":company.mobile,
                                            "address":company.address,
                                            "city":company.city,
                                            "state":company.state,
                                            "country":company.country,
                                            "pincode":company.pincode
                                        },
                                        "packing_details":{
                                            "dimensions":product.dimensions,
                                            "dead_weight":product.weight,
                                            "volumetric_weight": order_response.json()['data']['shipments']['volumetric_weight'],
                                            "applied_weight": order_response.json()['data']['shipments']['volumetric_weight'],
                                            "courier" : order_response.json()['data']['shipments']['courier'],
                                            "status":order_response.json()['data']['shipments']['status'],
                                            "awb":order_response.json()['data']['shipments']['awb'],
                                            "estimated_delivery":date_object.date(),
                                        },
                                        "shipping_details":lists,
                                        }
                                    return Response(data,status=status.HTTP_200_OK)
                                else:
                                    pass
                            except:
                                lists=[]
                                data={
                                "order_details" :{
                                    "parent_order_id":ord.order,
                                    "order_id":ord.id,
                                    "order_alias" :ord.alias,
                                    "order_status":ord.order_status,
                                    "shipment_status":ord.shipment_status,
                                    "created_at":ord.created_at,
                                    'updated_at':ord.updated_at,
                                    "product_id": product.id,
                                    "title":product.title,
                                    "image":img.src,
                                    "category":product.category,
                                    "brand":product.brand,
                                    "sku":variant.sku,
                                    "quantity":ord.quantity,
                                    "seller" : company.org_name,
                                    "unit_price" : round(ord.item_price,2),
                                    "total" : round(total_price,2),
                                    "shipping_charges":ord.shipment_charge,
                                    "processing_fee": round((ord.item_price*ord.quantity)*(8/100),2),
                                    "order_total" : round(total_price + ord.shipment_charge + total_price*0.08,2)
                                    },
                                    "customer_details":{
                                        "name" : customer.name,
                                        'mobile' : customer.mobile,
                                        "email": us.email,
                                        "address":customer.address,
                                        "city":customer.city,
                                        "state":customer.state,
                                        "country":customer.country,
                                        "pincode":customer.pincode
                                    },
                                    "pickup_address":{
                                        "company_name":company.org_name,
                                        "email":company.email,
                                        "phone":company.mobile,
                                        "address":company.address,
                                        "city":company.city,
                                        "state":company.state,
                                        "country":company.country,
                                        "pincode":company.pincode
                                    },
                                    "packing_details":{
                                        "dimensions":product.dimensions,
                                        "dead_weight":product.weight,
                                        "volumetric_weight": '',
                                        "applied_weight": '',
                                        "courier" : '',
                                        "status":'',
                                        "awb":'',
                                        "estimated_delivery":ord.delivery_date.date(),
                                    },
                                    "shipping_details":lists,
                                    # "estimated_delivery":estimated_delivery_date
                                }
                                return Response(data,status=status.HTTP_200_OK)  
                        else:
                            return Response({'message':"Invalid Order Item Id"},status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response(serializer.error_messages)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)



class ProductAPI(CreateAPIView):

    @transaction.atomic
    def get(self,request,pid):
        pro = Product.objects.get(id=pid)
        var = variants.objects.filter(id=pid).values_list('id')
        print(var)
        img = images.objects.filter(variant_id__in=var)
        print(img)

        data = {
            "id": pro.id,
            "title": pro.title,
            "description": pro.description, 
            "type": pro.type,
            "brand": pro.brand,
            "shipping_charge":pro.shipping_charges,
            "other_charge":pro.other_charges
            # "collection": col,
            # "category": pro.category,
            # "price": pro.price,
            # "sale": pro.sale,
            # "discount": pro.discount,
            # "stock": pro.stock,
            # "new": pro.new,
            # "weight":pro.weight,
            # "dimensions":pro.dimensions,
            # "variants" : var,
            # "images" : img,
            # "Rating":pro.rating,
            # "tag":t,
            # "sold_by" : cp.org_name,
            # "estimated_delivery_date" : max(date_list),
        }
        return Response(data)
       