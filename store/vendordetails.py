from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.db import transaction
from store.models import UserProfile, OrgProfile, UserRole,KnoxAuthtoken,Product, Category, Role
from rest_framework.response import Response
from django.http import HttpResponse
from datetime import datetime,timedelta
from pytz import utc




######      Vendor organisation details   #######

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
def Vendor_org_register(request,token):
    if request.method == 'POST':
        try:
            token = KnoxAuthtoken.objects.get(token_key = token)
            id1 = token.user_id
            use = UserProfile.objects.get(id=id1)
            user1 = use.id
            roles = Role.objects.get(role='SUPER_ADMIN')
            role1 = roles.role_id
            role4 = UserRole.objects.filter(user_id=user1, role_id=role1)
            if role4.exists():
                return HttpResponse("User exists")
            elif(UserRole.objects.filter(user_id=user1, role_id=2)):
                return HttpResponse("User exists")
            else:
                if token.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user1).delete()
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
                    role1 = Role.objects.get(role='VENDOR')
                    role2 = role1.role_id
                    user2 = UserRole.objects.create(role_id = role2, user_id =user1)
                    vendor.save()
                    return Response (
                        {
                            "200 ok"
                        }
                    )
        except:
            return HttpResponse("Error")






#######  Vendor products add     #########################

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
def vendorproductsadd(request,token):
    if request.method == 'POST':
        try:
            token = KnoxAuthtoken.objects.get(token_key = token)
            id1 = token.user_id
            use = UserProfile.objects.get(id=id1)
            user = use.id
            roles = Role.objects.get(role='VENDOR')
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
    else:
        return HttpResponse("Error")
        



#######  Vendor products    #######
@transaction.atomic
@csrf_exempt
@api_view(['GET'])
def vendorproducts(request,token):
    if request.method == 'GET':
            token = KnoxAuthtoken.objects.get(token_key = token)
            id1 = token.user_id
            use = UserProfile.objects.get(id=id1)
            user = use.id
            roles = Role.objects.get(role='VENDOR')
            roles1 = roles.role_id
            data = UserRole.objects.filter(role_id=roles1, user_id=user)
            if data.exists():
                data = Product.objects.filter(user=user)
                data1 = list(data.values('product_name'))
                return Response({
                    "data":data1
                })
            else:
                return HttpResponse("Error")


def xyx_akk():
    pass

def abc(request):
    pass