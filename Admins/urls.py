from django.urls import path
from Admins import views
from .views import (AdminRegisterView,AdminCompanyRegistrationView,CompanyDetailsUpdateView,EmailUpdateView,MobileUpdateView,TaxIDUpdateView,
                    AddProductView,AddProductVariant,ProductDetailsUpdate,MobileSpecification,LaptopSpecification,AddCategory,
                    AdminDashboardDetails,ProductRestoreAPI,AdminOrderDetailPageAPI)

from .filters import (GetAdminProductsIncludingFilters,GetAllProductsIncludingFilters,GetAllOrdersListIncludingFilters,GetSalesListIncludingFilters,
                      GetUsersListIncludingFilters,GetVendorsListIncludingFilters,
                      GetMyOrdersListIncludingFilters)

# from .order_tabs import (GetNewOrdersListIncludingFilters,GetPickedOrdersListIncludingFilters,GetCancelOrdersListIncludingFilters,
#                      GetInProgressOrdersListIncludingFilters)


urlpatterns = [
    #  SuperAdmin Creating Admins
    path('adminsignup/<token>',AdminRegisterView.as_view(),name='adminsignup'),

    # Admin Company Profile [POST, GET, DELETE]
    path('adminorgregister/<token>',AdminCompanyRegistrationView.as_view(),name='adminorgregister'),

    path('adminstripe/<token>',views.admin_stripe_api,name='admin org register in stripe'),

    path('adminretrystripe/<token>',views.admin_retry_stripe_api,name='admin org register link creation'),

    path('adminstripelogin/<token>', views.admin_stripe_login,name='admin login link fo rstripe transaction and update'),

    # Admin Company Details Updation  [PUT]
    path('adminorgupdate/<token>',CompanyDetailsUpdateView.as_view(),name='adminorgupdate'),

    # Update Company Email-ID  [PUT]
    path('adminorgemailupdate/<token>',EmailUpdateView.as_view(), name='adminorgemailupdate'),

    # Update Company Mobile  [PUT]
    path('adminorgmobileupdate/<token>',MobileUpdateView.as_view(), name='adminorgmobileupdate'),

    # Update Company TAX ID  [PUT]
    path('adminorgtaxidupdate/<token>',TaxIDUpdateView.as_view(), name='adminorgtaxidupdate'),

#     # Admin Products POST FETCH
    path('adminproducts/<token>',AddProductView.as_view(), name='admin products'),

    path('a/addvariant/<token>/<int:pid>',AddProductVariant.as_view(),name='adding Variant'),

    # Product Details Update and Delete
    path('adminproductsupdate/<token>/<int:pid>',ProductDetailsUpdate.as_view(),name='adminproductsupdate'),

    # Mobile Specifications [POST, GET, UPDATE, DELETE]
    path('admindropdownmobile/<token>/<int:pid>',MobileSpecification.as_view(),name='admindropdownmobile'),

    # Laptop Specifications [POST, GET, UPDATE, DELETE]
    path('admindropdownlaptop/<token>/<int:pid>',LaptopSpecification.as_view(),name='admindropdownlaptop'),

    # Admin adding category
    path('admincategory/<token>',AddCategory.as_view(), name='admincategory'),

    # Filters on Admin Modules Functionalities
    path('f/adminproducts/<token>',GetAdminProductsIncludingFilters.as_view(), name='Admin products'),

    path('f/allproducts/<token>',GetAllProductsIncludingFilters.as_view(), name='All products'),

    path('f/list-vendors/<token>',GetVendorsListIncludingFilters.as_view(), name='List all Vendors'),

    path('f/list-users/<token>',GetUsersListIncludingFilters.as_view(), name='List all Users'),

    path('f/list-all-orders/<token>',GetAllOrdersListIncludingFilters.as_view(), name='List all Orders'),

    path('f/list-my-orders/<token>',GetMyOrdersListIncludingFilters.as_view(), name='List My Orders'),

    path('f/list-sales/<token>',GetSalesListIncludingFilters.as_view(), name='List all Sales'),

    # Total Orders & Pending Order KPI Count
    path('admin/kpi/<token>', AdminDashboardDetails.as_view(), name='Admin KPI Details'),

    # Orders Tab
    # path('list/new_order/<token>',GetNewOrdersListIncludingFilters.as_view(),name='list New Orders Details'),

    # path('list/pickup_order/<token>',GetPickedOrdersListIncludingFilters.as_view(),name='list all Pickup Orders'),

    # path('list/cancel_order/<token>',GetCancelOrdersListIncludingFilters.as_view(),name='list all Cancel Orders'),
    
    # path('list/inprogress_order/<token>',GetInProgressOrdersListIncludingFilters.as_view(),name='list all InProgress Orders'),

    path('product/restore/<token>/<int:pid>',ProductRestoreAPI.as_view(),name='Product Roll Back to Product List'),

    path('order/detail/page/<token>',AdminOrderDetailPageAPI.as_view(),name='Order Detail Page')
]
