from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from .models import Cliente, Proveedor, Perfil, Rol, Presupuesto, Proyecto, Obra, Material, Pedido, MaterialPedido, Contacto
from .forms import *
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
import re, locale, json
from datetime import date
from django.contrib import messages
from .decorators import gerente_required, administrador_required, ingeniero_required
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from openpyxl import Workbook
from openpyxl.utils import get_column_letter



def inicio(request):
    perfil = Perfil.objects.get(user=request.user)
    rol_usuario = perfil.rol.nombre
    if rol_usuario == 'GERENTE':
        return render(request, 'inicios/inicio.html')
    elif rol_usuario == 'ADMINISTRADOR':
        return render(request, 'inicios/inicio.html')
    elif rol_usuario == 'INGENIERO':
        return redirect(inicio_ingenieros)


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
        cliente_form = ClienteForm(request.POST)

        # Extraemos la data de los contactos desde el request.
        # La estructura de contactos_data será una lista de diccionarios, donde cada diccionario tiene la información de un contacto.
        contactos_data = request.POST.getlist('contactos[]')
        contactos_list = [(contactos_data[i], contactos_data[i + 1]) for i in range(0, len(contactos_data), 2)]

        if cliente_form.is_valid():
            cliente = cliente_form.save()

            # Ahora, para cada contacto en contactos_data, lo creamos y asociamos con el cliente.
            for nombre_contacto, numero_contacto in contactos_list:
                Contacto.objects.create(nombre=nombre_contacto, numero=numero_contacto, cliente=cliente)

            return redirect('ver_clientes')
        else:
            # Si hay un error en el formulario, lo retornamos como una respuesta JSON.
            # Esto es útil para manejar errores de validación en el frontend si decides implementar una respuesta AJAX en el futuro.
            return JsonResponse({'error': 'Datos inválidos'}, status=400)

    else:
        form = ClienteForm()

    return render(request, 'ABM/clientes/registro_cliente.html', {'form': form})


def get_cliente_data(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    data = {
        "nombre": cliente.nombre,
        "ruc": cliente.ruc,
        "email": cliente.email
        # ... otros campos ...
    }
    return JsonResponse(data)


def get_contactos_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    contactos = cliente.contacto_set.all()

    data_contactos = [{"id":contacto.id, "nombre": contacto.nombre, "numero": contacto.numero} for contacto in contactos]
    return JsonResponse({"contactos": data_contactos})


def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(instance=cliente)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success"})
        else:
            # En caso de que el formulario no sea válido, devolvemos los errores en formato JSON
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    return render(request, 'ABM/clientes/editar_cliente.html', {'form': form})


def ver_clientes(request):
    clientes = Cliente.objects.all()
    form_buscar = BuscadorClienteForm()

    # Configuración de la paginación
    paginator = Paginator(clientes, 10)  # Muestra 10 clientes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        cliente = get_object_or_404(Cliente, pk=cliente_id)

        proyectos_asociados = Proyecto.objects.filter(cliente=cliente)

        if proyectos_asociados.exists():
            messages.error(request, 'El cliente tiene proyectos activos y no puede ser eliminado')
        else:
            cliente.delete()
            messages.success(request, 'Cliente eliminado exitosamente')
            return redirect('ver_clientes')

    elif request.method == 'GET':
        form_buscar = BuscadorClienteForm(request.GET)
        if form_buscar.is_valid():
            termino_busqueda = form_buscar.cleaned_data['termino_busqueda']
            if termino_busqueda:
                clientes = clientes.filter(Q(ruc__icontains=termino_busqueda) | Q(nombre__icontains=termino_busqueda))

    return render(request, 'ABM/clientes/ver_clientes.html', {'clientes': clientes, 'form_buscar': form_buscar, 'page_obj': page_obj})


def buscar_clientes(request):
    query = request.GET.get('q', '')
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=query) |
        Q(ruc__icontains=query)
    )
    data = [{'id': cliente.id, 'nombre': cliente.nombre, 'ruc': cliente.ruc} for cliente in clientes]
    return JsonResponse(data, safe=False)


