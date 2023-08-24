from django.urls import path
from payments import views
# from payments.views import checkout



urlpatterns = [
    path('checkout/<token>',views.checkoutapi,name='checkout'),
    path('payment/<token>/<session>',views.newdatart,name='payment'),
    path('retrypayment/<token>',views.retrypayment,name='retry payment'),
    path('tax/<token>',views.tax_api,name='tax creation'),
]