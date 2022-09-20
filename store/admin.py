from django.contrib import admin
from .models import Category, Product, Sub_Category, Vendor_Products, Vendor_Profile

admin.site.register(Vendor_Products)
admin.site.register(Vendor_Profile)
admin.site.register(Category)
admin.site.register(Sub_Category)
admin.site.register(Product)