def ver_cliente(request, id_cliente):
    cliente = Cliente.objects.get(pk=id_cliente)
    return render(request, 'ABM/clientes/ver_cliente.html', {'cliente': cliente})


def agregar_contacto(request, tipo, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        nombre = data.get('nombre')
        numero = data.get('numero')
        print(nombre)
        print(numero)
        contacto = Contacto(nombre=nombre, numero=numero)
        if tipo == 'cliente':
            contacto.cliente = Cliente.objects.get(pk=id)
        elif tipo == 'proveedor':
            contacto.proveedor = Proveedor.objects.get(pk=id)
        else:
            return JsonResponse({'status': 'error', 'message': 'Tipo no válido'})
        contacto.save()

        return JsonResponse({'status': 'success', 'message': 'Contacto agregado correctamente'})


def eliminar_contacto(request, contacto_id):
    if request.method == 'POST':
        contacto = Contacto.objects.get(pk=contacto_id)
        contacto.delete()

        return JsonResponse({'status': 'success', 'message': 'Contacto eliminado correctamente'})

#                   VISTAS PARA INGENIERO


def registrar_ingeniero(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = request.POST['username']
            password = request.POST['password1']
            nombre = request.POST['first_name']
            apellido = request.POST['last_name']
            if User.objects.filter(username=username).exists():
                error = 'El nombre de usuario ya está en uso.'
                return render(request, 'ABM/ingenieros/registrar_ingeniero.html', {'form': form, 'error': error})
            elif not re.match(r'^[A-Za-z]+$', nombre):
                error = "Nombre inválido. Solo se permiten letras."
                return render(request, 'ABM/ingenieros/registrar_ingeniero.html', {'form': form, 'error': error})
            elif not re.match(r'^[A-Za-z]+$', apellido):
                error = "Apellido inválido. Solo se permiten letras."
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

    # Configuración de la paginación
    paginator = Paginator(usuarios_ingenieros, 10)  # Muestra 10 ingenieros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ABM/ingenieros/ver_ingenieros.html', {'page_obj': page_obj})


def editar_ingeniero(request, pk):
    ingeniero = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=ingeniero)
        if form.is_valid():
            nombre = request.POST['first_name']
            apellido = request.POST['last_name']
            email = form.cleaned_data['email']
            if not re.match(r'^[A-Za-z]+$', nombre):
                error = "Nombre inválido. Solo se permiten letras."
                return render(request, 'ABM/ingenieros/editar_ingeniero.html', {'form': CustomUserChangeForm(instance=ingeniero), 'ingeniero': ingeniero, 'error':error})
            elif not re.match(r'^[A-Za-z]+$', apellido):
                error = "Apellido inválido. Solo se permiten letras."
                return render(request, 'ABM/ingenieros/editar_ingeniero.html', {'form': CustomUserChangeForm(instance=ingeniero), 'ingeniero': ingeniero, 'error':error})
            elif User.objects.filter(email=email).exists() and email != ingeniero.email:
                error = 'El email ya está registrado.'
                return render(request, 'ABM/ingenieros/editar_ingeniero.html', {'form': CustomUserChangeForm(instance=ingeniero), 'ingeniero': ingeniero, 'error':error})
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                error = "Email inválido."
                return render(request, 'ABM/ingenieros/editar_ingeniero.html', {'form': CustomUserChangeForm(instance=ingeniero), 'ingeniero': ingeniero, 'error':error})
            else:
                form.save()
                return redirect('ver_ingenieros')
    else:
        return render(request, 'ABM/ingenieros/editar_ingeniero.html', {'form': CustomUserChangeForm(instance=ingeniero), 'ingeniero': ingeniero})
    return render(request, 'ABM/ingenieros/editar_ingeniero.html', {'form': CustomUserChangeForm(instance=ingeniero), 'ingeniero': ingeniero})


def eliminar_ingeniero(request, pk):
    ingeniero = get_object_or_404(User, pk=pk)

    # Verificamos si el ingeniero tiene obras o presupuestos asociados que no estén en los estados mencionados.
    obras_asociadas = Obra.objects.filter(encargado=ingeniero).exclude(estado='F')
    presupuestos_asociados = Presupuesto.objects.filter(encargado=ingeniero).exclude(estado='A')
    # Si tiene recursos asociados, obtenemos una lista de todos los ingenieros disponibles para la reasignación
    if obras_asociadas.exists() or presupuestos_asociados.exists():
        otros_ingenieros = Perfil.objects.filter(rol__nombre='INGENIERO').exclude(user=ingeniero).all()
    else:
        otros_ingenieros = []

    if request.method == 'POST' and 'confirmar' in request.POST:
        reasignaciones_completas = True
        # Reasignamos cada recurso al ingeniero seleccionado en la lista desplegable
        if obras_asociadas:
            for obra in obras_asociadas:
                nuevo_ingeniero_id = request.POST.get(f"reassign_obra_{obra.id}")
                if nuevo_ingeniero_id:
                    obra_original = get_object_or_404(Obra, pk=obra.pk)
                    obra_original.encargado = User.objects.get(pk=nuevo_ingeniero_id)
                    obra_original.save()
                else:
                    reasignaciones_completas = False
        if presupuestos_asociados:
            for presupuesto in presupuestos_asociados:
                nuevo_ingeniero_id = request.POST.get(f"reassign_presupuesto_{presupuesto.id}")
                if nuevo_ingeniero_id:
                    presupuesto_original = get_object_or_404(Presupuesto, pk=presupuesto.pk)
                    presupuesto_original.encargado = User.objects.get(pk=nuevo_ingeniero_id)
                    presupuesto_original.save()
                else:
                    reasignaciones_completas = False
        # Ahora podemos eliminar al ingeniero original
        if reasignaciones_completas:
            ingeniero.delete()
            return redirect('ver_ingenieros')
        else:
            messages.error(request, 'No se pudo eliminar el ingeniero porque no se asignaron otros ingenieros a los recursos asociados.')
    context = {
        'ingeniero': ingeniero,
        'obras_asociadas': obras_asociadas,
        'presupuestos_asociados': presupuestos_asociados,
        'otros_ingenieros': otros_ingenieros
    }
    return render(request, 'ABM/ingenieros/eliminar_ingeniero.html', context)


def buscar_ingenieros(request):
    query = request.GET.get('q', '')
    ingenieros = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query),
        perfil__rol=Rol.objects.get(nombre='INGENIERO')
    )
    data = [{'id': ingeniero.id, 'username': ingeniero.username, 'nombre': ingeniero.first_name, 'apellido': ingeniero.last_name} for ingeniero in ingenieros]
    return JsonResponse(data, safe=False)


