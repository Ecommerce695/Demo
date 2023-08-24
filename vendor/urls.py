from django.urls import path
from .views import (VendorRegistration,VendorAccountActivateView,VendorResendActivationView,OrganizationDetailsUpdate,
                    EmailUpdate,EmailUpdateVerification,MobileUpdate,TaxIDUpdate,VendorProductsView,AddProductVariantView,
                    ProductDetailsUpdate,MobileSpecificationView,LaptopSpecificationView,colour_api,ven_SearchAPIView,
                    ven_price,ven_categoryapi,vendorproductsapiget)
from vendor.ve_filters import GetvendorProductsIncludingFilters,GetMyOrdersListIncludingFilters,GetSalesListIncludingFilters
from vendor import views

urlpatterns = [
    #Vendor Registration
    path('vendororgregister/<token>',VendorRegistration.as_view(),name='vendororgregister'),

    path('vendor/activate/<token>', VendorAccountActivateView.as_view(),name='vendoractivate'),

    path('vestripe/<token>', views.stri_api,name='vendor account details'),

    path('retryvestripe/<token>', views.retry_stripe_api,name='vendor account details'),

    path('vendorstripelogin/<token>', views.vendor_stripe_login,name='vendor login link fo rstripe transaction and update'),

    path('vendor/reactivate/<token>',VendorResendActivationView.as_view(),name='Account re_activation'),

    # Update Details
    path('vendororgupdate/<token>',OrganizationDetailsUpdate.as_view(),name='vendororgupdate'),

    # Update Company Email-ID with OTP validation
    path('vendororgemail/<token>',EmailUpdate.as_view(), name='vendororgemail'),

    path('vendororgemailupdate/<token>/<act_token>',EmailUpdateVerification.as_view(), name='vendororgemailupdate'),

    path('vendormobileupdate/<token>',MobileUpdate.as_view(), name='Mobile Update'),

    path('vendortaxidupdate/<token>',TaxIDUpdate.as_view(), name='TaxID Update'),

    # Vendor Products Upload
    path('vendorproducts/<token>',VendorProductsView.as_view(), name='vendorproducts'),

    path('vendorproductsget/<token>',vendorproductsapiget.as_view(), name='vendorproducts get'),

    path('v/addvariant/<token>/<int:pid>',AddProductVariantView.as_view(),name='adding Variant'),

    path('vendorproductsupdate/<token>/<int:pid>',ProductDetailsUpdate.as_view(), name='vendorproductsupdate'),

    # Product Specifications
    path('dropdownmobile/<token>/<int:pid>',MobileSpecificationView.as_view(),name='dropdownmobile'),

    path('dropdownlaptop/<token>/<int:pid>',LaptopSpecificationView.as_view(),name='dropdownlaptop'),

#####  Vendor category filters
    path('vencategory/<token>',ven_categoryapi.as_view(),name='vendor category api'),

    # path('vendororders/<token>',views.vend_orders,name='vendor products orders'),

    path('vendcolourfilter/<token>',colour_api.as_view(),name='vendor colour products filter'),

    path('vendorsearch/<token>',ven_SearchAPIView.as_view(),name='vendor search'),

    path('vendorcount/<token>',views.ven_count,name='vendor count'),

    path('vendorprice/<token>',ven_price.as_view(),name='vendor price filter'),

#####   Vendor filters in vendor dashboard
    path('vendorproductsfilter/<token>',GetvendorProductsIncludingFilters.as_view(),name='vendor products'),

    path('vendorordersfilter/<token>',GetMyOrdersListIncludingFilters.as_view(),name='vendor orders'),

    path('vendorsalesfilter/<token>',GetSalesListIncludingFilters.as_view(),name='vendor sales'),

]