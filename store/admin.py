from django.contrib import admin
from .models import Category, UserProfile, Product, ProductLaptop, ProductMobile, OrgProfile

admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductLaptop)
admin.site.register(ProductMobile)
admin.site.register(OrgProfile)