def ver_ingeniero(request, id_ingeniero):
    ingeniero = User.objects.get(pk=id_ingeniero)
    return render(request, 'ABM/ingenieros/ver_ingeniero.html', {'ingeniero': ingeniero})


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
    # Configuración de la paginación
    paginator = Paginator(proveedores, 10)  # Muestra 10 ingenieros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'GET':
        form_buscar = BuscadorProveedorForm(request.GET)
        if form_buscar.is_valid():
            termino_busqueda = form_buscar.cleaned_data['termino_busqueda']
            if termino_busqueda:
                if termino_busqueda.isdigit():
                    proveedores = proveedores.filter(ruc__icontains=termino_busqueda)
                else:
                    proveedores = proveedores.filter(nombre__icontains=termino_busqueda)

    return render(request, 'ABM/proveedores/ver_proveedores.html', {'proveedores': proveedores, 'form_buscar': form_buscar, 'page_obj': page_obj})


def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)

    # Verificamos si el proveedor tiene materiales asociados
    materiales_asociados = Material.objects.filter(id_proveedor=proveedor.pk)

    # Si tiene materiales asociados, obtenemos una lista de todos los proveedores disponibles para la reasignación
    if materiales_asociados.exists():
        otros_proveedores = Proveedor.objects.exclude(pk=proveedor.pk).all()
    else:
        otros_proveedores = []

    if request.method == 'POST' and 'confirmar' in request.POST:
        reasignaciones_completas = True

        # Reasignamos cada material al proveedor seleccionado en la lista desplegable
        for material in materiales_asociados:
            nuevo_proveedor_id = request.POST.get(f"reassign_material_{material.id}")
            if nuevo_proveedor_id:
                material_original = get_object_or_404(Material, pk=material.pk)
                material_original.id_proveedor = Proveedor.objects.get(pk=nuevo_proveedor_id)
                material_original.save()
            else:
                reasignaciones_completas = False

        # Si todas las reasignaciones están completas, eliminamos al proveedor
        if reasignaciones_completas:
            proveedor.delete()
            return redirect('ver_proveedores')
        else:
            # Añadimos un mensaje indicando que no se pudo eliminar al proveedor
            messages.error(request, 'El proveedor tiene materiales asociados, reasignelos a otro proveedor o elimine el material desde la pantalla de Materiales.')

    context = {
        'proveedor': proveedor,
        'materiales_asociados': materiales_asociados,
        'otros_proveedores': otros_proveedores
    }
    return render(request, 'ABM/proveedores/eliminar_proveedor.html', context)


