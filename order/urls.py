from django.urls import path
from order.views import (singleproductorder,OrderCancelApi,OrderReturnAPI,address_api,pr_remove)
from order import views

urlpatterns = [
    #Order and Pay API CART
    path('buynow/<token>',singleproductorder.as_view(), name='order single product'),
    path('ordercart/<token>',views.ordercart , name='cart order'),
    path('address/<token>',address_api.as_view(),name='User address'),
    path('productremove/<token>',pr_remove.as_view(),name='product removing'),
    path('ordercancel/<token>',OrderCancelApi.as_view(), name='order cancel'),
    path('orderreturn/<token>',OrderReturnAPI.as_view(), name='order returned'),

]