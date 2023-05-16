from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from .models import Cliente, Proveedor, Perfil, Rol, Presupuesto, Proyecto, Obra, Material, Pedido, MaterialPedido
from .forms import *
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
import re, locale
from datetime import date
from .decorators import gerente_required, administrador_required, ingeniero_required


def inicio(request):
    perfil = Perfil.objects.get(user=request.user)
    rol_usuario = perfil.rol.nombre
    if rol_usuario == 'Gerente':
        return render(request, 'inicios/inicio.html')
    elif rol_usuario == 'Administrador':
        return render(request, 'inicios/inicio.html')
    elif rol_usuario == 'Ingeniero':
        return render(request, 'inicios/inicio_ingenieros.html')
    else:
        return render(request, 'inicios/inicio.html')


def inicio_ingenieros(request):
    nombre = request.user.first_name
    return render(request, 'inicios/inicio_ingenieros.html', {'nombre': nombre})

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
    return render(request, 'ABM/usuarios/login.html', {'error': error})


def registrar_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        first_name = request.POST['first_name']  # nombre
        last_name = request.POST['last_name']  # apellido
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
            user = User.objects.create_user(username=username, email=email, password=password1, first_name=first_name, last_name=last_name)
            perfil = Perfil.objects.create(user=user, rol=Rol.objects.get(nombre='INGENIERO'))
            user = authenticate(username=username, password=password1)
            login(request, user)
            return redirect('inicio')

        return render(request, 'ABM/usuarios/registro.html', {'error': error})
    else:
        error = ''
    return render(request, 'ABM/usuarios/registro.html')


def salir_usuario(request):
    logout(request)
    return redirect('login')

#                   VISTAS PARA CLIENTE


def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_clientes')
    else:
        form = ClienteForm()

    return render(request, 'ABM/clientes/registro_cliente.html', {'form': form})


def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(instance=cliente)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('ver_clientes')
    return render(request, 'ABM/clientes/editar_cliente.html', {'form': form})


def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST' and 'confirmar' in request.POST:
        cliente.delete()
        return redirect('ver_clientes')
    return render(request, 'ABM/clientes/eliminar_cliente.html', {'cliente': cliente})


def ver_clientes(request):
    clientes = Cliente.objects.all()
    form_buscar = BuscadorClienteForm()
    if request.method == 'GET':
        form_buscar = BuscadorClienteForm(request.GET)
        if form_buscar.is_valid():
            termino_busqueda = form_buscar.cleaned_data['termino_busqueda']
            if termino_busqueda:
                clientes = clientes.filter(Q(ruc__icontains=termino_busqueda) | Q(nombre__icontains=termino_busqueda))

    return render(request, 'ABM/clientes/ver_clientes.html', {'clientes': clientes, 'form_buscar': form_buscar})

#                   VISTAS PARA INGENIERO


def registrar_ingeniero(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = request.POST['username']
            password = request.POST['password1']
            # Verificar si el nombre de usuario ya está en uso
            if User.objects.filter(username=username).exists():
                error = 'El nombre de usuario ya está en uso.'
                return render(request, 'ABM/ingenieros/registrar_ingeniero.html', {'form': form, 'error': error})
            elif User.objects.filter(email=email).exists():
                error = 'El email ya está registrado.'
                return render(request, 'ABM/ingenieros/registrar_ingeniero.html', {'form': form, 'error': error})
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                error = "Email inválido."
                return render(request, 'ABM/ingenieros/registrar_ingeniero.html', {'form': form, 'error': error})
            elif not re.search(r'[A-Za-z]', username):
                error = "Nombre de usuario inválido."
                return render(request, 'ABM/ingenieros/registrar_ingeniero.html', {'form': form, 'error': error})
            else:
                usuario = User.objects.create_user(username=username, first_name=request.POST['first_name'], last_name=request.POST['last_name'], password=password, email=email)
                rol = Rol.objects.get(nombre='INGENIERO')
                perfil = Perfil.objects.create(user=usuario, rol=rol)
                return redirect('ver_ingenieros')
        else:
            form = CustomUserCreationForm(request.POST)
            error = ''
            return render(request, 'ABM/ingenieros/registrar_ingeniero.html', {'form': form, 'error': error})

    else:
        form = CustomUserCreationForm()
        error = ''
        return render(request, 'ABM/ingenieros/registrar_ingeniero.html', {'form': form, 'error': error})


def ver_ingenieros(request):
    usuarios_ingenieros = User.objects.filter(perfil__rol=Rol.objects.get(nombre='INGENIERO'))
    return render(request, 'ABM/ingenieros/ver_ingenieros.html', {'ingenieros': usuarios_ingenieros})


def editar_ingeniero(request, pk):
    ingeniero = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=ingeniero)
        if form.is_valid():
            form.save()
            return redirect('ver_ingenieros')
    else:
        return render(request, 'ABM/ingenieros/editar_ingeniero.html', {'form': CustomUserChangeForm(instance=ingeniero), 'ingeniero': ingeniero})
    return render(request, 'ABM/ingenieros/editar_ingeniero.html', {'form': CustomUserChangeForm(instance=ingeniero), 'ingeniero': ingeniero})