def get_proveedor_data(request, proveedor_id):
    proveedor = Proveedor.objects.get(pk=proveedor_id)
    data = {
        "nombre": proveedor.nombre,
        "ruc": proveedor.ruc,
        "email": proveedor.email
        # ... otros campos ...
    }
    return JsonResponse(data)


def get_contactos_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
    contactos = proveedor.contacto_set.all()

    data_contactos = [{"id":contacto.id, "nombre": contacto.nombre, "numero": contacto.numero} for contacto in contactos]
    return JsonResponse({"contactos": data_contactos})


def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    form = ProveedorForm(instance=proveedor)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "Proveedor actualizado con éxito"})
        else:
            # En caso de que el formulario no sea válido, devolvemos los errores en formato JSON
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    return render(request, 'ABM/proveedores/editar_proveedor.html', {'form': form})


def buscar_proveedores(request):
    query = request.GET.get('q', '')
    proveedores = Proveedor.objects.filter(
        Q(nombre__icontains=query) |
        Q(ruc__icontains=query)
    )
    data = [{'id': proveedor.id, 'nombre': proveedor.nombre, 'ruc': proveedor.ruc} for proveedor in proveedores]
    return JsonResponse(data, safe=False)


def ver_proveedor(request, id_proveedor):
    proveedor = Proveedor.objects.get(pk=id_proveedor)
    return render(request, 'ABM/proveedores/ver_proveedor.html', {'proveedor': proveedor})


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

    # Configuración de la paginación
    paginator = Paginator(materiales, 10)  # Muestra 10 materiales por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Lógica para eliminar el material
    material_id = request.GET.get('eliminar_material_id')
    if material_id:
        material = get_object_or_404(Material, id=material_id)

        # Verificamos si el material está siendo utilizado en pedidos
        pedidos_asociados = Pedido.objects.filter(materiales=material)

        # Verificamos si las obras asociadas a esos pedidos están activas
        obras_activas_asociadas = Obra.objects.filter(pedido__in=pedidos_asociados, estado='E')

        if obras_activas_asociadas.exists():
            # Si hay obras activas que hacen referencia al material, mostramos un mensaje de error
            messages.error(request, 'No se puede eliminar el material porque está siendo utilizado en obras activas.')
        else:
            material.delete()
            messages.success(request, 'Material eliminado exitosamente.')

    if request.method == 'GET':
        form_buscar = BuscadorMaterialForm(request.GET)
        if form_buscar.is_valid():
            termino_busqueda = form_buscar.cleaned_data['termino_busqueda']
            if termino_busqueda:
                materiales = materiales.filter(nombre__icontains=termino_busqueda)

    return render(request, 'ABM/materiales/ver_materiales.html', {'materiales': materiales, 'form_buscar': form_buscar, 'page_obj': page_obj})


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


