from django.urls import path,include
from . import views


urlpatterns = [
    # User Module APIs
    path('signup/', views.register_api, name='signup'),
    path('login/', views.login_api, name='login'),
    path('logout/', views.logout_api, name='logout'),
    path('user_profile/<int:id>/',views.user_detail_api, name= 'user_detail'),

    path('address/<int:id>/',views.add_address_api, name='address add'),
    path('delete_address/<int:id>/<int:aid>/',views.delete_address_api, name='address delete'),


    # Update User Profile Module API
    path('update_password/<int:id>/',views.reset_pwd_api, name='password_update'),
    path('fname_update/<int:id>/',views.fname_update_api, name= 'update firstname'),
    path('lname_update/<int:id>/',views.lname_update_api, name= 'update lastname'),
    path('email_update/<int:id>/',views.email_update_api, name= 'update email'),

    # LIST of Products API
    path('products/', views.products, name='product'),
    # path('category/', views.category_product_api, name='category'),

    #Cart & Wishlist Modeule APIs
    path('wish_list/<int:id>/<int:pid>/',views.wish_list_api,name='wish_list'),

    # Search Bar API
    path('searchbar/<int:id>/', views.searchbar, name='filter'),

    #Category wise Products API
    path('mobiles/', views.mobile_category_api, name='filter'),
    path('laptops/', views.laptop_category_api, name='filter'),
    path('gadgets/', views.gadget_category_api, name='filter'),

    # Recommendation API
    path('recommendation/<int:id>/',views.recommendation_api, name= 'recommendation'),

    # Latest Products added by Vendor 
    path('latest/',views.latest_product_api, name= 'latest_products'),

    # Cart Operations
    path('cart/<int:id>/<int:pid>/',views.add_to_cart_api, name='cart'),
    path('delete_cart/<int:id>/<int:pid>/', views.delete_from_cart_api, name='delete_cart'), 
    path('add_items/<int:id>/<int:pid>/', views.cart_quantity_add_api, name='add_items'),
    path('remove_items/<int:id>/<int:pid>/', views.cart_quantity_remove_api, name='remove_items'),
    path('cart_details/<int:id>/',views.cart_details_api, name= 'cart_details'),

    #Price Filter
    path('price_range/', views.price_filter_api, name='price range'),

    path('prod/<str:name>/', views.category_name_wise_product_filter_api, name='prod'),

    path('review/<int:uid>/<int:pid>/', views.review, name='review'),
    path('topproducts/', views.topratedproducts, name='topproducts'),
]
