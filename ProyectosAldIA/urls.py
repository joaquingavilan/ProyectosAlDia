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
from Aplicacion import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('clientes/registro/', views.registrar_cliente, name='registro_cliente'),
    path('clientes/ver/', views.ver_clientes, name='ver_clientes'),
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('ingenieros/registrar/', views.registrar_ingeniero, name='registrar_ingeniero'),
    path('ingenieros/ver', views.ver_ingenieros, name='ver_ingenieros'),
    path('ingenieros/eliminar/<int:pk>/', views.eliminar_ingeniero, name='eliminar_ingeniero'),
    path('ingenieros/editar/<int:pk>/', views.editar_ingeniero, name='editar_ingeniero')
]
