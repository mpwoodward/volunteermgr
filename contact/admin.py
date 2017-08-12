from django.contrib import admin

from .models import Category, Contact, Organization


admin.site.register(Category)
admin.site.register(Contact)
admin.site.register(Organization)
