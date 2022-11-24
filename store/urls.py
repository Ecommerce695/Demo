from django.urls import path,include
from . import views
from . import vendordetails, superadmin, admindetails
from store.superadmin import SuperAdminRegisterAPI, SUPERAdminloginAPI
from store.admindetails import AdminRegisterAPI, AdminloginAPI


urlpatterns = [
    # User Module APIs
    path('signup/', views.register_api, name='signup'),
    path('login/', views.login_api, name='login'),
    path('logout/', views.logout_api, name='logout'),
    
    # Add Address API
    path('address/<token>/',views.add_address_api, name='address add'),

    # Update Address
    path('update_address/<token>/',views.update_address, name='update address'),
    
    # Delete Address
    path('delete_address/<token>/<int:aid>/',views.delete_address_api, name='address delete'),

    # UPDATE Password API
    path('update_password/<token>/',views.reset_pwd_api, name='password_update'),

    # GET, UPDATE and DELETE Methods
    path('user_profile/<token>/',views.user_detail_api, name= 'user_detail'),

    # (GET)LIST of Products API
    path('products/', views.products, name='product'),
    # path('category/', views.category_product_api, name='category'),

    # (POST)Cart & Wishlist Modeule APIs
    path('wish_list/<token>/<int:pid>/',views.wish_list_api,name='wish_list'),

    # (POST)Search Bar API
    path('searchbar/<token>/', views.searchbar, name='filter'),

    # (GET)Category wise Products API
    path('mobiles/', views.mobile_category_api, name='filter'),
    path('laptops/', views.laptop_category_api, name='filter'),
    path('gadgets/', views.gadget_category_api, name='filter'),

    # (GET)Recommendation API
    path('recommendation/<token>/',views.recommendation_api, name= 'recommendation'),

    # (GET)Newly Added Product Details
    path('latest/',views.latest_product_api, name= 'latest_products'),

    # Cart Operations (POST, DELETE, PUT, GET)
    path('cart/<token>/<int:pid>/',views.add_to_cart_api, name='cart'),
    path('delete_cart/<token>/<int:pid>/', views.delete_from_cart_api, name='delete_cart'), 
    path('add_items/<token>/<int:pid>/', views.cart_quantity_add_api, name='add_items'),
    path('remove_items/<token>/<int:pid>/', views.cart_quantity_remove_api, name='remove_items'),
    path('cart_details/<token>/',views.cart_details_api, name= 'cart_details'),

    # (GET)Price Filter on Products
    path('price_range/', views.price_filter_api, name='price range'),

    # Category Based Product Display
    path('prod/<str:name>/', views.category_name_wise_product_filter_api, name='prod'),

    # POST Method
    path('review/<token>/<int:pid>/', views.review_api, name='review'),
    
    # GET Method
    # path('topproducts/', views.topratedproducts_api, name='topproducts'),

    # path('add_products/<token>/', views.vendorproductsadd, name='add products'),




       #######################################   SUPER ADMIN     #################################

   path('superadminregister/', SuperAdminRegisterAPI.as_view(), name='superadminregister'),
   path('superadminlogin/', SUPERAdminloginAPI.as_view(), name='superadminlogin'),
   path('superadminorg/<token>/', superadmin.SA_org_register, name='superadminorg'),
   path('superadminproductsadd/<token>/',superadmin.superadminproductsadd, name='superadminproductsadd'),
   path('superadminproducts/<token>/',superadmin.superadminproducts, name='superadminproducts'),
   path('superadminproductsupdate/<token>/<int:pid>/',superadmin.superadminproductsupdate, name='superadminproducts'),


#    ######################   ADMIN   #########################################

   path('adminregister/', AdminRegisterAPI.as_view(), name='adminregister'),
   path('adminlogin/',AdminloginAPI.as_view(), name='adminlogin'),
   path('adminorg/<token>/',admindetails.Admin_org_register, name='adminorg'),
   path('adminproductsadd/<token>/',admindetails.adminproductsadd, name='adminproductsadd'),
   path('adminproducts/<token>/',admindetails.adminproducts, name='adminproducts'),
   path('adminproductsupdate/<token>/<int:pid>/',admindetails.adminproductsupdate, name='adminproducts'),



   ############################    VENDOR     #######################################

   path('vendororgregister/<token>/',vendordetails.Vendor_org_register, name='vendororgregister'),
   path('vendorproductsadd/<token>/',vendordetails.vendorproductsadd, name='vendorproductsadd'),
   path('vendorproducts/<token>/',vendordetails.vendorproducts, name='vendorproducts'),
]
