"""ProyectosAldIA URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Aplicacion import decorators, views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(template_name='ABM/usuarios/login.html'), name='login'),
    path('inicio/', views.inicio, name='inicio'),
    path('inicio_ingenieros/', views.inicio_ingenieros, name='inicio_ingenieros'),
    path('clientes/registro/', views.registrar_cliente, name='registro_cliente'),
    path('clientes/ver/', views.ver_clientes, name='ver_clientes'),
    path('editar_cliente/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('get_cliente_data/<int:cliente_id>/', views.get_cliente_data, name='get_cliente_data'),
    path('get_contactos_cliente/<int:cliente_id>/', views.get_contactos_cliente, name='get_contactos_cliente'),
    path('buscar_clientes/', views.buscar_clientes, name='buscar_clientes'),
    path('ver_cliente/<int:id_cliente>/', views.ver_cliente, name='ver_cliente'),
    path('agregar_contacto/<str:tipo>/<int:id>/', views.agregar_contacto, name='agregar_contacto'),
    path('eliminar_contacto/<int:contacto_id>/', views.eliminar_contacto, name='eliminar_contacto'),
    path('ingenieros/registrar/', views.registrar_ingeniero, name='registrar_ingeniero'),
    path('ingenieros/ver', views.ver_ingenieros, name='ver_ingenieros'),
    path('ingenieros/editar/<int:pk>/', views.editar_ingeniero, name='editar_ingeniero'),
    path('ingenieros/eliminar/<int:pk>/', views.eliminar_ingeniero, name='eliminar_ingeniero'),
    path('buscar_ingenieros/', views.buscar_ingenieros, name='buscar_ingenieros'),
    path('ver_ingeniero/<int:id_ingeniero>/', views.ver_ingeniero, name='ver_ingeniero'),
    path('proveedores/registro/', views.registrar_proveedor, name='registrar_proveedor'),
    path('proveedores/ver/', views.ver_proveedores, name='ver_proveedores'),
    path('editar_proveedor/<int:pk>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/<int:pk>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('get_proveedor_data/<int:proveedor_id>/', views.get_proveedor_data, name='get_proveedor_data'),
    path('get_contactos_proveedor/<int:proveedor_id>/', views.get_contactos_proveedor, name='get_contactos_proveedor'),
    path('buscar_proveedores/', views.buscar_proveedores, name='buscar_proveedores'),
    path('ver_proveedor/<int:id_proveedor>/', views.ver_proveedor, name='ver_proveedor'),
    path('materiales/registro/', views.registrar_material, name='registrar_material'),
    path('materiales/ver/', views.ver_materiales, name='ver_materiales'),
    path('materiales/editar/<int:pk>/', views.editar_material, name='editar_material'),
    path('buscar_materiales/', views.buscar_materiales, name='buscar_materiales'),
    path('ver_material/<int:id_material>/', views.ver_material, name='ver_material'),
    path('ABM/usuarios/login/', views.loguear_usuario, name='login'),
    path('usuarios/registro/', views.registrar_usuario, name='registro'),
    path('usuarios/salir/', views.salir_usuario, name='salir'),
    path('proyectos/registro/', views.registrar_proyecto, name='registrar_proyecto'),
    path('proyectos/ver/', views.ver_proyectos, name='ver_proyectos'),
    path('proyectos/eliminar/<int:pk>/', views.eliminar_proyecto, name='eliminar_proyecto'),
    path('proyectos/modificar/<int:pk>/', views.modificar_proyecto, name='modificar_proyecto'),
    path('buscar_proyectos/', views.buscar_proyectos, name='buscar_proyectos'),
    path('ver_proyecto/<int:id_proyecto>/', views.ver_proyecto, name='ver_proyecto'),
    path('pantallas_ing/ver_presupuestos/', views.ver_presupuestos, name='ver_presupuestos'),
    path('pantallas_ing/ver_obras/', views.ver_obras, name='ver_obras'),
    path('pedido_materiales/', views.pedido_materiales, name='pedido_materiales'),
    path('confirmar_pedido/', views.confirmar_pedido, name='confirmar_pedido'),
    path('ver_pedidos/', views.ver_pedidos, name='ver_pedidos'),
    path('obtener_clientes_con_proyectos/', views.obtener_clientes_con_proyectos, name='obtener_clientes_con_proyectos'),
    path('obtener_ingenieros_presupuesto/', views.obtener_ingenieros_presupuesto, name='obtener_ingenieros_presupuesto'),
    path('obtener_estados_presupuesto/', views.obtener_estados_presupuesto, name='obtener_estados_presupuesto'),
    path('obtener_ingenieros_obra/', views.obtener_ingenieros_obra, name='obtener_ingenieros_obra'),
    path('obtener_estados_obra/', views.obtener_estados_obra, name='obtener_estados_obra'),
    path('obtener_ciudades_con_proyectos/', views.obtener_ciudades_con_proyectos, name='obtener_ciudades_con_proyectos'),
    path('ver_proyectos_cliente/<str:cliente_nombre>/', views.ver_proyectos_cliente,name='ver_proyectos_cliente'),
    path('ver_proyectos_encargado_presupuesto/<str:ingeniero_user>/',views.ver_proyectos_encargado_presupuesto, name='ver_proyectos_encargado_presupuesto'),
    path('ver_proyectos_encargado_obra/<str:ingeniero_user>/', views.ver_proyectos_encargado_obra,name='ver_proyectos_encargado_obra'),
    path('ver_proyectos_estado_presupuesto/<str:estado>/', views.ver_proyectos_estado_presupuesto,name='ver_proyectos_estado_presupuesto'),
    path('ver_proyectos_estado_obra/<str:estado>/', views.ver_proyectos_estado_obra,name='ver_proyectos_estado_obra'),
    path('ver_proyectos_ciudad/<str:ciudad>/', views.ver_proyectos_ciudad, name='ver_proyectos_ciudad'),
    path('exportar_excel/', views.exportar_excel, name='exportar_excel'),
    path('obtener_materiales_marca/', views.obtener_materiales_marca, name='obtener_materiales_marca'),
    path('obtener_materiales_proveedor/', views.obtener_materiales_proveedor, name='obtener_materiales_proveedor'),
    path('obtener_materiales_stock/', views.obtener_materiales_stock, name='obtener_materiales_stock'),
    path('ver_materiales_marca/<str:marca>/', views.ver_materiales_marca, name='ver_materiales_marca'),
    path('ver_materiales_proveedor/<str:proveedor>/', views.ver_materiales_proveedores, name='ver_materiales_proveedores'),
    path('ver_materiales_stock/<str:cantidad>/', views.ver_materiales_stock, name='ver_materiales_stock'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
