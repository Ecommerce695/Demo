from django.urls import path,include
from . import views


urlpatterns = [
    path('signup/', views.register_api, name='signup'),
    path('login/', views.login_api, name='login'),
    path('logout/', views.signoff, name='logout'),
#     # to Fetch All Records from the DB
#     path('details/', views.details, name='details'),
#     # This Url is used to Update the User Details
    path('user_detail/<uuid:pk>',views.user_detail, name= 'user_detail'),
    path('address/<uuid:id>/',views.address_api, name='address'),
    path('wish_list/<uuid:id>/<int:pid>/',views.wish_list,name='wish_list'),
#     path('product/',views.product_view, name='product'),
#     path('orders/<int:id>/<int:pid>/',views.my_order,name='orders'),
#     path('myorders/<int:id>/',views.purchase),
#     # re_path(r'search/(?P<cat>\D+)',views.search_bar,name='search'),
#     # path('fetch/<int:id>', views.fetch)

]
