from rest_framework.generics import CreateAPIView
from django.db import transaction
from rest_framework.response import Response
from django.http import HttpResponse,JsonResponse
from rest_framework import status
from pytz import utc
from datetime import datetime,timezone
import random,re
from django.utils.crypto import get_random_string
from customer.models import UserProfile, UserRole, Role,KnoxAuthtoken,UserAddress
from .serializers import (AdminRegisterSerializer,Admin_org_serializer,AdminOrgupdate,comapanyemailserializer,
                          comapanymobileserializer,comapanytaxidserializer,admin_variant,
                          drop_laptop,drop_mobile,admin_category,DateFilter,ProductNameFilter,
                          ProductPriceFilter,ProductCategoryFilter,ProductColorFilter, ProductAvailabeFilter,
                          ProductTypeFilter, ProductDiscountFilter,OrderIdFilter,OrderPaymentStatusFilter,
                          OrderStatusFilter,SalesDeliveryStatusFilter, SalesInvoiceIDFilter, SalesOrderIDFilter, SalesTxnIDFilter,
                          OrderSerializer,)
from super_admin.models import Category,Product ,variants,tags,images,collection,CompanyProfile,ProductLaptop,ProductMobile
import json, requests
from Ecomerce_project.settings import SHIPMENT_TOKEN
from order.models import OrderItemHistory,Order
from payments.models import Payment_details_table,Transaction_table
import stripe
from django.conf import settings
from django.core.mail import send_mail
from vendor.models import company_stripe
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from Ecomerce_project.settings import STRIPE_SECRET_KEY, STRIPE_SECRET_US_KEY
from shipment.models import shipment


