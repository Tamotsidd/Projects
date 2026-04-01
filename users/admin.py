
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PatientProfile, DoctorProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display    = ['full_name', 'phone', 'role', 'is_active', 'created_at']
    list_filter     = ['role', 'is_active']
    search_fields   = ['full_name', 'phone', 'email']
    ordering        = ['-created_at']
    fieldsets       = (
        (None,           {'fields': ('phone', 'password')}),
        ('Personal Info',{'fields': ('full_name', 'email', 'role')}),
        ('Permissions',  {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets   = (
        (None, {
            'classes': ('wide',),
            'fields':  ('phone', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'gender', 'blood_group', 'date_of_birth']
    search_fields = ['user__full_name', 'user__phone']


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'specialization', 'license_number', 'years_experience', 'available_days']
    search_fields = ['user__full_name', 'specialization']