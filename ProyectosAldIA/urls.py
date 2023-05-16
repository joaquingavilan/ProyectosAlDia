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
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('ingenieros/registrar/', views.registrar_ingeniero, name='registrar_ingeniero'),
    path('ingenieros/ver', views.ver_ingenieros, name='ver_ingenieros'),
    path('ingenieros/editar/<int:pk>/', views.editar_ingeniero, name='editar_ingeniero'),
    path('ingenieros/eliminar/<int:pk>/', views.eliminar_ingeniero, name='eliminar_ingeniero'),
    path('proveedores/registro/', views.registrar_proveedor, name='registrar_proveedor'),
    path('proveedores/ver/', views.ver_proveedores, name='ver_proveedores'),
    path('proveedores/editar/<int:pk>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/<int:pk>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('materiales/registro/', views.registrar_material, name='registrar_material'),
    path('materiales/ver/', views.ver_materiales, name='ver_materiales'),
    path('materiales/editar/<int:pk>/', views.editar_material, name='editar_material'),
    path('materiales/eliminar/<int:pk>/', views.eliminar_material, name='eliminar_material'),
    path('ABM/usuarios/login/', views.loguear_usuario, name='login'),
    path('usuarios/registro/', views.registrar_usuario, name='registro'),
    path('usuarios/salir/', views.salir_usuario, name='salir'),
    path('proyectos/registro/', views.registrar_proyecto, name='registrar_proyecto'),
    path('proyectos/ver/', views.ver_proyectos, name='ver_proyectos'),
    path('proyectos/eliminar/<int:pk>/', views.eliminar_proyecto, name='eliminar_proyecto'),
    path('proyectos/modificar/<int:pk>/', views.modificar_proyecto, name='modificar_proyecto'),
    path('pantallas_ing/ver_presupuestos/', views.ver_presupuestos, name='ver_presupuestos'),
    path('pantallas_ing/ver_obras/', views.ver_obras, name='ver_obras'),
    path('pedido_materiales/', views.pedido_materiales, name='pedido_materiales'),
    path('confirmar_pedido/', views.confirmar_pedido, name='confirmar_pedido'),
    path('ver_pedidos/', views.ver_pedidos, name='ver_pedidos'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