####################  Admin register   #################
class AdminRegisterView(CreateAPIView):
    serializer_class= AdminRegisterSerializer

    @transaction.atomic()
    def post(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role2 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role2.role_id
        if(token1.expiry < datetime.now(utc)):
            KnoxAuthtoken.objects.filter(user=user).delete()
            data = {"message":'Session Expired, Please login again'}
            return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
        else:
            table = UserRole.objects.filter(user_id=userdata, role_id=sarole)
            if table.exists():
                serializer = self.serializer_class(data = request.data)
                if serializer.is_valid(raise_exception=True):
                    u=serializer.validated_data['username']
                    email = serializer.validated_data['email']
                    if (UserProfile.objects.filter(username__iexact=u)):
                        error ={
                            "username": ['user profile with this username already exists.']
                        }
                        return Response(error, status=status.HTTP_400_BAD_REQUEST)

                    pwd=serializer.validated_data['password']
                    pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$!%*?&])[A-Za-z\d@#$!%*?&]{8,}$"

                    r= re.findall(pattern,pwd)
                    if not r:
                        data={
                            "message":"Password is invalid.Min 8 character. Password must contain at least :one small alphabet one capital alphabet one special character \nnumeric digit."
                        }
                        return Response(data,status=status.HTTP_406_NOT_ACCEPTABLE)
                    
                    try:
                        protocol ='http://'
                        # current_site = get_current_site(request).domain
                        current_site = '54.67.88.195/'
                        api = 'core/login'
                        message = "Dear {},\nWe're thrilled to have you as a new member of our community at xShop!. \nYour registration was successful, and we're excited to help you get started. \n Click below link to login \n{}{}{}".format(u,protocol,current_site,api)
                        subject = "Welcome to xShop!"
                        from_email = settings.EMAIL_HOST_USER
                        to_email = [email.lower()]
                        send_mail(subject, message, from_email, to_email)

                        serializer.save()
                        aliass = get_random_string(length=10)
                        if (UserProfile.objects.filter(alias=aliass).exists()):
                            aliass = get_random_string(length=10)
                            UserProfile.objects.filter(email=serializer.data['email']).update(alias=aliass)
                        else:
                            UserProfile.objects.filter(email=serializer.data['email']).update(alias=aliass)

                        u = UserProfile.objects.get(email = serializer.data['email'])
                        role = Role.objects.get(role='ADMIN')
                        r_id = role.role_id
                        user_role = UserRole.objects.create(role_id = r_id, user_id = u.id)
                        user_role.save()
                        return Response({"message" : "Admin Account Created Successfully"}, status=status.HTTP_200_OK)
                    except:
                        return Response({"message":"Authentication Required"},status=status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    return Response({"message" :serializer.errors},status=status.HTTP_409_CONFLICT)
            else:
                return Response({"message":"Incorrect SuperAdmin Details"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#########  Admin org_register   ########
class AdminCompanyRegistrationView(CreateAPIView):
    serializer_class = Admin_org_serializer

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
                elif(CompanyProfile.objects.filter(user=userdata)):
                    data = {'message' : "Admin Details Already Exists"}
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
                            # if(orgcountry=='india' or orgcountry=='India' or orgcountry=='IN' or orgcountry=='INDIA' or orgcountry=='in'): 
                            #     stripe.api_key = STRIPE_SECRET_KEY
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
                                # "country": 'INDIA',
                                # "pin_code": orgpincode,
                                # "gstin" : taxdata.upper()
                                # })
                                # headers = {
                                # 'Content-Type': 'application/json',
                                # 'Authorization': SHIPMENT_TOKEN
                                # }
                                # response=requests.request("POST", url, headers=headers, data=payload)
                                # if response.status_code==200:
                                #     stracnt=stripe.Account.create(
                                #         country="IN",
                                #         type="standard",
                                #         business_type="company",
                                #         tos_acceptance={"service_agreement": "full"},   # recipient
                                #     )
                                #     strlink=stripe.AccountLink.create(
                                #         account=stracnt['id'],
                                #         refresh_url="https://localhost:8000/login/",
                                #         return_url="http://54.67.88.195/vendor/dashboard",
                                #         type="account_onboarding",
                                #     )
                                #     serializer.save()
                                    # stracntretr=stripe.Account.retrieve(stracnt['id'])
                            CompanyProfile.objects.filter(email=dataemail, mobile=datamobile, tax_id=taxdata,
                                org_name=orgdata).update(user=usertable, is_active='True', tax_id = taxdata.upper(), tax_status = 'Verified',country='INDIA')
                            # a1 = CompanyProfile.objects.get(user=userdata)
                            # company_stripe.objects.create(accountid=stracntretr['id'],type=stracntretr['type'],companyid=a1)
                            data = {
                                # "link":strlink['url'],
                                # "Shiprocket":response.json(),
                                "message" : "Successfully Created"
                            }
                            return Response(data,status=status.HTTP_200_OK)
                                # else:
                                #     return Response(response.json(),status=status.HTTP_401_UNAUTHORIZED)
                            # elif(orgcountry=='UNITED STATES' or orgcountry=='US' or orgcountry=='United States' or orgcountry=='united states' or orgcountry=='us'):
                            #     stripe.api_key = STRIPE_SECRET_US_KEY
                            #     url = "https://apiv2.shiprocket.in/v1/external/settings/company/addpickup"
                            #     payload = json.dumps({
                            #     "pickup_location": orgdata,
                            #     "name": orgdata,
                            #     "email": dataemail,
                            #     "phone": datamobile,
                            #     "address": orgaddress,
                            #     "address_2": "",
                            #     "city": orgcity,
                            #     "state": orgstate,
                            #     "country": 'UNITED STATES',
                            #     "pin_code": orgpincode,
                            #     "gstin" : taxdata.upper()
                            #     })
                            #     headers = {
                            #     'Content-Type': 'application/json',
                            #     'Authorization': SHIPMENT_TOKEN
                            #     }
                            #     response=requests.request("POST", url, headers=headers, data=payload)
                            #     if response.status_code==200:
                            #         stracnt=stripe.Account.create(
                            #             country="US",
                            #             type="express",
                            #             business_type="company",
                            #             tos_acceptance={"service_agreement": "full"},   # recipient
                            #             settings={
                            #                 "payouts":{
                            #                     "schedule":{
                            #                         "delay_days":15,
                            #                         "interval":"daily",
                            #                     }
                            #                 }
                            #             }
                            #         )
                            #         strlink=stripe.AccountLink.create(
                            #             account=stracnt['id'],
                            #             refresh_url="https://localhost:8000/login/",
                            #             return_url="http://54.67.88.195/vendor/dashboard",
                            #             type="account_onboarding",
                            #         )
                            #         serializer.save()
                            #         stracntretr=stripe.Account.retrieve(stracnt['id'])
                            #         CompanyProfile.objects.filter(email=dataemail, mobile=datamobile, tax_id=taxdata,
                            #             org_name=orgdata).update(user=usertable, tax_id = taxdata.upper(), tax_status = 'Verified',country='UNITED STATES')
                            #         a1 = CompanyProfile.objects.get(user=userdata)
                            #         company_stripe.objects.create(accountid=stracntretr['id'],type=stracntretr['type'],companyid=a1)
                            #         data = {
                            #             "link":strlink['url'],
                            #             "Shiprocket":response.json(),
                            #             "message" : "Fill the details in link to activate the account"
                            #         }
                            #         return Response(data,status=status.HTTP_200_OK)
                            #     else:
                            #         return Response(response.json(),status=status.HTTP_401_UNAUTHORIZED)
                            # else:
                            #     return Response({"message":"Country is not allowed"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            return Response({"message":"Invalid GSTIN Number"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        data = {'message' : "Incorrect Input Fields"}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data={"message":'Current User is not Admin'}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


    @transaction.atomic
    def get(self,request,token):
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
                    table = CompanyProfile.objects.filter(user=userdata)
                    if table.exists():
                        data = list(table.values())
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        data = {"message" : "Details Not Found"}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data={'message' : "Current User is not Admin"}
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
                    table = CompanyProfile.objects.filter(user=userdata)
                    if table.exists():
                        table.delete()
                        return Response({"message" :"Deleted Successfully"},status=status.HTTP_200_OK)
                    else:
                        data = {'message' : "Details Not Found"}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data={'message' : "Current User is not Admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        



####### call this api while calling return url is calling in account link.
@csrf_exempt
@api_view(['GET'])
@transaction.atomic
def admin_stripe_api(request,token):
    if request.method == 'GET':
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='ADMIN')
        adminrole = role.role_id
        roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
        if roles.exists():
            if token1.expiry < datetime.now(utc):
                KnoxAuthtoken.objects.filter(user=user).delete()
                data = {"message":'Session Expired, Please login again'}
                return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
            else:
                if((CompanyProfile.objects.filter(user=userdata,is_active=True) and UserProfile.objects.filter(id=userdata,is_vendor_com_user=True)).exists()):
                    return Response({"message":"company details exists"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
                else:
                    cmpdata=CompanyProfile.objects.get(user=userdata)
                    cmpdt=company_stripe.objects.get(companyid=cmpdata.id)
                    if cmpdata.country == 'IN' or cmpdata.country == 'in' or cmpdata.country == 'INDIA' or cmpdata.country == 'india' or cmpdata.country == 'India':
                        stripe.api_key = STRIPE_SECRET_KEY
                        stracntretr=stripe.Account.retrieve(cmpdt.accountid)
                        if(stracntretr['details_submitted']!='null'):
                            a2=dict(stracntretr['external_accounts']['data'][0])
                            company_stripe.objects.filter(accountid=stracntretr['id'],companyid=cmpdt.companyid).update(
                                country=stracntretr['country'],
                                email=stracntretr['business_profile']['support_email'],companyname=stracntretr['business_profile']['name'],
                                mobile=stracntretr['business_profile']['support_phone'],bankid=a2['id']
                            )
                            CompanyProfile.objects.filter(user=userdata).update(is_active=True)
                            return Response({"message":"Account activation completed successfully"},status=status.HTTP_200_OK)
                        else:
                            return Response({"message":"please submit the details"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    elif cmpdata.country == 'US' or cmpdata.country == 'us' or cmpdata.country == 'UNITED STATES' or cmpdata.country == 'United States' or cmpdata.country == 'united states':
                        stripe.api_key = STRIPE_SECRET_US_KEY
                        stracntretr=stripe.Account.retrieve(cmpdt.accountid)
                        if(stracntretr['details_submitted']!='null'):
                            a2=dict(stracntretr['external_accounts']['data'][0])
                            company_stripe.objects.filter(accountid=stracntretr['id'],companyid=cmpdt.companyid).update(
                                country=stracntretr['country'],
                                email=stracntretr['business_profile']['support_email'],companyname=stracntretr['business_profile']['name'],
                                mobile=stracntretr['business_profile']['support_phone'],bankid=a2['id']
                            )
                            CompanyProfile.objects.filter(user=userdata).update(is_active=True)
                            return Response({"message":"Account activation completed successfully"},status=status.HTTP_200_OK)
                        else:
                            return Response({"message":"please submit the details"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        pass
        else:
            message = {
            "warning" : "User not assigned to Role",
                "message" : "Activate your account"
                }
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    




#### create a page like payment failed page and add a button to generate a link.
####  use that page link in refresh url.
#### use this api for link generate button in that page.
@csrf_exempt
@api_view(['GET'])
@transaction.atomic
def admin_retry_stripe_api(request,token):
    if request.method == 'GET':
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='ADMIN')
        adminrole = role.role_id
        roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
        if roles.exists():
            if token1.expiry < datetime.now(utc):
                KnoxAuthtoken.objects.filter(user=user).delete()
                data = {"message":'Session Expired, Please login again'}
                return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
            else:
                if((CompanyProfile.objects.filter(user=userdata,is_active=True) and UserProfile.objects.filter(id=userdata,is_vendor_com_user=True)).exists()):
                    return Response({"message":"company details exists"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
                else:
                    cmpdata=CompanyProfile.objects.get(user=userdata)
                    cmpdt=company_stripe.objects.get(companyid=cmpdata.id)
                    if cmpdata.country == 'IN' or cmpdata.country == 'in' or cmpdata.country == 'INDIA' or cmpdata.country == 'india' or cmpdata.country == 'India':
                        stripe.api_key = STRIPE_SECRET_KEY
                        strlink = stripe.AccountLink.create(
                            account=cmpdt.accountid,
                            refresh_url="https://localhost:8000/login/",
                            return_url="http://54.67.88.195/vendor/dashboard",
                            type="account_onboarding",
                        )
                        data = {
                            "link":strlink['url'],
                            "message" : "Fill the details in link to activate the account"
                        }
                        return Response(data,status=status.HTTP_200_OK)
                    elif cmpdata.country == 'US' or cmpdata.country == 'us' or cmpdata.country == 'UNITED STATES' or cmpdata.country == 'United States' or cmpdata.country == 'united states':
                        stripe.api_key = STRIPE_SECRET_US_KEY
                        strlink = stripe.AccountLink.create(
                            account=cmpdt.accountid,
                            refresh_url="https://localhost:8000/login/",
                            return_url="http://54.67.88.195/vendor/dashboard",
                            type="account_onboarding",
                        )
                        data = {
                            "link":strlink['url'],
                            "message" : "Fill the details in link to activate the account"
                        }
                        return Response(data,status=status.HTTP_200_OK)
                    else:
                        pass
        else:
            message = {
            "warning" : "User not assigned to Role",
                "message" : "Activate your account"
                }
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    




########  stripe payment account details update and login 

@csrf_exempt
@api_view(['GET'])
@transaction.atomic
def admin_stripe_login(request,token):
    if request.method == 'GET':
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='ADMIN')
        adminrole = role.role_id
        roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
        if roles.exists():
            if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    cmpn = CompanyProfile.objects.get(user=userdata)
                    actb = company_stripe.objects.get(companyid=cmpn.id)
                    orgcountry = cmpn.country
                    if(orgcountry=='india' or orgcountry=='India' or orgcountry=='IN' or orgcountry=='INDIA' or orgcountry=='in'): 
                        stripe.api_key = STRIPE_SECRET_KEY
                        data = {"message":"INDIAN accounts are not allowed to create login due to STANDARD account types"}
                        return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
                    elif(orgcountry=='UNITED STATES' or orgcountry=='US' or orgcountry=='United States' or orgcountry=='united states' or orgcountry=='us'):
                        stripe.api_key = STRIPE_SECRET_US_KEY
                        a1=stripe.Account.create_login_link(actb.accountid)
                        data = {
                            "login_link":a1['url'],
                            "message":"please clink on the link to login to stripe payments and update details."
                        }
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Country is not allowed"},status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                data = {"message":'Vendor is In-Active, please Activate your account'}
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            message = {
            "warning" : "User not assigned to Role",
                "message" : "Activate your account"
                }
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    




####################################   Admin org update   ###################################
class CompanyDetailsUpdateView(CreateAPIView):
    serializer_class = AdminOrgupdate

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
                    if(CompanyProfile.objects.filter(user=userdata)):
                        serializer = self.get_serializer(usertable, data=request.data)
                        if serializer.is_valid(raise_exception=True):
                            c=CompanyProfile.objects.get(user=userdata)
                            orgname = serializer.validated_data['org_name']
                            description = serializer.validated_data['description']
                            address = serializer.validated_data['address']
                            city = serializer.validated_data['city']
                            state = serializer.validated_data['state']
                            pincode = serializer.validated_data['pincode']
                            country = serializer.validated_data['country']

                            if(country=='india' or country=='India' or country=='IN' or country=='in' or country=='INDIA'):
                                url = "https://apiv2.shiprocket.in/v1/external/settings/company/addpickup"
                                payload = json.dumps({
                                "pickup_location": orgname,
                                "name": orgname,
                                "email": c.email,
                                "phone": c.mobile,
                                "address": address,
                                "address_2": "",
                                "city": city,
                                "state": state,
                                "country": 'INDIA',
                                "pin_code": pincode,
                                "gstin" : c.tax_id.upper()
                                })
                                headers = {
                                'Content-Type': 'application/json',
                                'Authorization': SHIPMENT_TOKEN
                                }
                                r=requests.request("POST", url, headers=headers, data=payload)
                                if r.status_code==200:
                                    CompanyProfile.objects.filter(user=userdata).update(org_name=orgname, 
                                    description=description, address=address, city=city, state=state, pincode=pincode, 
                                    country='INDIA')
                                    data = {'message':'Details Updated Successfully',
                                            "Shiprocket":r.json()}
                                    return Response(data, status=status.HTTP_200_OK)
                                else:
                                    return Response(r.json(),status=status.HTTP_401_UNAUTHORIZED)
                            elif(country=='UNITED STATES' or country=='US' or country=='United States' or country=='united states' or country=='us'):
                                url = "https://apiv2.shiprocket.in/v1/external/settings/company/addpickup"
                                payload = json.dumps({
                                "pickup_location": orgname,
                                "name": orgname,
                                "email": c.email,
                                "phone": c.mobile,
                                "address": address,
                                "address_2": "",
                                "city": city,
                                "state": state,
                                "country": 'UNITED STATES',
                                "pin_code": pincode,
                                "gstin" : c.tax_id.upper()
                                })
                                headers = {
                                'Content-Type': 'application/json',
                                'Authorization': SHIPMENT_TOKEN
                                }
                                r=requests.request("POST", url, headers=headers, data=payload)
                                if r.status_code==200:
                                    CompanyProfile.objects.filter(user=userdata).update(org_name=orgname, 
                                    description=description, address=address, city=city, state=state, pincode=pincode, 
                                    country='UNITED STATES')
                                    data = {'message':'Details Updated Successfully',
                                            "Shiprocket":r.json()}
                                    return Response(data, status=status.HTTP_200_OK)
                                else:
                                    return Response(r.json(),status=status.HTTP_401_UNAUTHORIZED)
                            else:
                                return Response({"message":"Country is not allowed"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            data = {'message' : "Incorrect Input Details"}
                            return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data = {'message' : 'Details Not Found'}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : "Current User is not Admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {'message':'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


##################   Company email update ######################
class EmailUpdateView(CreateAPIView):
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
        roles = Role.objects.get(role='ADMIN')
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
            return Response({"message":"Current User is not Admin"}, status=status.HTTP_406_NOT_ACCEPTABLE)


##################   Company mobile update ######################
class MobileUpdateView(CreateAPIView):
    serializer_class = comapanymobileserializer

    @transaction.atomic
    def put(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        roles = Role.objects.get(role='ADMIN')
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
            return Response({"message":"Current User is not Admin"}, status=status.HTTP_406_NOT_ACCEPTABLE)


##################   Company tax_id update ######################
class TaxIDUpdateView(CreateAPIView):
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
        roles = Role.objects.get(role='ADMIN')
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
                        #####   validations want to do for email while updating
                        pattern = re.compile("^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}")
                        if len(serializerdata)==15 and pattern.match(serializerdata) :
                            CompanyProfile.objects.filter(user=userdata).update(tax_id=serializerdata.upper())
                            return Response({"message":"tax_id updated successfully"}, status=status.HTTP_200_OK)
                        return Response({"message":"Invalid GSTIN Number"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({"message":"Invalid Input field"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message":"Company details not exists for this user"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":"Current User is not Admin"}, status=status.HTTP_406_NOT_ACCEPTABLE)

##################  Admin Products  ###############   
# class AddProductView(CreateAPIView):
#     serializer_class = ad_products

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
#         role3 = Role.objects.get(role='ADMIN')
#         sarole = role3.role_id
#         roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if(CompanyProfile.objects.filter(user=userdata,is_active='True')):
#                 if roles.exists():
#                     if token1.expiry < datetime.now(utc):
#                         KnoxAuthtoken.objects.filter(user=user).delete()
#                         data = {"message":'Session Expired, Please login again'}
#                         return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                     else:
#                         serializer = self.get_serializer(data=request.data)
#                         if serializer.is_valid(raise_exception=True):
#                             procategory = serializer.validated_data['category']
#                             protitle = serializer.validated_data['title']
#                             prodescription = serializer.validated_data['description']
#                             protype = serializer.validated_data['type']
#                             probrand = serializer.validated_data['brand'] 
#                             proquantity = serializer.validated_data['quantity']
#                             proprice = serializer.validated_data['price']
#                             prodiscount = serializer.validated_data['discount']
#                             pronew = serializer.validated_data['new']
#                             prosale =  serializer.validated_data['sale']
#                             procollection = serializer.validated_data['collection']
#                             prosize = serializer.validated_data['size']
#                             procolor = serializer.validated_data['color']
#                             propath = serializer.validated_data['path']
#                             prodimension = serializer.validated_data['dimensions']
#                             proweight = serializer.validated_data['weight']
                            
#                             if prodimension =='':
#                                 return Response({"messgae":"Please use the following format: L X B X H and values should be greater than 0.5 cm"})
#                             strval = 'SKU'+'-'+probrand.upper()+'-'+prosize.upper()+'-'+procolor.upper()

#                             custom_url = 'http://50.18.24.167/media/product/images/' + str(propath)
                            
#                             if(Category.objects.filter(category_name__iexact=procategory)):
#                                 tablecategory = Category.objects.get(category_name__iexact=procategory)
#                                 if proprice >= prodiscount:
#                                     protable = Product.objects.create(title=protitle,
#                                     description=prodescription, 
#                                     quantity=proquantity, 
#                                     price=round(proprice+proprice*0.18,2),
#                                     discount=prodiscount,
#                                     user=usertable, 
#                                     category_id=tablecategory.id, 
#                                     category = tablecategory.category_name,
#                                     type = protype,
#                                     brand=probrand,
#                                     new=pronew,
#                                     sale=prosale,
#                                     dimensions=prodimension,
#                                     weight=proweight
#                                     )
#                                     ava = protable.stock
#                                     total = ava + proquantity

#                                     cmpny=CompanyProfile.objects.get(user=userdata)
#                                     countrycmpn=cmpny.country
#                                     if countrycmpn=='INDIA':
#                                         stripe.api_key = STRIPE_SECRET_KEY
#                                         stpr=stripe.Product.create(name=protable.title)
#                                         amount = protable.price-(protable.price*protable.discount/100)
#                                         stpric=stripe.Price.create(unit_amount=int(amount*100),currency="inr",product=stpr['id'])
#                                         Product.objects.filter(id = protable.id,category_id=tablecategory.id).update(stock=total,alias='PRO-'+str(protable.id),strproduct=stpr['id'],strprice=stpric['id'])
#                                     elif countrycmpn=='UNITED STATES':
#                                         stripe.api_key = STRIPE_SECRET_US_KEY
#                                         stpr=stripe.Product.create(name=protable.title)
#                                         amount = protable.price-(protable.price*protable.discount/100)
#                                         stpric=stripe.Price.create(unit_amount=int(amount),currency="usd",product=stpr['id'])
#                                         Product.objects.filter(id = protable.id,category_id=tablecategory.id).update(stock=total,alias='PRO-'+str(protable.id),strproduct=stpr['id'],strprice=stpric['id'])
#                                     else:
#                                         return Response({"message":"Country not allowed"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                    
#                                     var = variants.objects.create(id=protable.id,sku=strval,size=prosize,color=procolor)
                                    
#                                     i=images.objects.create(id=protable.id,alt=var.color,path=propath,src=custom_url,variant_id=var.variant_id)
#                                     variants.objects.filter(variant_id=i.variant_id).update(image_id=i.image_id)
                                    
#                                     col = collection.objects.create(id=protable.id,collection=procollection)

#                                     tag = tags.objects.create(id=protable.id,tags=probrand)
#                                     tag = tags.objects.create(id=protable.id,tags=prosize)
#                                     tag = tags.objects.create(id=protable.id,tags=procolor)

#                                     if pronew ==True:
#                                         tags.objects.create(id=protable.id,tags='new')
                                    
                                

#                                     data = {"message":'Product Added successfully'}
#                                     return Response(data, status=status.HTTP_200_OK)
#                                 else:
#                                     return Response({"message" : "Discount percentage should be inbetween 0 to 100."}, status=status.HTTP_406_NOT_ACCEPTABLE)
#                             else:
#                                 data = {'message': "Category Not Found"}
#                                 return Response(data, status=status.HTTP_400_BAD_REQUEST)
#                         else:
#                             data = {'message': "Details Not Found"}
#                             return Response(data, status=status.HTTP_400_BAD_REQUEST)
#                 else:
#                     data={'message' : "Current User is not Admin"}
#                     return Response(data, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {"message":'Please activate the company profile to add the product'}
#                 return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
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
#         role3 = Role.objects.get(role='ADMIN')
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
#                             vendor = CompanyProfile.objects.get(user=pro.user)

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
#                                 "tags":t,
#                                 "variants" : var,
#                                 "images" : img,
#                                 "sold_by" : vendor.org_name,
#                                 "weight": pro.weight,
#                                 "dimensions":pro.dimensions
#                             }
#                             datalist.append(data)
#                         return Response(datalist, status=status.HTTP_200_OK)
#                     else:
#                         data = {"message":'Details Not Found'}
#                         return Response(data, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data={'message':"Current User is not Admin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


# class AddProductVariant(CreateAPIView):
#     serializer_class = admin_variant

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
#         role3 = Role.objects.get(role='ADMIN')
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


# class ProductDetailsUpdate(CreateAPIView):
#     serializer_class = admin_products_update

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
#         role3 = Role.objects.get(role='ADMIN')
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
#                             category = serializer.data['category']
#                             productname = serializer.data['title']
#                             description = serializer.data['description']
#                             unitprice = serializer.data['price']
#                             discount = serializer.data['discount']
#                             dimension = serializer.data['dimensions']
#                             weight = serializer.data['weight']

#                             if(Category.objects.filter(category_name__iexact=category)):
#                                 cat = Category.objects.get(category_name__iexact=category)
#                                 if unitprice >= discount:
#                                     Product.objects.filter(id=pid, user=userdata).update(
#                                         category = cat.id, title=productname, description=description,
#                                         price=round(unitprice,2), dis_price=discount,dimensions=dimension,weight=weight)
#                                     data = {"message":'Product Details Updated successfully'}
#                                     return Response(data, status=status.HTTP_200_OK)
#                                 else:
#                                     return Response({"message" : "Discount Price should be greater than Unit Price"}, status=status.HTTP_406_NOT_ACCEPTABLE)
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
#                 data={'message' : "Current User is not Admin"}
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
#         role3 = Role.objects.get(role='ADMIN')
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
#                         Product.objects.filter(user=userdata, id=pid).update(is_deleted=True)
#                         data = {"message":'Product Removed Successfully'}
#                         return Response(data, status=status.HTTP_200_OK)
#                     else:
#                         data = {'message' : "Details Not Found"}
#                         return Response(data, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {'message' : "Current User is not Admin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

############  Drop down apis for product_category  #########

class MobileSpecification(CreateAPIView):    
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
        role3 = Role.objects.get(role='ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(ProductMobile.objects.filter(product=pid).exists()):
            return Response({"message" :"Can't add Multiple Specifications for Same Product"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            if(UserProfile.objects.filter(id=userdata, is_active='True')):
                if roles.exists():
                    if token1.expiry < datetime.now(utc):
                        KnoxAuthtoken.objects.filter(user=user).delete()
                        data = {"message":'Session Expired, Please login again'}
                        return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                    else:
                        if(Category.objects.filter(category_name__iexact='Mobiles')):
                            tablecategory = Category.objects.get(category_name__iexact='Mobiles')
                            categoryid = tablecategory.id
                            tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                            if tableproduct.exists():
                                serializer = self.get_serializer(data=request.data)
                                if serializer.is_valid(raise_exception=True):
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
                                    data = {'message':"Product Specifications Added successfully"}
                                    return Response(data, status=status.HTTP_200_OK)
                                else:
                                    data = {'message' : "Incorrect Input Fields"}
                                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                data = {'message' : "Details Not Found"}
                                return Response(data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            return Response({"Category not found"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    data={'message' : "Current User is not Admin"}
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
        role3 = Role.objects.get(role='ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Category.objects.filter(category_name__iexact='Mobiles')):
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
                                data = {'message' : "Incorrect Input Fields"}
                                return Response(status=status.HTTP_400_BAD_REQUEST)
                        else:
                            data = {'message' : "Details Not Found"}
                            return Response(data, status=status.HTTP_404_NOT_FOUND)
                    else:
                            return Response({"Category not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                data={'message' : "Current User is not Admin"}
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
        role3 = Role.objects.get(role='ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Category.objects.filter(category_name__iexact='Mobiles')):
                        tablecategory = Category.objects.get(category_name__iexact='Mobiles')
                        categoryid = tablecategory.id
                        tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                        table = ProductMobile.objects.filter(product=pid)
                        if table.exists() and tableproduct.exists():
                            table.delete()
                            data = {"message":'Deleted successfully'}
                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            data = {'message' : "Details Not Found"}
                            return Response(data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"Category not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : 'Current User is not Admin'}
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
        role3 = Role.objects.get(role='ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    tablecategory = Category.objects.get(category_name__iexact='Mobiles')
                    categoryid = tablecategory.id
                    tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                    table = ProductMobile.objects.filter(product=pid)
                    if table.exists() and tableproduct.exists():
                        data = list(table.values('model_number','model_name','storage_spec','battery_spec','device_spec','camera_spec','other_spec'))
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        data = {'message' : "Details Not Found"}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : "Current User is not Admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


class LaptopSpecification(CreateAPIView):
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
        role3 = Role.objects.get(role='ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Category.objects.filter(category_name__iexact='Laptops')):
                        tablecategory = Category.objects.get(category_name__iexact='Laptops')
                        categoryid = tablecategory.id
                        tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                        if tableproduct.exists():
                            serializer = self.get_serializer(data=request.data)
                            if serializer.is_valid(raise_exception=True):
                                if(ProductLaptop.objects.filter(product=pid).exists()):
                                    return Response({"Product with specifications exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
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
                                    data = {'message': "Product Specifications Added successfully"}
                                    return Response(data, status=status.HTTP_200_OK)
                            else:
                                data = {'message' : "Incorrect Input Fields"}
                                return Response(data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            data = {'message' : "Details Not Found"}
                            return Response(data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"Category not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : 'Current User is not Admin'}
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
        role3 = Role.objects.get(role='ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if(Category.objects.filter(category_name__iexact='Laptops')):
                        tablecategory = Category.objects.get(category_name__iexact='Laptops')
                        categoryid = tablecategory.id
                        tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                        tablecheck = ProductLaptop.objects.filter(product=pid)
                        if tableproduct.exists and tablecheck.exists():
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
                            data = {'message' : "Details Not Found"}
                            return Response(data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"Category not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : "Current User is not Admin"}
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
        role3 = Role.objects.get(role='ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    tablecategory = Category.objects.get(category_name__iexact='Laptops')
                    categoryid = tablecategory.id
                    tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                    table = ProductLaptop.objects.filter(product=pid)
                    if table.exists() and tableproduct.exists():
                        table.delete()
                        data = {"message":'Deleted successfully'}
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        data = {'message' : "Details Not Found"}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : 'Current User is not Admin'}
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
        role3 = Role.objects.get(role='ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    tablecategory = Category.objects.get(category_name__iexact='Laptops')
                    categoryid = tablecategory.id
                    tableproduct = Product.objects.filter(user=userdata, id=pid, category=categoryid)
                    table = ProductLaptop.objects.filter(product=pid)
                    if table.exists() and tableproduct.exists():
                        data = list(table.values())
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        data = {'message' : "Details Not Found"}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : "Current User is not Admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

###################   Admin adding category   ###################

class AddCategory(CreateAPIView):
    serializer_class = admin_category

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
        adminrole = role3.role_id
        roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
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
                            return Response({"Category Exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            Category.objects.create(category_name=serializerdata.upper())
                            return Response({"Category created successfully, please add specifications"},status=status.HTTP_200_OK)
                    else:
                        return Response({"Seralizer is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {'message' : "Current User is not Admin"}
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
        role3 = Role.objects.get(role='ADMIN')
        adminrole = role3.role_id
        roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
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
                            return Response({"Category Removed successfully"},status=status.HTTP_200_OK)
                        else:
                            return Response({"Category not found"},status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"Seralizer is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {'message' : "Current User is not Admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)



# class VendorsList(CreateAPIView):

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)
#         if role.exists():
#             r_vendor= Role.objects.get(role='VENDOR')
#             role_v=UserRole.objects.filter(role_id=r_vendor.role_id).values()
#             if(UserProfile.objects.filter(id=user, is_active='True')):
#                 if role_v.exists():
#                     if token1.expiry < datetime.now(utc):
#                         KnoxAuthtoken.objects.filter(user=user).delete()
#                         data = {"message":'Session Expired, Please login again'}
#                         return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                     else: 
#                         list=[]
#                         for i in role_v:
#                             v = CompanyProfile.objects.get(user=i["user_id"])
#                             data = {
#                             "org_name" : v.org_name,
#                             "mobile" : v.mobile,
#                             "email" : v.email,
#                             "tax_id" : v.tax_id,
#                             "tax_status": v.tax_status,
#                             "is_active" : v.is_active
#                             }
#                             list.append(data)
#                         return Response(list,status=status.HTTP_200_OK)
#                 return Response({},status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {"message":'User is in In-Active, please Activate your account'}
#                 return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
#         return Response({"message":"Doesnot exists"},status=status.HTTP_404_NOT_FOUND)

# class UsersList(CreateAPIView):

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)
#         if role.exists():
#             r_user= Role.objects.get(role='USER')
#             role_u=UserRole.objects.filter(role_id=r_user.role_id).values()
#             if(UserProfile.objects.filter(id=user, is_active='True')):
#                 if role_u.exists():
#                     if token1.expiry < datetime.now(utc):
#                         KnoxAuthtoken.objects.filter(user=user).delete()
#                         data = {"message":'Session Expired, Please login again'}
#                         return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                     else: 
#                         list=[]
#                         for i in role_u:
#                             if (UserRole.objects.filter(user_id=i['user_id'],role_id=3)):
#                                 assigned_role = 'USER/VENDOR'
#                             else:
#                                 assigned_role = 'USER'
#                             usertable = UserProfile.objects.get(id=i["user_id"])
#                             count = datetime.now(timezone.utc)- usertable.last_login
#                             data = {
#                             "id" : usertable.id,
#                             "username":usertable.username,
#                             "mobile_number":usertable.mobile_number,
#                             "email":usertable.email,
#                             "first_name":usertable.first_name,
#                             "last_name":usertable.last_name,
#                             "is_active" : usertable.is_active,
#                             "last_Login" : count.days,
#                             "is_vendor" : usertable.is_vendor_com_user,
#                             "roles" : assigned_role
#                             }
#                             list.append(data)
#                         return Response(list,status=status.HTTP_200_OK)
#                 return Response({},status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {"message":'User is in In-Active, please Activate your account'}
#                 return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
#         else:
#             data = {'message' : "Current User is not Admin"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)

# class OrdersList(CreateAPIView):

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

#         if role.exists():
#             o = OrderItemHistory.objects.all().values()
#             if o.exists():
#                 if(token1.expiry < datetime.now(utc)):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else: 
#                     list=[]
#                     for i in o:
#                         if (images.objects.filter(id = i['product']).exists()):
#                             src = images.objects.get(id = i['product'])
#                             img=src.src
#                         else:
#                             img='null'
                            
#                         if (Transaction_table.objects.filter(orderitem=str(i['id'])).exists()):
#                             pay = Transaction_table.objects.get(orderitem=str(i['id'])) 
#                             payment = pay.status
#                         else:
#                             payment = 'null'

#                         ord =OrderItemHistory.objects.get(id=i['id'])

#                         data = {
#                             "order_id" :ord.id,
#                             "image" : img,
#                             "payment_status" : payment,
#                             "order_status": ord.order_status,
#                             "date": ord.created_at.date(),
#                             "total" : ord.item_price
#                         }
#                         list.append(data)
#                     return Response(list, status=status.HTTP_200_OK)
#             else:
#                 return Response([],status=status.HTTP_204_NO_CONTENT)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


# class SalesList(CreateAPIView):

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

#         if role.exists():
#             tx = Transaction_table.objects.filter(status='paid').all().values()
#             if tx.exists():
#                 list=[]
#                 for i in tx:
#                     if (OrderItemHistory.objects.filter(id=i['orderitem']).exists()):
#                         o = OrderItemHistory.objects.get(id=i['orderitem'])
#                         ord=o.id
#                         odate = o.created_at.date()
#                         am = o.item_price
#                         st = o.order_status
#                     else:
#                         ord='null'
#                         odate = 'null'
#                         am = 'null'
#                         st='null'
#                     tnx  = Transaction_table.objects.get(id=i['id'])
#                     data={
#                         "order_id" : ord,
#                         "transaction_id" : tnx.id,
#                         "delivery_status" : st,
#                         "invoice_id" : "",
#                         "date" : odate,
#                         "amount" : am
#                     }
#                     list.append(data)
#                 return Response(list)
#             return Response([], status=status.HTTP_204_NO_CONTENT)
#         else:
#             return Response({"message": "ROle Doent exists"}, status=status.HTTP_404_NOT_FOUND)
    
# class GetProductsListBasedOnDateFilter(CreateAPIView):
#     serializer_class = DateFilter

#     @transaction.atomic
#     def get(self,request, token):
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
#         role3 = Role.objects.get(role='ADMIN')
#         adminrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     p = Product.objects.all()
#                     if serializer.is_valid(raise_exception=True):
#                         date1 = serializer.validated_data['from_date']
#                         date2 = serializer.validated_data['to_date']
                        
#                         p=Product.objects.filter(created_at__range=[date1, date2]).values()
#                         list=[]
#                         if p.exists():
#                             for i in p:
#                                 pro = Product.objects.get(id = i['id'])
#                                 col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
#                                 var = variants.objects.filter(id=i['id']).values()
#                                 img = images.objects.filter(id=i['id']).values()
#                                 t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
#                                 vendor = CompanyProfile.objects.get(user=pro.user)

#                                 data = {
#                                     "id": pro.id,
#                                     "title": pro.title,
#                                     "description": pro.description, 
#                                     "type": pro.type,
#                                     "brand": pro.brand,
#                                     "collection": col,
#                                     "category": pro.category,
#                                     "price": pro.price,
#                                     "sale": pro.sale,
#                                     "discount": pro.discount,
#                                     "stock": pro.stock,
#                                     "new": pro.new,
#                                     "tags":t,
#                                     "variants" : var,
#                                     "images" : img,
#                                     "sold_by" : vendor.org_name
#                                 }
#                                 list.append(data)
#                             return Response(list, status=status.HTTP_200_OK)
#                         else:
#                             data = {"message":'Details Not Found'}
#                             return Response(data, status=status.HTTP_404_NOT_FOUND)
#                     else:
#                         return Response({"message":"Date field is missing"}, status=status.HTTP_404_NOT_FOUND)
            
#             else:
#                 data = {'message' : "Current User is not Admin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
    
            
# class GetProductsListBasedOnProductName(CreateAPIView):
#     serializer_class = ProductNameFilter

#     @transaction.atomic
#     def get(self,request, token):
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
#         role3 = Role.objects.get(role='ADMIN')
#         adminrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         name_filter = serializer.validated_data['name']              
#                         p=Product.objects.filter(title__icontains=name_filter).values()
#                         if p.exists():
#                             list=[]
#                             for i in p:
#                                 pro = Product.objects.get(id = i['id'])
#                                 col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
#                                 var = variants.objects.filter(id=i['id']).values()
#                                 img = images.objects.filter(id=i['id']).values()
#                                 t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
#                                 vendor = CompanyProfile.objects.get(user=pro.user)

#                                 data = {
#                                     "id": pro.id,
#                                     "title": pro.title,
#                                     "description": pro.description, 
#                                     "type": pro.type,
#                                     "brand": pro.brand,
#                                     "collection": col,
#                                     "category": pro.category,
#                                     "price": pro.price,
#                                     "sale": pro.sale,
#                                     "discount": pro.discount,
#                                     "stock": pro.stock,
#                                     "new": pro.new,
#                                     "tags":t,
#                                     "variants" : var,
#                                     "images" : img,
#                                     "sold_by" : vendor.org_name
#                                 }
#                                 list.append(data)
#                             return Response(list, status=status.HTTP_200_OK)
#                         else:
#                             data = {"message":'Details Not Found'}
#                             return Response(data, status=status.HTTP_404_NOT_FOUND)
#                     return Response({"message":"Name Field Error"}, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {'message' : "Current User is not Admin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
            

# class GetProductsListBasedOnProductPrice(CreateAPIView):
#     serializer_class = ProductPriceFilter

#     @transaction.atomic
#     def get(self,request, token):
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
#         role3 = Role.objects.get(role='ADMIN')
#         adminrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         price_filter1 = serializer.validated_data['from_price']
#                         price_filter2 = serializer.validated_data['to_price']              
#                         p=Product.objects.filter(price__range=[price_filter1,price_filter2]).values()
#                         if p.exists():
#                             list=[]
#                             for i in p:
#                                 pro = Product.objects.get(id = i['id'])
#                                 col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
#                                 var = variants.objects.filter(id=i['id']).values()
#                                 img = images.objects.filter(id=i['id']).values()
#                                 t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
#                                 vendor = CompanyProfile.objects.get(user=pro.user)

#                                 data = {
#                                     "id": pro.id,
#                                     "title": pro.title,
#                                     "description": pro.description, 
#                                     "type": pro.type,
#                                     "brand": pro.brand,
#                                     "collection": col,
#                                     "category": pro.category,
#                                     "price": pro.price,
#                                     "sale": pro.sale,
#                                     "discount": pro.discount,
#                                     "stock": pro.stock,
#                                     "new": pro.new,
#                                     "tags":t,
#                                     "variants" : var,
#                                     "images" : img,
#                                     "sold_by" : vendor.org_name
#                                 }
#                                 list.append(data)
#                             return Response(list, status=status.HTTP_200_OK)
#                         else:
#                             data = {"message":'Details Not Found'}
#                             return Response(data, status=status.HTTP_404_NOT_FOUND)
#                     return Response({"message":"Name Field Error"}, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {'message' : "Current User is not Admin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

# class GetProductsListBasedOnProductCategory(CreateAPIView):
#     serializer_class = ProductCategoryFilter

#     @transaction.atomic
#     def get(self,request, token):
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
#         role3 = Role.objects.get(role='ADMIN')
#         adminrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         name_filter = serializer.validated_data['category']              
#                         p=Product.objects.filter(category__icontains=name_filter).values()
#                         if p.exists():
#                             list=[]
#                             for i in p:
#                                 pro = Product.objects.get(id = i['id'])
#                                 col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
#                                 var = variants.objects.filter(id=i['id']).values()
#                                 img = images.objects.filter(id=i['id']).values()
#                                 t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
#                                 vendor = CompanyProfile.objects.get(user=pro.user)

#                                 data = {
#                                     "id": pro.id,
#                                     "title": pro.title,
#                                     "description": pro.description, 
#                                     "type": pro.type,
#                                     "brand": pro.brand,
#                                     "collection": col,
#                                     "category": pro.category,
#                                     "price": pro.price,
#                                     "sale": pro.sale,
#                                     "discount": pro.discount,
#                                     "stock": pro.stock,
#                                     "new": pro.new,
#                                     "tags":t,
#                                     "variants" : var,
#                                     "images" : img,
#                                     "sold_by" : vendor.org_name
#                                 }
#                                 list.append(data)
#                             return Response(list, status=status.HTTP_200_OK)
#                         else:
#                             data = {"message":'Details Not Found'}
#                             return Response(data, status=status.HTTP_404_NOT_FOUND)
#                     return Response({"message":"Name Field Error"}, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {'message' : "Current User is not Admin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
   

# class GetProductsListBasedOnProductColor(CreateAPIView):
#     serializer_class = ProductColorFilter

#     @transaction.atomic
#     def get(self,request, token):
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
#         role3 = Role.objects.get(role='ADMIN')
#         adminrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         color_filter = serializer.validated_data['color']              
#                         p=variants.objects.filter(color=color_filter).values()
#                         if p.exists():
#                             list=[]
#                             for i in p:
#                                 pro = Product.objects.get(id = i['id'])
#                                 col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
#                                 var = variants.objects.filter(id=i['id']).values()
#                                 img = images.objects.filter(id=i['id']).values()
#                                 t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
#                                 vendor = CompanyProfile.objects.get(user=pro.user)

#                                 data = {
#                                     "id": pro.id,
#                                     "title": pro.title,
#                                     "description": pro.description, 
#                                     "type": pro.type,
#                                     "brand": pro.brand,
#                                     "collection": col,
#                                     "category": pro.category,
#                                     "price": pro.price,
#                                     "sale": pro.sale,
#                                     "discount": pro.discount,
#                                     "stock": pro.stock,
#                                     "new": pro.new,
#                                     "tags":t,
#                                     "variants" : var,
#                                     "images" : img,
#                                     "sold_by" : vendor.org_name
#                                 }
#                                 list.append(data)
#                             return Response(list, status=status.HTTP_200_OK)
#                         else:
#                             data = {"message":'Details Not Found'}
#                             return Response(data, status=status.HTTP_404_NOT_FOUND)
#                     return Response({"message":"Color Field Error"}, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {'message' : "Current User is not Admin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


# class GetProductsListBasedOnProductAvailablity(CreateAPIView):
#     serializer_class = ProductAvailabeFilter

#     @transaction.atomic
#     def get(self,request, token):
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
#         role3 = Role.objects.get(role='ADMIN')
#         adminrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         available_filter = serializer.validated_data['is_available']
#                         if available_filter ==True:
#                             p = Product.objects.filter(stock__gte=1).values()
#                         else:
#                             p = Product.objects.filter(stock__lte=0).values()

#                         if p.exists():
#                             list=[]
#                             for i in p:
#                                 pro = Product.objects.get(id = i['id'])
#                                 col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
#                                 var = variants.objects.filter(id=i['id']).values()
#                                 img = images.objects.filter(id=i['id']).values()
#                                 t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
#                                 vendor = CompanyProfile.objects.get(user=pro.user)

#                                 data = {
#                                     "id": pro.id,
#                                     "title": pro.title,
#                                     "description": pro.description, 
#                                     "type": pro.type,
#                                     "brand": pro.brand,
#                                     "collection": col,
#                                     "category": pro.category,
#                                     "price": pro.price,
#                                     "sale": pro.sale,
#                                     "discount": pro.discount,
#                                     "stock": pro.stock,
#                                     "new": pro.new,
#                                     "tags":t,
#                                     "variants" : var,
#                                     "images" : img,
#                                     "sold_by" : vendor.org_name
#                                 }
#                                 list.append(data)
#                             return Response(list, status=status.HTTP_200_OK)
#                         else:
#                             data = {"message":'Details Not Found'}
#                             return Response(data, status=status.HTTP_404_NOT_FOUND)
#                     return Response({"message":"Name Field Error"}, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {'message' : "Current User is not Admin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        
# class GetProductsListBasedOnProductType(CreateAPIView):
#     serializer_class = ProductTypeFilter

#     @transaction.atomic
#     def get(self,request, token):
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
#         role3 = Role.objects.get(role='ADMIN')
#         adminrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         type_filter = serializer.validated_data['type']              
#                         p=Product.objects.filter(type__icontains=type_filter).values()
#                         if p.exists():
#                             list=[]
#                             for i in p:
#                                 pro = Product.objects.get(id = i['id'])
#                                 col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
#                                 var = variants.objects.filter(id=i['id']).values()
#                                 img = images.objects.filter(id=i['id']).values()
#                                 t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
#                                 vendor = CompanyProfile.objects.get(user=pro.user)

#                                 data = {
#                                     "id": pro.id,
#                                     "title": pro.title,
#                                     "description": pro.description, 
#                                     "type": pro.type,
#                                     "brand": pro.brand,
#                                     "collection": col,
#                                     "category": pro.category,
#                                     "price": pro.price,
#                                     "sale": pro.sale,
#                                     "discount": pro.discount,
#                                     "stock": pro.stock,
#                                     "new": pro.new,
#                                     "tags":t,
#                                     "variants" : var,
#                                     "images" : img,
#                                     "sold_by" : vendor.org_name
#                                 }
#                                 list.append(data)
#                             return Response(list, status=status.HTTP_200_OK)
#                         else:
#                             data = {"message":'Details Not Found'}
#                             return Response(data, status=status.HTTP_404_NOT_FOUND)
#                     return Response({"message":"Name Field Error"}, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {'message' : "Current User is not Admin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        
# class GetProductsListBasedOnProductDiscount(CreateAPIView):
#     serializer_class = ProductDiscountFilter

#     @transaction.atomic
#     def get(self,request, token):
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
#         role3 = Role.objects.get(role='ADMIN')
#         adminrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=adminrole).filter(user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         discount_filter = serializer.validated_data['discount']              
#                         p=Product.objects.filter(discount__gte=discount_filter).values()
#                         if p.exists():
#                             list=[]
#                             for i in p:
#                                 pro = Product.objects.get(id = i['id'])
#                                 col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
#                                 var = variants.objects.filter(id=i['id']).values()
#                                 img = images.objects.filter(id=i['id']).values()
#                                 t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
#                                 vendor = CompanyProfile.objects.get(user=pro.user)

#                                 data = {
#                                     "id": pro.id,
#                                     "title": pro.title,
#                                     "description": pro.description, 
#                                     "type": pro.type,
#                                     "brand": pro.brand,
#                                     "collection": col,
#                                     "category": pro.category,
#                                     "price": pro.price,
#                                     "sale": pro.sale,
#                                     "discount": pro.discount,
#                                     "stock": pro.stock,
#                                     "new": pro.new,
#                                     "tags":t,
#                                     "variants" : var,
#                                     "images" : img,
#                                     "sold_by" : vendor.org_name
#                                 }
#                                 list.append(data)
#                             return Response(list, status=status.HTTP_200_OK)
#                         else:
#                             data = {"message":'Details Not Found'}
#                             return Response(data, status=status.HTTP_404_NOT_FOUND)
#                     return Response({"message":"Name Field Error"}, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {'message' : "Current User is not Admin"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

# class GetOrderListBasedOnOrderItem(CreateAPIView):
#     serializer_class = OrderIdFilter

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

#         if role.exists():
#             o = OrderItemHistory.objects.all().values()
#             if o.exists():
#                 if(token1.expiry < datetime.now(utc)):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else: 
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         id_filter = serializer.validated_data['id']              
#                         o=OrderItemHistory.objects.filter(id=id_filter).values()
#                         list=[]
#                         for i in o:
#                             if (images.objects.filter(id = i['product']).exists()):
#                                 src = images.objects.get(id = i['product'])
#                                 img=src.src
#                             else:
#                                 img='null'
                                
#                             if (Transaction_table.objects.filter(orderitem=str(i['id'])).exists()):
#                                 pay = Transaction_table.objects.get(orderitem=str(i['id'])) 
#                                 payment = pay.status
#                             else:
#                                 payment = 'null'

#                             ord =OrderItemHistory.objects.get(id=i['id'])

#                             data = {
#                                 "order_id" :ord.id,
#                                 "image" : img,
#                                 "payment_status" : payment,
#                                 "order_status": ord.order_status,
#                                 "date": ord.created_at.date(),
#                                 "total" : ord.item_price
#                             }
#                             list.append(data)
#                         return Response(list, status=status.HTTP_200_OK)
#                     else:
#                         return Response({"message":"Id not found"}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return Response([],status=status.HTTP_204_NO_CONTENT)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

# class GetOrderListBasedOnPaymentStatus(CreateAPIView):
#     serializer_class = OrderPaymentStatusFilter

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

#         if role.exists():
#             o = OrderItemHistory.objects.all().values()
#             if o.exists():
#                 if(token1.expiry < datetime.now(utc)):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else: 
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         status_filter = serializer.validated_data['status']              
#                         o=Transaction_table.objects.filter(status=status_filter).values()
#                         list=[]
#                         for i in o:
#                             oi=Transaction_table.objects.get(id=i['id'])
#                             p = OrderItemHistory.objects.get(id=oi.orderitem)
                
#                             if (images.objects.filter(id = p.product).exists()):
#                                 src = images.objects.get(id = p.product)
#                                 img=src.src
#                             else:
#                                 img='null'
                                
#                             if (Transaction_table.objects.filter(orderitem=p.id).exists()):
#                                 pay = Transaction_table.objects.get(orderitem=p.id) 
#                                 payment = pay.status
#                             else:
#                                 payment = 'null'

#                             ord =OrderItemHistory.objects.get(id=oi.orderitem)

#                             data = {
#                                 "order_id" :ord.id,
#                                 "image" : img,
#                                 "payment_status" : payment,
#                                 "order_status": ord.order_status,
#                                 "date": ord.created_at.date(),
#                                 "total" : ord.item_price
#                             }
#                             list.append(data)
#                         return Response(list, status=status.HTTP_200_OK)
#                     else:
#                         return Response({"message":"Id not found"}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return Response([],status=status.HTTP_204_NO_CONTENT)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


# class GetOrderListBasedOnOrderStatus(CreateAPIView):
#     serializer_class = OrderStatusFilter

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

#         if role.exists():
#             o = OrderItemHistory.objects.all().values()
#             if o.exists():
#                 if(token1.expiry < datetime.now(utc)):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else: 
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         status_filter = serializer.validated_data['status']              
#                         o=OrderItemHistory.objects.filter(order_status=status_filter).values()
#                         list=[]
#                         for i in o:
                           
#                             if (images.objects.filter(id = i['product']).exists()):
#                                 src = images.objects.get(id = i['product'])
#                                 img=src.src
#                             else:
#                                 img='null'
                                
#                             if (Transaction_table.objects.filter(orderitem=i['id']).exists()):
#                                 pay = Transaction_table.objects.get(orderitem=i['id']) 
#                                 payment = pay.status
#                             else:
#                                 payment = 'null'

#                             ord =OrderItemHistory.objects.get(id=i['id'])

#                             data = {
#                                 "order_id" :ord.id,
#                                 "image" : img,
#                                 "payment_status" : payment,
#                                 "order_status": ord.order_status,
#                                 "date": ord.created_at.date(),
#                                 "total" : ord.item_price
#                             }
#                             list.append(data)
#                         return Response(list, status=status.HTTP_200_OK)
#                     else:
#                         return Response({"message":"Id not found"}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return Response([],status=status.HTTP_204_NO_CONTENT)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

# class GetOrderListBasedOnDateFilter(CreateAPIView):
#     serializer_class = DateFilter

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

#         if role.exists():
#             o = OrderItemHistory.objects.all().values()
#             if o.exists():
#                 if(token1.expiry < datetime.now(utc)):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else: 
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         date1 = serializer.validated_data['from_date']
#                         date2 = serializer.validated_data['to_date']
                        
#                         o=OrderItemHistory.objects.filter(created_at__range=[date1, date2]).values()
#                         list=[]
#                         for i in o:
                           
#                             if (images.objects.filter(id = i['product']).exists()):
#                                 src = images.objects.get(id = i['product'])
#                                 img=src.src
#                             else:
#                                 img='null'
                                
#                             if (Transaction_table.objects.filter(orderitem=i['id']).exists()):
#                                 pay = Transaction_table.objects.get(orderitem=i['id']) 
#                                 payment = pay.status
#                             else:
#                                 payment = 'null'

#                             ord =OrderItemHistory.objects.get(id=i['id'])

#                             data = {
#                                 "order_id" :ord.id,
#                                 "image" : img,
#                                 "payment_status" : payment,
#                                 "order_status": ord.order_status,
#                                 "date": ord.created_at.date(),
#                                 "total" : ord.item_price
#                             }
#                             list.append(data)
#                         return Response(list, status=status.HTTP_200_OK)
#                     else:
#                         return Response({"message":"Id not found"}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return Response([],status=status.HTTP_204_NO_CONTENT)
#         else:
#             data = {"message":'User is in In-Active, please Activate your account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


# class GetSalesListBasedOnOrderID(CreateAPIView):
#     serializer_class = SalesOrderIDFilter

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

#         if role.exists():
#             if(token1.expiry < datetime.now(utc)):
#                 KnoxAuthtoken.objects.filter(user=user).delete()
#                 data = {"message":'Session Expired, Please login again'}
#                 return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#             else: 
#                 serializer = self.get_serializer(data=request.data)
#                 if serializer.is_valid(raise_exception=True):
#                     order_id = serializer.validated_data['id']

#                     tx = Transaction_table.objects.filter(status='paid',orderitem=order_id).all().values()
#                     if tx.exists():
#                         list=[]
#                         for i in tx:
#                             if (OrderItemHistory.objects.filter(id=i['orderitem']).exists()):
#                                 o = OrderItemHistory.objects.get(id=i['orderitem'])
#                                 ord=o.id
#                                 odate = o.created_at.date()
#                                 am = o.item_price
#                                 st = o.order_status
#                             else:
#                                 ord='null'
#                                 odate = 'null'
#                                 am = 'null'
#                                 st='null'
#                             try:
#                                 tnx  = Transaction_table.objects.get(orderitem=i['id'])
#                                 tnx_id=tnx.id
#                             except: 
#                                 tnx_id=''  
#                             data={
#                                 "order_id" : ord,
#                                 "transaction_id" : tnx_id,
#                                 "delivery_status" : st,
#                                 "invoice_id" : "",
#                                 "date" : odate,
#                                 "amount" : am
#                             }
#                             list.append(data)
#                         return Response(list)
#                     return Response([], status=status.HTTP_204_NO_CONTENT)
#                 else:
#                     return Response({"message":"ID is Missing"}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({"message": "Role Doent exists"}, status=status.HTTP_404_NOT_FOUND)
    

# class GetSalesListBasedOnTransactionID(CreateAPIView):
#     serializer_class = SalesTxnIDFilter

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

#         if role.exists():
#             if(token1.expiry < datetime.now(utc)):
#                 KnoxAuthtoken.objects.filter(user=user).delete()
#                 data = {"message":'Session Expired, Please login again'}
#                 return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#             else: 
#                 serializer = self.get_serializer(data=request.data)
#                 if serializer.is_valid(raise_exception=True):
#                     tnx_id = serializer.validated_data['id']
                    
#                     tx = Transaction_table.objects.filter(status='paid',id=tnx_id).all().values()
#                     if tx.exists():
#                         list=[]
#                         for i in tx:
#                             if (OrderItemHistory.objects.filter(id=i['orderitem']).exists()):
#                                 o = OrderItemHistory.objects.get(id=i['orderitem'])
#                                 ord=o.id
#                                 odate = o.created_at.date()
#                                 am = o.item_price
#                                 st = o.order_status
#                             else:
#                                 ord='null'
#                                 odate = 'null'
#                                 am = 'null'
#                                 st='null'
#                             try:
#                                 tnx  = Transaction_table.objects.get(orderitem=i['id'])
#                                 tnx_id=tnx.id
#                             except: 
#                                 tnx_id=''  
#                             data={
#                                 "order_id" : ord,
#                                 "transaction_id" : tnx_id,
#                                 "delivery_status" : st,
#                                 "invoice_id" : "",
#                                 "date" : odate,
#                                 "amount" : am
#                             }
#                             list.append(data)
#                         return Response(list)
#                     return Response([], status=status.HTTP_204_NO_CONTENT)
#                 else:
#                     return Response({"message":"Transaction ID is Missing"}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({"message": "Role Doent exists"}, status=status.HTTP_404_NOT_FOUND)


# class GetSalesListBasedOnInvoiceID(CreateAPIView):
#     serializer_class = SalesInvoiceIDFilter

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

#         if role.exists():
#             if(token1.expiry < datetime.now(utc)):
#                 KnoxAuthtoken.objects.filter(user=user).delete()
#                 data = {"message":'Session Expired, Please login again'}
#                 return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#             else: 
#                 serializer = self.get_serializer(data=request.data)
#                 if serializer.is_valid(raise_exception=True):
#                     invoice_id = serializer.validated_data['id']
                    
#                     inv = Payment_details_table.objects.filter(invoice=invoice_id).all().values()
#                     if inv.exists():
#                         list=[]
#                         for i in inv:
#                             if (OrderItemHistory.objects.filter(id=i['orderitem']).exists()):
#                                 o = OrderItemHistory.objects.get(id=i['orderitem'])
#                                 ord=o.id
#                                 odate = o.created_at.date()
#                                 am = o.item_price
#                                 st = o.order_status
#                             else:
#                                 ord='null'
#                                 odate = 'null'
#                                 am = 'null'
#                                 st='null'
#                             try:
#                                 tnx  = Transaction_table.objects.get(orderitem=i['id'])
#                                 tnx_id=tnx.id
#                             except: 
#                                 tnx_id=''  
#                             data={
#                                 "order_id" : ord,
#                                 "transaction_id" : tnx_id,
#                                 "delivery_status" : st,
#                                 "invoice_id" : "",
#                                 "date" : odate,
#                                 "amount" : am
#                             }
#                             list.append(data)
#                         return Response(list)
#                     return Response([], status=status.HTTP_204_NO_CONTENT)
#                 else:
#                     return Response({"message":"Transaction ID is Missing"}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({"message": "Role Doent exists"}, status=status.HTTP_404_NOT_FOUND)


# class GetSalesListBasedOnDevliveryStatus(CreateAPIView):
#     serializer_class = SalesDeliveryStatusFilter

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

#         if role.exists():
#             # if o.exists():
#             if(token1.expiry < datetime.now(utc)):
#                 KnoxAuthtoken.objects.filter(user=user).delete()
#                 data = {"message":'Session Expired, Please login again'}
#                 return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#             else: 
#                 serializer = self.get_serializer(data=request.data)
#                 if serializer.is_valid(raise_exception=True):
#                     delivery_status = serializer.validated_data['status']
                    
#                     inv = OrderItemHistory.objects.filter(shipment_status=delivery_status).all().values()
#                     if inv.exists():
#                         list=[]
#                         for i in inv:
#                             if (OrderItemHistory.objects.filter(id=i['id']).exists()):
#                                 o = OrderItemHistory.objects.get(id=i['id'])
#                                 ord=o.id
#                                 odate = o.created_at.date()
#                                 am = o.item_price
#                                 st = o.order_status
#                             else:
#                                 ord='null'
#                                 odate = 'null'
#                                 am = 'null'
#                                 st='null'
#                             try:
#                                 tnx  = Transaction_table.objects.get(orderitem=i['id'])
#                                 tnx_id=tnx.id
#                             except: 
#                                 tnx_id=''  
#                             data={
#                                 "order_id" : ord,
#                                 "transaction_id" : tnx_id,
#                                 "delivery_status" : st,
#                                 "invoice_id" : "",
#                                 "date" : odate,
#                                 "amount" : am
#                             }
#                             list.append(data)
#                         return Response(list)
#                     return Response([], status=status.HTTP_204_NO_CONTENT)
#                 else:
#                     return Response({"message":"Transaction ID is Missing"}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({"message": "Role Doent exists"}, status=status.HTTP_404_NOT_FOUND)


# class GetSalesListBasedOnDateFilter(CreateAPIView):
#     serializer_class = DateFilter

#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {
#                     "message" : "Invalid Access Token"
#                 }
#             return Response(data, status=status.HTTP_404_NOT_FOUND)
#         user = token1.user_id
#         r_admin = Role.objects.get(role='ADMIN')
#         role=UserRole.objects.filter(user_id=user, role_id=r_admin.role_id)

#         if role.exists():
#             if(token1.expiry < datetime.now(utc)):
#                 KnoxAuthtoken.objects.filter(user=user).delete()
#                 data = {"message":'Session Expired, Please login again'}
#                 return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#             else: 
#                 serializer = self.get_serializer(data=request.data)
#                 if serializer.is_valid(raise_exception=True):
#                     date1 = serializer.validated_data['from_date']
#                     date2 = serializer.validated_data['to_date']
                    
#                     tx = Transaction_table.objects.filter(status='paid',created_at__range=[date1, date2]).all().values()
#                     if tx.exists():
#                         list=[]
#                         for i in tx:
#                             if (OrderItemHistory.objects.filter(id=i['orderitem']).exists()):
#                                 o = OrderItemHistory.objects.get(id=i['orderitem'])
#                                 ord=o.id
#                                 odate = o.created_at.date()
#                                 am = o.item_price
#                                 st = o.order_status
#                             else:
#                                 ord='null'
#                                 odate = 'null'
#                                 am = 'null'
#                                 st='null'
#                             try:
#                                 tnx  = Transaction_table.objects.get(orderitem=i['id'])
#                                 tnx_id=tnx.id
#                             except: 
#                                 tnx_id=''  
#                             data={
#                                 "order_id" : ord,
#                                 "transaction_id" : tnx_id,
#                                 "delivery_status" : st,
#                                 "invoice_id" : "",
#                                 "date" : odate,
#                                 "amount" : am
#                             }
#                             list.append(data)
#                         return Response(list)
#                     return Response([], status=status.HTTP_204_NO_CONTENT)
#                 else:
#                     return Response({"message":"Transaction ID is Missing"}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({"message": "Role Doent exists"}, status=status.HTTP_404_NOT_FOUND)
class AdminDashboardDetails(CreateAPIView):
    def get(self, request,token):
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
                cp=CompanyProfile.objects.get(user=user)
                p=Product.objects.filter(user=cp.user).values()
                total_list=[]
                pending_list=[]
                for i in p:
                    total_orders = OrderItemHistory.objects.filter(product=i['id']).count()
                    total_list.append(total_orders)
                    pending_orders = OrderItemHistory.objects.filter(product=i['id'],order_status='INPROGRESS').count()
                    pending_list.append(pending_orders)
                return Response({
                            "total_orders":sum(total_list),
                            "pending_orders":sum(pending_list)
                            })
        return Response({"message":"Userdata not found in Role"}, status=status.HTTP_404_NOT_FOUND)


class ProductRestoreAPI(CreateAPIView):
    @transaction.atomic
    def put(self,request,token,pid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role3 = Role.objects.get(role='ADMIN')
        sarole = role3.role_id
        roles = UserRole.objects.filter(role_id=sarole).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    
                    if (Product.objects.filter(user=userdata, id=pid).exists()):
                        Product.objects.filter(user=userdata, id=pid).update(is_deleted=False)
                        data = {"message":'Product Restored Successfully'}
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        data = {'message' : "Details Not Found"}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data = {'message' : "Current User is not Admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


class AdminOrderDetailPageAPI(CreateAPIView):
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
        role = Role.objects.get(role='ADMIN')
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
                                # print(order_response.json()['data'][a'shipments'])
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
                    
