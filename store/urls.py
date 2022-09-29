from django.urls import path,include
from . import views


urlpatterns = [
    path('signup/', views.register_api, name='signup'),
    path('login/', views.login_api, name='login'),
    path('logout/', views.signoff, name='logout'),
<<<<<<< HEAD
#     # to Fetch All Records from the DB
#     path('details/', views.details, name='details'),
#     # This Url is used to Update the User Details
    path('user_detail/<uuid:pk>/',views.user_detail_api, name= 'user_detail'),
    path('address/<uuid:id>/',views.address_api, name='address'),
    path('wish_list/<uuid:id>/<int:pid>/',views.wish_list_api,name='wish_list'),
    path('cart/<uuid:id>/<int:pid>/',views.add_to_cart_api, name='cart'),
    # path('reset_password/<uuid:id>/',views.reset_password_api, name='password reset'),
    path('reset/<uuid:pk>/',views.reset, name='password_reset'),

    # path('remove/<uuid:id>/<int:pid>/',views.remove_from_cart_api, name='remove_items'),

#     path('orders/<int:id>/<int:pid>/',views.my_order,name='orders'),
#     path('myorders/<int:id>/',views.purchase),
#     # re_path(r'search/(?P<cat>\D+)',views.search_bar,name='search'),
#     # path('fetch/<int:id>', views.fetch)
=======
    path('user_detail/<uuid:pk>',views.user_detail, name= 'user_detail'),
    path('address/<uuid:id>/',views.address_api, name='address'),
    path('wish_list/<uuid:id>/<int:pid>/',views.wish_list,name='wish_list'),
>>>>>>> f8038fe51dc52d035b4cffa96319ed57c652b950

]
