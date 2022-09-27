from django.urls import path,include
from . import views


urlpatterns = [
    path('signup/', views.register_api, name='signup'),
    path('login/', views.login_api, name='login'),
    path('logout/', views.signoff, name='logout'),
    path('user_detail/<uuid:pk>',views.user_detail, name= 'user_detail'),
    path('address/<uuid:id>/',views.address_api, name='address'),
    path('wish_list/<uuid:id>/<int:pid>/',views.wish_list,name='wish_list'),

]
