from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.auth import AuthToken
from store.models import User_profile
from .serializers import RegisterSerializer
import random
from django.core.mail import send_mail
from Ecomerce_project.settings import EMAIL_HOST_USER
from django.http import JsonResponse



@api_view(['POST'])
def login_api(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']

    _, token = AuthToken.objects.create(user)

    return Response (
        {
            'user_info' :{
                'id' : user.id,
                'username' : user.username,
                'email' : user.email,
                "mobile" : user.mobile
            },
            'token' : token
        }
    )

@api_view(['GET'])
def get_user_data(request):
    user = request.user

    if user.is_authenticated:
        return Response (
        {
            'user_info' :{
                'id' : user.id,
                'username' : user.username,
                'email' : user.email,
                'firstname' : user.first_name,
                'lastname' : user.last_name,
                'active' : user.is_active,
            },
        }
    )
        

    return Response({'error' : 'Not Authenticated'}, status=400)


@api_view(['POST'])
def register_api(request):
    serializer = RegisterSerializer(data = request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    generated_otp = random.randint(1000,9999)
    subject = 'OTP Verification is Pending'
    message = "Hello " + user.username +"," + " \n\n Welcome to Eshop  \n\n  " + f'Your One-Time Password { generated_otp}'
    recepient = user.email
    send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently = False)

    if generated_otp == int(input("Enter OTP")):
        user.save()
    else: 
        int(input("Enter Valid OTP"))

    _, token = AuthToken.objects.create(user)

    return Response (
        {
            'user_info' :{
                'id' : user.id,
                'username' : user.username,
                'email' : user.email,
                'password' : user.password,
                'mobile' : user.mobile
            },
            'token' : token
        }
    )

@api_view(['GET'])
def details(request):
    if request.method =='GET':
        # Creating a Object 
        user = User_profile.objects.all() 
        # Converting it into QuerySet 
        data = list(user.values())
        # returning it
        return JsonResponse(data,safe=False)