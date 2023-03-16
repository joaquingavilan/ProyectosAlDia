from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from .models import Cliente, Ingeniero
from .forms import ClienteForm, IngenieroForm, BuscadorIngenieroForm, BuscadorClienteForm
from django.db.models import Q


def inicio(request):
    return render(request, 'inicio.html')


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

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('ver_clientes')
    else:
        form = ClienteForm(instance=cliente)

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


def registrar_ingeniero(request):
    if request.method == 'POST':
        form = IngenieroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_ingenieros')
    else:
        form = IngenieroForm()
    return render(request, 'ingenieros/registrar_ingeniero.html', {'form': form})


def ver_ingenieros(request):
    form_buscar = BuscadorIngenieroForm()
    ingenieros = Ingeniero.objects.all()

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

    if request.method == 'POST' and 'confirmar' in request.POST:
        ingeniero.delete()
        return redirect('ver_ingenieros')

    return render(request, 'ingenieros/eliminar_ingeniero.html', {'ingeniero': ingeniero})
