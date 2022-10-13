from django.urls import path,include
from . import views


urlpatterns = [
    # User Module APIs
    path('signup/', views.register_api, name='signup'),
    path('login/', views.login_api, name='login'),
    path('logout/', views.logout_api, name='logout'),
    path('user_profile/<uuid:pk>/',views.user_detail_api, name= 'user_detail'),
    path('address/<uuid:id>/',views.address_api, name='address'),

    # Update User Profile Module API
    path('update_password/<uuid:pk>/',views.reset_pwd_api, name='password_update'),
    path('fname_update/<uuid:id>/',views.fname_update_api, name= 'update firstname'),
    path('lname_update/<uuid:id>/',views.lname_update_api, name= 'update lastname'),
    path('email_update/<uuid:id>/',views.email_update_api, name= 'update email'),

    # LIST of Products API
    path('products/', views.products, name='product'),

    #Cart & Wishlist Modeule APIs
    path('wish_list/<uuid:id>/<int:pid>/',views.wish_list_api,name='wish_list'),

    # Cart Operations
    path('cart/<uuid:id>/<int:pid>/',views.add_to_cart_api, name='cart'),
    path('delete_cart/<uuid:id>/<int:pid>/', views.delete_from_cart_api, name='delete_cart'), 
    path('add_items/<uuid:id>/<int:pid>/', views.cart_quantity_add_api, name='add_items'),
    path('remove_items/<uuid:id>/<int:pid>/', views.cart_quantity_remove_api, name='remove_items'),
    path('cart_details/<uuid:id>/',views.cart_details_api, name= 'cart_details'),


]
