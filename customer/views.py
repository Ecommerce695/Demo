from django.db import transaction
from rest_framework.decorators import api_view
from .serializers import (RegisterSerializer,UpdatePasswordSerializer, ActivateAccountSerializer,UsernameSerializer, UserUpdateSerializer,useraddressdelete, 
                          Useremailserializer,Usermobileserializer,LoginSerializer, ResetActivationSerializer,Userotpactivateserializer,
                          ForgetPasswordSerializer,ConfirmPasswordSerializer,UserAddressSerializer,ca_products,
                          reviewserializer,WishlistSerializer,SearchSerializer,UpdateAddressSerializer,
                          ProductSerializer,PaginationSerializer,CategoryBasedProductPagination,GetEstDeliveryDate,OrderSerializer)
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from .models import (UserProfile,Account_Activation,UserRole, Role, Reset_Password,
                     avg_rating, AddressType,UserAddress,SaveForLater, Reviews, Search_History,Wishlist)
from rest_framework import views
from django.contrib.auth import authenticate, login as login1, logout
from knox.auth import AuthToken
from .models import KnoxAuthtoken
from datetime import datetime, timedelta
from pytz import utc 
import random,requests,json,geocoder
from django.utils.crypto import get_random_string
from django.contrib.sites.shortcuts import get_current_site 
from django_user_agents.utils import get_user_agent
from django.core.mail import send_mail
from Ecomerce_project import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Avg, Count
from rest_framework.generics import CreateAPIView
from super_admin.models import Product,collection,tags,images,variants,Category,CompanyProfile
from cart.models import Cart
from django.views.decorators.csrf import csrf_exempt
from order.models import Order, OrderItemHistory
from django.core.paginator import Paginator
from Ecomerce_project.settings import prperpage
from shipment.models import shipment
from payments.models import Transaction_table
from order.models import OrderItemHistory
import pytz,re


class RegisterView(APIView):
    serializer_class= RegisterSerializer

    @transaction.atomic()
    def post(self,request):
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
                unique_id = get_random_string(length=64)
                protocol ='http://'
                # current_site = get_current_site(request).domain
                current_site = '54.67.88.195/'
                api = 'core/activate_account/'
                Gotp = random.randint(10000,99999)
                message = "Thank you for registering with xShop.\nYour One-Time Password is {}\nTo activate your account, please click on the following url:\n {}{}{}{}\n".format(Gotp,protocol,current_site,api,unique_id)
                subject = "xShop Account Activation"
                from_email = settings.EMAIL_HOST_USER
                to_email = [email.lower()]
                send_mail(subject, message, from_email, to_email)

                aliass = get_random_string(length=10)
                serializer.save()
                u = UserProfile.objects.get(email = email.lower())
                if (UserProfile.objects.filter(alias=aliass).exists()):
                    aliass = get_random_string(length=10)
                    UserProfile.objects.filter(email=email.lower()).update(alias=aliass)
                else:
                    UserProfile.objects.filter(email=email.lower()).update(alias=aliass)
                
                Account_Activation.objects.create(user = u.id, key = unique_id, agent = current_site,otp=Gotp)
                role = Role.objects.get(role='USER')
                r_id = role.role_id
                user_role = UserRole.objects.create(role_id = r_id, user_id = u.id)
                user_role.save()

                data = {
                    "message" : "Account Activation Email Sent",
                    "email" : email.lower(),
                    "emailActivationToken"  : unique_id
                }
                return Response(data, status=status.HTTP_201_CREATED)
            except :
                return Response({"message":"Authentication Required"},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return Response({"message" :serializer.errors},status=status.HTTP_409_CONFLICT)    

class AccountActivateView(views.APIView):
    serializer_class = ActivateAccountSerializer

    @transaction.atomic()
    def put(self, request, token):
        try:
            token = Account_Activation.objects.get(key=token)
        except:
            return Response({"message" : "Invalid Token in URL"}, status=status.HTTP_404_NOT_FOUND)
        if token.expiry_date >= token.created_at:
            serializer = ActivateAccountSerializer(data = request.data)
            if serializer.is_valid(raise_exception=True):
                u_id = token.user
                otp_valid = token.otp
                otp = serializer.data['otp']

                if otp_valid ==otp:
                    UserProfile.objects.filter(id=u_id).update(is_active='True')
                    Account_Activation.objects.filter(user = u_id).delete()
                    return Response({"message" : "Account successfully activated"},status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Incorrect OTP, Please try again"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message":"Enter OTP"},status=status.HTTP_429_TOO_MANY_REQUESTS)
        else:
            return Response({"message" : "Activation Token/ OTP Expired"} , status=status.HTTP_401_UNAUTHORIZED)
        
    def post(self, request, token):
        try:
            token = Account_Activation.objects.get(key=token)
        except:
            return Response({"message" : "Invalid Token in URL"}, status=status.HTTP_404_NOT_FOUND)

        if token.expiry_date <= token.created_at:
            protocol ='http://'
            # current_site = get_current_site(request).domain
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
            Account_Activation.objects.filter(user = token.user).update(otp = Gotp, created_at = now, expiry_date=now + timedelta(days=2))
            return Response({"message" : "OTP has send again"})


class ResendActivationView(APIView):
    serializer_class = ResetActivationSerializer

    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            mail_id = serializer.data['email']

            if UserProfile.objects.filter(email=email).exists():


                name = UserProfile.objects.get(email = mail_id)
                u_id = name.id
                Account_Activation.objects.filter(user = u_id).delete()
                unique_id = get_random_string(length=64)
                # current_site = get_current_site(request).domain
                protocol ='http://'
                current_site = '54.67.88.195/'
                api = 'core/activate_account/'

                Gotp = random.randint(10000,99999)
                message = "Your Account Activation One-Time Password is {}\nTo activate your account, please click on the following url:\n {}{}{}{}\n".format(Gotp,protocol,current_site,api,unique_id)
                subject = "xShop Account Reset"
                from_email = settings.EMAIL_HOST_USER
                to_email = [email]
                send_mail(subject, message, from_email, to_email)
                Account_Activation.objects.create(user = u_id, key = unique_id, otp=Gotp)
                data = {
                    "message" : "Account Activation Email Sent",
                    "email" : serializer.data['email'],
                    "emailActivationToken"  : unique_id
                }
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                return Response({"message":"This Email is Not Registered"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"message":"Missing Value"}, status=status.HTTP_401_UNAUTHORIZED)


class LoginApiView(views.APIView):
    serializer_class = LoginSerializer

    @transaction.atomic()
    def post(self, request):
        serializer = LoginSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            username  = serializer.data['username']
            password = serializer.data['password']
            if (UserProfile.objects.filter(username__icontains=username)) or (UserProfile.objects.filter(email=username)):
                if(UserProfile.objects.filter(username__icontains=username, is_active='True') or UserProfile.objects.filter(email__icontains=username, is_active='True')):
                    try:
                        data = UserProfile.objects.get(email__icontains=username)
                        try:
                            user = authenticate(username=data, password=password)
                            # KnoxAuthtoken.objects.filter(user=data.id).delete()
                            _, token = AuthToken.objects.create(user)
                        except:
                            return Response({"message":"Incorrect Password"}, status=status.HTTP_401_UNAUTHORIZED)
                    except:
                        data = UserProfile.objects.get(username__iexact=username)
                        try:
                            user = authenticate(username=data, password=password)
                            # KnoxAuthtoken.objects.filter(user=data.id).delete()
                            _, token = AuthToken.objects.create(user)
                        except:
                            return Response({"message":"Incorrect Password"}, status=status.HTTP_401_UNAUTHORIZED)      
                    KnoxAuthtoken.objects.filter(expiry__lte=datetime.now(utc)).delete()
                    if user is not None:
                        user1 = user.id
                        login1(request, user)
                        userrole = UserRole.objects.filter(user_id=user1).values('role_id')
                        roles_list=[]
                        for i in userrole:
                            role = i['role_id']
                            roles_list.append(role)
                        
                        if 3 in roles_list:
                            user_role=3
                        elif 2 in roles_list:
                            user_role=2
                        elif 1 in roles_list:
                            user_role=1
                        else:
                            user_role=4
                        data = ({
                            "accessToken":token,
                            "role_id":user_role
                        })
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        return Response({"message" : "User doesn't exixts"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    data = {"message":'Account is in In-Active, please Activate your account'}
                    return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                data = {"message" :"Username Not Found"}
                return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"message" : "Enter Username or Password"}, status=status.HTTP_400_BAD_REQUEST)


#################################  GET User details #######################
class UserRoleDetailsView(views.APIView):

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
        userrole = UserRole.objects.filter(user_id=userdata).values('role_id')
        for i in userrole:
            role = i['role_id']
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if(token1.expiry < datetime.now(utc)):
                KnoxAuthtoken.objects.filter(user=user).delete()
                data = {"message":'Session Expired, Please login again'}
                return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
            else:
                data = {
                    "username":usertable.username,
                    "mobile_number":usertable.mobile_number,
                    "email":usertable.email,
                    "first_name":usertable.first_name,
                    "last_name":usertable.last_name,
                    "is_active" : usertable.is_active,
                    "role":role
                }
                return Response(data, status=status.HTTP_200_OK)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