def buscar_materiales(request):
    query = request.GET.get('q', '')
    materiales = Material.objects.filter(
        Q(nombre__icontains=query)
    )
    data = [{'id': material.id, 'nombre': material.nombre} for material in materiales]
    return JsonResponse(data, safe=False)


def ver_material(request, id_material):
    material = Material.objects.get(pk=id_material)
    return render(request, 'ABM/materiales/ver_material.html', {'material': material})


#                   VISTAS PARA PROYECTOS


def registrar_proyecto(request):
    ingenieros = User.objects.filter(perfil__rol__nombre='INGENIERO')
    clientes = Cliente.objects.all()

    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            presupuesto = Presupuesto(encargado=form.cleaned_data['encargado'])
            proyecto.cliente = form.cleaned_data['cliente']
            proyecto.nombre = request.POST.get('nombre')
            proyecto.ciudad = request.POST.get('ciudad')
            obra = Obra()

            # Primero guardamos el proyecto para obtener su ID
            proyecto.save()

            # Luego asignamos el proyecto a las instancias de Presupuesto y Obra
            presupuesto.proyecto = proyecto
            presupuesto.save()
            obra.proyecto = proyecto
            obra.save()

            # Ahora asignamos las instancias de Presupuesto y Obra al Proyecto
            proyecto.presupuesto = presupuesto
            proyecto.obra = obra
            proyecto.save()

            return redirect('ver_proyectos')
    else:
        form = ProyectoForm()
    return render(request, 'ABM/proyectos/registrar_proyecto.html',
                  {'form': form, 'ingenieros': ingenieros, 'clientes': clientes})


