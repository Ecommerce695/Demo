from django.urls import path
from .views import (SARegisterView,SuperAdminOrganizationRegister,SuperAdminOrganizationDetailsUpdate,EmailUpdate,
                    MobileUpdate,TaxIdUpdate,MobileSpecificationView,
                    LaptopSpecificationView,AddCategoryView,SuperAdminDashboardDetails,SuperAdminOrderDetailPageAPI,ProductAPI)

from .filters import (SAProductsIncludingFilters,SAGetAllProductsIncludingFilters,SAAllGetOrdersListIncludingFilters,SAGetSalesListIncludingFilters,
                      SAGetUsersListIncludingFilters,SAGetVendorsListIncludingFilters,SAGetAdminsListIncludingFilters)

from .productApis import SuperAdminAddProductsAPI,SuperAdminUpdateProductsAPI
from .variants import AddProductVariantView,SuperAdminUpdateVariantsAPI

urlpatterns = [
    # Registration
    path('sasignup/',SARegisterView.as_view(),name='sasignup'),

    #Company Details Registration
    path('superadminorgregister/<token>',SuperAdminOrganizationRegister.as_view(),name='superadminorgregister'),
    
    #Update Organization Details
    path('superadminorgupdate/<token>',SuperAdminOrganizationDetailsUpdate.as_view(),name='superadminorgupdate'),
    
    # Update Company Email-ID  [PUT]
    path('adminorgemailupdate/<token>',EmailUpdate.as_view(), name='superadminorgemailupdate'),
    
    # Update Company Mobile  [PUT]
    path('adminorgmobileupdate/<token>',MobileUpdate.as_view(), name='superadminorgmobileupdate'),
    
    # Update Company TAX ID  [PUT]
    path('adminorgtaxidupdate/<token>',TaxIdUpdate.as_view(), name='superadminorgtaxidupdate'),

    # Adding Products API
    # path('superadminproducts/<token>',SuperAdminProductsView.as_view(), name='superadminproducts'),

    # Adding Product Variants
    # path('addvariant/<token>/<int:pid>',AddProductVariantView.as_view(),name='adding Variant'),

    path('sacategory/<token>',AddCategoryView.as_view(),name='sacategory'),

    ## Below Api are Still pending
    # Details Update 
    # path('superadminproductsupdate/<token>/<int:pid>',ProductDetailsUpdate.as_view(),name='superadminproductsupdate'),
    path('sadropdownmobile/<token>/<int:pid>',MobileSpecificationView.as_view(),name='sadropdownmobile'),
    path('sadropdownlaptop/<token>/<int:pid>',LaptopSpecificationView.as_view(),name='sadropdownlaptop'),

    # Filters for Admin
    path('sa/f/adminproducts/<token>',SAProductsIncludingFilters.as_view(), name='Super Admin products'),

    path('sa/f/allproducts/<token>',SAGetAllProductsIncludingFilters.as_view(), name='All products'),

    path('sa/f/list-vendors/<token>',SAGetVendorsListIncludingFilters.as_view(), name='List all Vendors'),

    path('sa/f/list-admins/<token>',SAGetAdminsListIncludingFilters.as_view(), name='List all Admins'),

    path('sa/f/list-users/<token>',SAGetUsersListIncludingFilters.as_view(), name='List all Users'),

    path('sa/f/list-all-orders/<token>',SAAllGetOrdersListIncludingFilters.as_view(), name='List all Orders'),

    path('sa/f/list-sales/<token>',SAGetSalesListIncludingFilters.as_view(), name='List all Sales'),

    path('superadmin/kpi/<token>', SuperAdminDashboardDetails.as_view(), name='Super Admin KPI Details'),

    path('sa/order/detail/page/<token>',SuperAdminOrderDetailPageAPI.as_view(),name='Order Detail Page'),

    path('p/<pid>',ProductAPI.as_view(),name=''),

    path('product/<token>',SuperAdminAddProductsAPI.as_view(),name='Add Product API'),
    path('update/product/<token>/<pid>',SuperAdminUpdateProductsAPI.as_view(),name=''),

    path('variant/<token>/<pid>',AddProductVariantView.as_view(),name='Add Product Variant API'),
    path('update/variant/<token>/<pid>/<vid>',SuperAdminUpdateVariantsAPI.as_view(),name='Update Product Variant API'),
]