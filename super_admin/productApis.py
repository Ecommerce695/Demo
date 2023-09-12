from rest_framework.generics import CreateAPIView
from .serializers import ProductSerilaizer,ProductDetailsUpdate
from customer.models import Role, UserRole,UserProfile,KnoxAuthtoken
from .models import CompanyProfile,Category,collection,images,tags,variants,Product
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from pytz import utc
from datetime import datetime
import json, requests,re
from Ecomerce_project.settings import SHIPMENT_TOKEN


# Super Admin Product Upload API 
class SuperAdminAddProductsAPI(CreateAPIView):
    serializer_class = ProductSerilaizer

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

        try:
            cp = CompanyProfile.objects.get(user=userdata)
        except:
            return Response({"message":"Not registered with Company Profile"},status=status.HTTP_401_UNAUTHORIZED)
        
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):

                        protitle = serializer.validated_data['title']
                        prodescription = serializer.validated_data['description']
                        protype = serializer.validated_data['type']
                        probrand = serializer.validated_data['brand'] 
                        pronew = serializer.validated_data['new']
                        prosale =  serializer.validated_data['sale']
                        procategory = serializer.validated_data['category']
                        prodimension = serializer.validated_data['dimensions']
                        proweight = serializer.validated_data['weight']
                        prowarranty = serializer.validated_data['warranty']
                        prowarrantyfile = serializer.validated_data['warranty_file']
                        prowarrantymonths = serializer.validated_data['warranty_months']
                        prostatus = serializer.validated_data['status']
                        charged = serializer.validated_data['charge_checked']
                        procollection = serializer.validated_data['collection']
                        variant_price = serializer.validated_data['price']
                        variant_discount = serializer.validated_data['discount']
                        variant_quantity = serializer.validated_data['quantity']
                        variant_color = serializer.validated_data['color']
                        variant_src = serializer.validated_data['variant_images']
                        varinat_sku = serializer.validated_data['sku']

                        if variant_discount >100 or variant_discount<0:
                            return Response({'message':"Invalid discount percentage","error":"Percentage should be >=0 (or) <=100"},status=status.HTTP_400_BAD_REQUEST)
                        
                        if varinat_sku=='':
                            skuval = probrand.upper()+'-'+variant_color.upper()
                        else:
                            skuval = varinat_sku

                        if prodimension =='':
                            return Response({"messgae":"Please use the following format: L X B X H"})
                        if proweight<0.1:
                            return Response({"message":"The minimum chargeable weight is 0.1 Kg"})

                        delivery = [380006,382345,282001,676305,600001,643253,797001,751003,180001,587315,560063,
                                    110001,110020,500001,500058,600001,600082,515001,515311,403001,403405,560001,
                                    800001,800016,226001,226017,302001,302017,400001,400065,700001,700046,560015,522020]
                        
                        charger_list=[]
                        for j in range(len(delivery)):
                            try:
                                url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"

                                payload=json.dumps({
                                    "pickup_postcode":cp.pincode, 
                                    "delivery_postcode":delivery[j],
                                    "cod":"0",  # 1 for COD and 0 for Prepaid orders.
                                    "weight":proweight,
                                    # "declared_value":10000
                                })
                                headers = {
                                'Content-Type': 'application/json',
                                'Authorization': SHIPMENT_TOKEN
                                }

                                response = requests.request("GET", url, headers=headers, data=payload)
                                data=response.json()
                                
                                if response.status_code==200:            
                                    for i in range(len(data['data']['available_courier_companies'])):
                                        # date = data['data']['available_courier_companies'][i]['etd']
                                        shipping_chargers = data['data']['available_courier_companies'][i]["freight_charge"]
                                        i=i+1
                                        # date_list.append(date)
                                        charger_list.append(shipping_chargers)
                            except:
                                pass
                        if(Category.objects.filter(category_name__iexact=procategory)):
                            tablecategory = Category.objects.get(category_name__iexact=procategory)
                            if procategory.upper() in ('MOBILES','LAPTOPS','WATCHES'):
                                gst_percentage=18

                            dimension_pattern = r'^\d+(\.\d+)?X\d+(\.\d+)?X\d+(\.\d+)?$'
                            if re.match(dimension_pattern, prodimension):
                                if prowarrantyfile=='':
                                    warranty_doc=''
                                else:
                                    warranty_doc= 'http://127.0.0.1:8000/media/product/warranty/' + str(prowarrantyfile)
                                if prowarranty==True:
                                    no_of_month=prowarrantymonths
                                else:
                                    no_of_month=0
                                dis_percentage =variant_discount/100
                                dis_price = variant_price*dis_percentage
                                final_price=(variant_price - dis_price)
                                charges = round((final_price)*0.15)
                                sellingPrice = final_price + charges + max(charger_list)
                                shipping = round(max(charger_list))

                                product = Product.objects.create(
                                    title=protitle,
                                    description=prodescription,
                                    type = protype,
                                    brand=probrand,
                                    new=pronew,
                                    sale=prosale,
                                    user=usertable, 
                                    category_id=tablecategory.id, 
                                    category = tablecategory.category_name,
                                    dimensions=prodimension,
                                    weight=proweight,
                                    status=prostatus,
                                    warranty_src=warranty_doc,
                                    warranty_path=prowarrantyfile,
                                    warranty_months = no_of_month,
                                    is_charged = charged,
                                    is_wattanty=prowarranty
                                )
                                
                                if charged==True and product.is_charged==True:
                                    variant = variants.objects.create(
                                        id=product.id,
                                        price = variant_price,
                                        gst = gst_percentage,
                                        discount=variant_discount,
                                        selling_price = round(sellingPrice),
                                        sku=skuval,
                                        color=variant_color,
                                        quantity = variant_quantity,
                                        stock=variant_quantity
                                    )
                                    Product.objects.filter(id=product.id).update(is_charged = charged,shipping_charges=round(shipping*2),other_charges=round(charges),alias='PRO-'+str(product.id))
                                else:
                                    Product.objects.filter(id=product.id).update(is_charged = charged,shipping_charges=0,other_charges=0,alias='PRO-'+str(product.id))
                                    variant = variants.objects.create(
                                        id=product.id,
                                        price = variant_price,
                                        gst = gst_percentage,
                                        discount=variant_discount,
                                        selling_price = final_price,
                                        sku=skuval,
                                        color=variant_color,
                                        quantity = variant_quantity,
                                        stock=variant_quantity)
                                
                                for image in variant_src:
                                    variant_image = 'http://127.0.0.1:8000/media/variants/images/' + str(image)
                                    i=images.objects.create(id=product.id,alt=variant.color,path=image,src=variant_image,variant_id=variant.variant_id)

                                variants.objects.filter(variant_id=i.variant_id).update(image_id=i.image_id)
                                
                                col = collection.objects.create(id=product.id,collection=procollection,variant_id=variant.variant_id)
                                tag = tags.objects.create(id=product.id,tags=probrand,variant_id=variant.variant_id)
                                # tag = tags.objects.create(id=protable.id,tags=prosize)
                                tag = tags.objects.create(id=product.id,tags=variant_color,variant_id=variant.variant_id)
                                
                                if product.status=='Publish':
                                    Product.objects.filter(id=product.id).update(is_active=True)

                                if pronew ==True:
                                    tags.objects.create(id=product.id,tags='new',variant_id=variant.variant_id)

                                data = {"message":'Product Added successfully'}
                                return Response(data, status=status.HTTP_200_OK)
                            else:
                                return Response({'message':"Please use the following format: L X B X H"},status=status.HTTP_400_BAD_REQUEST)
                        else:
                            data = {'message': "Category Not Found"}
                            return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data = {'message': "Details Not Found"}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data={'message' : "Current User is not Super Admin"}
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
                    product = Product.objects.filter(user=userdata).values()
                    if product.exists():
                        datalist =[] 

                        for i in product:
                            pro = Product.objects.get(id = i['id'])
                            col = collection.objects.filter(id=i['id']).values_list('collection',flat=True)
                            var = variants.objects.filter(id=i['id']).values()
                            img = images.objects.filter(id=i['id']).values()
                            t = tags.objects.filter(id=i['id']).values_list('tags',flat=True)
                            sold_by = CompanyProfile.objects.get(user=userdata)

                            data = {
                                "id": pro.id,
                                "title": pro.title,
                                "description": pro.description, 
                                "type": pro.type,
                                "brand": pro.brand,
                                "collection": col,
                                "sale": pro.sale,
                                "new": pro.new,
                                "user_id": userdata,
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
                                "sold_by" : sold_by.org_name,
                                "weight": pro.weight,
                                "dimensions":pro.dimensions
                            }
                            datalist.append(data)
                        return Response(datalist, status=status.HTTP_200_OK)
                    else:
                        data = {"message":'Details Not Found'}
                        return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                data={'message':"Current User is not Super Admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


class SuperAdminUpdateProductsAPI(CreateAPIView):
    serializer_class = ProductDetailsUpdate

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

        try:
            p = Product.objects.get(id=pid,user=userdata)
        except:
            data = {
                    "message" : "Invalid Product Id"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
    
        try:
            cp = CompanyProfile.objects.get(user=userdata)
        except:
            return Response({"message":"Not registered with Company Profile"},status=status.HTTP_401_UNAUTHORIZED)
        
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        protitle = serializer.validated_data['title']
                        prodescription = serializer.validated_data['description']
                        protype = serializer.validated_data['type']
                        probrand = serializer.validated_data['brand'] 
                        pronew = serializer.validated_data['new']
                        prosale =  serializer.validated_data['sale']
                        procategory = serializer.validated_data['category']
                        prodimension = serializer.validated_data['dimensions']
                        proweight = serializer.validated_data['weight']
                        prostatus = serializer.validated_data['status']
                        prowarranty = serializer.validated_data['is_wattanty']
                        prowarrantyfile = serializer.validated_data['warranty_path']
                        prowarrantymonths = serializer.validated_data['warranty_months']
                        
                        # procollection = serializer.validated_data['collection']

                        
                        # variant_price = serializer.validated_data['price']
                        # variant_discount = serializer.validated_data['discount']
                        # variant_quantity = serializer.validated_data['quantity']
                        # variant_color = serializer.validated_data['color']
                        # variant_src = serializer.validated_data['variant_images']
                        # varinat_sku = serializer.validated_data['sku']
                        if(Category.objects.filter(category_name__iexact=procategory)):
                            if prowarrantyfile !=None or prowarrantyfile !=p.warranty_path.name:
                                p.warranty_path.delete(save=False)
                                warranty_doc = 'http://127.0.0.1:8000/media/product/warranty/' + str(prowarrantyfile)
                                p.warranty_src=warranty_doc
                                p.warranty_path=prowarrantyfile
                                p.save()
                            else:
                                Product.objects.filter(id=p.id).update(warranty_src=p.warranty_src,warranty_path=p.warranty_path)
                            
                            Product.objects.filter(id=p.id).update(
                                title=protitle,
                                description=prodescription,
                                type=protype,
                                brand=probrand,
                                new=pronew,
                                sale=prosale,
                                category=procategory,
                                dimensions=prodimension,
                                weight=proweight,
                                status=prostatus,
                                is_wattanty=prowarranty,
                                # warranty_file=prowarrantyfile,
                                warranty_months=prowarrantymonths,
                                updated_at=datetime.now(),
                            )
                            return Response({"message":"Successfully Updated"},status=status.HTTP_200_OK)
                        else:
                            data = {'message': "Category Not Found"}
                            return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    else :
                        return Response({'message': 'Serializer error'})
            else:
                data={'message':"Current User is not Super Admin"}
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

        try:
            p = Product.objects.get(id=pid,user=userdata)
        except:
            data = {
                    "message" : "Invalid Product Id"
                }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
        if(UserProfile.objects.filter(id=userdata, is_active='True')):
            if roles.exists():
                if token1.expiry < datetime.now(utc):
                    KnoxAuthtoken.objects.filter(user=user).delete()
                    data = {"message":'Session Expired, Please login again'}
                    return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    if CompanyProfile.objects.filter(user=userdata).exists():
                        Product.objects.filter(id=pid).delete()
                        variants.objects.filter(id=pid).delete()
                        tags.objects.filter(id=pid).delete()
                        collection.objects.filter(id=pid).delete()
                        images.objects.filter(id=pid).delete()
                        return Response({'message':"Product Deleted Successfully"},status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Not registered with Company Profile"},status=status.HTTP_401_UNAUTHORIZED)
            else:
                data={'message':"Current User is not Super Admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)