def eliminar_ingeniero(request, pk):
    ingeniero = get_object_or_404(User, pk=pk)
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

    return render(request, 'ABM/ingenieros/eliminar_ingeniero.html', {'ingeniero': ingeniero})

#                   VISTAS PARA PROVEEDOR


def registrar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_proveedores')
    else:
        form = ProveedorForm()

    return render(request, 'ABM/proveedores/registrar_proveedor.html', {'form': form})


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

    return render(request, 'ABM/proveedores/ver_proveedores.html', {'proveedores': proveedores, 'form_buscar': form_buscar})


def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)

    if request.method == 'POST' and 'confirmar' in request.POST:
        proveedor.delete()
        return redirect('ver_proveedores')
    return render(request, 'ABM/proveedores/eliminar_proveedor.html', {'proveedor': proveedor})


def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    form = ProveedorForm(instance=proveedor)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect('ver_proveedores')

    return render(request, 'ABM/proveedores/editar_proveedor.html', {'form': form, 'proveedor': proveedor})

#                   VISTAS PARA MATERIAL


def registrar_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('ver_materiales')
    else:
        form = MaterialForm()
    return render(request, 'ABM/materiales/registrar_material.html', {'form': form})


def ver_materiales(request):
    materiales = Material.objects.all()
    form_buscar = BuscadorMaterialForm()
    if request.method == 'GET':
        form_buscar = BuscadorMaterialForm(request.GET)
        if form_buscar.is_valid():
            termino_busqueda = form_buscar.cleaned_data['termino_busqueda']
            if termino_busqueda:
                materiales = materiales.filter(nombre__icontains=termino_busqueda)

    return render(request, 'ABM/materiales/ver_materiales.html', {'materiales': materiales, 'form_buscar': form_buscar})


def editar_material(request, pk):
    material = get_object_or_404(Material, id=pk)

    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            return redirect('ver_materiales')
    else:
        form = MaterialForm(instance=material)

    return render(request, 'ABM/materiales/editar_material.html', {'form': form})


def eliminar_material(request, pk):
    material = get_object_or_404(Material, id=pk)

    if request.method == 'POST':
        material.delete()
        return redirect('ver_materiales')

    return render(request, 'ABM/materiales/eliminar_material.html', {'material': material})


#                   VISTAS PARA PROYECTOS


def registrar_proyecto(request):
    ingenieros = User.objects.filter(perfil__rol__nombre='INGENIERO')
    clientes = Cliente.objects.all()

    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            presupuesto = Presupuesto.objects.create(encargado=form.cleaned_data['encargado'])
            proyecto.presupuesto = presupuesto
            proyecto.cliente = form.cleaned_data['cliente']
            proyecto.nombre = request.POST.get('nombre')
            proyecto.obra = Obra.objects.create()
            proyecto.save()
            return redirect('ver_proyectos')
    else:
        form = ProyectoForm()
    return render(request, 'ABM/proyectos/registrar_proyecto.html', {'form': form, 'ingenieros': ingenieros, 'clientes': clientes})


def ver_proyectos(request):
    proyectos = Proyecto.objects.all()
    for proyecto in proyectos:
        print("Proyecto:", proyecto.nombre)
        print("Cliente:", proyecto.cliente.nombre)
        print("Encargado de presupuesto:", proyecto.presupuesto.encargado.first_name, proyecto.presupuesto.encargado.last_name if proyecto.presupuesto.encargado else "-")
        print("Estado de presupuesto:", proyecto.presupuesto.get_estado_display())
    return render(request, 'ABM/proyectos/ver_proyectos.html', {'proyectos': proyectos})


def eliminar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)

    if request.method == 'POST' and 'confirmar' in request.POST:
        proyecto.delete()
        return redirect('ver_proyectos')

    return render(request, 'ABM/proyectos/eliminar_proyecto.html', {'proyecto': proyecto})


