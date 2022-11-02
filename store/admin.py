from django.contrib import admin
from .models import Category, UserProfile, Product, ProductLaptop, ProductMobile, VendorOrgProfile

admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductLaptop)
admin.site.register(ProductMobile)
admin.site.register(VendorOrgProfile)