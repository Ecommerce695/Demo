from django.contrib import admin
from django.urls import path,include
from .views import cart_api, cart_quantity
from cart import views


urlpatterns = [
    #POST. GET
    path('cart/<token>',cart_api.as_view(), name='cart'),
    # path('cartget/<token>',views.CartGet, name=''),

    #PUT
    path('cartquantityadd/<token>', cart_quantity.as_view(), name='cartquantity'),
    # path('cartquantitydecrease/<token>', cart_quantitydecrease.as_view(), name='cartquantitydecrease'),
    path('cartdelete/<token>/<pid>',views.cartdelete, name='Delete Item in Cart')
]