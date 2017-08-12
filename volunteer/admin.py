from django.contrib import admin

from .models import Category, Volunteer, VolunteerSource, VolunteerActivity


admin.site.register(Category)
admin.site.register(Volunteer)
admin.site.register(VolunteerSource)
admin.site.register(VolunteerActivity)