def ver_proyectos(request):
    proyectos = Proyecto.objects.all()
    # Configuración de la paginación
    paginator = Paginator(proyectos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ABM/proyectos/ver_proyectos.html', {'proyectos': proyectos,'page_obj':page_obj})


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


def buscar_proyectos(request):
    query = request.GET.get('q', '')
    proyectos = Proyecto.objects.filter(
        Q(nombre__icontains=query)
    )
    data = [{'id': proyecto.id, 'nombre': proyecto.nombre} for proyecto in proyectos]
    return JsonResponse(data, safe=False)


def ver_proyecto(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    return render(request, 'ABM/proyectos/ver_proyecto.html', {'proyecto': proyecto})


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
    # Manejar el formulario de búsqueda
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        if search_query:
            # Filtrar los materiales por nombre o marca según la búsqueda
            materiales = materiales.filter(
                Q(nombre__icontains=search_query) |
                Q(marca__icontains=search_query)
            )
    context = {
        'obras': obras,
        'materiales': materiales,
        'search_query': search_query
    }
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


def ver_pedidos(request):
    # Obtener todos los pedidos del usuario actualmente logueado
    pedidos = Pedido.objects.filter(solicitante=request.user)

    context = {
        'pedidos': pedidos
    }
    return render(request, 'pantallas_ing/ver_pedidos.html', context)


# vistas para filtros


def obtener_clientes_con_proyectos(request):
    clientes = Proyecto.objects.values_list('cliente__nombre', flat=True).distinct()
    return JsonResponse(list(clientes), safe=False)


def obtener_ingenieros_presupuesto(request):
    ingenieros = Presupuesto.objects.values_list('encargado__username', flat=True).distinct()
    return JsonResponse(list(ingenieros), safe=False)


def obtener_estados_presupuesto(request):
    # Obtener los estados que realmente están en la base de datos
    estados_presentes = Presupuesto.objects.values_list('estado', flat=True).distinct()
    # Convertir esos estados a sus representaciones legibles
    estados = [dict(Presupuesto.ESTADOS)[estado] for estado in estados_presentes]
    return JsonResponse(list(estados), safe=False)


def obtener_ingenieros_obra(request):
    ingenieros = Obra.objects.values_list('encargado__username', flat=True).distinct()
    return JsonResponse(list(ingenieros), safe=False)


def obtener_estados_obra(request):
    # Obtener los estados que realmente están en la base de datos
    estados_presentes = Obra.objects.values_list('estado', flat=True).distinct()
    # Convertir esos estados a sus representaciones legibles
    estados = [dict(Obra.ESTADOS)[estado] for estado in estados_presentes]
    return JsonResponse(list(estados), safe=False)


def obtener_ciudades_con_proyectos(request):
    ciudades = Proyecto.objects.values_list('ciudad', flat=True).distinct()
    return JsonResponse(list(ciudades), safe=False)


def ver_proyectos_cliente(request, cliente_nombre):
    proyectos = Proyecto.objects.filter(cliente__nombre=cliente_nombre)
    # Configuración de la paginación
    paginator = Paginator(proyectos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ABM/proyectos/ver_proyectos_filtrados.html', {'proyectos': proyectos, 'page_obj': page_obj})


def ver_proyectos_encargado_presupuesto(request, ingeniero_user):
    ingeniero = User.objects.filter(username=ingeniero_user)
    proyectos = Proyecto.objects.filter(presupuesto__encargado__in=ingeniero)
    # Configuración de la paginación
    paginator = Paginator(proyectos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ABM/proyectos/ver_proyectos_filtrados.html', {'proyectos': proyectos, 'page_obj': page_obj})


def ver_proyectos_encargado_obra(request, ingeniero_user):
    ingeniero = User.objects.filter(username=ingeniero_user)
    proyectos = Proyecto.objects.filter(presupuesto__encargado__in=ingeniero)
    # Configuración de la paginación
    paginator = Paginator(proyectos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ABM/proyectos/ver_proyectos_filtrados.html', {'proyectos': proyectos, 'page_obj': page_obj})


def ver_proyectos_estado_presupuesto(request, estado):
    # Convertir el nombre legible del estado a su código correspondiente
    estado_codigo = {value: key for key, value in dict(Presupuesto.ESTADOS).items()}[estado]

    # Filtrar los proyectos basándose en el código del estado
    proyectos = Proyecto.objects.filter(presupuesto__estado=estado_codigo)
    # Configuración de la paginación
    paginator = Paginator(proyectos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ABM/proyectos/ver_proyectos_filtrados.html', {'proyectos': proyectos, 'page_obj': page_obj})


def ver_proyectos_estado_obra(request, estado):
    # Convertir el nombre legible del estado a su código correspondiente
    estado_codigo = {value: key for key, value in dict(Obra.ESTADOS).items()}[estado]

    # Filtrar los proyectos basándose en el código del estado
    proyectos = Proyecto.objects.filter(presupuesto__estado=estado_codigo)
    # Configuración de la paginación
    paginator = Paginator(proyectos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ABM/proyectos/ver_proyectos_filtrados.html', {'proyectos': proyectos, 'page_obj': page_obj})


def ver_proyectos_ciudad(request, ciudad):
    proyectos = Proyecto.objects.filter(ciudad=ciudad)
    # Configuración de la paginación
    paginator = Paginator(proyectos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ABM/proyectos/ver_proyectos_filtrados.html', {'proyectos': proyectos, 'page_obj': page_obj})


def obtener_materiales_marca(request):
    marcas = Material.objects.values_list('marca', flat=True).distinct()
    return JsonResponse(list(marcas), safe=False)


def obtener_materiales_proveedor(request):
    id_proveedores = Material.objects.values_list('id_proveedor', flat=True).distinct()
    lista_proveedores = Proveedor.objects.filter(id__in=id_proveedores)
    proveedores = lista_proveedores.values_list('nombre', flat=True).distinct()
    return JsonResponse(list(proveedores), safe=False)


def obtener_materiales_stock(request):
    cantidades = ['Menos de 10', 'Menos de 50', 'Menos de 100']
    return JsonResponse(list(cantidades), safe=False)


def ver_materiales_marca(request, marca):
    materiales = Material.objects.filter(marca=marca)
    return render(request, 'ABM/materiales/ver_materiales_filtrados.html', {'materiales': materiales})


def ver_materiales_proveedores(request, proveedor):
    id_proveedor = Proveedor.objects.get(nombre=proveedor)
    materiales = Material.objects.filter(id_proveedor=id_proveedor)
    return render(request, 'ABM/materiales/ver_materiales_filtrados.html', {'materiales': materiales})


def ver_materiales_stock(request, cantidad):
    if cantidad == 'Menos de 10':
        materiales = Material.objects.filter(unidades_stock__lt=10)
    elif cantidad == 'Menos de 50':
        materiales = Material.objects.filter(unidades_stock__lt=50)
    elif cantidad == 'Menos de 100':
        materiales = Material.objects.filter(unidades_stock__lt=100)
    return render(request, 'ABM/materiales/ver_materiales_filtrados.html', {'materiales': materiales})


def exportar_excel(request):
    # Crear un nuevo libro de Excel y una nueva hoja
    wb = Workbook()
    ws = wb.active
    tipo_dato = request.POST.get('tipo_dato')  # Por ejemplo, 'Ingenieros', 'Proyectos', etc.
    criterio = request.POST.get('criterio')  # Por ejemplo, el nombre del cliente

    if tipo_dato == 'Ingenieros':
        ws.title = "Ingenieros"
        # Añadir encabezados a la hoja
        encabezados = ['ID', 'Username', 'First Name', 'Last Name', 'Email']
        for col_num, encabezado in enumerate(encabezados, 1):
            col_letter = get_column_letter(col_num)
            ws['{}1'.format(col_letter)] = encabezado
            ws.column_dimensions[col_letter].width = 15

        # Obtener datos de los ingenieros
        ingenieros = User.objects.filter(perfil__rol=Rol.objects.get(nombre='INGENIERO'))

        # Añadir datos a la hoja
        for ingeniero in ingenieros:
            ws.append([ingeniero.id, ingeniero.username, ingeniero.first_name, ingeniero.last_name, ingeniero.email])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Ingenieros.xlsx'
        wb.save(response)

    elif tipo_dato == 'Clientes':
        ws.title = "Clientes"
        # Añadir encabezados a la hoja
        encabezados = ['ID', 'Nombre', 'RUC', 'Email']
        for col_num, encabezado in enumerate(encabezados, 1):
            col_letter = get_column_letter(col_num)
            ws['{}1'.format(col_letter)] = encabezado
            ws.column_dimensions[col_letter].width = 15

        # Obtener datos de los clientes
        clientes = Cliente.objects.all()

        # Añadir datos a la hoja
        for cliente in clientes:
            ws.append([cliente.id, cliente.nombre, cliente.ruc, cliente.email])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Clientes.xlsx'
        wb.save(response)

    elif tipo_dato == 'Proveedores':

        ws.title = "Proveedores"
        encabezados = ['ID', 'Nombre', 'RUC', 'Email']
        for col_num, encabezado in enumerate(encabezados, 1):
            col_letter = get_column_letter(col_num)
            ws['{}1'.format(col_letter)] = encabezado
            ws.column_dimensions[col_letter].width = 15
        proveedores = Proveedor.objects.all()
        for proveedor in proveedores:
            ws.append([proveedor.id, proveedor.nombre, proveedor.ruc, proveedor.email])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Proveedores.xlsx'
        wb.save(response)

    return response
