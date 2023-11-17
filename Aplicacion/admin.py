from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Proyecto)
admin.site.register(Proveedor)
admin.site.register(Material)
admin.site.register(Obra)
admin.site.register(Presupuesto)
admin.site.register(Pedido)
admin.site.register(MaterialPedido)
admin.site.register(Contacto)
admin.site.register(Seccion)
admin.site.register(SubSeccion)
admin.site.register(Detalle)

