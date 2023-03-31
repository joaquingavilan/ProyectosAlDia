from django.contrib import admin
from .models import Cliente, Ingeniero, Proveedor, Material, Perfil, Rol

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Ingeniero)
admin.site.register(Proveedor)
admin.site.register(Material)
admin.site.register(Perfil)
admin.site.register(Rol)