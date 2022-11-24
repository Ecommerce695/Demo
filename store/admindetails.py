from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.db import transaction
from store.models import Role, UserProfile, UserRole, OrgProfile, Product, Category, KnoxAuthtoken
from rest_framework.response import Response
from store.serializers import Adminregisterserializer, AdminLoginSerializer
from rest_framework import generics
from knox.models import AuthToken
from django.http import HttpResponse
from datetime import datetime,timedelta
from pytz import utc






########################    Admin registeration    ##############################

class AdminRegisterAPI(generics.GenericAPIView):
    serializer_class = Adminregisterserializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
        "user": "Success"          # use , for error
        #"token": Token.objects.create(user)[1]
        })

    def get(self,request,*args, **kwargs):
        list1 = UserProfile.objects.all()
        #list1 = registerpage.objects.filter(user_id=id)
        serializer = Adminregisterserializer(list1, many=True)
        return Response(serializer.data)



#######################  Admin login    ##################################

class AdminloginAPI(generics.GenericAPIView):
    serializer_class = AdminLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        _, token = AuthToken.objects.create(user)

        data = ({
            "user": "success",
            "token": token
        })
        return Response(data)




######   Admin organisation details   #######

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
def Admin_org_register(request,token):
    if request.method == 'POST':
        try:
            token = KnoxAuthtoken.objects.get(token_key = token)
            id1 = token.user_id
            use = UserProfile.objects.get(id=id1)
            user = use.id
            roles = Role.objects.get(role='ADMIN')
            roles1 = roles.role_id
            data = UserRole.objects.filter(role_id=roles1, user_id=user)
            if data.exists():
                if token.expiry < datetime.now(utc):
                        KnoxAuthtoken.objects.filter(user=user).delete()
                        return HttpResponse("Session Expired, Please login again")
                else:
                    org_name = request.POST['org_name']
                    email = request.POST['email']
                    mobile = request.POST['mobile']
                    tax_id = request.POST['tax_id']
                    description = request.POST['description']
                    address = request.POST['address']
                    city = request.POST['city']
                    state = request.POST['state']
                    country = request.POST['country']
                    pincode = request.POST['pincode']

                    vendor = OrgProfile.objects.create(
                        user = use,
                        org_name = org_name,
                        email = email,
                        mobile = mobile,
                        tax_id = tax_id,
                        description = description,
                        address = address,
                        city = city,
                        state = state,
                        country = country,
                        pincode = pincode
                    )
                    vendor.save()
                    return Response (
                        {
                            "200 ok"
                        }
                    )
            else:
                return HttpResponse("Error")
        except:
            return HttpResponse("Session expired")




#####   Admin adding products   ########

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
def adminproductsadd(request,token,):
    if request.method == 'POST':
        try:
            token = KnoxAuthtoken.objects.get(token_key = token)
            id1 = token.user_id
            use = UserProfile.objects.get(id=id1)
            user = use.id
            roles = Role.objects.get(role='ADMIN')
            roles1 = roles.role_id
            data = UserRole.objects.filter(role_id=roles1, user_id=user)
            if data.exists():
                if token.expiry < datetime.now(utc):
                        KnoxAuthtoken.objects.filter(user=user).delete()
                        return HttpResponse("Session Expired, Please login again")
                else:
                    category_name = request.POST['category_name']
                    cate = Category.objects.get(category_name=category_name)
                
                    product_name = request.POST['product_name']
                    description = request.POST['description']
                    quantity = request.POST['quantity']
                    unit_price = request.POST['unit_price']
                    dis_price = request.POST['dis_price']
                    available_qty = request.POST['available_qty']

                    table = Product.objects.create(
                        category = cate,
                        user = use,
                        product_name = product_name,
                        description = description,
                        quantity = quantity,
                        unit_price = unit_price,
                        dis_price = dis_price,
                        available_qty = available_qty
                    )
                    table.save()
                    return HttpResponse('Success')
            else:
                return HttpResponse("Error")
        except:
            return HttpResponse("Session Expired")





######     Admin products update  #######

@transaction.atomic
@csrf_exempt
@api_view(['PUT'])
def adminproductsupdate(request,token,pid):
    if request.method == 'PUT':
        try:
            token = KnoxAuthtoken.objects.get(token_key = token)
            id1 = token.user_id
            use = UserProfile.objects.get(id=id1)
            user1 = use.id
            roles = Role.objects.get(role='ADMIN')
            roles1 = roles.role_id
            data = UserRole.objects.filter(role_id=roles1, user_id=user1)
            if data.exists():
                if token.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user_id=user1).delete()
                    return HttpResponse("Session Expired, please login again")
                else:
                    product_name = request.POST['product_name']
                    description = request.POST['description']
                    quantity = request.POST['quantity']
                    unit_price = request.POST['unit_price']
                    dis_price = request.POST['dis_price']

                    table = Product.objects.filter(user=user1).filter(id=pid)
                    if table.exists():
                        Product.objects.update(
                            product_name = product_name,
                            description = description,
                            quantity = quantity,
                            unit_price = unit_price,
                            dis_price = dis_price,
                        )
                        return HttpResponse('Success')
                    else:
                        return HttpResponse("Error")
            else:
                return HttpResponse("Error1")
        except:
            return HttpResponse("Error")






#######  Admin products    #######
@transaction.atomic
@csrf_exempt
@api_view(['GET'])
def adminproducts(request,token):
    if request.method == 'GET':
        try:
            token = KnoxAuthtoken.objects.get(token_key = token)
            id1 = token.user_id
            use = UserProfile.objects.get(id=id1)
            user1 = use.id
            roles = Role.objects.get(role='ADMIN')
            roles1 = roles.role_id
            data = UserRole.objects.filter(role_id=roles1, user_id=user1)
            if data.exists():
                if token.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user_id=user1).delete()
                    return HttpResponse("Session Expired, please login again")
                else:
                    data = Product.objects.filter(user=user1)
                    data1 = list(data.values('product_name'))
                    return Response({
                        "data":data1
                    })
            else:
                return HttpResponse("Error")
        except:
            return HttpResponse("Error")





