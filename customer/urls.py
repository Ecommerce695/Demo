from django.urls import path
from customer import views
from .views import (RegisterView,AccountActivateView,ResendActivationView,LoginApiView,UserRoleDetailsView,
                    NamesUpdateAPI,CustomerEmailUpdateView,UsernameUpdateAPI,CustomerEmailView,CustomerMobileView,ForgotPasswordView,
                    ConfirmPasswordView,UpdatePasswordAPI,AddressView,UpdateAddressView,
                    WishlistView,SaveForLaterAPI,ListSaveLaterProductAPI,MoveToCartAPI,SearchAPIView,ReviewProductsView,
                    SimilarProductsView,TopRatedProductsView,LatestProductsView,AccountDeactivateView,WishlistGetApi,myorders,
                    EstimatedDeliveryDateOfProduct,ViewOrderDetailPage)


urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('a/activate/<token>', AccountActivateView.as_view(),name='account activate'),

    path('a/reactivate/',ResendActivationView.as_view(),name='Account re-activation'),

    path('login/', LoginApiView.as_view(), name='login'),
    path('logout/<token>', views.logout_api, name='logout'),

    # Describe the Role type and there details
    path('role/details/<token>', UserRoleDetailsView.as_view(), name='userroledetails'),  #<-- Newly added

    path('a/deactivate/<token>', AccountDeactivateView.as_view(),name="Account Deactivation"),

    # User FirstName and LastName Update API
    path('namesupdate/<token>', NamesUpdateAPI.as_view(), name='user details Get '),

    # Customer email update api
    path('emailupdate/<token>', CustomerEmailView.as_view(), name='user email update'),

    # updated email validaton with OTP
    path('useremailupdate/<token>/<act_token>', CustomerEmailUpdateView.as_view(), name='user email update verification'),
    
    # User Mobile Number update
    path('mobileupdate/<token>', CustomerMobileView.as_view(), name='User Mobile Update'),

    # Username Update
    path('usernameupdate/<token>',UsernameUpdateAPI.as_view(),name= 'username update api'),
    
    # Update Password API
    path('update/password/<token>', UpdatePasswordAPI.as_view(), name='Update Password'),
    
    # Reset / Forget Password API
    path('reset_password/', ForgotPasswordView.as_view(), name='Reset Password'),
    path('reset_password/confirm/Token=<token>', ConfirmPasswordView.as_view(), name='Reset Password Confirm'),

    # Addess API(post, get)
    path('useraddress/<token>',AddressView.as_view(), name='useraddress'),
    # Update and Delete Address
    path('updateaddress/<token>/<int:aid>',UpdateAddressView.as_view(), name='Update Address'),

    # (GET)LIST of Products API
    # path('products/', ProductsView.as_view(), name='product'),
    path('products/',views.ProductsAPI, name ='List all Products'),

    path('product/detail/page/<p_id>',views.ProductsDetailsAPI,name='Single Product Details'),

    #Category Wise Products
    path('category/',views.CategoryBasedProductsAPI, name ='List all Category Based Products'),
    # path('laptops/',views.LaptopCategoryAPI, name ='List all Laptops Products'),
    # path('watches/',views.WatchCategoryAPI, name ='List all Watches Products'),

    #Wishlist API(post,get)
    path('wishlist/<token>',WishlistView.as_view(), name='wishlist'),

    path('mywishlist/<token>',WishlistGetApi.as_view(), name='wishlist get api'),
    
    # Wishlist API[DELETE]
    path('deletewishlist/<token>/<int:pid>/<int:vid>',views.wishlistdelete, name='Delete Product from wishlist'),

    # Save for Later[POST,DELETE]
    path('savelater/<token>/<pid>',SaveForLaterAPI.as_view(),name='save for later'),
    
    # MOVE to CART from SAVE LATER [PUT]
    path('movetocart/<token>/<pid>', MoveToCartAPI.as_view(),name='move to cart from save later'),
    
    #List Out ALL Products in SaveForLater Tab [GET]
    path('listsavelaterproducts/<token>', ListSaveLaterProductAPI.as_view(),name='move to cart from save later'),


    # Search Filter API
    path('search/<token>',SearchAPIView.as_view(), name='search'),
    
    path('productreview/<token>',ReviewProductsView.as_view(), name='productreview'),
    
    path('latestproducts/<token>',LatestProductsView.as_view(),name='latestproducts'),

    path('topratedproducts/<token>',TopRatedProductsView.as_view(),name='topratedproducts'),

    path('similarproducts/<token>',SimilarProductsView.as_view(),name='similarproducts'),

    path('myorders/<token>',myorders.as_view(), name='My orders'),

    path('orderscount/<token>',views.orderscount,name='orders count'),

    # Get Estimated Delivery Date of Product
    path('get/est_delivery_date/',EstimatedDeliveryDateOfProduct.as_view(),name='Get Estimated Delivery Date of Product'),

    path('view-order_details/<token>',ViewOrderDetailPage.as_view(),name='View Single Order Details'),
    
]