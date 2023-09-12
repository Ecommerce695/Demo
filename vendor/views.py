from django.db import transaction
from rest_framework.response import Response
from datetime import datetime,timedelta
from pytz import utc
from rest_framework import status
from rest_framework.generics import CreateAPIView
import random
from django.utils.crypto import get_random_string
from Ecomerce_project import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site 
from vendor.serializers import (VendorOrgRegistration,vendorActivateAccountSerializer,vendorResetActivationSerializer,
                          VendorOrgupdate,vecomapanyemailserializer,vecomapanymobileserializer,vecomapanytaxidserializer,
                          MobileSpecification,LaptopSpecification,
                          seri_colour,ven_search,price_seri,CategoryBasedProductPagination)
from customer.models import KnoxAuthtoken,UserProfile,Role,UserRole
from super_admin.models import CompanyProfile,Category,Product,variants,images,collection,tags,ProductLaptop,ProductMobile
from .models import Vendor_Account_Activation
import requests, json
from Ecomerce_project.settings import SHIPMENT_TOKEN
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.db import transaction
from order.models import (OrderItemHistory)
import re
import stripe
from django.conf import settings
from Ecomerce_project.settings import prperpage
from django.core.paginator import Paginator
from django.db.models import Count
from django.conf import settings
from vendor.models import company_stripe
from Ecomerce_project.settings import STRIPE_SECRET_KEY, STRIPE_SECRET_US_KEY




