from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from app.core.models import Region, Area, Person

class PersonAdmin(admin.ModelAdmin):
    exclude = ['person_id']

class PersonInline(admin.StackedInline):
    model = Person
    can_delete = False
    verbose_name_plural = 'Person'

    exclude = ['person_id']

# Define a new UserAdmin class
class UserAdmin(BaseUserAdmin):
    inlines = (PersonInline,)


admin.site.register(Region)
admin.site.register(Area)
admin.site.register(Person, PersonAdmin)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
