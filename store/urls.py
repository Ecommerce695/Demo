from django.urls import path,include
from . import views


urlpatterns = [
    # User Module APIs
    path('signup/', views.register_api, name='signup'),
    path('login/', views.login_api, name='login'),
    path('logout/', views.signoff, name='logout'),
    path('user_detail/<uuid:pk>/',views.user_detail_api, name= 'user_detail'),
    path('update_password/<uuid:pk>/',views.reset, name='password_update'),
    path('address/<uuid:id>/',views.address_api, name='address'),
    
    #Cart & Wishlist Modeule APIs
    path('wish_list/<uuid:id>/<int:pid>/',views.wish_list_api,name='wish_list'),

    # Cart Operations
    path('cart/<uuid:id>/<int:pid>/',views.add_to_cart_api, name='cart'),
    path('delete_cart/<uuid:id>/<int:pid>/', views.delete_from_cart, name='delete_cart'), 
    path('add_items/<uuid:id>/<int:pid>/', views.cart_quantity_add_api, name='add_items'),
    path('remove_items/<uuid:id>/<int:pid>/', views.cart_quantity_remove_api, name='remove_items'),

]