def modificar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    clientes = Cliente.objects.all()
    ingenieros = User.objects.filter(perfil__rol=Rol.objects.get(nombre='INGENIERO'))
    if request.method == 'POST':
        cliente = request.POST['cliente']
        encargado_obra = request.POST['encargado_obra']
        encargado_presupuesto = request.POST['encargado_presupuesto']
        nombre_proyecto = request.POST['nombre']
        proyecto.cliente = Cliente.objects.get(id=cliente)
        proyecto.nombre = nombre_proyecto
        proyecto.presupuesto.encargado = User.objects.get(id=encargado_presupuesto)
        proyecto.presupuesto.save()
        if encargado_obra != '':
            proyecto.obra.encargado = User.objects.get(id=encargado_obra)
            proyecto.obra.save()
        proyecto.save()
        return redirect('ver_proyectos')
    return render(request, 'ABM/proyectos/modificar_proyecto.html', {'proyecto': proyecto, 'clientes': clientes, 'ingenieros': ingenieros})


# vistas para inicio_ingenieros


def ver_presupuestos(request):
    # falta verificar que el monto total sea valido y mostrar la misma pagina con el error si no lo es
    presupuestos = Presupuesto.objects.filter(encargado=request.user)
    # Configurar el locale y el formato de moneda
    locale.setlocale(locale.LC_ALL, 'gn_PY.UTF-8')
    for presupuesto in presupuestos:
        if presupuesto.monto_total is not None:
            presupuesto.monto_total = locale.format_string('%.f', presupuesto.monto_total, grouping=True)

    if request.method == 'POST':
        presupuesto_id = request.POST.get('presupuesto_id')
        monto_total = request.POST.get('monto_total')
        monto_total = monto_total.replace('.', '')
        estado = request.POST.get('estado')

        presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id)
        presupuesto.monto_total = monto_total
        presupuesto.estado = estado
        presupuesto.save()
        return redirect('ver_presupuestos')

    return render(request, 'pantallas_ing/ver_presupuestos.html', {'presupuestos': presupuestos})


def ver_obras(request):
    obras = Obra.objects.filter(encargado=request.user)
    if request.method == 'POST':
        obra_id = request.POST.get('obra_id')
        estado = request.POST.get('estado')
        obra = Obra.objects.get(id=obra_id)

        if estado == 'E':
            # si el estado se cambia a 'En ejecución', actualizamos la fecha de inicio
            obra.fecha_inicio = timezone.now().date()

        if estado == 'F':
            # si el estado se cambia a 'Finalizada', actualizamos la fecha de fin
            obra.fecha_fin = timezone.now().date()

        obra.estado = estado
        obra.save()

    return render(request, 'pantallas_ing/ver_obras.html', {'obras': obras})


def pedido_materiales(request):
    # Obtener todas las obras del ingeniero logueado
    obras = Obra.objects.filter(encargado=request.user)

    # Obtener todos los materiales disponibles
    materiales = Material.objects.all()
    search_query = ''
    context = {
        'obras': obras,
        'materiales': materiales,
        'search_query': search_query
    }
    # Manejar el formulario de búsqueda
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        if search_query:
            # Filtrar los materiales por nombre o marca según la búsqueda
            materiales = materiales.filter(
                Q(nombre__icontains=search_query) |
                Q(marca__icontains=search_query)
            )
    # Recibir los materiales seleccionados y mandarlos a la siguiente pantalla
    if request.method == 'POST':
        materiales_pedido = []
        obra = Obra.objects.get(id=request.POST.get('obra'))
        for key, value in request.POST.items():
            if key.startswith('cantidad_') and int(value) > 0:
                material_id = key.split('_')[1]
                material = Material.objects.get(id=material_id)
                cantidad = int(value)
                materiales_pedido.append({'material': material, 'cantidad': cantidad})
        # Pasa los materiales del pedido a la plantilla para mostrarlos
        context = {'materiales_pedido': materiales_pedido, 'obra': obra}
        return render(request, 'pantallas_ing/confirmar_pedido.html', context)
    return render(request, 'pantallas_ing/pedido_materiales.html', context)


def confirmar_pedido(request):
    if request.method == 'POST':
        # Obtener los materiales seleccionados del formulario
        materiales_pedido = []
        for key, value in request.POST.items():
            if key.startswith('cantidad_') and int(value) > 0:
                material_id = key.split('_')[1]
                material = Material.objects.get(id=material_id)
                cantidad = int(value)
                materiales_pedido.append({'material': material, 'cantidad': cantidad})

        # Crear el objeto Pedido y guardar en la base de datos
        pedido = Pedido.objects.create(
            solicitante=request.user,
            obra=Obra.objects.get(id=request.POST.get('obra')),
            fecha_solicitud=date.today(),
            fecha_entrega=None,
            estado='P'
        )

        # Crear los objetos MaterialPedido y guardar en la base de datos
        for material_pedido in materiales_pedido:
            material = material_pedido['material']
            cantidad = material_pedido['cantidad']
            MaterialPedido.objects.create(pedido=pedido, material=material, cantidad=cantidad)

        # Redirigir a una página de éxito o realizar alguna acción adicional
        return redirect('inicio_ingenieros')  # Reemplaza 'pagina_de_exito' con la URL a

