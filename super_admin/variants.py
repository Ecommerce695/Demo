from rest_framework.generics import CreateAPIView
from .serializers import product_variant
from customer.models import Role, UserRole,UserProfile,KnoxAuthtoken
from .models import CompanyProfile,Category,collection,images,tags,variants,Product,ProductLaptop,ProductMobile
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from pytz import utc
from datetime import datetime
import json, requests,re,os
from Ecomerce_project.settings import SHIPMENT_TOKEN
from PIL import Image

class AddProductVariantView(CreateAPIView):
    serializer_class = product_variant

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
                    if(Product.objects.filter(user=userdata, id=pid)):
                        
                        serializer = self.get_serializer(data=request.data)
                        if serializer.is_valid(raise_exception=True):
                            variant_price = serializer.validated_data['price']
                            variant_discount = serializer.validated_data['discount']
                            variant_quantity = serializer.validated_data['quantity']
                            variant_sku = serializer.validated_data['sku']
                            variant_color = serializer.validated_data['color']
                            variant_images = serializer.validated_data['images']

                            product = Product.objects.get(user=userdata, id=pid)
                            coll = collection.objects.filter(id=pid).values('id','collection_id').earliest('-collection_id')
                            print(coll['id'])
                            col = collection.objects.get(id=coll['id'],collection_id=coll['collection_id'])
                            print(col.id,col.collection,col.collection_id)
                            dis_percentage =variant_discount/100
                            dis_price = variant_price*dis_percentage
                            final_price=(variant_price - dis_price)

                            if product.category.upper() in ('MOBILES','LAPTOPS','WATCHES'):
                                gst_percentage=18

                            if variant_sku=='':
                                skuval = product.brand.upper()+'-'+variant_color.upper()
                            else:
                                skuval = variant_sku

                            if product.is_charged==True:
                                variant = variants.objects.create(
                                    id=product.id,
                                    price = variant_price,
                                    gst = gst_percentage,
                                    discount=variant_discount,
                                    selling_price = round(final_price+product.shipping_charges+product.other_charges),
                                    sku=skuval,
                                    color=variant_color,
                                    quantity = variant_quantity,
                                    stock=variant_quantity
                                )
                            else:
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
                            
                            for image in variant_images:
                                variant_image = 'http://127.0.0.1:8000/media/variants/images/' + str(image)
                                i=images.objects.create(id=product.id,alt=variant.color,path=image,src=variant_image,variant_id=variant.variant_id)

                            variants.objects.filter(variant_id=i.variant_id).update(image_id=i.image_id)

                            col = collection.objects.create(id=product.id,collection=col.collection,variant_id=variant.variant_id)
                            tags.objects.create(id=product.id,tags=product.brand,variant_id=variant.variant_id)
                            tags.objects.create(id=product.id,tags=variant_color,variant_id=variant.variant_id)
                            if product.new ==True:
                                    tags.objects.create(id=product.id,tags='new',variant_id=variant.variant_id)

                            return Response({"message":"Successfully Added New Varinat"}, status=status.HTTP_201_CREATED)
                        else :
                            return Response({"message":"Missing value"},status=status.HTTP_204_NO_CONTENT)
                    else:
                        return Response({"message":"This Product Does not exists"},status=status.HTTP_404_NOT_FOUND)     
            else:
                data={'message':"Current User is not Super Admin"}
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
                    if(Product.objects.filter(user=userdata, id=pid)):
                        variant=variants.objects.filter(id=pid).values()
                        image = images.objects.filter(id=pid).values()
                        data={
                            "variant":variant,
                            "images":image
                        }
                        return Response(data,status=status.HTTP_200_OK)
                    return Response({"message":"Invalid Product ID"})
            else:
                data={'message':"Current User is not Super Admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
            

    


class SuperAdminUpdateVariantsAPI(CreateAPIView):
    serializer_class = product_variant

    @transaction.atomic
    def put(self,request,token,pid,vid):
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
            v = variants.objects.get(id=p.id,variant_id=vid)
        except:
            data = {
                    "message" : "Invalid Variant Id"
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
                        variant_price = serializer.validated_data['price']
                        variant_discount = serializer.validated_data['discount']
                        variant_quantity = serializer.validated_data['quantity']
                        variant_sku = serializer.validated_data['sku']
                        variant_color = serializer.validated_data['color']
                        variant_images = serializer.validated_data['images']

                        deletes= images.objects.filter(variant_id=vid,id=pid).values_list('path')
                        img_list = [t[0] for t in deletes]

                        for i in img_list:
                            im = images.objects.get(variant_id=v.variant_id,path=i)
                            im.path.delete(save=False)

                        images.objects.filter(variant_id=vid).all().delete()

                        for j in variant_images:
                            variant_image = 'http://127.0.0.1:8000/media/variants/images/' + str(j)
                            i=images.objects.create(id=pid,alt=variant_color,path=j,src=variant_image,variant_id=vid)

                        variants.objects.filter(variant_id=i.variant_id).update(image_id=i.image_id)
                        v=variants.objects.get(variant_id=vid)

                        product = Product.objects.get(user=userdata, id=v.id)
                        dis_percentage =variant_discount/100
                        dis_price = variant_price*dis_percentage
                        final_price=(variant_price - dis_price)

                        if product.category.upper() in ('MOBILES','LAPTOPS','WATCHES'):
                            gst_percentage=18

                        if variant_sku=='':
                            skuval = product.brand.upper()+'-'+variant_color.upper()
                        else:
                            skuval = variant_sku
                        if product.is_charged==True:
                            variants.objects.filter(id=product.id,variant_id=v.variant_id).update(
                                price = variant_price,
                                gst = gst_percentage,
                                discount=variant_discount,
                                selling_price = round(final_price+product.shipping_charges+final_price*0.08),
                                sku=skuval,
                                color=variant_color,
                                quantity = variant_quantity,
                                stock=variant_quantity
                            )
                        else:
                            variants.objects.filter(id=product.id,variant_id=v.variant_id).update(
                                id=product.id,
                                price = variant_price,
                                gst = gst_percentage,
                                discount=variant_discount,
                                selling_price = final_price,
                                sku=skuval,
                                color=variant_color,
                                quantity = variant_quantity,
                                stock=variant_quantity)
                        tags.objects.create(id=product.id,tags=variant_color,variant_id=v.variant_id)
                        return Response({'message':'Product updated successfully'},status= status.HTTP_201_CREATED)
            else:
                data={'message':"Current User is not Super Admin"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"message":'User is in In-Active, please Activate your account'}
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)            