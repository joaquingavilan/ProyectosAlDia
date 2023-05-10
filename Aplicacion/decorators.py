from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from .models import Rol
from django.shortcuts import redirect


def gerente_required(function=None):
    def wrapper(request, *args, **kwargs):
        if request.user.perfil.rol.nombre == 'GERENTE':
            return function(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return wrapper


def administrador_required(function=None):
    def wrapper(request, *args, **kwargs):
        if request.user.perfil.rol.nombre == 'ADMINISTRADOR':
            return function(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return wrapper


def ingeniero_required(function=None):
    def wrapper(request, *args, **kwargs):
        if request.user.perfil.rol.nombre == 'INGENIERO':
            return function(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return wrapper