class VendorRegistration(CreateAPIView):
    serializer_class = VendorOrgRegistration

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
        userrole = role.role_id
        role2 = Role.objects.get(role='ADMIN')
        adminrole = role2.role_id
        role3 = Role.objects.get(role='SUPER_ADMIN')
        sarole = role3.role_id
        role5 = Role.objects.get(role='VENDOR')
        vendorrole = role5.role_id
        if(UserRole.objects.filter(user_id=userdata, role_id=adminrole)):
            return Response({"message" : "Can't Register as vendor, with Admin Credentials"},status=status.HTTP_406_NOT_ACCEPTABLE)
        elif(UserRole.objects.filter(user_id=userdata, role_id=sarole)):
            return Response({"message" : "Can't Register as vendor, with Super Admin Credentials"},status=status.HTTP_406_NOT_ACCEPTABLE)
        roles = UserRole.objects.filter(role_id=userrole).filter(user_id=userdata)
        if roles.exists():
            if token1.expiry <= datetime.now(utc):
                KnoxAuthtoken.objects.filter(user=user).delete()
                data = {"message":'Session Expired, Please login again'}
                return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
            elif(CompanyProfile.objects.filter(user=userdata)):
                data = {"message" : "Vendor data with this account Exists, please activate company account"}
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)    
            elif(UserRole.objects.filter(user_id=userdata, role_id=vendorrole)):
                data = {"message" : "Vendor with this role Exists"}
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
            
                        unique_id = get_random_string(length=64)
                        protocol ='http://'
                        current_site = '54.67.88.195/'
                        api = 'core/activate_account/'

                        try:
                            Gotp = random.randint(10000,99999)
                            message = "Request for Vendor Account Registration.\nYour One-Time Password is{}\nTo activate your account, please click on the following url:\n {}{}{}{}\n".format(Gotp,protocol,current_site,api,unique_id)
                            subject = "xShop Vendor Registration"
                            from_email = settings.EMAIL_HOST_USER
                            to_email = [dataemail]
                            send_mail(subject, message, from_email, to_email)
                            Vendor_Account_Activation.objects.create(user = userdata, key = unique_id, otp=Gotp)
                            # if(orgcountry=='india' or orgcountry=='India' or orgcountry=='IN' or orgcountry=='INDIA' or orgcountry=='in'): 
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
                            #     "country": 'INDIA',
                            #     "pin_code": orgpincode,
                            #     "gstin" : taxdata.upper()
                            #     })
                            #     headers = {
                            #     'Content-Type': 'application/json',
                            #     'Authorization': SHIPMENT_TOKEN
                            #     }
                            #     response = requests.request("POST", url, headers=headers, data=payload)
                            #     if response.status_code==200:
                            #         serializer.save()
                            #         role = Role.objects.get(role='VENDOR')
                            #         r_id = role.role_id
                            #         UserRole.objects.create(role_id = r_id, user_id = userdata)
                                    
                            #         CompanyProfile.objects.filter(email=dataemail, mobile=datamobile, 
                            #         org_name=orgdata).update(user=usertable,tax_id=taxdata.upper(),country='INDIA')
                                    
                            #         data = {
                            #             "message" : "Vendor Account activate mail sent to {}, Please activate account".format(dataemail), 
                            #             "id": unique_id,
                            #             "Shiprocket":response.text
                            #         }
                            #         return Response(data, status=status.HTTP_200_OK)
                            #     else:
                            #         return Response(response.json(),status=status.HTTP_401_UNAUTHORIZED)  
                            # elif(orgcountry=='UNITED STATES' or orgcountry=='US' or orgcountry=='United States' or orgcountry=='united states' or orgcountry=='us'):
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
                            #     response = requests.request("POST", url, headers=headers, data=payload)
                            #     if response.status_code==200:
                            #         serializer.save()
                            #         role = Role.objects.get(role='VENDOR')
                            #         r_id = role.role_id
                            #         UserRole.objects.create(role_id = r_id, user_id = userdata)
                                    
                            #         CompanyProfile.objects.filter(email=dataemail, mobile=datamobile, 
                            #         org_name=orgdata).update(user=usertable,tax_id=taxdata.upper(),country='UNITED STATES')
                                    
                            #         data = {
                            #             "message" : "Vendor Account activate mail sent to {}, Please activate account".format(dataemail), 
                            #             "id": unique_id,
                            #             "Shiprocket":response.text
                            #         }
                            #         return Response(data, status=status.HTTP_200_OK)
                            #     else:
                            #         return Response(response.json(),status=status.HTTP_401_UNAUTHORIZED)
                            # else:
                            #     return Response({"message":"INDIA and UNITED STATES are only allowed"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        except:
                            return Response({"message":"SMTP mail error"},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"message":"Invalid GSTIN Number"},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    return Response(serializer.errors,status=status.HTTP_401_UNAUTHORIZED )
        else:
            message = {
                "warning" : "User not assigned to Role",
                "message" : "Activate your account"
                }
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)



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
        role = Role.objects.get(role='VENDOR')
        vendorrole = role.role_id
        roles = UserRole.objects.filter(role_id=vendorrole).filter(user_id=userdata)
        if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    table = CompanyProfile.objects.filter(user=userdata)
                    if table.exists():
                        vendor = CompanyProfile.objects.get(user=userdata)
                        data = {
                            "org_name": vendor.org_name,
                            "email": vendor.email,
                            "mobile": vendor.mobile,
                            "tax_id": vendor.tax_id.upper(),
                            "description": vendor.description,
                            "address": vendor.address,
                            "city": vendor.city,
                            "state":vendor.state,
                            "pincode":vendor.pincode,
                            "country": vendor.country
                        }
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        data = {"message":'Vendor Data not exist'}
                        return Response(data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                message = {
                "warning" : "User not assigned to Role",
                "message" : "Activate your account"
                }
                return Response(message, status=status.HTTP_401_UNAUTHORIZED)
        else:
            data = {"message": "Please activte vendor account"}
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    # Deactivating as Vendor
    @transaction.atomic
    def delete(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='VENDOR')
        vendorrole = role.role_id
        roles = UserRole.objects.filter(role_id=vendorrole).filter(user_id=userdata)
        if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    table = CompanyProfile.objects.filter(user=userdata)
                    if table.exists():
                        CompanyProfile.objects.filter(user = userdata).update(is_active = False)
                        UserRole.objects.filter(role_id=vendorrole, user_id=userdata).delete()
                        return Response({"message" :"Deactivated Successfully"},status=status.HTTP_200_OK)
                    else:
                        data = {"message" :'Vendor Data not exist'}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                message = {
                "warning" : "User not assigned to Role",
                "message" : "Activate your account"
                }
                return Response(message, status=status.HTTP_401_UNAUTHORIZED)
        else:
            data = {"message":'Vendor is In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


class VendorAccountActivateView(CreateAPIView):
    serializer_class = vendorActivateAccountSerializer

    @transaction.atomic()
    def put(self, request, token):
        try:
            token = Vendor_Account_Activation.objects.get(key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        if token.expiry_date >= token.created_at:
            serializer = self.get_serializer(data = request.data)
            if serializer.is_valid(raise_exception=True):
                u_id = token.user
                otp_valid = token.otp
                otp = serializer.data['otp']
                if otp_valid ==otp:
                    cmtb=CompanyProfile.objects.get(user=u_id)
                    orgcountry=cmtb.country
                    if(orgcountry=='india' or orgcountry=='India' or orgcountry=='IN' or orgcountry=='INDIA' or orgcountry=='in'): 
                        stripe.api_key = STRIPE_SECRET_KEY
                        stracnt=stripe.Account.create(
                            country="IN",
                            type="standard",
                            business_type="company",
                            tos_acceptance={"service_agreement": "full"},   # recipient
                        )
                        strlink=stripe.AccountLink.create(
                            account=stracnt['id'],
                            refresh_url="https://localhost:8000/login/",
                            return_url="http://54.67.88.195/vendor/dashboard",
                            type="account_onboarding",
                        )
                        stracntretr=stripe.Account.retrieve(stracnt['id'])
                        company_stripe.objects.create(accountid=stracntretr['id'],type=stracntretr['type'],companyid=cmtb)
                        data = {
                            "link":strlink['url'],
                            "message" : "Fill the details in link to activate the account"
                        }
                        return Response(data,status=status.HTTP_200_OK)
                    elif(orgcountry=='UNITED STATES' or orgcountry=='US' or orgcountry=='United States' or orgcountry=='united states' or orgcountry=='us'):
                        stripe.api_key = STRIPE_SECRET_US_KEY
                        stracnt=stripe.Account.create(
                            country="US",
                            type="express",
                            business_type="company",
                            tos_acceptance={"service_agreement": "full"},   # recipient
                            settings={
                                "payouts":{
                                    "schedule":{
                                        "delay_days":15,
                                        "interval":"daily",
                                    }
                                }
                            }
                        )
                        strlink=stripe.AccountLink.create(
                            account=stracnt['id'],
                            refresh_url="https://localhost:8000/login/",
                            return_url="http://54.67.88.195/vendor/dashboard",
                            type="account_onboarding",
                        )
                        stracntretr=stripe.Account.retrieve(stracnt['id'])
                        company_stripe.objects.create(accountid=stracntretr['id'],type=stracntretr['type'],companyid=cmtb)
                        data = {
                            "link":strlink['url'],
                            "message" : "Fill the details in link to activate the account"
                        }
                        return Response(data,status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Country is not allowed"},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    return Response({"message": "Incorrect OTP, Please try again"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"message" : "Activation Token/ OTP Expired"} , status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, token):
        try:
            token = Vendor_Account_Activation.objects.get(key=token)
        except:
            return Response({"message" : "Invalid Token in URL"}, status=status.HTTP_404_NOT_FOUND)

        if token.expiry_date <= token.created_at:
            # current_site = get_current_site(request).domain
            protocol ='http://'
            current_site = '54.67.88.195/'
            api = 'core/activate_account/'
            user = UserProfile.objects.get(id = token.user)

            Gotp = random.randint(10000,99999)
            message = "Thank you for registering with xShop.\nYour One-Time Password is {}\nTo activate your account, please click on the following url:\n {}{}{}{}\n".format(Gotp,protocol,current_site,api,token)
            subject = "xShop Account Activation"
            from_email = settings.EMAIL_HOST_USER
            to_email = [user.email]
            send_mail(subject, message, from_email, to_email)
            now = datetime.now()
            Vendor_Account_Activation.objects.filter(user = token.user).update(otp = Gotp, created_at = now, expiry_date=now + timedelta(days=2))
            return Response({"message" : "OTP has send again"})
        


####### call this api while calling return url is calling in account link.
@csrf_exempt
@api_view(['GET'])
@transaction.atomic
def stri_api(request,token):
    if request.method == 'GET':
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='VENDOR')
        vendorrole = role.role_id
        roles = UserRole.objects.filter(role_id=vendorrole).filter(user_id=userdata)
        if roles.exists():
            if token1.expiry < datetime.now(utc):
                KnoxAuthtoken.objects.filter(user=user).delete()
                data = {"message":'Session Expired, Please login again'}
                return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
            else:
                if((CompanyProfile.objects.filter(user=userdata,is_active=True) and UserProfile.objects.filter(id=userdata,is_vendor_com_user=True)).exists()):
                    return Response({"message":"details exists"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
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
                            UserProfile.objects.filter(id=userdata).update(is_vendor_com_user=True)
                            Vendor_Account_Activation.objects.filter(user = userdata).delete()
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
                            UserProfile.objects.filter(id=userdata).update(is_vendor_com_user=True)
                            Vendor_Account_Activation.objects.filter(user = userdata).delete()
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
def retry_stripe_api(request,token):
    if request.method == 'GET':
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='VENDOR')
        vendorrole = role.role_id
        roles = UserRole.objects.filter(role_id=vendorrole).filter(user_id=userdata)
        if roles.exists():
            if token1.expiry < datetime.now(utc):
                KnoxAuthtoken.objects.filter(user=user).delete()
                data = {"message":'Session Expired, Please login again'}
                return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
            else:
                if((CompanyProfile.objects.filter(user=userdata,is_active=True) and UserProfile.objects.filter(id=userdata,is_vendor_com_user=True)).exists()):
                    return Response({"message":"details exists"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
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
def vendor_stripe_login(request,token):
    if request.method == 'GET':
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='VENDOR')
        vendorrole = role.role_id
        roles = UserRole.objects.filter(role_id=vendorrole).filter(user_id=userdata)
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





class VendorResendActivationView(CreateAPIView):
    serializer_class = vendorResetActivationSerializer

    def post(self, request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            email1 = serializer.validated_data['email']
            if(CompanyProfile.objects.filter(email=email1, user=userdata)):
                name = CompanyProfile.objects.get(email = email1)   
                user_id = name.user
                table = UserProfile.objects.get(username=user_id)
                u_id = table.id
                Vendor_Account_Activation.objects.filter(user = u_id).delete()

                unique_id = get_random_string(length=64)
                # current_site = get_current_site(request).domain
                current_site = '54.67.88.195/'
                protocol ='http://'
                api = 'core/activate_account/'

                Gotp = random.randint(10000,99999)
                message = "Your Account Activation One-Time Password is {}\nTo activate your account, please click on the following url:\n {}{}{}{}\n".format(Gotp,protocol,current_site,api,unique_id)
                subject = "xShop Account Reset"
                from_email = settings.EMAIL_HOST_USER
                to_email = [email1]
                send_mail(subject, message, from_email, to_email)
                Vendor_Account_Activation.objects.create(user = u_id, key = unique_id, otp=Gotp)
                data1 = {
                    "message" : "OTP sent to Email",
                    "token" : unique_id
                }
                return Response(data1, status=status.HTTP_202_ACCEPTED)
            else:
                data = {"message":'Please enter valid EMAIL ID, email id not found for user'}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":"This Email is Not Registered"}, status=status.HTTP_401_UNAUTHORIZED)

class OrganizationDetailsUpdate(CreateAPIView):
    serializer_class = VendorOrgupdate

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
        role = Role.objects.get(role='VENDOR')
        vendorrole = role.role_id
        roles = UserRole.objects.filter(role_id=vendorrole).filter(user_id=userdata)
        if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
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
                            orgcountry = serializer.validated_data['country']

                            if(orgcountry=='india' or orgcountry=='India' or orgcountry=='IN' or orgcountry=='in' or orgcountry=='INDIA'):
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
                                    description=description, address=address,city=city, 
                                    state=state, pincode=pincode, country='INDIA')
                                    data = {'message':'Details Updated Successfully',
                                            "Shiprocket":r.json()}
                                    return Response(data, status=status.HTTP_200_OK)
                                else:
                                    return Response(r.json(),status=status.HTTP_401_UNAUTHORIZED)
                            elif(orgcountry=='UNITED STATES' or orgcountry=='US' or orgcountry=='United States' or orgcountry=='united states' or orgcountry=='us'):
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
                                    description=description, address=address,city=city, 
                                    state=state, pincode=pincode, country='UNITED STATES')
                                    data = {'message':'Details Updated Successfully',
                                            "Shiprocket":r.json()}
                                    return Response(data, status=status.HTTP_200_OK)
                                else:
                                    return Response(r.json(),status=status.HTTP_401_UNAUTHORIZED)
                            else:
                                return Response({"message":"Country is not allowed"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            data = {"message" : "Not a valid Serializer data"}
                            return Response(data,status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data = {"message":"Vendor Data doesn't exists"}
                        return Response(data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                message = {
                "warning" : "User not assigned to Role",
                "message" : "Activate your account"
                }
                return Response(message, status=status.HTTP_401_UNAUTHORIZED)
        else:
            data = {"message":'Vendor is In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

class EmailUpdate(CreateAPIView):
    serializer_class = vecomapanyemailserializer

    @transaction.atomic
    def put(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        roles = Role.objects.get(role='VENDOR')
        vendorrole = roles.role_id
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        companytable = CompanyProfile.objects.filter(user=userdata, is_active='True')
        if(UserRole.objects.filter(role_id=vendorrole, user_id=userdata)):
            if companytable.exists():
                if(token1.expiry < datetime.now(utc)):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        serializerdata = serializer.validated_data['email']
                        if(CompanyProfile.objects.filter(email=serializerdata).exists()):
                            return Response({"message":"Email Already Exists, try other"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            unique_id = get_random_string(length=64)
                            current_site = '54.67.88.195/'
                            protocol ='http://'
                            api = 'activate_account/'

                            Gotp = random.randint(10000,99999)
                            message = "Request for Email Update.\nYour One-Time Password is {}\n Please click on the following url:\n {}{}{}{}\n".format(Gotp,protocol,current_site,api,unique_id)
                            subject = "Company Email Update Request"
                            from_email = settings.EMAIL_HOST_USER
                            to_email = [serializerdata]
                            send_mail(subject, message, from_email, to_email)
                            Vendor_Account_Activation.objects.create(user = userdata, key = unique_id, otp=Gotp, email=serializerdata)

                            data = {
                                "message" : "Request for Email Update \n OTP sent to {}".format(serializerdata), 
                                "id": unique_id
                                }
                            return Response(data, status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Serializer is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message":"Company details not exists for this user"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":"Only Vendor allowed"}, status=status.HTTP_406_NOT_ACCEPTABLE)


class EmailUpdateVerification(CreateAPIView):
    serializer_class = vendorActivateAccountSerializer

    @transaction.atomic
    def put(self,request,token,act_token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
        try:
            token = Vendor_Account_Activation.objects.get(key=act_token)
        except:
            data = {"message" : "Invalid verification Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        roles = Role.objects.get(role='VENDOR')
        vendrole = roles.role_id
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        roles = UserRole.objects.filter(role_id=vendrole).filter(user_id=userdata)        
        if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
            if roles.exists():
                if(token1.expiry < datetime.now(utc)):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        userotp = serializer.validated_data['otp']
                        dbotp = token.otp
                        dbemail = token.email
                        if userotp == dbotp:
                            CompanyProfile.objects.filter(user=userdata).update(email=dbemail)
                            Vendor_Account_Activation.objects.filter(user=userdata).delete()
                            return Response({"message":"Email updated successfully"},status=status.HTTP_200_OK)
                        else:
                            return Response({"message":"OTP is invalid"},status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"message":"serializer value error"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message" : "User not assigned to Role"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message" : "Account is in In-Active, please Activate your Company account",}, status=status.HTTP_406_NOT_ACCEPTABLE)



class MobileUpdate(CreateAPIView):
    serializer_class = vecomapanymobileserializer

    @transaction.atomic
    def put(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        roles = Role.objects.get(role='VENDOR')
        vendorrole = roles.role_id
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        companytable = CompanyProfile.objects.filter(user=userdata, is_active='True')
        if(UserRole.objects.filter(role_id=vendorrole, user_id=userdata)):
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
                        return Response({"message":"Serializer is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message":"Company details not exists for this user"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":"Only vendor allowed"}, status=status.HTTP_406_NOT_ACCEPTABLE)


class TaxIDUpdate(CreateAPIView):
    serializer_class = vecomapanytaxidserializer

    @transaction.atomic
    def put(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        roles = Role.objects.get(role='VENDOR')
        vendorrole = roles.role_id
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        companytable = CompanyProfile.objects.filter(user=userdata, is_active='True')
        if(UserRole.objects.filter(role_id=vendorrole, user_id=userdata)):
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
                        if len(serializerdata)==15 and pattern.match(serializerdata) :
                            CompanyProfile.objects.filter(user=userdata).update(tax_id=serializerdata.upper())
                            return Response({"message":"TAXID updated successfully"}, status=status.HTTP_200_OK)
                        return Response({"message":"Invalid GSTIN Number"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({"message":"Serializer is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message":"Company details not exists for this user"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":"Only vendor allowed"}, status=status.HTTP_406_NOT_ACCEPTABLE)



# class VendorProductsView(CreateAPIView):
#     serializer_class = vendor_products

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
#         role3 = Role.objects.get(role='VENDOR')
#         venrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=venrole).filter(user_id=userdata)
#         if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         procategory = serializer.validated_data['category']
#                         protitle = serializer.validated_data['title']
#                         prodescription = serializer.validated_data['description']
#                         protype = serializer.validated_data['type']
#                         probrand = serializer.validated_data['brand'] 
#                         proquantity = serializer.validated_data['quantity']
#                         proprice = serializer.validated_data['price']
#                         prodiscount = serializer.validated_data['discount']
#                         pronew = serializer.validated_data['new']
#                         prosale =  serializer.validated_data['sale']
#                         procollection = serializer.validated_data['collection']
#                         prosize = serializer.validated_data['size']
#                         procolor = serializer.validated_data['color']
#                         propath = serializer.validated_data['path']
#                         prodimension = serializer.validated_data['dimensions']
#                         proweight = serializer.validated_data['weight']
                        
#                         if prodimension =='':
#                             return Response({"messgae":"Please use the following format: L X B X H and values should be greater than 0.5 cm"})
#                         strval = 'SKU'+'-'+probrand.upper()+'-'+prosize.upper()+'-'+procolor.upper()

#                         custom_url = 'http://50.18.24.167/media/product/images/' + str(propath)
                        
#                         if(Category.objects.filter(category_name__iexact=procategory)):
#                             tablecategory = Category.objects.get(category_name__iexact=procategory)
#                             if proprice >= prodiscount:
#                                 protable = Product.objects.create(title=protitle,
#                                 description=prodescription, 
#                                 quantity=proquantity, 
#                                 price=round(proprice+proprice*0.18,2),
#                                 discount=prodiscount,
#                                 user=usertable, 
#                                 category_id=tablecategory.id, 
#                                 category = tablecategory.category_name,
#                                 type = protype,
#                                 brand=probrand,
#                                 new=pronew,
#                                 sale=prosale,
#                                 dimensions=prodimension,
#                                 weight=proweight,
#                                 created_at=datetime.now(),
#                                 updated_at=datetime.now()
#                                 )
#                                 ava = protable.stock
#                                 total = ava + proquantity

#                                 cmpny=CompanyProfile.objects.get(user=userdata)
#                                 countrycmpn=cmpny.country
#                                 if countrycmpn=='INDIA':
#                                     stripe.api_key = STRIPE_SECRET_KEY
#                                     stpr=stripe.Product.create(name=protable.title)
#                                     amount = protable.price-(protable.price*protable.discount/100)
#                                     stpric=stripe.Price.create(unit_amount=int(amount*100),currency="inr",product=stpr['id'])
#                                     Product.objects.filter(id = protable.id,category_id=tablecategory.id).update(stock=total,alias='PRO-'+str(protable.id),strproduct=stpr['id'],strprice=stpric['id'])
#                                 elif countrycmpn=='UNITED STATES':
#                                     stripe.api_key = STRIPE_SECRET_US_KEY
#                                     stpr=stripe.Product.create(name=protable.title)
#                                     amount = protable.price-(protable.price*protable.discount/100)
#                                     stpric=stripe.Price.create(unit_amount=int(amount),currency="usd",product=stpr['id'])
#                                     Product.objects.filter(id = protable.id,category_id=tablecategory.id).update(stock=total,alias='PRO-'+str(protable.id),strproduct=stpr['id'],strprice=stpric['id'])
#                                 else:
#                                     return Response({"message":"Country not allowed"},status=status.HTTP_406_NOT_ACCEPTABLE)

#                                 var = variants.objects.create(id=protable.id,sku=strval,size=prosize,color=procolor)
                                
#                                 i=images.objects.create(id=protable.id,alt=var.color,path=propath,src=custom_url,variant_id=var.variant_id)
#                                 variants.objects.filter(variant_id=i.variant_id).update(image_id=i.image_id)
                                
#                                 col = collection.objects.create(id=protable.id,collection=procollection)

#                                 tag = tags.objects.create(id=protable.id,tags=probrand)
#                                 tag = tags.objects.create(id=protable.id,tags=prosize)
#                                 tag = tags.objects.create(id=protable.id,tags=procolor)

#                                 if pronew ==True:
#                                     tags.objects.create(id=protable.id,tags='new')
#                                 else:
#                                     pass
                                
#                                 data = {"message":'Product Added successfully'}
#                                 return Response(data, status=status.HTTP_200_OK)
#                             else:
#                                 return Response({"message" : "Discount percentage should be inbetween 0 to 100."}, status=status.HTTP_406_NOT_ACCEPTABLE)
#                         else:
#                             data = {'message': "Category Not Found"}
#                             return Response(data, status=status.HTTP_400_BAD_REQUEST)
#                     else:
#                         data = {'message': "Details Not Found"}
#                         return Response(data, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 data={'message' : "Current User is not Vendor"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your company account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)




# class vendorproductsapiget(CreateAPIView):
#     serializer_class = vend_products

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
#         role3 = Role.objects.get(role='VENDOR')
#         venrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=venrole).filter(user_id=userdata)
#         if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid(raise_exception=True):
#                         pageno = serializer.validated_data['pageno']
#                         table = Product.objects.filter(user=userdata)
#                         if table.exists():
#                             prodata = table.values('id')
#                             datalist =[] 

#                             for i in prodata:
#                                 try:
#                                     pro = Product.objects.get(id = i['id'])
#                                     col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
#                                     var = variants.objects.filter(id=i['id']).values()
#                                     img = images.objects.filter(id=i['id']).values()
#                                     t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
#                                     vendor = CompanyProfile.objects.get(user=pro.user)

#                                     data = {
#                                         "id": pro.id,
#                                         "title": pro.title,
#                                         "description": pro.description, 
#                                         "type": pro.type,
#                                         "brand": pro.brand,
#                                         "collection": col,
#                                         "category": pro.category,
#                                         "price": pro.price,
#                                         "sale": pro.sale,
#                                         "discount": pro.discount,
#                                         "stock": pro.stock,
#                                         "new": pro.new,
#                                         "tags":t,
#                                         "variants" : var,
#                                         "images" : img,
#                                         "sold_by" : vendor.org_name,
#                                         "weight": pro.weight,
#                                         "dimensions":pro.dimensions
#                                     }
#                                     datalist.append(data)
#                                     paginator = Paginator(datalist,prperpage)
#                                     page = request.GET.get("page",pageno)
#                                     object_list = paginator.page(page)
#                                     a=list(object_list)
#                                     data1 = {
#                                         "products_data":a,
#                                         "total_pages":paginator.num_pages,
#                                         "products_per_page":prperpage,
#                                         "total_products":paginator.count
#                                     }
#                                 except:
#                                     pass
#                             try:
#                                 return Response(data1,status=status.HTTP_200_OK)
#                             except:
#                                 return Response({"message":"pagination value error"},status=status.HTTP_400_BAD_REQUEST)
#                         else:
#                             data = {"message":'Details Not Found'}
#                             return Response(data, status=status.HTTP_404_NOT_FOUND)
#                     else:
#                         return Response({"message":"Serializer value error"},status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 data={'message':"Current User is not Vendor"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your Company account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)



# class AddProductVariantView(CreateAPIView):
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
#         role3 = Role.objects.get(role='VENDOR')
#         venrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=venrole).filter(user_id=userdata)
#         if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
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
#                             return Response({"message":"Serializer value error"},status=status.HTTP_400_BAD_REQUEST)
#                     else:
#                         return Response({"message":"This Product Does not exists fot this user"},status=status.HTTP_404_NOT_FOUND)    
#             else:
#                 data={'message' : "Current User is not Vendor"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your company account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)



# # class ProductDetailsUpdate(CreateAPIView):
#     serializer_class = vendor_products_update

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
#         role3 = Role.objects.get(role='VENDOR')
#         venrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=venrole).filter(user_id=userdata)
#         if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
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
#                             discount1= serializer.data['discount']
#                             dimension = serializer.data['dimensions']
#                             weight = serializer.data['weight']

#                             if(Category.objects.filter(category_name__iexact=category)):
#                                 cat = Category.objects.get(category_name__iexact=category)
#                                 if unitprice >= discount1:
#                                     Product.objects.filter(id=pid, user=userdata).update(
#                                         category=cat.category_name,category_id = cat.id, title=productname, description=description,
#                                         price=round(unitprice,2), discount=discount1,dimensions=dimension,weight=weight,updated_at=datetime.now())
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
#                         data = {'message' : "Product details Not Found for this user"}
#                         return Response(data, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data={'message' : "Current User is not Vendor"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your Company account'}
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
#         role3 = Role.objects.get(role='VENDOR')
#         venrole = role3.role_id
#         roles = UserRole.objects.filter(role_id=venrole).filter(user_id=userdata)
#         if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     table = Product.objects.filter(user=userdata, id=pid)
#                     if table.exists():
#                         Product.objects.filter(user=userdata, id=pid).update(is_deleted=True,updated_at=datetime.now())
#                         data = {"message":'Product Removed Successfully'}
#                         return Response(data, status=status.HTTP_200_OK)
#                     else:
#                         data = {'message' : "Details Not Found"}
#                         return Response(data, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 data = {'message' : "Current User is not Vendor"}
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'User is in In-Active, please Activate your Company account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)    


class MobileSpecificationView(CreateAPIView):    
    serializer_class  = MobileSpecification

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
        role3 = Role.objects.get(role='VENDOR')
        venrole = role3.role_id
        roles = UserRole.objects.filter(role_id=venrole).filter(user_id=userdata)
        if(ProductMobile.objects.filter(product=pid).exists()):
            return Response({"message" :"Can't add Multiple Specifications for Same Product"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
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
                    data={'message' : "Current User is not Vendor"}
                    return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data = {"message":'User is in In-Active, please Activate your Company account'}
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
                data={'message' : "Current User is not Vendor"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your Company account'}
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
                data = {'message' : 'Current User is not Vendor'}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your Company account'}
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
                data = {'message' : "Current User is not Vendor"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your Company account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


class LaptopSpecificationView(CreateAPIView):
    serializer_class  = LaptopSpecification

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
                data = {'message' : 'Current User is not Vendor'}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your Company account'}
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
                data = {'message' : "Current User is not Vendor"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your Company account'}
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
                data = {'message' : 'Current User is not Vendor'}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your Company account'}
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
                data = {'message' : "Current User is not Vendor"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your Company account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)








# ###########################   vendor orders (LIKE RECENT WISE ORDERS(DESC))   ##############################
# @transaction.atomic
# @api_view(['GET'])
# @csrf_exempt
# def vend_orders(request,token):
#     if request.method == 'GET':
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {"message" : "Invalid Access Token"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)

#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role = Role.objects.get(role='VENDOR')
#         vendorrole = role.role_id
#         roles = UserRole.objects.filter(role_id=vendorrole).filter(user_id=userdata)
#         if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     try:
#                         vp = Product.objects.get(user=userdata)
#                     except:
#                         return Response({"message":"Vendor had no products to order"},status=status.HTTP_404_NOT_FOUND)
#                     try:
#                         a = OrderItemHistory.objects.filter(product=vp.id).values('id','product').order_by('-id')
#                         datalist = []
#                     except:
#                         return Response([],status=status.HTTP_404_NOT_FOUND)
                    
#                     for i in a:
#                         try:
#                             prdata= Product.objects.get(id=i['product'])
#                         except:
#                             return Response({"message":"Product not found in product table"},status=status.HTTP_404_NOT_FOUND)
                        
#                         oritdata = OrderItemHistory.objects.get(id=i['id'])
#                         img = images.objects.get(id=i["product"])
#                         data = {  
#                             "product_id":prdata.id,
#                             "alias":prdata.alias,
#                             "title":prdata.title,
#                             "order_id":oritdata.id,
#                             "or_alias":oritdata.alias,
#                             "order_status":oritdata.order_status,
#                             "shipment_status":oritdata.shipment_status,
#                             "order_quantity":oritdata.quantity,
#                             "item_price":oritdata.item_price,
#                             "image":img.src
#                         }
#                         datalist.append(data)
#                     return Response(datalist,status=status.HTTP_200_OK)
#             else:
#                 data ={
#                     "warning" : "Vendor not assigned to this Role",
#                 }
#                 return Response(data, status=status.HTTP_404_NOT_FOUND)
#         else:
#             data = {"message":'Vendor is in In-Active, please Activate your company account'}
#             return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
#     else:
#         return Response({"message":"Method not allowed"},status=status.HTTP_400_BAD_REQUEST)
    


#####################    Vendor category filter   #################

class ven_categoryapi(CreateAPIView):
    serializer_class = CategoryBasedProductPagination

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
        role = Role.objects.get(role='VENDOR')
        vendorrole = role.role_id
        roles = UserRole.objects.filter(role_id=vendorrole).filter(user_id=userdata)
        if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data = request.data)
                    if serializer.is_valid(raise_exception=True):
                        pageno = serializer.validated_data['pageno']
                        category = serializer.validated_data['category']
                        if category=='':
                            return Response({"message":"Category Field is Empty"}, status=status.HTTP_401_UNAUTHORIZED)
                        else:
                            if (Category.objects.filter(category_name__icontains=category).exists()):
                                c= Category.objects.get(category_name__icontains=category)

                                product = Product.objects.filter(category_id=c.id,user=userdata).all().values()
                                datalist =[] 

                                for i in product:
                                    pro = Product.objects.get(id = i['id'])
                                    col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
                                    var = variants.objects.filter(id=i['id']).values()
                                    img = images.objects.filter(id=i['id']).values()
                                    t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
                                    
                                    data = {
                                        "id": pro.id,
                                        "alias":pro.alias,
                                        "title": pro.title,
                                        "description": pro.description, 
                                        "type": pro.type,
                                        "brand": pro.brand,
                                        "collection": col,
                                        "category": pro.category,
                                        "price": pro.price,
                                        "sale": pro.sale,
                                        "discount": pro.discount,
                                        "stock": pro.stock,
                                        "new": pro.new,
                                        "variants" : var,
                                        "images" : img,
                                        "tag":t
                                    }
                                    datalist.append(data)
                                try:
                                    paginator = Paginator(datalist,prperpage)
                                    page = request.GET.get("page",pageno)
                                    object_list = paginator.page(page)
                                    a = list(object_list)
                                    data1 = {
                                        "orders_data":a,
                                        "total_pages":paginator.num_pages,
                                        "products_per_page":prperpage,
                                        "total_products":paginator.count
                                    }
                                    return Response(data1, status=status.HTTP_200_OK)
                                except:
                                    return Response({"message":"Pagination Value Error"},status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({"message":"Invaild Category Name"}, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"message":"Invalid Field Name for Serializer"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {'message' : "Current User is not Vendor"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your Company account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
  
    



##########################################   Vendor colour filter   #################################################

class colour_api(CreateAPIView):
    serializer_class = seri_colour

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
        role = Role.objects.get(role='VENDOR')
        vendorrole = role.role_id
        roles = UserRole.objects.filter(role_id=vendorrole).filter(user_id=userdata)
        if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        sericolo = serializer.validated_data['colour']
                        pageno = serializer.validated_data['pageno']
                        a = variants.objects.filter(color__iexact=sericolo).values('id')
                        if(Product.objects.filter(id__in=a,user=userdata).exists()):
                            product = Product.objects.filter(id__in=a,user=userdata).all().values()
                            datalist =[] 
                            for i in product:
                                pro = Product.objects.get(id = i['id'])
                                col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
                                var = variants.objects.filter(id=i['id']).values()
                                img = images.objects.filter(id=i['id']).values()
                                t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
                                
                                data = {
                                    "id": pro.id,
                                    "alias":pro.alias,
                                    "title": pro.title,
                                    "description": pro.description, 
                                    "type": pro.type,
                                    "brand": pro.brand,
                                    "collection": col,
                                    "category": pro.category,
                                    "price": pro.price,
                                    "sale": pro.sale,
                                    "discount": pro.discount,
                                    "stock": pro.stock,
                                    "new": pro.new,
                                    "variants" : var,
                                    "images" : img,
                                    "tag":t
                                }
                                datalist.append(data)
                            try:
                                paginator = Paginator(datalist,prperpage)
                                page = request.GET.get("page",pageno)
                                object_list = paginator.page(page)
                                a = list(object_list)
                                data1 = {
                                    "product_data":a,
                                    "total_pages":paginator.num_pages,
                                    "products_per_page":prperpage,
                                    "total_products":paginator.count
                                }
                                return Response(data1, status=status.HTTP_200_OK)
                            except:
                                return Response({"message":"Pagination Value Error"},status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response([],status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"message":"Serializer is not valid"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to this Role",
                    "message" : "Activate your company account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'Vendor is in In-Active, please Activate your company account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)





######  check with the vendor data for search #######################
class ven_SearchAPIView(CreateAPIView):
    serializer_class = ven_search

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
        role = Role.objects.get(role='VENDOR')
        vendorrole = role.role_id
        roles = UserRole.objects.filter(role_id=vendorrole).filter(user_id=userdata)
        if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data = request.data)
                    if serializer.is_valid():
                        ab = serializer.validated_data['search_item']
                        productsearch = Product.objects.filter(title__icontains=ab,user=userdata).values('id') or Product.objects.filter(price__icontains=ab,user=userdata).values('id') or Product.objects.filter(brand__icontains=ab,user=userdata).values('id') or Product.objects.filter(description__icontains=ab,user=userdata).values('id') or Product.objects.filter(type__icontains=ab,user=userdata).values('id') or Product.objects.filter(category__icontains=ab,user=userdata).values('id') or Product.objects.filter(alias__icontains=ab,user=userdata).values('id')
                        secol = collection.objects.filter(collection__icontains=ab).values('id')
                        searchproduct = variants.objects.filter(size__icontains=ab).values('id') or variants.objects.filter(color__icontains=ab).values('id')
                        datalist = []
                        if productsearch.exists():
                            for i in productsearch:
                                a = Product.objects.get(id=i['id'])
                                b = collection.objects.filter(id=i['id']).values()
                                c = variants.objects.filter(id=i['id']).values()
                                d = images.objects.filter(id=i['id']).values()
                                data = {
                                    "id":a.id,
                                    "alias":a.alias,
                                    "title":a.title,
                                    "description":a.description,
                                    "brand":a.brand,
                                    "type":a.type,
                                    "category":a.category,
                                    "price":a.price,
                                    "stock":a.stock,
                                    "discount":a.discount,
                                    "sale":a.sale,
                                    "new":a.new,
                                    "collection":b,
                                    "variants":c,
                                    "images":d
                                }
                                datalist.append(data)
                            return Response(datalist,status=status.HTTP_200_OK)
                        elif(secol.exists()):
                            for i1 in secol:
                                try:
                                    a1 = Product.objects.filter(user=userdata,id=i1['id']).values('id')
                                except:
                                    return Response([],status=status.HTTP_404_NOT_FOUND)
                                for i in a1:
                                    a = Product.objects.get(id=i['id'])
                                    b = collection.objects.filter(id=i['id']).values()
                                    c = variants.objects.filter(id=i['id']).values()
                                    d = images.objects.filter(id=i['id']).values()
                                    data = {
                                        "id":a.id,
                                        "alias":a.alias,
                                        "title":a.title,
                                        "description":a.description,
                                        "brand":a.brand,
                                        "type":a.type,
                                        "category":a.category,
                                        "price":a.price,
                                        "stock":a.stock,
                                        "discount":a.discount,
                                        "sale":a.sale,
                                        "new":a.new,
                                        "collection":b,
                                        "variants":c,
                                        "images":d
                                    }
                                    datalist.append(data)
                            return Response(datalist,status=status.HTTP_200_OK)
                        elif(searchproduct.exists()):
                            for i1 in searchproduct:
                                try:
                                    a1 = Product.objects.filter(id=i1['id'],user=userdata).values('id')
                                except:
                                    return Response([],status=status.HTTP_404_NOT_FOUND)
                                for i in a1:
                                    a = Product.objects.get(id=i['id'])
                                    b = collection.objects.filter(id=i['id']).values()
                                    c = variants.objects.filter(id=i['id']).values()
                                    d = images.objects.filter(id=i['id']).values()
                                    data = {
                                        "id":a.id,
                                        "alias":a.alias,
                                        "title":a.title,
                                        "description":a.description,
                                        "brand":a.brand,
                                        "type":a.type,
                                        "category":a.category,
                                        "price":a.price,
                                        "stock":a.stock,
                                        "discount":a.discount,
                                        "sale":a.sale,
                                        "new":a.new,
                                        "collection":b,
                                        "variants":c,
                                        "images":d
                                    }
                                    datalist.append(data)
                            return Response(datalist,status=status.HTTP_200_OK)
                        elif(Category.objects.filter(category_name__icontains=ab).exists()):
                            categorysearch = Category.objects.get(category_name__icontains=ab)
                            products = Product.objects.filter(category_id=categorysearch.id).values('id')
                            for i1 in products:
                                try:
                                    a1 = Product.objects.filter(user=userdata,id=i1['id']).values('id')
                                except:
                                    return Response([],status=status.HTTP_404_NOT_FOUND)
                                for i in a1:
                                    a = Product.objects.get(id=i['id'])
                                    b = collection.objects.filter(id=i['id']).values()
                                    c = variants.objects.filter(id=i['id']).values()
                                    d = images.objects.filter(id=i['id']).values()
                                    data = {
                                        "id":a.id,
                                        "alias":a.alias,
                                        "title":a.title,
                                        "description":a.description,
                                        "brand":a.brand,
                                        "type":a.type,
                                        "category":a.category,
                                        "price":a.price,
                                        "stock":a.stock,
                                        "discount":a.discount,
                                        "sale":a.sale,
                                        "new":a.new,
                                        "collection":b,
                                        "variants":c,
                                        "images":d
                                    }
                                    datalist.append(data)
                            return Response(datalist,status=status.HTTP_200_OK)
                        else:
                            return Response([],status=status.HTTP_404_NOT_FOUND)
                    else:
                        data = {"message":'Serializer not valid'}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to this Role",
                    "message" : "Activate your company account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'Vendor is in In-Active, please Activate your company account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)



########################  vendor price_filter   ########################
class ven_price(CreateAPIView):
    serializer_class = price_seri

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
        role = Role.objects.get(role='VENDOR')
        vendorrole = role.role_id
        roles = UserRole.objects.filter(role_id=vendorrole).filter(user_id=userdata)
        if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        ser_min = serializer.validated_data['min_price']
                        ser_max = serializer.validated_data['max_price']
                        pr=Product.objects.filter(user=userdata).values('price','discount')
                        for i in pr:
                            pr1 = i['price']
                            pr2 = i['discount']
                            price1 = pr1-(pr1*pr2/100)
                        #######    Use the discount price while filtering in product table 
                        prod = Product.objects.filter(price__range=(ser_min,ser_max),user=userdata).values().all()
                        datalist=[]
                        for m in prod:
                            # data = {
                            #     "id":m['id']
                            # }
                            datalist.append(prod)
                        return Response(datalist,status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Serializer is not valid"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to this Role",
                    "message" : "Activate your company account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'Vendor is in In-Active, please Activate your company account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        



##########   vendor orders,sales count  ##################

@transaction.atomic
@api_view(['GET'])
@csrf_exempt
def ven_count(request,token):
    if request.method == 'GET':
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='VENDOR')
        vendorrole = role.role_id
        roles = UserRole.objects.filter(role_id=vendorrole).filter(user_id=userdata)
        if(CompanyProfile.objects.filter(user=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    prtb = Product.objects.filter(user=userdata).values('id')
                    datalist = []
                    prcn = prtb.aggregate(Count('id')).get('id__count')
                    for m in prtb:
                        ortb = OrderItemHistory.objects.filter(product=m['id'],order_status__iexact='order placed').values('id')
                        orcn = ortb.aggregate(Count('id')).get('id__count')
                        ortbl1 = OrderItemHistory.objects.filter(product=m['id'],order_status__iexact='inprogress').values('id')
                        orpncnt = ortbl1.aggregate(Count('id')).get('id__count')
                        data = {
                            "total_products":prcn,
                            "total_sales":orcn,
                            "pending_orders":orpncnt
                        }
                        datalist.append(data)
                        return Response(datalist,status=status.HTTP_200_OK)
            else:
                data ={
                    "warning" : "User not assigned to this Role",
                    "message" : "Activate your company account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'Vendor is in In-Active, please Activate your company account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_400_BAD_REQUEST)

