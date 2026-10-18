from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Hospital, Medico

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'api_key', 'activo', 'fecha_registro')
    search_fields = ('codigo', 'nombre')
    list_filter = ('activo',)
    readonly_fields = ('fecha_registro',)

@admin.register(Medico)
class MedicoAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'hospital', 'cedula', 'especialidad', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos Clínicos y Hospitalarios', {
            'fields': ('hospital', 'cedula', 'especialidad')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos Clínicos y Hospitalarios', {
            'fields': ('hospital', 'cedula', 'especialidad')
        }),
    )
