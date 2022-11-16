from django.urls import path,include
from . import views


urlpatterns = [
    # User Module APIs
    path('signup/', views.register_api, name='signup'),
    path('login/', views.login_api, name='login'),
    path('logout/', views.logout_api, name='logout'),
    
    # POST Method
    path('address/<token>/',views.add_address_api, name='address add'),
    
    # DELETE Method
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
    # POST(Vendor Organization Registration)
    path('vendor/register/<token>/', views.vendor_register_api, name='vendor_register_form'),
]