class AccountDeactivateView(views.APIView):

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
       
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if(token1.expiry < datetime.now(utc)):
                KnoxAuthtoken.objects.filter(user=user).delete()
                data = {"message":'Session Expired, Please login again'}
                return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
            else:
                user= UserProfile.objects.get(id=userdata)
                UserProfile.objects.filter(id=userdata).update(is_active=False)
                # UserRole.objects.filter(user_id=userdata).delete()
                message = "Your Account is De-activated Successfully"
                subject = "Account Deactivated"
                from_email = settings.EMAIL_HOST_USER
                to_email = [user.email]
                send_mail(subject, message, from_email, to_email)
                return Response({"message":"Account deactivated Successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"User is in In-Active, please Activate your account"})


@api_view(["DELETE"])
def logout_api(request,token):
    try:
        KnoxAuthtoken.objects.get(token_key=token).delete()
        logout(request)
        return Response({"message":"Logout Success"})
    except:
        return Response({'message':"Invalid Access Token"},status=status.HTTP_400_BAD_REQUEST)


##################   User First and Last Name update   ###################
class NamesUpdateAPI(CreateAPIView):
    serializer_class = UserUpdateSerializer

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
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1).filter(user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        firstname = serializer.validated_data['first_name']
                        lastname = serializer.validated_data['last_name']
                        if lastname=='':
                            lname = ''
                        else:
                            lname = lastname

                        UserProfile.objects.filter(id=userdata).update(first_name=firstname, last_name=lname)
                        return Response({"message":"Updated successfully"}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


##################   User email update ######################
class CustomerEmailView(CreateAPIView):
    serializer_class = Useremailserializer

    @transaction.atomic
    def put(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        roles = Role.objects.get(role='USER')
        userrole = roles.role_id
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        table1 = UserProfile.objects.filter(id=userdata, is_active='True')
        if(UserRole.objects.filter(role_id=userrole, user_id=userdata)):
            if table1.exists():
                if(token1.expiry < datetime.now(utc)):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(usertable, data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializerdata = serializer.validated_data['email']
                        if(UserProfile.objects.filter(email=serializerdata).exists()):
                            return Response({"message":"Email already exists, try another "}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            Account_Activation.objects.filter(email=serializerdata).delete()
                            unique_id = get_random_string(length=64)
                            # current_site = get_current_site(request).domain
                            protocol ='http://'
                            current_site = '54.67.88.195/'
                            api = 'core/activate_account/'

                            Gotp = random.randint(10000,99999)
                            message = "Hi {},\n\n Request For Email Update.\nYour One-Time Password is {}\nTo Change your Email, please click on the following url:\n {}{}{}{}\n".format(usertable.username,Gotp,protocol,current_site,api,unique_id)
                            subject = "xShop Account Activation"
                            from_email = settings.EMAIL_HOST_USER
                            to_email = [serializerdata]
                            send_mail(subject, message, from_email, to_email)
                            Account_Activation.objects.create(user = userdata, key = unique_id, otp=Gotp, email=serializerdata)

                            data = {
                                "message" : "Requested for Email Update", 
                                "emailActivationToken": unique_id
                                }
                            return Response(data, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message" : "Account is in In-Active, please Activate your account"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message" : "User not assigned to Role",}, status=status.HTTP_406_NOT_ACCEPTABLE)


#################   User email update Verification   #############
class CustomerEmailUpdateView(CreateAPIView):
    serializer_class = Userotpactivateserializer

    @transaction.atomic
    def put(self,request,token,act_token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
        try:
            token = Account_Activation.objects.get(key=act_token)
        except:
            data = {"message" : "Invalid verification Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        roles = Role.objects.get(role='USER')
        userrole = roles.role_id
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        table1 = UserProfile.objects.filter(id=userdata, is_active='True')
        if(UserRole.objects.filter(role_id=userrole, user_id=userdata)):
            if table1.exists():
                if(token1.expiry < datetime.now(utc)):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(usertable, data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        u_id = token.user
                        otp_valid = token.otp
                        otp = serializer.validated_data['otp']
                        if otp_valid ==otp:
                            UserProfile.objects.filter(id=u_id).update(email=token.email)
                            Account_Activation.objects.filter(user = u_id).delete()
                            return Response({"message" : "Email Updated Successfully"},status=status.HTTP_200_OK)
                        else:
                            return Response({"message": "Incorrect OTP, Please try again"}, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message" : "Account is in In-Active, please Activate your account"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message" : "User not assigned to Role",}, status=status.HTTP_406_NOT_ACCEPTABLE)


##################   User mobile update ######################
class CustomerMobileView(CreateAPIView):
    serializer_class = Usermobileserializer

    @transaction.atomic
    def put(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        roles = Role.objects.get(role='USER')
        userrole = roles.role_id
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        table1 = UserProfile.objects.filter(id=userdata, is_active='True')
        if(UserRole.objects.filter(role_id=userrole, user_id=userdata)):
            if table1.exists():
                if(token1.expiry < datetime.now(utc)):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(usertable, data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializerdata = serializer.validated_data['mobile_number']
                        if(UserProfile.objects.filter(mobile_number=serializerdata).exists()):
                            return Response({"message":"Mobile Number already exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            if len(str(serializerdata)) <10 or len(str(serializerdata)) >10:
                                return Response({"message":"mobile number should be 10 digits"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                UserProfile.objects.filter(id=userdata).update(mobile_number=serializerdata)
                                data = {
                                    "message":"Mobile Number Updated Successfully "
                                    }
                                return Response(data, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message" : "Account is in In-Active, please Activate your account"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message" : "User not assigned to Role",}, status=status.HTTP_406_NOT_ACCEPTABLE)

########################## Customer Username Update API
class UsernameUpdateAPI(CreateAPIView):
    serializer_class = UsernameSerializer

    @transaction.atomic
    def put(self,request,token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {
                    "message" : "Invalid Access Token"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        roles = Role.objects.get(role='USER')
        userrole = roles.role_id
        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        table1 = UserProfile.objects.filter(id=userdata, is_active='True')
        if(UserRole.objects.filter(role_id=userrole, user_id=userdata)):
            if table1.exists():
                if(token1.expiry < datetime.now(utc)):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(usertable, data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializerdata = serializer.validated_data['username']
                        if(UserProfile.objects.filter(username=serializerdata).exists()):
                            return Response({"message":"Username already exists, try another "}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            UserProfile.objects.filter(id=userdata).update(username=serializerdata)
                            data = {
                                "message":"Username Updated Successfully "
                                }
                            return Response(data, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {"message" : "Account is in In-Active, please Activate your account"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message" : "User not assigned to Role",}, status=status.HTTP_406_NOT_ACCEPTABLE)

class ForgotPasswordView(APIView):
    serializer_class = ForgetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            mail_id = serializer.data['email']

            name = UserProfile.objects.get(email = mail_id)
            u_id = name.id
            Reset_Password.objects.filter(user=u_id).delete()

            unique_id = get_random_string(length=32)
            # current_site = get_current_site(request).domain
            current_site = '54.67.88.195/'
            protocol ='http://'
            interface = get_user_agent(request)
            Reset_Password.objects.create(user = u_id, key=unique_id, ip_address=current_site, user_agent=interface)
            subject = "xShop Reset Password Assistance"

            api = '/core/reset/password/'
            send_mail(
                subject = subject,
                message = "Hi {}, \n\nThere was a request to change your password! \n\nIf you did not make this request then please ignore this email. \n\nYour password reset link \n {}{}{}{}".format(name.username,protocol,current_site, api, unique_id),
                from_email = settings.EMAIL_HOST_USER,
                recipient_list=[email]
            )
            return Response({"message" : "Password reset email sent"})
        else:
            return Response (serializer.error, status=status.HTTP_401_UNAUTHORIZED)


class ConfirmPasswordView(APIView):
    serializer_class = ConfirmPasswordSerializer

    def put(self, request, token):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            token = Reset_Password.objects.get(key=token)
            name = token.user
            use = UserProfile.objects.get(id =name)
            pwd = serializer.data['password']

            UserProfile.objects.filter(id = name).update(password=make_password(pwd))
            Reset_Password.objects.filter(user=use.id).delete()
            return Response({"message" : "Password changed Successfully, Please Login"}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Password Fields didn't Match"}, status=status.HTTP_400_BAD_REQUEST)

# Update/Change Password 
class UpdatePasswordAPI(CreateAPIView):
    serializer_class = UpdatePasswordSerializer

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
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if roles.exists():
            if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
            else:
                serializer = self.get_serializer(data = request.data)
                if serializer.is_valid(raise_exception=True):
                    current_pwd = serializer.validated_data['current_password']
                    new_pwd = serializer.validated_data['new_password']
                    confirm_pwd = serializer.validated_data['confirm_password']
                    if check_password(current_pwd, usertable.password):
                        if len(new_pwd) <8 or len(confirm_pwd)<8:
                             return Response({"message":"Check Password Length"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            if new_pwd==confirm_pwd:
                                UserProfile.objects.filter(id=usertable.id).update(password=make_password(new_pwd))
                                return Response({"message":"Successfully Changed Your Password"}, status=status.HTTP_200_OK)
                            else:
                                return Response({"message":"There was an error with your Password combination"}, status=status.HTTP_406_NOT_ACCEPTABLE)                        
                    else:
                        return Response({"message":"Incorrect Current Password"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    return Response({"message":"Missing Field Values"}, status=status.HTTP_204_NO_CONTENT)


##########  User address   #########
class AddressView(CreateAPIView):
    serializer_class = UserAddressSerializer

    @transaction.atomic
    def post(self, request,token, *args, **kwargs):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1, user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializerdata = serializer.validated_data['mobile']
                        serializertype = serializer.validated_data['type']
                        serializername= serializer.validated_data['name']
                        serializeraddress = serializer.validated_data['address']
                        serializernearby = serializer.validated_data['landmark']
                        serializerstreetno = serializer.validated_data['area']
                        serializercity = serializer.validated_data['city']
                        serializerstate= serializer.validated_data['state']
                        serializercountry = serializer.validated_data['country']
                        serializerpostalcode = serializer.validated_data['pincode']
                        serializerdefault = serializer.validated_data['is_default']

                        if(serializercountry=='in' or serializercountry=='India' or serializercountry=='INDIA' or serializercountry=='india' or serializercountry=='IN'):                
                            if(AddressType.objects.filter(type__iexact=serializertype).exists()):
                                a1 = AddressType.objects.get(type=serializertype.upper())
                                if UserAddress.objects.filter(user=usertable).exists():
                                    if serializerdefault ==True:
                                        UserAddress.objects.filter(user=usertable,is_default=True).update(is_default=False)
                                        table = UserAddress.objects.create(name=serializername, user=usertable, type=a1,
                                        mobile=serializerdata, address=serializeraddress, landmark=serializernearby, area=serializerstreetno,
                                        city=serializercity, state=serializerstate, country='INDIA', pincode=serializerpostalcode, is_default=serializerdefault)
                                        table.save()
                                        return Response({"message":"Address added Successfully"},status=status.HTTP_200_OK)
                                    else:
                                        table = UserAddress.objects.create(name=serializername, user=usertable, type=a1,
                                        mobile=serializerdata, address=serializeraddress, landmark=serializernearby, area=serializerstreetno,
                                        city=serializercity, state=serializerstate, country='INDIA', pincode=serializerpostalcode, is_default=serializerdefault)
                                        table.save()
                                        return Response({"message":"Address added Successfully"},status=status.HTTP_200_OK)
                                else:
                                    UserAddress.objects.create(name=serializername, user=usertable, type=a1,
                                    mobile=serializerdata, address=serializeraddress, landmark=serializernearby, area=serializerstreetno,
                                    city=serializercity, state=serializerstate, country=serializercountry, pincode=serializerpostalcode, is_default=True)
                                return Response({"message" : "Address added Successfully"},status=status.HTTP_200_OK)
                            else:
                                return Response({"message":"Address type not found"}, status=status.HTTP_404_NOT_FOUND)
                        elif(serializercountry=='US' or serializercountry=='UNITED STATES' or serializercountry=='United States' or serializercountry=='united states' or serializercountry=='us'):
                            if(AddressType.objects.filter(type__iexact=serializertype).exists()):
                                a1 = AddressType.objects.get(type=serializertype.upper())
                                if UserAddress.objects.filter(user=usertable).exists():
                                    if serializerdefault ==True:
                                        UserAddress.objects.filter(user=usertable,is_default=True).update(is_default=False)
                                        table = UserAddress.objects.create(name=serializername, user=usertable, type=a1,
                                        mobile=serializerdata, address=serializeraddress, landmark=serializernearby, area=serializerstreetno,
                                        city=serializercity, state=serializerstate, country='UNITED STATES', pincode=serializerpostalcode, is_default=serializerdefault)
                                        table.save()
                                        return Response({"message":"Address added Successfully"},status=status.HTTP_200_OK)
                                    else:
                                        table = UserAddress.objects.create(name=serializername, user=usertable, type=a1,
                                        mobile=serializerdata, address=serializeraddress, landmark=serializernearby, area=serializerstreetno,
                                        city=serializercity, state=serializerstate, country='UNITED STATES', pincode=serializerpostalcode, is_default=serializerdefault)
                                        table.save()
                                        return Response({"message":"Address added Successfully"},status=status.HTTP_200_OK)
                                else:
                                    UserAddress.objects.create(name=serializername, user=usertable, type=a1,
                                    mobile=serializerdata, address=serializeraddress, landmark=serializernearby, area=serializerstreetno,
                                    city=serializercity, state=serializerstate, country=serializercountry, pincode=serializerpostalcode, is_default=True)
                                return Response({"message" : "Address added Successfully"},status=status.HTTP_200_OK)
                            else:
                                return Response({"message":"Address type not found"}, status=status.HTTP_404_NOT_FOUND)
                        else:
                            return Response({"message":"Country not allowed to add"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({"message" : "Serializer not valid"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                "warning" : "User not assigned to Role, can't add Address",
                "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


    # @transaction.atomic
    # def put(self, request, token):
    #     try:
    #         token1 = KnoxAuthtoken.objects.get(token_key=token)
    #     except:
    #         data = {"message" : "Invalid Access Token"}
    #         return Response(data, status=status.HTTP_404_NOT_FOUND)

    #     user = token1.user_id
    #     usertable = UserProfile.objects.get(id=user)
    #     userdata = usertable.id
    #     role = Role.objects.get(role='USER')
    #     role1 = role.role_id
    #     roles = UserRole.objects.filter(role_id=role1, user_id=userdata)
    #     if(UserProfile.objects.filter(id=userdata, is_active='True')):
    #         if roles.exists():
    #             if token1.expiry < datetime.now(utc):
    #                 KnoxAuthtoken.objects.filter(user=user).delete()
    #                 data = {"message":"Session Expired, Please login again"}
    #                 return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
    #             else:                 
    #                 serializer = self.get_serializer(usertable, data = request.data)
    #                 if serializer.is_valid():
    #                     name = serializer.validated_data['name']
    #                     type1 = serializer.validated_data['type']
    #                     mobile = serializer.validated_data['mobile']
    #                     address = serializer.validated_data['address']
    #                     nearby = serializer.validated_data['landmark']
    #                     streetno = serializer.validated_data['area']
    #                     city = serializer.validated_data['city']
    #                     state = serializer.validated_data['state']
    #                     country = serializer.validated_data['country']
    #                     pincode = serializer.validated_data['pincode']

    #                     if(UserAddress.objects.filter(user=userdata, type=type1.upper()).exists()):
    #                         UserAddress.objects.filter(user=userdata, type=type1.upper()).update(
    #                             mobile=mobile, address=address, landmark=nearby,
    #                             area=streetno, city=city, state=state, 
    #                             country=country, pincode=pincode, name=name
    #                         )
    #                         return Response({"message":"Updated Sucessfully"},status=status.HTTP_200_OK)
    #                     else:
    #                         return Response({"message":"User had not address on this address type"}, status=status.HTTP_404_NOT_FOUND)
    #                 else:
    #                     data = {"message":'Serializer not valid'}
    #                     return Response(data, status=status.HTTP_400_BAD_REQUEST)
    #         else:
    #             data ={
    #                 "warning" : "User not assigned to Role",
    #                 "message" : "Activate your account"
    #             }
    #             return Response(data, status=status.HTTP_404_NOT_FOUND)
    #     else:
    #         data = {"message":'User is in In-Active, please Activate your account'}
    #         return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


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
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    data = UserAddress.objects.filter(user=userdata)
                    if data.exists():
                        data1 = list(data.values())
                        return Response(data1, status=status.HTTP_200_OK)
                    else:
                        data ={
                            "message" :"No Address associated with current user",
                            "warning" : "Add Address"
                        }
                        return Response(data,status=status.HTTP_204_NO_CONTENT)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

class UpdateAddressView(APIView):
    serializer_class = UpdateAddressSerializer

    @transaction.atomic
    def put(self, request, token,aid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1, user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:                 
                    serializer = UpdateAddressSerializer(usertable,data = request.data)
                    if serializer.is_valid():
                        name = serializer.validated_data['name']
                        type1 = serializer.validated_data['type']
                        mobile = serializer.validated_data['mobile']
                        address = serializer.validated_data['address']
                        nearby = serializer.validated_data['landmark']
                        streetno = serializer.validated_data['area']
                        city = serializer.validated_data['city']
                        state = serializer.validated_data['state']
                        serializercountry = serializer.validated_data['country']
                        pincode = serializer.validated_data['pincode']
                        default = serializer.validated_data['is_default']

                        if(UserAddress.objects.filter(user=userdata,id=aid).exists()):
                            if(serializercountry=='in' or serializercountry=='India' or serializercountry=='INDIA' or serializercountry=='india' or serializercountry=='IN'):
                                if default==True:
                                    UserAddress.objects.filter(user=usertable,is_default=True).update(is_default=False)
                                    UserAddress.objects.filter(user=userdata, id=aid).update(
                                        mobile=mobile, address=address, landmark=nearby,type=type1,
                                        area=streetno, city=city, state=state, 
                                        country='INDIA',pincode=pincode, name=name, is_default=True
                                    )
                                    return Response({"message":"Updated Successfully"},status=status.HTTP_200_OK)
                                else:
                                    UserAddress.objects.filter(user=userdata, id=aid).update(
                                        mobile=mobile, address=address, landmark=nearby,type=type1,
                                        area=streetno, city=city, state=state, 
                                        country='INDIA', pincode=pincode, name=name)
                                    return Response({"message":"Updated Sucessfully"},status=status.HTTP_200_OK)
                            elif(serializercountry=='US' or serializercountry=='UNITED STATES' or serializercountry=='United States' or serializercountry=='united states' or serializercountry=='us'):
                                if default==True:
                                    UserAddress.objects.filter(user=usertable,is_default=True).update(is_default=False)
                                    UserAddress.objects.filter(user=userdata, id=aid).update(
                                        mobile=mobile, address=address, landmark=nearby,type=type1,
                                        area=streetno, city=city, state=state, 
                                        country='UNITED STATES',pincode=pincode, name=name, is_default=True
                                    )
                                    return Response({"message":"Updated Successfully"},status=status.HTTP_200_OK)
                                else:
                                    UserAddress.objects.filter(user=userdata, id=aid).update(
                                        mobile=mobile, address=address, landmark=nearby,type=type1,
                                        area=streetno, city=city, state=state, 
                                        country='UNITED STATES', pincode=pincode, name=name)
                                    return Response({"message":"Updated Sucessfully"},status=status.HTTP_200_OK)
                            else:
                                return Response({"message":"Country not allowed to update"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            return Response({"message":"Address with id not Found"}, status=status.HTTP_404_NOT_FOUND)
                    else:
                        data = {"message":'Serializer not valid'}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        
    @transaction.atomic
    def delete(self, request, token,aid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1, user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:                 
                    if UserAddress.objects.filter(user=usertable,id=aid).exists():
                        UserAddress.objects.filter(user=usertable,id=aid).delete()
                        return Response({"message":"Address Deleted Successful"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Address with id not Found"},status=status.HTTP_404_NOT_FOUND)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


@transaction.atomic
@api_view(['GET'])
def ProductsAPI(request):
    serializer_class = ProductSerializer
    if request.method == 'GET':

        time_zone = pytz.timezone('UTC')
        a = time_zone.localize(datetime.now())
        b = a.astimezone(pytz.utc)
        uptabl = Transaction_table.objects.filter(expired_at__lte=b,status='ON HOLD').values('orderitem')
        for i in uptabl:
            Transaction_table.objects.filter(orderitem=i['orderitem']).update(status='UNPAID',updated_at=datetime.now())
            OrderItemHistory.objects.filter(id=i['orderitem']).update(order_status='FAILED',updated_at=datetime.now())

        product = Product.objects.filter(is_deleted=False).values('id')
        datalist =[]

        serializer = serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            postal = serializer.validated_data['pincode']

            for i in product:
                pro = Product.objects.get(id = i['id'])
                col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
                var = variants.objects.filter(id=i['id']).values()
                img = images.objects.filter(id=i['id']).values()
                t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
                cp = CompanyProfile.objects.get(user=pro.user)

                if postal=='':
                    pass
                else:
                    pincode=postal
                
                    url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"

                    payload=json.dumps({
                        "pickup_postcode":cp.pincode, # Pickup Location
                        "delivery_postcode":pincode,  # Delivery Location
                        "cod":"0",  # 1 for COD and 0 for Prepaid orders
                        "weight":pro.weight # Product Weight in Kgs
                    })
                    headers = {
                    'Content-Type': 'application/json',
                    'Authorization': settings.SHIPMENT_TOKEN
                    }

                    response = requests.request("GET", url, headers=headers, data=payload)
                    data=response.json()
                    if data['status']==401 or response.status_code==401:
                        return Response({"message":"Shipment token expired"},status=status.HTTP_401_UNAUTHORIZED)
                    if response.status_code and data['status']==200:
                        i=1
                        date_list=[]
                        date_list.clear()                
                        charger_list=[]
                        for i in range(len(data['data']['available_courier_companies'])):
                            date = data['data']['available_courier_companies'][i]['etd']
                            shipping_chargers = data['data']['available_courier_companies'][i]["freight_charge"]
                            i=i+1
                            date_list.append(date)
                            charger_list.append(shipping_chargers)
                    else:
                        return Response(response.text)

                try:
                    data = {
                        "id": pro.id,
                        "title": pro.title,
                        "description": pro.description, 
                        "type": pro.type,
                        "brand": pro.brand,
                        "collection": col,
                        "sale": pro.sale,
                        "new": pro.new,
                        # "user_id": userdata,
                        "category_id": pro.category_id,
                        "category": pro.category,
                        "rating": pro.rating,
                        "is_active": pro.is_active,
                        "alias": pro.alias,
                        "dimensions": pro.dimensions,
                        "weight": pro.weight,
                        "status": pro.status,
                        "is_charged": pro.is_charged,
                        "shipping_charges": pro.shipping_charges,
                        "other_charges": pro.other_charges,
                        "is_wattanty": pro.is_wattanty,
                        "warranty_months": pro.warranty_months,
                        "warranty_src": pro.warranty_src,
                        "warranty_path": pro.warranty_path.name,
                        "created_at": pro.created_at.date(),
                        "updated_at" : pro.updated_at.date(),
                        "new": pro.new,
                        "tags":t,
                        "variants" : var,
                        "images" : img,
                        "sold_by" : cp.org_name,
                        "weight": pro.weight,
                        "dimensions":pro.dimensions,
                        "estimated_delivery_date" : max(date_list),
                    }
                except:
                    data = {
                        "id": pro.id,
                        "title": pro.title,
                        "description": pro.description, 
                        "type": pro.type,
                        "brand": pro.brand,
                        "collection": col,
                        "sale": pro.sale,
                        "new": pro.new,
                        # "user_id": userdata,
                        "category_id": pro.category_id,
                        "category": pro.category,
                        "rating": pro.rating,
                        "is_active": pro.is_active,
                        "alias": pro.alias,
                        "dimensions": pro.dimensions,
                        "weight": pro.weight,
                        "status": pro.status,
                        "is_charged": pro.is_charged,
                        "shipping_charges": pro.shipping_charges,
                        "other_charges": pro.other_charges,
                        "is_wattanty": pro.is_wattanty,
                        "warranty_months": pro.warranty_months,
                        "warranty_src": pro.warranty_src,
                        "warranty_path": pro.warranty_path.name,
                        "created_at": pro.created_at.date(),
                        "updated_at" : pro.updated_at.date(),
                        "new": pro.new,
                        "tags":t,
                        "variants" : var,
                        "images" : img,
                        "sold_by" : cp.org_name,
                        "weight": pro.weight,
                        "dimensions":pro.dimensions
                    }
                datalist.append(data)
            return Response(datalist, status=status.HTTP_200_OK)
        else:
         return Response({"message":"Enter Pincode"},status=status.HTTP_406_NOT_ACCEPTABLE)
    else:   
        return Response({"message":"Method Not Allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

###############    Whishlist   #######################
class WishlistView(CreateAPIView):
    serializer_class = WishlistSerializer

    @transaction.atomic
    def post(self, request, token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data = request.data)
                    if serializer.is_valid():
                        seri = serializer.validated_data['id']
                        if(variants.objects.filter(id=seri).exists()):
                            variant = variants.objects.get(id=seri)
                            product = Product.objects.get(id=seri)

                            tb2 = Wishlist.objects.filter(user=userdata, product=seri)
                            if tb2.exists():
                                data = {"message":'product already exists in wishlist'}
                                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
                            else:
                                img = images.objects.get(id=variant.id)
                                tb3 = Wishlist.objects.create(
                                    user = usertable,
                                    product = product,
                                    price = product.price,
                                    title = product.title,
                                    category = product.category,
                                    brand = product.brand,
                                    discount = product.discount,
                                    variant = variant.id,
                                    sku = variant.sku,
                                    size = variant.size,
                                    color = variant.color,
                                    src = img.src,
                                    type = product.type
                                )
                                data = {"message":'Added to wishlist'}
                                return Response(data, status=status.HTTP_200_OK)
                        else:
                            return Response({"message":"Product not exists"}, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"message":"Serializer is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "message" : "Incorrect Username and Password",
                    "warning" : "User not assigned to Role, can't login"
                }
                return Response(data, status=status.HTTP_401_UNAUTHORIZED)
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
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    data = Wishlist.objects.filter(user=userdata)
                    if data.exists():
                        product = Wishlist.objects.filter(user=userdata).values('product')
                        datalist =[] 

                        for i in product:
                            pro = Product.objects.get(id = i['product'])
                        
                            col = collection.objects.filter(id=i["product"]).values_list('collection',flat=True)
                            var = variants.objects.filter(id=i["product"]).values()
                            img = images.objects.filter(id=i["product"]).values()
                            t = tags.objects.filter(id=i["product"]).values_list('tags',flat=True)
                            
                            data = {
                                "id": pro.id,
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
                        return Response(datalist, status=status.HTTP_200_OK)
                    else:
                        return Response([],status=status.HTTP_200_OK)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

        

class WishlistGetApi(CreateAPIView):
    serializer_class = PaginationSerializer

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
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        pageno = serializer.validated_data['pageno']
                        data = Wishlist.objects.filter(user=userdata)
                        l=[]
                        if data.exists():
                            product = Wishlist.objects.filter(user=userdata).values('product').order_by('-id')
                            datalist =[] 

                            for i in product:
                                try:
                                    pro = Product.objects.get(id = i['product'])
                                
                                    col = collection.objects.filter(id=i["product"]).values_list('collection',flat=True)
                                    var = variants.objects.filter(id=i["product"]).values()
                                    img = images.objects.filter(id=i["product"]).values()
                                    t = tags.objects.filter(id=i["product"]).values_list('tags',flat=True)
                                    
                                    data = {
                                        "id": pro.id,
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
                                    paginator = Paginator(datalist,prperpage)
                                    page = request.GET.get("page",pageno)
                                    object_list = paginator.page(page)
                                    a = list(object_list)
                                    data1 = {
                                        "wishlist_data":a,
                                        "total_pages":paginator.num_pages,
                                        "products_per_page":prperpage,
                                        "total_products":paginator.count
                                    }
                                except:
                                    pass
                            try:
                                return Response(data1, status=status.HTTP_200_OK)
                            except:
                                return Response({"message":"value error"},status=status.HTTP_400_BAD_REQUEST)
                        else:
                            paginator = Paginator(l,prperpage)
                            page = request.GET.get("page",pageno)
                            object_list = paginator.page(page)
                            a = list(object_list)
                            data1 = {
                                "wishlist_data":a,
                                "total_pages":paginator.num_pages,
                                "products_per_page":prperpage,
                                "total_products":paginator.count
                            }
                            return Response(data1,status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"value error"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)



@csrf_exempt
@transaction.atomic
def wishlistdelete(request, token,pid):
    try:
        token1 = KnoxAuthtoken.objects.get(token_key=token)
    except:
        data = {"message" : "Invalid Access Token"}
        return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)

    user = token1.user_id
    usertable = UserProfile.objects.get(id=user)
    userdata = usertable.id
    role = Role.objects.get(role='USER')
    role1 = role.role_id
    roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
    if request.method=='DELETE':
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return JsonResponse(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:                   
                    if(Wishlist.objects.filter(user=userdata,product=pid).exists()):
                        Wishlist.objects.filter(user=userdata, product=pid).delete() 
                        data = {"message":'Removed successfully'}
                        return JsonResponse(data, status=status.HTTP_200_OK)
                    else:
                        data = {"message":'Data not exists'}
                        return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return JsonResponse(data, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return JsonResponse({"message":"Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

#############  Product review ############
class ReviewProductsView(CreateAPIView):
    serializer_class = reviewserializer

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
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializercomments = serializer.validated_data['comments']
                        serializerrating = serializer.validated_data['rating']
                        serializerimages = serializer.validated_data['images']
                        serializerorder = serializer.validated_data['orderitem_id']
                        if(serializerrating>5):
                            return Response({"message":"Rating can accetable upto 5"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        elif(Reviews.objects.filter(user=userdata,oritemid=serializerorder).exists()):
                            return Response({"message":'Review already exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            if(OrderItemHistory.objects.filter(user=userdata,id=serializerorder,order_status='ORDER PLACED',shipment_status='DELIVERED').exists()):
                                serializerproduct = OrderItemHistory.objects.filter(user=userdata,id=serializerorder).values('product')
                                for i in serializerproduct:
                                    a = i['product']
                                    tableproduct = Product.objects.get(id=a)
                                    table = Reviews.objects.create(comments=serializercomments, oritemid=serializerorder,
                                    rating=serializerrating, user=usertable, product=tableproduct, src='http://50.18.24.167/media/product/images/'+str(serializerimages), images=serializerimages,created_at=datetime.now())
                                    table.save()
                                    ###   Single product_id
                                    tbprod = Reviews.objects.filter(product=a).values_list('rating')
                                    tbupdate = tbprod.aggregate(Avg('rating')).get('rating__avg')
                                    Product.objects.filter(id=a).update(rating=tbupdate)
                                    productname = Product.objects.filter(id=a).values('title')
                                    for n in productname:
                                        prname = n['title']
                                    productid = Product.objects.filter(title=prname).values('id')
                                    ###   Multiple product_ids
                                    reviewsfilter = Reviews.objects.filter(product__in=productid).values('rating')
                                    queryavg = reviewsfilter.aggregate(Avg('rating')).get('rating__avg')
                                    if(avg_rating.objects.filter(product_name=prname)):
                                        avg_rating.objects.filter(product_name=prname).update(rating=queryavg)
                                    else:
                                        tablerating = avg_rating.objects.create(product_name=prname, rating=queryavg)
                                        tablerating.save()
                                    data = {"message":'Review taken successfully'}
                                    return Response(data, status=status.HTTP_200_OK)
                            else:
                                return Response({"message":"order not placed/undelivered"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        data = {"message":'Serializer not valid'}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


    
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
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializercomments = serializer.validated_data['comments']
                        serializerrating = serializer.validated_data['rating']
                        serializerimages = serializer.validated_data['images']
                        serializerorder = serializer.validated_data['orderitem_id']
                        if(serializerrating>5):
                            return Response({"message":"Rating can accecpatable upto 5"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        elif(Reviews.objects.filter(user=userdata,oritemid=serializerorder).exists()):
                            Reviews.objects.filter(user=userdata,oritemid=serializerorder).update(comments=serializercomments,rating=serializerrating,images=serializerimages,
                                                                                                  src='http://50.18.24.167/media/product/images/'+str(serializerimages))
                            prdata = Reviews.objects.filter(user=userdata,oritemid=serializerorder).values('product')
                            for i in prdata:
                                a = i['product']
                                ###   Single product_id
                                tbprod = Reviews.objects.filter(product=a).values_list('rating')
                                tbupdate = tbprod.aggregate(Avg('rating')).get('rating__avg')
                                Product.objects.filter(id=a).update(rating=tbupdate)
                                productname = Product.objects.filter(id=a).values('title')
                                for n in productname:
                                    prname = n['title']
                                productid = Product.objects.filter(title=prname).values('id')
                                ###   Multiple product_ids
                                reviewsfilter = Reviews.objects.filter(product__in=productid).values('rating')
                                queryavg = reviewsfilter.aggregate(Avg('rating')).get('rating__avg')
                                if(avg_rating.objects.filter(product_name=prname)):
                                    avg_rating.objects.filter(product_name=prname).update(rating=queryavg)
                                else:
                                    tablerating = avg_rating.objects.create(product_name=prname, rating=queryavg)
                                    tablerating.save()
                                data = {"message":'Review updated successfully'}
                                return Response(data, status=status.HTTP_200_OK)
                            # return Response({"Review updated sucessfully"},status=status.HTTP_200_OK)
                        else:
                            return Response({"User has no review data to edit in this order"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        data = {"message":'Serializer not valid'}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)



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
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    tablecheck = Reviews.objects.filter(user=userdata)
                    if tablecheck.exists():
                        table = Reviews.objects.filter(user=userdata).values().all()
                        return Response(table, status=status.HTTP_200_OK)
                    else:
                        data = {"message":'User had no reviews to show'}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)          
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        


#############   Search Histoty    #############

class SearchAPIView(CreateAPIView):
    serializer_class = SearchSerializer

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
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data = request.data)
                    if serializer.is_valid():
                        ab = serializer.validated_data['search_item']
                        pageno = serializer.validated_data['pageno']
                        Search_History.objects.create(user=usertable, search_item=ab)
                        productsearch = Product.objects.filter(title__icontains=ab).values('id') or Product.objects.filter(price__icontains=ab).values('id') or Product.objects.filter(brand__icontains=ab).values('id') or Product.objects.filter(description__icontains=ab).values('id') or Product.objects.filter(type__icontains=ab).values('id') or Product.objects.filter(category__icontains=ab).values('id') or Product.objects.filter(alias__icontains=ab).values('id')
                        secol = collection.objects.filter(collection__icontains=ab).values('id')
                        searchproduct = variants.objects.filter(size__icontains=ab).values('id') or variants.objects.filter(color__icontains=ab).values('id')
                        datalist = []
                        if productsearch.exists():
                            for i in productsearch:
                                try:
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
                                    paginator = Paginator(datalist,prperpage)
                                    page = request.GET.get("page",pageno)
                                    object_list = paginator.page(page)
                                    a = list(object_list)
                                    data1 = {
                                        "products_data":a,
                                        "total_pages":paginator.num_pages,
                                        "products_per_page":prperpage,
                                        "total_products":paginator.count
                                    }
                                except:
                                    pass
                            try:
                                return Response(data1,status=status.HTTP_200_OK)
                            except:
                                return Response({"message":"value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        elif(secol.exists()):
                            for i in secol:
                                try:
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
                                    paginator = Paginator(datalist,prperpage)
                                    page = request.GET.get("page",pageno)
                                    object_list = paginator.page(page)
                                    a = list(object_list)
                                    data1 = {
                                        "products_data":a,
                                        "total_pages":paginator.num_pages,
                                        "products_per_page":prperpage,
                                        "total_products":paginator.count
                                    }
                                except:
                                    pass
                            try:
                                return Response(data1,status=status.HTTP_200_OK)
                            except:
                                return Response({"message":"value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        elif(searchproduct.exists()):
                            for i in searchproduct:
                                try:
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
                                    paginator = Paginator(datalist,prperpage)
                                    page = request.GET.get("page",pageno)
                                    object_list = paginator.page(page)
                                    a = list(object_list)
                                    data1 = {
                                        "products_data":a,
                                        "total_pages":paginator.num_pages,
                                        "products_per_page":prperpage,
                                        "total_products":paginator.count
                                    }
                                except:
                                    pass
                            try:
                                return Response(data1,status=status.HTTP_200_OK)
                            except:
                                return Response({"message":"value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        elif(Category.objects.filter(category_name__icontains=ab).exists()):
                            categorysearch = Category.objects.get(category_name__icontains=ab)
                            products = Product.objects.filter(category_id=categorysearch.id).values('id')
                            for i in products:
                                try:
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
                                    paginator = Paginator(datalist,prperpage)
                                    page = request.GET.get("page",pageno)
                                    object_list = paginator.page(page)
                                    a = list(object_list)
                                    data1 = {
                                        "products_data":a,
                                        "total_pages":paginator.num_pages,
                                        "products_per_page":prperpage,
                                        "total_products":paginator.count
                                    }
                                except:
                                    pass
                            try:
                                return Response(data1,status=status.HTTP_200_OK)
                            except:
                                return Response({"message":"value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            return Response({"message":"Not exists"},status=status.HTTP_404_NOT_FOUND)
                    else:
                        data = {"message":'Serializer not valid'}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)





#######################   Latest Products   ########################

class LatestProductsView(CreateAPIView):
    serializer_class = PaginationSerializer

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
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        pageno = serializer.validated_data['pageno']
                        products = Product.objects.all().order_by('-id').values('id')
                        datalist=[]
                        for i in products:  
                            try: 
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
                                paginator = Paginator(datalist,prperpage)
                                page = request.GET.get("page",pageno)
                                object_list = paginator.page(page)
                                a = list(object_list)
                                data1 = {
                                    "products_data":a,
                                    "total_pages":paginator.num_pages,
                                    "products_per_page":prperpage,
                                    "total_products":paginator.count
                                }
                            except:
                                pass
                        try:
                            return Response(data1,status=status.HTTP_200_OK)
                        except:
                            return Response({"message":"value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({"message":"value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)




##############   Similar Products  ############################

class SimilarProductsView(CreateAPIView):
    serializer_class = PaginationSerializer

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
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        pageno = serializer.validated_data['pageno']
                        if(Search_History.objects.filter(user=userdata).exists()):
                            custid = Search_History.objects.filter(user=userdata).order_by('-created_at')[:1]
                            search = Search_History.objects.filter(id=custid).latest('search_item')
                            searchproduct = search.search_item
                            productsearch = Product.objects.filter(title__icontains=searchproduct).values('id') or Product.objects.filter(price__icontains=searchproduct).values('id') or Product.objects.filter(brand__icontains=searchproduct).values('id') or Product.objects.filter(description__icontains=searchproduct).values('id') or Product.objects.filter(type__icontains=searchproduct).values('id') or Product.objects.filter(category__icontains=searchproduct).values('id')
                            secol = collection.objects.filter(collection__icontains=searchproduct).values('id')
                            searchproduct = variants.objects.filter(size__icontains=searchproduct).values('id') or variants.objects.filter(color__icontains=searchproduct).values('id')
                            datalist = []
                            if productsearch.exists():
                                for i in productsearch:
                                    try:
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
                                        paginator = Paginator(datalist,prperpage)
                                        page = request.GET.get("page",pageno)
                                        object_list = paginator.page(page)
                                        a = list(object_list)
                                        data1 = {
                                            "products_data":a,
                                            "total_pages":paginator.num_pages,
                                            "products_per_page":prperpage,
                                            "total_products":paginator.count
                                        }
                                    except:
                                        pass
                                try:
                                    return Response(data1,status=status.HTTP_200_OK)
                                except:
                                    return Response({"message":"value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                            elif(secol.exists()):
                                for i in secol:
                                    try:
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
                                        paginator = Paginator(datalist,prperpage)
                                        page = request.GET.get("page",pageno)
                                        object_list = paginator.page(page)
                                        a = list(object_list)
                                        data1 = {
                                            "products_data":a,
                                            "total_pages":paginator.num_pages,
                                            "products_per_page":prperpage,
                                            "total_products":paginator.count
                                        }
                                    except:
                                        pass
                                try:
                                    return Response(data1,status=status.HTTP_200_OK)
                                except:
                                    return Response({"message":"value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                            elif(searchproduct.exists()):
                                for i in searchproduct:
                                    try:
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
                                        paginator = Paginator(datalist,prperpage)
                                        page = request.GET.get("page",pageno)
                                        object_list = paginator.page(page)
                                        a = list(object_list)
                                        data1 = {
                                            "products_data":a,
                                            "total_pages":paginator.num_pages,
                                            "products_per_page":prperpage,
                                            "total_products":paginator.count
                                        }
                                    except:
                                        pass
                                try:
                                    return Response(data1,status=status.HTTP_200_OK)
                                except:
                                    return Response({"message":"value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                            else:
                                categorysearch = Category.objects.get(category_name__icontains=searchproduct)
                                products = Product.objects.filter(category_id=categorysearch.id).values('id')
                                for i in products:
                                    try:
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
                                        paginator = Paginator(datalist,prperpage)
                                        page = request.GET.get("page",pageno)
                                        object_list = paginator.page(page)
                                        a = list(object_list)
                                        data1 = {
                                            "products_data":a,
                                            "total_pages":paginator.num_pages,
                                            "products_per_page":prperpage,
                                            "total_products":paginator.count
                                        }
                                    except:
                                        pass
                                try:
                                    return Response(data1,status=status.HTTP_200_OK)
                                except:
                                    return Response({"message":"value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            return Response({"message":"Data not exists in recent search"}, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"message":"value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)




##############   Top_rated products  #######################

class TopRatedProductsView(CreateAPIView):
    serializer_class = PaginationSerializer

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
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        pageno = serializer.validated_data['pageno']
                        if(avg_rating.objects.filter(rating__gte=4).exists()):
                            products = avg_rating.objects.filter(rating__gte=4).values('product_name')
                            prid = Product.objects.filter(title__in=products).values('id')
                            datalist=[]
                            for i in prid:
                                try:
                                    pro = Product.objects.get(id = i['id'])
                                    col = collection.objects.filter(id=i["id"]).values_list('collection',flat=True)
                                    var = variants.objects.filter(id=i["id"]).values()
                                    img = images.objects.filter(id=i["id"]).values()
                                    t = tags.objects.filter(id=i["id"]).values_list('tags',flat=True)
                                    data = {
                                        "id": pro.id,
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
                                    paginator = Paginator(datalist,prperpage)
                                    page = request.GET.get("page",pageno)
                                    object_list = paginator.page(page)
                                    a = list(object_list)
                                    data1 = {
                                        "wishlist_data":a,
                                        "total_pages":paginator.num_pages,
                                        "products_per_page":prperpage,
                                        "total_products":paginator.count
                                    }
                                except:
                                    pass
                            try:
                                return Response(data1,status=status.HTTP_200_OK)
                            except:
                                return Response({"message":"value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            return Response([],status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"message":"serializer value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


class SaveForLaterAPI(CreateAPIView):

    @transaction.atomic
    def post(self, request, token,pid):

        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    p = Cart.objects.filter(product=pid,user=usertable)
                    if p.exists():
                        pd = Cart.objects.get(product=pid,user=usertable)
                        p_id =Product.objects.get(id=pid)

                        if (SaveForLater.objects.filter(product=p_id.id, user=usertable).exists()):
                            SaveForLater.objects.filter(product=p_id,user=usertable).update(quantity=pd.quantity)
                            Cart.objects.filter(product=pid).delete()
                            Product.objects.filter(id=pid).update(stock = p_id.stock+pd.quantity)
                            return Response({"message":"Product Moved to Save Later"},status=status.HTTP_200_OK)
                        else:
                            SaveForLater.objects.create(product= p_id,user = usertable,quantity=pd.quantity)
                            Cart.objects.filter(product=pid).delete()
                            Product.objects.filter(id=pid).update(stock = p_id.stock+pd.quantity)
                        return Response({"message":"Product Moved to Save Later"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message" :"Product Does't exists"},status=status.HTTP_404_NOT_FOUND)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

    
    @transaction.atomic
    def delete(self, request, token,pid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    s=SaveForLater.objects.filter(product=pid)
                    if s.exists():
                        s=SaveForLater.objects.get(product=pid)
                        p=Product.objects.get(id=pid)
                        SaveForLater.objects.filter(product=pid).filter(user=usertable).delete()
                        return Response({"message" : "Product Removed from SaveForLater"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Product Doesn't Exists"},status=status.HTTP_404_NOT_FOUND)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

class MoveToCartAPI(CreateAPIView):

    @transaction.atomic
    def put(self, request, token,pid):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    s=SaveForLater.objects.filter(product=pid)
                    if s.exists():
                        s=SaveForLater.objects.get(product=pid)
                        p=Product.objects.get(id=pid)
                        if (Cart.objects.filter(user=usertable,product=p.id).exists()):
                            c =Cart.objects.get(product=p.id)
                            total_qty =c.quantity+s.quantity
                            Cart.objects.filter(user=usertable,product=p.id).update(quantity=total_qty,price=p.discount,cart_value=p.discount*total_qty)
                            Product.objects.filter(id=p.id).update(stock=p.stock-total_qty)
                            SaveForLater.objects.filter(product=p.id, user=usertable).delete()
                            return Response({"message":"Product Move to Cart"}, status=status.HTTP_200_OK)
                        else:
                            Cart.objects.create(product=p, user=usertable,quantity=s.quantity,price=p.discount,cart_value=p.discount*s.quantity)
                            SaveForLater.objects.filter(product=p.id, user=usertable).delete()
                            Product.objects.filter(id=p.id).update(stock=p.stock-s.quantity)
                            return Response({"message":"Product Move to Cart"}, status=status.HTTP_200_OK)
                    else:
                        return Response(status=status.HTTP_400_BAD_REQUEST)  
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE) 


class ListSaveLaterProductAPI(CreateAPIView):

    @transaction.atomic
    def get(self, request, token):
        try:
            token1 = KnoxAuthtoken.objects.get(token_key=token)
        except:
            data = {"message" : "Invalid Access Token"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = token1.user_id
        usertable = UserProfile.objects.get(id=user)
        userdata = usertable.id
        role = Role.objects.get(role='USER')
        role1 = role.role_id
        roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":"Session Expired, Please login again"}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    sfl = SaveForLater.objects.filter(user=userdata)
                    data = list(sfl.values())
                    return Response(data, status=status.HTTP_200_OK)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

@transaction.atomic
@api_view(['GET'])
def CategoryBasedProductsAPI(request):
    serializer_class = CategoryBasedProductPagination
    if request.method == 'GET':

        serializer = serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            pageno = serializer.validated_data['pageno']
            category = serializer.validated_data['category']

            if category=='':
                return Response({"message":"Category Field is Empty"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if (Category.objects.filter(category_name__icontains=category).exists()):
                    c= Category.objects.get(category_name__icontains=category)

                    product = Product.objects.filter(category_id=c.id).all().values()
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
                return Response({"message":"Invaild Category Name"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message":"Invalid Field Name for Serializer"},status=status.HTTP_400_BAD_REQUEST)
    return Response({"message":"Method Not Allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

# class LaptopCategoryAPI(APIView):
#     @transaction.atomic
#     def get(self,request,token):
#         try:
#             token1 = KnoxAuthtoken.objects.get(token_key=token)
#         except:
#             data = {"message" : "Invalid Access Token"}
#             return Response(data, status=status.HTTP_404_NOT_FOUND)

#         user = token1.user_id
#         usertable = UserProfile.objects.get(id=user)
#         userdata = usertable.id
#         role = Role.objects.get(role='USER')
#         role1 = role.role_id
#         roles = UserRole.objects.filter(role_id=role1,user_id=userdata)
#         if(UserProfile.objects.filter(id=userdata, is_active='True')):
#             if roles.exists():
#                 if token1.expiry < datetime.now(utc):
#                     KnoxAuthtoken.objects.filter(user=user).delete()
#                     data = {"message":'Session Expired, Please login again'}
#                     return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
#                 else:
#                     serializer = self.get_serializer(data=request.data)
#                     if serializer.is_valid():
#                         pageno = serializer.validated_data['pageno']

#                         if (Category.objects.filter(category_name__iexact='Laptops').exists()):
#                             c= Category.objects.get(category_name='Laptops')

#                             product = Product.objects.filter(category_id=c.id).all().values()
#                             datalist =[] 

#                             for i in product:
#                                 pro = Product.objects.get(id = i['id'])
#                                 col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
#                                 var = variants.objects.filter(id=i['id']).values()
#                                 img = images.objects.filter(id=i['id']).values()
#                                 t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
                                
#                                 data = {
#                                     "id": pro.id,
#                                     "alias":pro.alias,
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
#                                     "variants" : var,
#                                     "images" : img,
#                                     "tag":t
#                                 }
#                                 datalist.append(data)
#                                 paginator = Paginator(datalist,prperpage)
#                                 page = request.GET.get("page",pageno)
#                                 object_list = paginator.page(page)
#                                 a = list(object_list)
#                                 data1 = {
#                                     "orders_data":a,
#                                     "total_pages":paginator.num_pages,
#                                     "products_per_page":prperpage,
#                                     "total_products":paginator.count
#                                 }
#                             return Response(data1, status=status.HTTP_200_OK)
                    
#         else: 
#             return Response({"message":"Category Doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        
#     return Response({"message":"Method Not Allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)


# @transaction.atomic
# @api_view(['GET'])
# def WatchCategoryAPI(request):
#     if request.method == 'GET':

#         if (Category.objects.filter(category_name__iexact='Watches').exists()):
#             c= Category.objects.get(category_name='Watches')

#             product = Product.objects.filter(category_id=c.id).all().values()
#             datalist =[] 
#             for i in product:
#                 pro = Product.objects.get(id = i['id'])
#                 col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
#                 var = variants.objects.filter(id=i['id']).values()
#                 img = images.objects.filter(id=i['id']).values()
#                 t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
                
#                 data = {
#                     "id": pro.id,
#                     "alias":pro.alias,
#                     "title": pro.title,
#                     "description": pro.description, 
#                     "type": pro.type,
#                     "brand": pro.brand,
#                     "collection": col,
#                     "category": pro.category,
#                     "price": pro.price,
#                     "sale": pro.sale,
#                     "discount": pro.discount,
#                     "stock": pro.stock,
#                     "new": pro.new,
#                     "variants" : var,
#                     "images" : img,
#                     "tag":t
#                 }
#                 datalist.append(data)
#                 paginator = Paginator(datalist,prperpage)
#                 page = request.GET.get("page",pageno)
#                 object_list = paginator.page(page)
#                 a = list(object_list)
#                 data1 = {
#                     "orders_data":a,
#                     "total_pages":paginator.num_pages,
#                     "products_per_page":prperpage,
#                     "total_products":paginator.count
#                 }
#             return Response(data, status=status.HTTP_200_OK)
    
#         else: 
#             return Response({"message":"Category Doesn't exists"}, status=status.HTTP_404_NOT_FOUND)
#     return Response({"message":"Method Not Allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)



class myorders(CreateAPIView):
    serializer_class = PaginationSerializer

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
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        pageno = serializer.validated_data['pageno']
                        l=[]
                        if(OrderItemHistory.objects.filter(user=uid).exists()):
                            a = OrderItemHistory.objects.filter(user=uid).values('id','product').order_by('-id')
                            datalist = []
                            for i in a:
                                try:
                                    prdata= Product.objects.get(id=i['product'])
                                    oritdata = OrderItemHistory.objects.get(id=i['id'])
                                    img = images.objects.get(id=i["product"])

                                    if oritdata.shipment_status=='' and oritdata.order_status=='INPROGRESS':
                                        shipment_status=''
                                    elif oritdata.shipment_status=='NEW' and oritdata.order_status=='ORDER PLACED':
                                        shipment_status='PICKUP PENDING'
                                    elif oritdata.shipment_status=='PICKUP SCHEDULED' or oritdata.shipment_status=='PICKUP BOOKED' or oritdata.shipment_status=='OUT FOR PICKUP' or oritdata.shipment_status=='IN TRANSIT' or oritdata.shipment_status=='PICKED UP' or oritdata.shipment_status=='PICKED':
                                        shipment_status='IN TRANSIT'
                                    elif oritdata.shipment_status=='DELIVERED' and oritdata.order_status=='ORDER PLACED':
                                        shipment_status='DELIVERED'
                                    elif oritdata.shipment_status=='CANCELLATION REQUESTED' or oritdata.order_status=='CANCELLED' or oritdata.shipment_status =='CANCELLED':
                                        shipment_status='CANCELLED'
                                    elif oritdata.order_status=='RETURNED':
                                        shipment_status='RETURNED'
                                    else :
                                        shipment_status='NA'
                                    try:
                                        ship =shipment.objects.get(order_item_id=oritdata.id)
                                        shipment_id=ship.shipment_id
                                    except:
                                        shipment_id=''

                                    if oritdata.shipment_status =='CANCELLED' or oritdata.shipment_status=='CANCELLATION REQUESTED':
                                        order_status='CANCELLED'
                                    else:
                                        order_status=oritdata.order_status
                                    
                                    data = {  
                                        "order_id" :oritdata.alias,
                                        "order_item_id" :oritdata.id,
                                        "parent_order_id":oritdata.order,
                                        "product_id":prdata.id,
                                        "title":prdata.title,
                                        "order_status":order_status,
                                        "shipment_status":shipment_status,
                                        "order_quantity":oritdata.quantity,
                                        "item_price":oritdata.item_price,
                                        "image":img.src,
                                        "shipment_id" : shipment_id
                                    }
                                    datalist.append(data)         
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
                                except:
                                    pass
                            try:
                                return Response(data1,status=status.HTTP_200_OK)
                            except:
                                return Response({"message":"page value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
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
                            return Response(data1,status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"serialier value error"},status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST) 




############################   count of orders, wishlist    ########################

@transaction.atomic
@api_view(['GET'])
@csrf_exempt
def orderscount(request,token):
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
                    usor = OrderItemHistory.objects.filter(user=uid).values('id')
                    uscnt = usor.aggregate(Count('id')).get('id__count')
                    a1 = OrderItemHistory.objects.filter(user=uid,order_status__iexact='inprogress').values('id')
                    uscnt1 = a1.aggregate(Count('id')).get('id__count')
                    b1 = Wishlist.objects.filter(user=uid).values('id')
                    b12 = b1.aggregate(Count('id')).get('id__count')
                    data={
                        "total_orders":uscnt,
                        "pending_orders":uscnt1,
                        "wishlist_count":b12
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
        return Response({"message":"Method not allowed"},status=status.HTTP_400_BAD_REQUEST)

class EstimatedDeliveryDateOfProduct(CreateAPIView):
    serializer_class = GetEstDeliveryDate

    @transaction.atomic
    def put(self,request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            postal = serializer.validated_data['pincode']
            product = serializer.validated_data['product_id']
            if len(str(postal))==6:
                if Product.objects.filter(id=product).exists():
                    pro = Product.objects.get(id = product)
                    cp = CompanyProfile.objects.get(user=pro.user)

                    url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"
                    payload=json.dumps({
                        "pickup_postcode":cp.pincode, # Pickup Location
                        "delivery_postcode":postal,  # Delivery Location
                        "cod":"0",  # 1 for COD and 0 for Prepaid orders
                        "weight":pro.weight # Product Weight in Kgs
                    })
                    headers = {
                    'Content-Type': 'application/json',
                    'Authorization': settings.SHIPMENT_TOKEN
                    }
                    response = requests.request("GET", url, headers=headers, data=payload)
                    data=response.json()
                    if data['status']==200:
                        i=1
                        date_list=[]
                        date_list.clear()                
                        charger_list=[]
                        for i in range(len(data['data']['available_courier_companies'])):
                            date = data['data']['available_courier_companies'][i]['etd']
                            shipping_chargers = data['data']['available_courier_companies'][i]["freight_charge"]
                            i=i+1
                            date_list.append(date)
                            charger_list.append(shipping_chargers)
                        result = {
                            "product_id":pro.id,
                            "estimated_delivery_date" : max(date_list)
                        }
                        return Response(result, status=status.HTTP_200_OK)
                    elif data['status']==404:
                        return Response({'message': 'Delivery postcode not serviceable'},status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"message":"Something went wrong"},status=status.HTTP_400_BAD_REQUEST)
                return Response({"message":"Invalid Product ID"},status=status.HTTP_406_NOT_ACCEPTABLE)
            return Response({'message':"Length mismatch"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"Serializer error"},status=status.HTTP_406_NOT_ACCEPTABLE)



@transaction.atomic
@api_view(['GET'])
def ProductsDetailsAPI(request,p_id):
    if request.method == 'GET':
        product = Product.objects.filter(id=int(p_id)).values('id')
        if product.exists():
            reviewlist = []
            for i in product:
                pro = Product.objects.get(id = i['id'])
                col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
                var = variants.objects.filter(id=i['id']).values()
                img = images.objects.filter(id=i['id']).values()
                t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
                cp = CompanyProfile.objects.get(user=pro.user)
                usre = Reviews.objects.filter(product=i['id']).values('user','comments','rating','src','created_at','product')
                for n in usre:
                    ustb=UserProfile.objects.get(id=n['user'])
                    data1 = {
                        "username":ustb.username,
                        "product_id":n['product'],
                        "rating":n['rating'],
                        "comments":n['comments'],
                        "images":n['src'],
                        "created_at":n['created_at'].date()
                    }
                    reviewlist.append(data1)
                data = {
                    "id": pro.id,
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
                    "weight":pro.weight,
                    "dimensions":pro.dimensions,
                    "variants" : var,
                    "images" : img,
                    "tag":t,
                    "Rating":pro.rating,
                    "review":reviewlist,
                    "sold_by" : cp.org_name,
                    "is_deleted":pro.is_deleted
                }       
            return Response(data, status=status.HTTP_200_OK)
        return Response({"message":"Invalid Product ID"},status=status.HTTP_400_BAD_REQUEST)        
    return Response({"message":"Method Not Allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ViewOrderDetailPage(CreateAPIView):
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
                    # orderitem
                    serializer = self.serializer_class(data = request.data)
                    if serializer.is_valid(raise_exception=True):
                        item_id = serializer.validated_data['orderitem']
                        if OrderItemHistory.objects.filter(id=item_id,user=uid).exists():
                            ord = OrderItemHistory.objects.get(id=item_id)
                            o = Order.objects.get(id=ord.order)
                            product = Product.objects.get(id=ord.product)
                            company = CompanyProfile.objects.get(user=product.user)
                            customer = UserAddress.objects.get(id=o.delivery)
                            us = UserProfile.objects.get(id=uid)
                            img = images.objects.get(id=product.id)
                            variant= variants.objects.get(id=product.id) 
                            
                            try:
                                ship =shipment.objects.get(order_item_id=ord.id)
                                url = "https://apiv2.shiprocket.in/v1/external/courier/track/shipment/"+str(ship.shipment_id)
                                payload={}
                                headers = {
                                'Content-Type': 'application/json',
                                'Authorization': settings.SHIPMENT_TOKEN
                                }

                                response = requests.request("GET", url, headers=headers, data=payload)
                                data=response.json()
                                list=[]
                                if response.status_code==200 and data['tracking_data']['track_status']==1:
                                    shipment_track_activities = {
                                        "track":data['tracking_data']['shipment_track_activities'],
                                        "url":data['tracking_data']['track_url']
                                    }
                                    list.append(shipment_track_activities)
                                elif response.status_code==200 and data['tracking_data']['track_status']==0:
                                    message=[]
                                    list.append(message)
                                elif response.status_code==401 or data['status_code']==401:
                                    pass
                                else:
                                    pass
                            except:
                                list=[]

                            # try:
                            #     url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"
                            #     payload=json.dumps({
                            #         "pickup_postcode":company.pincode, # Pickup Location
                            #         "delivery_postcode":customer.pincode,  # Delivery Location
                            #         "cod":"0",  # 1 for COD and 0 for Prepaid orders
                            #         "weight":product.weight # Product Weight in Kgs
                            #     })
                            #     headers = {
                            #     'Content-Type': 'application/json',
                            #     'Authorization': settings.SHIPMENT_TOKEN
                            #     }
                            #     response = requests.request("GET", url, headers=headers, data=payload)
                            #     data=response.json()
                            #     if data['status']==200:
                            #         i=1
                            #         date_list=[]
                            #         for i in range(len(data['data']['available_courier_companies'])):
                            #             date = data['data']['available_courier_companies'][i]['etd']
                            #             i=i+1
                            #             date_list.append(date)
                            #     date_object = datetime.strptime(max(date_list), "%b %d, %Y")
                            
                            #     if date_object.date()<=ord.delivery_date.date():
                            #         estimated_delivery_date=ord.delivery_date.date()
                            #     else:
                            #         estimated_delivery_date=max(date_list)
                            # except:
                            #     if datetime.today().date() >ord.delivery_date:
                            #         estimated_delivery_date=ord.delivery_date.date()
                            #     else:
                            #         estimated_delivery_date=max(date_list)

                            total_price=ord.item_price*ord.quantity
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
                                "shipping_details":list,
                                # "estimated_delivery":estimated_delivery_date
                            }
                            return Response(data,status.HTTP_200_OK)
                        return Response({'message':'Order Item Not Found'},status=status.HTTP_404_NOT_FOUND)
                    return Response(serializer.errors)
            else:
                data ={
                    "warning" : "User not assigned to Role",
                    "message" : "Activate your account"
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)