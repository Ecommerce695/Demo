from re import search
from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    # path('', views.home, name="home"),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    # to Fetch All Records from the DB
    path('details/', views.details, name='details'),
    # This Url is used to Update the User Details
    path('user_detail/<int:pk>',views.user_detail, name= 'user_detail'),
    # path('address/<int:id>',views.address, name='address'),
    path('wish_list/<int:id>/<int:pid>/',views.wish_list,name='wish_list'),
    path('product/',views.product_view, name='product'),
    path('orders/<int:id>/<int:pid>/',views.my_order,name='orders'),
    path('myorders/<int:id>/',views.purchase),
    path(r'search/(?P<cat>\D+)',views.search_bar,name='search'),

]