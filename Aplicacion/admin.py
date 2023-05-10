from django.contrib import admin
from .models import Cliente, Proveedor, Material, Perfil, Rol, Proyecto

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Proyecto)
admin.site.register(Proveedor)
admin.site.register(Material)
admin.site.register(Perfil)
admin.site.register(Rol)