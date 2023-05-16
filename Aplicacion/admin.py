from django.contrib import admin
from .models import Cliente, Proveedor, Material, Perfil, Rol, Proyecto, MaterialPedido, Pedido, Presupuesto, Obra

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Proyecto)
admin.site.register(Proveedor)
admin.site.register(Material)
admin.site.register(Perfil)
admin.site.register(Rol)
admin.site.register(Obra)
admin.site.register(Presupuesto)
admin.site.register(Pedido)
admin.site.register(MaterialPedido)

