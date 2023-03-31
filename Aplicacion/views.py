from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from .models import Cliente, Ingeniero, Proveedor, Perfil, Rol
from .forms import *
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import re


def inicio(request):
    return render(request, 'inicio.html')

# VISTAS PARA USUARIOS


def loguear_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            error = 'Nombre de usuario o contraseña incorrectos.'
    else:
        error = ''
    return render(request, 'usuarios/login.html', {'error': error})


def registrar_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            error = 'Las contraseñas no coinciden.'
        elif User.objects.filter(username=username).exists():
            error = 'El nombre de usuario ya está en uso.'
        elif User.objects.filter(email=email).exists():
            error = 'El email ya está registrado.'
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error = "Email inválido."
        elif not re.search(r'[A-Za-z]', username):
            error = "Nombre de usuario inválido."
            return render(request, 'usuarios/registro.html', {'error': error})
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            perfil = Perfil.objects.create(user=user, rol=None)
            user = authenticate(username=username, password=password1)
            login(request, user)
            return redirect('inicio')

        return render(request, 'usuarios/registro.html', {'error': error})
    else:
        error = ''
    return render(request, 'usuarios/registro.html')

def salir_usuario(request):
    logout(request)
    return redirect('login')

#                   VISTAS PARA CLIENTE


def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registro_cliente')
    else:
        form = ClienteForm()

    return render(request, 'clientes/registro_cliente.html', {'form': form})


def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(instance=cliente)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('ver_clientes')
    return render(request, 'clientes/editar_cliente.html', {'form': form})


def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST' and 'confirmar' in request.POST:
        cliente.delete()
        return redirect('ver_clientes')
    return render(request, 'clientes/eliminar_cliente.html', {'cliente': cliente})


def ver_clientes(request):
    clientes = Cliente.objects.all()
    form_buscar = BuscadorClienteForm()
    if request.method == 'GET':
        form_buscar = BuscadorClienteForm(request.GET)
        if form_buscar.is_valid():
            termino_busqueda = form_buscar.cleaned_data['termino_busqueda']
            if termino_busqueda:
                clientes = clientes.filter(Q(ruc__icontains=termino_busqueda) | Q(nombre__icontains=termino_busqueda))

    return render(request, 'clientes/ver_clientes.html', {'clientes': clientes, 'form_buscar': form_buscar})

#                   VISTAS PARA INGENIERO


def registrar_ingeniero(request):
    if request.method == 'POST':
        form = IngenieroForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = request.POST['username']
            if User.objects.filter(username=username).exists():
                error = 'El nombre de usuario ya está en uso.'
            elif User.objects.filter(email=email).exists():
                error = 'El email ya está registrado.'
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                error = "Email inválido."
            elif not re.search(r'[A-Za-z]', username):
                error = "Nombre de usuario inválido."
            else:
                ingeniero = form.save()
                usuario = User.objects.create_user(username=username, password='12345', email=email)
                rol = Rol.objects.get(nombre='INGENIERO')
                perfil = Perfil.objects.create(user=usuario, rol=rol)
                return redirect('ver_ingenieros')

            return render(request, 'ingenieros/registrar_ingeniero.html', {'form': form, 'error': error})
    else:
        form = IngenieroForm()
        error = ''
    return render(request, 'ingenieros/registrar_ingeniero.html', {'form': form, 'error': error})


def ver_ingenieros(request):
    form_buscar = BuscadorIngenieroForm()
    ingenieros = Ingeniero.objects.all()
    usuarios_ingenieros = User.objects.filter(perfil__rol=Rol.objects.get(nombre='INGENIERO'))

    if request.method == 'POST':
        form_buscar = BuscadorIngenieroForm(request.POST)
        if form_buscar.is_valid():
            termino_busqueda = form_buscar.cleaned_data['termino_busqueda']
            ingenieros = Ingeniero.objects.filter(
                Q(nombre__icontains=termino_busqueda) | Q(apellido__icontains=termino_busqueda)
            )

    return render(request, 'ingenieros/ver_ingenieros.html', {'ingenieros': ingenieros, 'form_buscar': form_buscar})


def editar_ingeniero(request, pk):
    ingeniero = get_object_or_404(Ingeniero, pk=pk)
    if request.method == 'POST':
        form = IngenieroForm(request.POST, instance=ingeniero)
        if form.is_valid():
            form.save()
            return redirect('ver_ingenieros')
    else:
        form = IngenieroForm(instance=ingeniero)
    return render(request, 'ingenieros/editar_ingeniero.html', {'form': form, 'ingeniero': ingeniero})


def eliminar_ingeniero(request, pk):
    ingeniero = get_object_or_404(Ingeniero, pk=pk)
    if User.objects.filter(email=ingeniero.email):
        user = User.objects.get(email=ingeniero.email)
        perfil = user.perfil
    else:
        user = None
        perfil = None
    if request.method == 'POST' and 'confirmar' in request.POST:
        ingeniero.delete()
        if user and perfil:
            user.delete()
            perfil.delete()
        return redirect('ver_ingenieros')

    return render(request, 'ingenieros/eliminar_ingeniero.html', {'ingeniero': ingeniero})

#                   VISTAS PARA PROVEEDOR


def registrar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_proveedores')
    else:
        form = ProveedorForm()

    return render(request, 'proveedores/registrar_proveedor.html', {'form': form})


def ver_proveedores(request):
    proveedores = Proveedor.objects.all()
    form_buscar = BuscadorProveedorForm()
    if request.method == 'GET':
        form_buscar = BuscadorProveedorForm(request.GET)
        if form_buscar.is_valid():
            termino_busqueda = form_buscar.cleaned_data['termino_busqueda']
            if termino_busqueda:
                if termino_busqueda.isdigit():
                    proveedores = proveedores.filter(ruc__icontains=termino_busqueda)
                else:
                    proveedores = proveedores.filter(nombre__icontains=termino_busqueda)

    return render(request, 'proveedores/ver_proveedores.html', {'proveedores': proveedores, 'form_buscar': form_buscar})


def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)

    if request.method == 'POST' and 'confirmar' in request.POST:
        proveedor.delete()
        return redirect('ver_proveedores')
    return render(request, 'proveedores/eliminar_proveedor.html', {'proveedor': proveedor})


def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    form = ProveedorForm(instance=proveedor)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect('ver_proveedores')

    return render(request, 'proveedores/editar_proveedor.html', {'form': form, 'proveedor': proveedor})

#                   VISTAS PARA MATERIAL


def registrar_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('ver_materiales')
    else:
        form = MaterialForm()
    return render(request, 'materiales/registrar_material.html', {'form': form})


def ver_materiales(request):
    materiales = Material.objects.all()
    form_buscar = BuscadorMaterialForm()
    if request.method == 'GET':
        form_buscar = BuscadorMaterialForm(request.GET)
        if form_buscar.is_valid():
            termino_busqueda = form_buscar.cleaned_data['termino_busqueda']
            if termino_busqueda:
                materiales = materiales.filter(nombre__icontains=termino_busqueda)

    return render(request, 'materiales/ver_materiales.html', {'materiales': materiales, 'form_buscar': form_buscar})


def editar_material(request, pk):
    material = get_object_or_404(Material, id=pk)

    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            return redirect('ver_materiales')
    else:
        form = MaterialForm(instance=material)

    return render(request, 'materiales/editar_material.html', {'form': form})


def eliminar_material(request, pk):
    material = get_object_or_404(Material, id=pk)

    if request.method == 'POST':
        material.delete()
        return redirect('ver_materiales')

    return render(request, 'materiales/eliminar_material.html', {'material': material})



