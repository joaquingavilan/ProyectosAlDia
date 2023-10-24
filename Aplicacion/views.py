from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView
from .models import *
from .forms import *
from django.db.models import Q, F, Sum
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.utils import timezone
import re, locale, json, os
from datetime import date, datetime
from io import BytesIO
from django.contrib import messages
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponse, FileResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
import pandas as pd
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.core.serializers import serialize
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.core.exceptions import ObjectDoesNotExist


def inicio(request):
    verificar_obras_agendadas()
    cargar_distritos()
    if request.user.groups.filter(name='GERENTE').exists():
        return render(request, 'inicios/inicio.html')
    elif request.user.groups.filter(name='ADMINISTRADOR').exists():
        return render(request, 'inicios/inicio_adm.html')
    elif request.user.groups.filter(name='INGENIERO').exists():
        return redirect(inicio_ingenieros)


def inicio_ingenieros(request):
    nombre = request.user.first_name
    return render(request, 'inicios/inicio_ingenieros.html', {'nombre': nombre})


def inicio_adm(request):
    nombre = request.user.first_name
    return render(request, 'inicios/inicio_adm.html', {'nombre': nombre})
# VISTAS PARA USUARIOS


def cargar_distritos():
    # Verificar si ya hay 262 registros en el modelo Ciudad
    if Ciudad.objects.count() != 262:
        file_path = settings.BASE_DIR / "Aplicacion/static/distritos.geojson"
        with open(file_path, 'r') as file:
            data = json.load(file)

            # Obtener una lista de nombres de ciudades y ordenarla alfabéticamente
            nombres_ciudades = [feature['properties']['DIST_DESC_'] for feature in data['features']]

            # Reemplazar "Ñ" por "N" en cada nombre de ciudad
            nombres_ciudades = [nombre.replace('Ñ', 'N') for nombre in nombres_ciudades]
            nombres_ciudades_ordenados = sorted(nombres_ciudades)

            for nombre in nombres_ciudades_ordenados:
                Ciudad.objects.get_or_create(nombre=nombre)


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
            group = Group.objects.get(name='INGENIERO')
            user.groups.add(group)
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
        # Extraer datos directamente del POST
        nombre = request.POST.get('nombre')
        ruc = request.POST.get('ruc')
        email = request.POST.get('email')
        tipo_persona = request.POST.get('tipo_persona')
        direccion = request.POST.get('direccion')
        nombre_ciudad = request.POST.get('ciudad')
        ciudad = Ciudad.objects.get(nombre=nombre_ciudad)

        # Crear el objeto cliente
        cliente = Cliente(
            nombre=nombre,
            ciudad=ciudad,
            ruc=ruc,
            email=email,
            tipo_persona=tipo_persona,
            direccion=direccion
        )
        cliente.save()

        # Extraer contactos y guardarlos
        contactos_data = request.POST.getlist('contactos[]')
        contactos_list = [(contactos_data[i], contactos_data[i + 1]) for i in range(0, len(contactos_data), 2)]
        for nombre_contacto, numero_contacto in contactos_list:
            Contacto.objects.create(nombre=nombre_contacto, numero=numero_contacto, cliente=cliente)

        return redirect('ver_clientes')

    rucs_actuales = list(Cliente.objects.values_list('ruc', flat=True))
    rucs_json = json.dumps(rucs_actuales)
    emails = list(Cliente.objects.values_list('email', flat=True))
    emails_json = json.dumps(emails)

    ciudades = list(Ciudad.objects.values_list('nombre', flat=True))
    ciudades_json = json.dumps(ciudades)

    return render(request, 'ABM/clientes/registro_cliente.html', {'rucs_json': rucs_json, 'emails_json': emails_json, 'ciudades_json': ciudades_json})


def get_cliente_data(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    data = {
        "nombre": cliente.nombre,
        "ruc": cliente.ruc,
        "email": cliente.email,
        'tipo_persona': cliente.tipo_persona,
        'ciudad': cliente.ciudad.nombre,
        'direccion': cliente.direccion
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

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        tipo_persona = request.POST.get('tipo_persona')
        ruc = request.POST.get('ruc')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion', '')
        nombre_ciudad = request.POST.get('ciudad', '')

        # Si deseas realizar algunas validaciones básicas, puedes hacerlo aquí
        # Por ejemplo:
        if not nombre or not tipo_persona or not ruc or not email:
            return JsonResponse({"status": "error", "message": "Faltan campos requeridos."}, status=400)

        try:
            if nombre_ciudad:
                ciudad = Ciudad.objects.get(nombre=nombre_ciudad)
                cliente.ciudad = ciudad
            cliente.nombre = nombre
            cliente.tipo_persona = tipo_persona
            cliente.ruc = ruc
            cliente.email = email
            if direccion:
                cliente.direccion = direccion
            cliente.save()

            return JsonResponse({"status": "success"})

        except Ciudad.DoesNotExist:
            return JsonResponse({"status": "error", "message": "La ciudad proporcionada no existe."}, status=400)
        except Exception as e:
            # En caso de cualquier otro error
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return render(request, 'ABM/clientes/editar_cliente.html')


def ver_clientes(request):
    clientes = Cliente.objects.all()
    form_buscar = BuscadorClienteForm()
    rucs_actuales = list(Cliente.objects.values_list('ruc', flat=True))
    rucs_json = json.dumps(rucs_actuales)
    emails_actuales = list(Cliente.objects.values_list('email', flat=True))
    emails_json = json.dumps(emails_actuales)
    ciudades = list(Ciudad.objects.values_list('nombre', flat=True))
    ciudades_json = json.dumps(ciudades)
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

    return render(request, 'ABM/clientes/ver_clientes.html', {'clientes': clientes, 'form_buscar': form_buscar, 'page_obj': page_obj, 'rucs_json': rucs_json, 'emails_json': emails_json, 'ciudades_json': ciudades_json})


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
    return render(request, 'ABM/clientes/ver_cliente.html', {'cliente': cliente})


def agregar_contacto(request, tipo, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        nombre = data.get('nombre')
        numero = data.get('numero')
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
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            nombre = form.cleaned_data['first_name']
            apellido = form.cleaned_data['last_name']

            # Verificamos que el nombre y apellido solo contienen letras
            if not re.match(r'^[A-Za-z]+$', nombre):
                form.add_error('first_name', "Nombre inválido. Solo se permiten letras.")
            if not re.match(r'^[A-Za-z]+$', apellido):
                form.add_error('last_name', "Apellido inválido. Solo se permiten letras.")
            if not re.search(r'[A-Za-z]', username):
                form.add_error('username', "Nombre de usuario inválido.")

            # Si no hay errores adicionales, creamos el usuario
            if not form.errors:
                usuario = User.objects.create_user(username=username, first_name=nombre, last_name=apellido,
                                                   password=password, email=email)
                group = Group.objects.get(name='INGENIERO')
                usuario.groups.add(group)
                return redirect('ver_ingenieros')
        else:
            # Si el formulario no es válido, simplemente renderizamos la página con los errores
            return render(request, 'ABM/ingenieros/registrar_ingeniero.html', {'form': form})
    else:
        form = CustomUserCreationForm()
        return render(request, 'ABM/ingenieros/registrar_ingeniero.html', {'form': form})


def ver_ingenieros(request):
    group_ingeniero = Group.objects.get(name='INGENIERO')
    usuarios_ingenieros = group_ingeniero.user_set.all()
    # Configuración de la paginación
    paginator = Paginator(usuarios_ingenieros, 10)  # Muestra 10 ingenieros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ABM/ingenieros/ver_ingenieros.html', {'page_obj': page_obj})


def editar_ingeniero(request, pk):
    ingeniero = get_object_or_404(User, pk=pk)

    # Comprobamos si es una solicitud POST
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=ingeniero)

        if form.is_valid():
            nombre = request.POST['first_name']
            apellido = request.POST['last_name']
            email = form.cleaned_data['email']

            errors = {}

            if not re.match(r'^[A-Za-z]+$', nombre):
                errors["first_name"]="Nombre inválido. Solo se permiten letras."
            if not re.match(r'^[A-Za-z]+$', apellido):
                errors["last_name"]="Apellido inválido. Solo se permiten letras."
            if User.objects.filter(email=email).exclude(pk=pk).exists():
                return JsonResponse({"status": "error", "errors": {"email": ["El email ya está registrado."]}})
            if errors.keys():
                return JsonResponse({"status": "error", "errors": errors})
            else:
                form.save()
                return JsonResponse({"status": "success"})
        else:
            print(form.errors)
            return JsonResponse({"status": "error", "errors": form.errors})

    return JsonResponse({"status": "error", "message": "Metodo no permitido"})


def get_ingeniero_data(request, ingeniero_id):
    ingeniero = get_object_or_404(User, pk=ingeniero_id)
    data = {
        "first_name": ingeniero.first_name,
        "last_name": ingeniero.last_name,
        "email": ingeniero.email,
        # ... otros campos ...
    }
    return JsonResponse(data)


def eliminar_ingeniero(request, pk):
    ingeniero = get_object_or_404(User, pk=pk)

    # Verificamos si el ingeniero tiene obras o presupuestos asociados que no estén en los estados mencionados.
    obras_asociadas = Obra.objects.filter(encargado=ingeniero).exclude(estado='F')
    presupuestos_asociados = Presupuesto.objects.filter(encargado=ingeniero).exclude(estado='A')
    # Si tiene recursos asociados, obtenemos una lista de todos los ingenieros disponibles para la reasignación
    if obras_asociadas.exists() or presupuestos_asociados.exists():
        group_ingeniero = Group.objects.get(name='INGENIERO')
        otros_ingenieros = group_ingeniero.user_set.exclude(id=ingeniero.id)
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
    group_ingeniero = Group.objects.get(name='INGENIERO')
    ingenieros = group_ingeniero.user_set.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )

    data = [{'id': ingeniero.id, 'username': ingeniero.username, 'nombre': ingeniero.first_name,
             'apellido': ingeniero.last_name} for ingeniero in ingenieros]
    return JsonResponse(data, safe=False)


def ver_ingeniero(request, id_ingeniero):
    ingeniero = User.objects.get(pk=id_ingeniero)
    return render(request, 'ABM/ingenieros/ver_ingeniero.html', {'ingeniero': ingeniero})


#                   VISTAS PARA PROVEEDOR


def registrar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        # Extraemos la data de los contactos desde el request.
        # La estructura de contactos_data será una lista de diccionarios, donde cada diccionario tiene la información de un contacto.
        contactos_data = request.POST.getlist('contactos[]')
        contactos_list = [(contactos_data[i], contactos_data[i + 1]) for i in range(0, len(contactos_data), 2)]

        if form.is_valid():
            proveedor = form.save()
            # Ahora, para cada contacto en contactos_data, lo creamos y asociamos con el cliente.
            for nombre_contacto, numero_contacto in contactos_list:
                Contacto.objects.create(nombre=nombre_contacto, numero=numero_contacto, proveedor=proveedor)
            return redirect('ver_proveedores')
    else:
        form = ProveedorForm()
        rucs_actuales = list(Proveedor.objects.values_list('ruc', flat=True))
        rucs_json = json.dumps(rucs_actuales)
        emails = list(Proveedor.objects.values_list('email', flat=True))
        emails_json = json.dumps(emails)
        campos_con_asterisco = ["nombre", "ruc", "email"]
    return render(request, 'ABM/proveedores/registrar_proveedor.html', {'form': form, 'rucs_json': rucs_json, 'emails_json': emails_json, 'obligatorios': campos_con_asterisco})


def ver_proveedores(request):
    proveedores = Proveedor.objects.all()
    form_buscar = BuscadorProveedorForm()
    rucs_actuales = list(Proveedor.objects.values_list('ruc', flat=True))
    rucs_json = json.dumps(rucs_actuales)
    emails_actuales = list(Proveedor.objects.values_list('email', flat=True))
    emails_json = json.dumps(emails_actuales)
    ciudades = list(Ciudad.objects.values_list('nombre', flat=True))
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

    return render(request, 'ABM/proveedores/ver_proveedores.html', {'proveedores': proveedores, 'form_buscar': form_buscar, 'page_obj': page_obj, 'rucs_json': rucs_json, 'emails_json': emails_json, 'ciudades': ciudades})


def get_proveedor_data(request, proveedor_id):
    proveedor = Proveedor.objects.get(pk=proveedor_id)
    data = {
        "nombre": proveedor.nombre,
        "ruc": proveedor.ruc,
        "email": proveedor.email,
        'ciudad': proveedor.ciudad.nombre,
        'direccion': proveedor.direccion,
        'pagina_web': proveedor.pagina_web
        # ... otros campos ...
    }
    return JsonResponse(data)


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
        "email": proveedor.email,
        "ciudad": str(proveedor.ciudad),
        "pagina_web": proveedor.pagina_web,
        "direccion": proveedor.direccion
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

    if request.method == 'POST':
        # Actualizamos los atributos del proveedor con los datos recibidos
        proveedor.nombre = request.POST.get('nombre', proveedor.nombre)
        proveedor.ruc = request.POST.get('ruc', proveedor.ruc)
        proveedor.email = request.POST.get('email', proveedor.email)
        proveedor.direccion = request.POST.get('direccion', proveedor.direccion)
        nombre_ciudad = request.POST.get('ciudad')
        proveedor.ciudad = Ciudad.objects.get(nombre=nombre_ciudad)
        proveedor.pagina_web = request.POST.get('pagina_web', proveedor.pagina_web)

        # Guardamos el objeto proveedor
        try:
            proveedor.full_clean()  # Valida el objeto antes de guardarlo
            proveedor.save()
            return JsonResponse({"status": "success", "message": "Proveedor actualizado con éxito"})
        except ValidationError as e:
            # En caso de que el objeto no sea válido, devolvemos los errores en formato JSON
            return JsonResponse({"status": "error", "errors": e.message_dict}, status=400)

    return render(request, 'ABM/proveedores/editar_proveedor.html')


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
    group_ingeniero = Group.objects.get(name='INGENIERO')
    ingenieros = group_ingeniero.user_set.all()
    clientes = Cliente.objects.all()
    ciudades = Ciudad.objects.all()  # Obtiene todas las ciudades

    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            presupuesto = Presupuesto(encargado=form.cleaned_data['encargado'])
            proyecto.cliente = form.cleaned_data['cliente']
            proyecto.nombre = request.POST.get('nombre')
            ciudad_id = request.POST.get('ciudad')
            ciudad = Ciudad.objects.get(id=ciudad_id)
            proyecto.ciudad = ciudad
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
                  {'form': form, 'ingenieros': ingenieros, 'clientes': clientes, 'ciudades': ciudades})


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
    group_ingeniero = Group.objects.get(name='INGENIERO')
    ingenieros = group_ingeniero.user_set.all()
    clientes = Cliente.objects.all()
    if request.method == 'POST':
        cliente = request.POST['cliente']
        encargado_obra = request.POST['encargado_obra']
        encargado_presupuesto = request.POST['encargado_presupuesto']
        nombre_proyecto = request.POST['nombre']
        proyecto.cliente = Cliente.objects.get(id=cliente)
        proyecto.nombre = nombre_proyecto
        if encargado_presupuesto:
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

    return render(request, 'pantallas_ing/ver_presupuestos.html', {'presupuestos': presupuestos})


def ver_obras(request):
    obras = Obra.objects.filter(encargado=request.user)
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
    if request.method == 'POST':
        materiales_pedido = []
        obra = get_object_or_404(Obra, id=request.POST.get('obra'))
        for key, value in request.POST.items():
            if key.startswith('material_'):
                material_id = int(key.split('_')[1])
                material = get_object_or_404(Material, id=material_id)
                cantidad = int(value)
                materiales_pedido.append({'material': material, 'cantidad': cantidad})

        # Por ejemplo, puedes crear las instancias MaterialPedido aquí.
        return render(request, 'pantallas_ing/confirmar_pedido.html', {'materiales_pedido': materiales_pedido, 'obra': obra})

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
    # Excluyendo encargados que son None
    ingenieros = Obra.objects.exclude(encargado__isnull=True).values_list('encargado__username', flat=True).distinct()

    # Convertir a lista y agregar "No asignado"
    ingenieros_list = list(ingenieros)
    ingenieros_list.append("No asignado")
    return JsonResponse(ingenieros_list, safe=False)


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
    if ingeniero_user == "No asignado":
        proyectos = Proyecto.objects.filter(obra__encargado__isnull=True)
    else:
        ingeniero = User.objects.get(username=ingeniero_user)
        proyectos = Proyecto.objects.filter(obra__encargado=ingeniero)

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
    # Configuración de la paginación
    paginator = Paginator(materiales, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ABM/materiales/ver_materiales_filtrados.html', {'materiales': materiales, 'page_obj': page_obj})


def ver_materiales_proveedores(request, proveedor):
    id_proveedor = Proveedor.objects.get(nombre=proveedor)
    materiales = Material.objects.filter(id_proveedor=id_proveedor)
    # Configuración de la paginación
    paginator = Paginator(materiales, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ABM/materiales/ver_materiales_filtrados.html', {'materiales': materiales, 'page_obj': page_obj})


def ver_materiales_stock(request, cantidad):

    if cantidad == 'Menos de 10':
        materiales = Material.objects.filter(unidades_stock__lt=10)
    elif cantidad == 'Menos de 50':
        materiales = Material.objects.filter(unidades_stock__lt=50)
    elif cantidad == 'Menos de 100':
        materiales = Material.objects.filter(unidades_stock__lt=100)
    # Configuración de la paginación
    paginator = Paginator(materiales, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ABM/materiales/ver_materiales_filtrados.html', {'materiales': materiales, 'page_obj': page_obj})


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
        group_ingeniero = Group.objects.get(name='INGENIERO')
        ingenieros = group_ingeniero.user_set.all()
        # Añadir datos a la hoja
        for ingeniero in ingenieros:
            ws.append([ingeniero.id, ingeniero.username, ingeniero.first_name, ingeniero.last_name, ingeniero.email])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Ingenieros.xlsx'
        wb.save(response)

    elif tipo_dato == 'Clientes':
        ws.title = "Clientes"
        # Añadir encabezados a la hoja
        encabezados = ['ID', 'Tipo_persona', 'Nombre', 'RUC', 'Email', 'Ciudad', 'Direccion']
        for col_num, encabezado in enumerate(encabezados, 1):
            col_letter = get_column_letter(col_num)
            ws['{}1'.format(col_letter)] = encabezado
            ws.column_dimensions[col_letter].width = 15

        # Obtener datos de los clientes
        clientes = Cliente.objects.all()

        # Añadir datos a la hoja
        for cliente in clientes:
            ws.append([cliente.id, cliente.tipo_persona, cliente.nombre, cliente.ruc, cliente.email, cliente.ciudad, cliente.direccion])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Clientes.xlsx'
        wb.save(response)

    elif tipo_dato == 'Proveedores':

        ws.title = "Proveedores"
        encabezados = ['ID', 'Nombre', 'RUC', 'Email', 'Pagina web', 'Ciudad', 'Direccion']
        for col_num, encabezado in enumerate(encabezados, 1):
            col_letter = get_column_letter(col_num)
            ws['{}1'.format(col_letter)] = encabezado
            ws.column_dimensions[col_letter].width = 15
        proveedores = Proveedor.objects.all()
        for proveedor in proveedores:
            ws.append([proveedor.id, proveedor.nombre, proveedor.ruc, proveedor.email, proveedor.pagina_web, proveedor.ciudad, proveedor.direccion])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Proveedores.xlsx'
        wb.save(response)
    elif tipo_dato == 'Materiales':
        ws.title = "Materiales"
        # Añadir encabezados a la hoja
        encabezados = ['ID', 'Nombre', 'Marca', 'Proveedor', 'Medida', 'Mínimo', 'Unidades en Stock']
        for col_num, encabezado in enumerate(encabezados, 1):
            col_letter = get_column_letter(col_num)
            ws['{}1'.format(col_letter)] = encabezado
            ws.column_dimensions[col_letter].width = 15

        # Obtener datos de los materiales
        materiales = Material.objects.all().select_related(
            'id_proveedor')  # select_related para optimizar la consulta relacionada con Proveedor

        # Añadir datos a la hoja
        for material in materiales:
            ws.append([material.id, material.nombre, material.marca, material.id_proveedor.nombre, material.medida,
                       material.minimo, material.unidades_stock])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Materiales.xlsx'
        wb.save(response)

    return response


def exportar_pdf(request):
    tipo_dato = request.POST.get('tipo_dato')  # Por ejemplo, 'Ingenieros', 'Proyectos', etc.
    criterio = request.POST.get('criterio')  # Por ejemplo, el nombre del cliente
    # Crear un nuevo documento PDF
    response = HttpResponse(content_type='application/pdf')

    if tipo_dato == 'Ingenieros':
        response['Content-Disposition'] = 'attachment; filename="Ingenieros.pdf"'
        doc = SimpleDocTemplate(response, pagesize=A4)
        # Obtener datos de los ingenieros
        group_ingeniero = Group.objects.get(name='INGENIERO')
        ingenieros = group_ingeniero.user_set.all()
        data = [['ID', 'Usuario', 'Nombre', 'Apellido', 'Email']]
        for ingeniero in ingenieros:
            data.append([ingeniero.id, ingeniero.username, ingeniero.first_name, ingeniero.last_name, ingeniero.email])

        # Crear una tabla con los datos
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        # Construir el documento
        story = [table]
        doc.build(story)

    elif tipo_dato =='Clientes':
        response['Content-Disposition'] = 'attachment; filename="Clientes.pdf"'
        doc = SimpleDocTemplate(response, pagesize=landscape(A4))
        # Datos para la tabla
        data = [['ID', 'Tipo de Persona', 'Nombre', 'RUC', 'Email', 'Ciudad', 'Direccion']]

        # Obtener datos de los clientes
        clientes = Cliente.objects.all()
        for cliente in clientes:
            data.append([cliente.id, cliente.tipo_persona, cliente.nombre, cliente.ruc, cliente.email, cliente.ciudad,
                         cliente.direccion])

        # Crear tabla
        table = Table(data)

        # Aplicar estilos a la tabla
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)

        # Alternar colores de fondo para las filas
        rowNumb = len(data)
        for i in range(1, rowNumb):
            if i % 2 == 0:
                bc = colors.bisque
            else:
                bc = colors.beige
            ts = TableStyle(
                [('BACKGROUND', (0, i), (-1, i), bc)]
            )
            table.setStyle(ts)

        # Agregar tabla al documento
        elems = []
        elems.append(table)

        doc.build(elems)
    elif tipo_dato == 'Proveedores':
        response['Content-Disposition'] = 'attachment; filename="Proveedores.pdf"'
        doc = SimpleDocTemplate(response, pagesize=landscape(A4))
        # Datos para la tabla
        data = [['ID', 'Nombre', 'RUC', 'Email', 'Ciudad', 'Direccion', 'Página Web']]

        # Obtener datos de los proveedores
        proveedores = Proveedor.objects.all()
        for proveedor in proveedores:
            data.append(
                [proveedor.id, proveedor.nombre, proveedor.ruc, proveedor.email, proveedor.ciudad, proveedor.direccion,
                 proveedor.pagina_web or ""])

        # Crear tabla
        table = Table(data)

        # Aplicar estilos a la tabla
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)

        # Alternar colores de fondo para las filas
        rowNumb = len(data)
        for i in range(1, rowNumb):
            if i % 2 == 0:
                bc = colors.bisque
            else:
                bc = colors.beige
            ts = TableStyle(
                [('BACKGROUND', (0, i), (-1, i), bc)]
            )
            table.setStyle(ts)

        # Agregar tabla al documento
        elems = []
        elems.append(table)

        doc.build(elems)
    elif tipo_dato == 'Materiales':
        response['Content-Disposition'] = 'attachment; filename="Materiales.pdf"'
        doc = SimpleDocTemplate(response, pagesize=landscape(A4))
        # Datos para la tabla
        data = [['ID', 'Nombre', 'Marca', 'Proveedor', 'Medida', 'Mínimo', 'Unidades en Stock']]

        # Obtener datos de los materiales
        materiales = Material.objects.all().select_related(
            'id_proveedor')  # select_related para optimizar la consulta relacionada con Proveedor
        for material in materiales:
            data.append(
                [material.id, material.nombre, material.marca, material.id_proveedor.nombre, material.medida,
                 material.minimo, material.unidades_stock])

        # Crear tabla
        table = Table(data)

        # Aplicar estilos a la tabla
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)

        # Alternar colores de fondo para las filas
        rowNumb = len(data)
        for i in range(1, rowNumb):
            if i % 2 == 0:
                bc = colors.bisque
            else:
                bc = colors.beige
            ts = TableStyle(
                [('BACKGROUND', (0, i), (-1, i), bc)]
            )
            table.setStyle(ts)

        # Agregar tabla al documento
        elems = []
        elems.append(table)

        doc.build(elems)
    return response


def extraer_plazo(sheet):
    for row in sheet.iter_rows(values_only=True):
        for cell in row:
            if cell and "Plazo de ejecución" in str(cell):
                match = re.search(r'Plazo de ejecución: (\d+) días', cell)
                if match:
                    return int(match.group(1))
    return None


def cargar_presupuesto(request, pk):
    presupuesto = get_object_or_404(Presupuesto, pk=pk)
    if request.method == "POST" and request.FILES['archivo_presupuesto']:
        archivo_excel = request.FILES['archivo_presupuesto']
        # No necesitas la ruta completa aquí, simplemente el nombre del archivo.
        # Django se encargará de guardar el archivo en la ubicación correcta según tu configuración de MEDIA_ROOT.
        nombre_archivo = os.path.basename(archivo_excel.name)

        # Crear una instancia de ArchivoPresupuesto
        archivo_presupuesto = ArchivoPresupuesto(presupuesto=presupuesto, nombre=nombre_archivo)

        # Guardar el archivo en el modelo
        archivo_presupuesto.archivo.save(nombre_archivo, archivo_excel)

        # Guardar el modelo en la base de datos

        workbook = load_workbook(archivo_presupuesto.archivo)
        sheet = workbook.active

        #extraemos el plazo de ejecucion
        plazo = extraer_plazo(sheet)
        if plazo:
            obra = presupuesto.proyecto.obra
            obra.plazo = plazo
            obra.save()
            print(plazo)

        # Variables para identificar el inicio de la tabla
        inicio_tabla_fila = None
        inicio_tabla_columna = None

        # Navegar por cada fila
        for idx, row in enumerate(sheet.iter_rows(values_only=True)):
            found_rubros = False
            for cell in row:
                if cell and "Rubros" == cell.strip():
                    found_rubros = True
                    break
            if found_rubros:
                # Obtener el índice de la celda que contiene "Rubros"
                rubros_index = row.index(cell)
                # Si la siguiente celda es "Un", entonces hemos encontrado el inicio de la tabla
                if row[rubros_index + 1].strip() == "Un":
                    inicio_tabla_fila = idx
                    inicio_tabla_columna = rubros_index
                    print(
                        f'Inicio de tabla identificado en la fila {inicio_tabla_fila} y columna {inicio_tabla_columna}')
                    break

        # Si encontramos el inicio de la tabla, procesamos los datos
        if inicio_tabla_fila is not None and inicio_tabla_columna is not None:
            categoria_actual = None
            item_actual = None

            idx = inicio_tabla_fila + 2  # Comenzamos en la fila siguiente a inicio_tabla

            while idx < sheet.max_row and sheet[idx][inicio_tabla_columna].value:  # Mientras no lleguemos al final del archivo
                fila_actual = [cell.value for cell in sheet[idx]]
                valor_rubros = fila_actual[inicio_tabla_columna].strip() if fila_actual[inicio_tabla_columna] else None
                valor_un = fila_actual[inicio_tabla_columna + 1].strip() if fila_actual[inicio_tabla_columna + 1] else None
                # Comprobar si la fila siguiente tiene valor en "Un"
                fila_siguiente = [cell.value for cell in sheet[idx + 1]] if idx + 1 <= sheet.max_row else None
                valor_un_siguiente = fila_siguiente[inicio_tabla_columna + 1].strip() if fila_siguiente and \
                                                                                         fila_siguiente[
                                                                                             inicio_tabla_columna + 1] else None

                if valor_rubros and not valor_un:
                    if valor_un_siguiente:
                        # Es un Item
                        item_actual = Item(nombre=valor_rubros, categoria=categoria_actual, archivo=archivo_presupuesto)
                        item_actual.save()
                        # NO limpiamos la categoría actual aquí
                    else:
                        # Es una Categoría
                        categoria_actual = Categoria(nombre=valor_rubros, archivo=archivo_presupuesto)
                        categoria_actual.save()
                        item_actual = None  # Limpiamos el ítem actual
                elif valor_rubros and valor_un:
                    # Es un SubItem
                    subitem = SubItem(
                        item=item_actual,
                        rubro=valor_rubros,
                        unidad_medida=valor_un,
                        cantidad=fila_actual[inicio_tabla_columna + 2],
                        precio_unitario=fila_actual[inicio_tabla_columna + 3],
                        precio_total=(fila_actual[inicio_tabla_columna + 2] * fila_actual[inicio_tabla_columna + 3])
                    )
                    subitem.save()
                else:
                    # Aquí puedes manejar casos no previstos o simplemente ignorarlos
                    pass

                idx += 1  # Avanzar a la siguiente fila

        else:
            print("No se encontró la tabla en el archivo proporcionado.")

        workbook.close()
        # Calcular la suma de todos los campos `precio_total` de los subitems que pertenecen al presupuesto en cuestión, y cargarlas como monto_total del presupuesto
        suma_total = SubItem.objects.filter(item__categoria__archivo__presupuesto=presupuesto).aggregate(suma=Sum('precio_total'))['suma']
        presupuesto.monto_total = suma_total
        presupuesto.monto_anticipo = suma_total/2
        presupuesto.save()

        # Redirige al usuario a donde desees luego de procesar el archivo
        return redirect('ver_presupuestos')
    # Redirige al usuario a donde desees luego de procesar el archivo
    return redirect('ver_presupuestos')


def ver_archivo_presupuesto(request, pk):
    archivo_presupuesto = get_object_or_404(ArchivoPresupuesto, presupuesto=pk)
    categorias = Categoria.objects.filter(archivo=archivo_presupuesto).order_by('pk')
    presupuesto = archivo_presupuesto.presupuesto
    # Pasamos el archivo_presupuesto y las categorías al template
    context = {
        'archivo_presupuesto': archivo_presupuesto,
        'categorias': categorias,
        'presupuesto': presupuesto
    }
    return render(request, 'pantallas_ing/ver_presupuesto.html', context)


def modificar_presupuesto(request, pk):
    archivo_presupuesto = get_object_or_404(ArchivoPresupuesto, presupuesto=pk)
    categorias = Categoria.objects.filter(archivo=archivo_presupuesto).order_by('pk')
    presupuesto = archivo_presupuesto.presupuesto
    # Pasamos el archivo_presupuesto y las categorías al template
    context = {
        'archivo_presupuesto': archivo_presupuesto,
        'categorias': categorias,
        'presupuesto': presupuesto
    }
    return render(request, 'pantallas_ing/modificar_presupuesto.html', context)


def editar_categoria(request, categoria_id):
    # Lógica para editar la categoría
    return JsonResponse({'status': 'success'})


def editar_item(request, item_id):
    # Lógica para editar el item
    return JsonResponse({'status': 'success'})


# Función para actualizar el monto_total de un presupuesto basado en sus subitems
def actualizar_monto_total(presupuesto):
    suma_total = SubItem.objects.filter(item__categoria__archivo__presupuesto=presupuesto).aggregate(suma=Sum('precio_total'))['suma']
    presupuesto.monto_total = suma_total
    presupuesto.monto_anticipo = suma_total/2
    presupuesto.save()


@csrf_exempt
def editar_subitem(request, subitem_id):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            subitem = SubItem.objects.get(pk=subitem_id)
            subitem.rubro = data.get('rubro')
            subitem.unidad_medida = data.get('unidad_medida')
            subitem.cantidad = Decimal(data.get('cantidad'))
            subitem.precio_unitario = Decimal(data.get('precio_unitario'))
            subitem.precio_total = subitem.cantidad * subitem.precio_unitario
            subitem.save()

            presupuesto_asociado = subitem.item.categoria.archivo.presupuesto
            actualizar_monto_total(presupuesto_asociado)

            return JsonResponse({'status': 'success'})

        except SubItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Subitem no encontrado'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


@csrf_exempt
def eliminar_subitem(request, subitem_id):
    if request.method == "DELETE":
        try:
            subitem = SubItem.objects.get(pk=subitem_id)
            presupuesto_asociado = subitem.item.categoria.archivo.presupuesto
            # Capturamos el Item asociado al SubItem antes de eliminarlo
            item_asociado = subitem.item
            subitem.delete()

            # Verificar si el Item no tiene otros SubItems asociados
            if not item_asociado.subitem_set.exists():
                # Capturamos la Categoría asociada al Item antes de eliminarlo
                categoria_asociada = item_asociado.categoria
                item_asociado.delete()

                # Verificar si la Categoría no tiene otros Items asociados
                if not categoria_asociada.item_set.exists():
                    categoria_asociada.delete()

            actualizar_monto_total(presupuesto_asociado)
            return JsonResponse({'status': 'success'})

        except SubItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Subitem no encontrado'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


@csrf_exempt
def actualizar_estado(request, presupuesto_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            nuevo_estado = data.get('estado')
            presupuesto = Presupuesto.objects.get(pk=presupuesto_id)
            presupuesto.estado = nuevo_estado
            presupuesto.save()
            return JsonResponse({'status': 'success'})
        except Presupuesto.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Presupuesto no encontrado'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


def ver_presupuestos_adm(request):

    # Si hay filtros en la petición, úsalos.
    filtro_campo = request.GET.get('campo', None)
    filtro_valor = request.GET.get('valor', None)

    presupuestos = Presupuesto.objects.all()

    if filtro_campo and filtro_valor:
        if filtro_campo == 'cliente':
            presupuestos = presupuestos.filter(proyecto__cliente__nombre=filtro_valor)
        elif filtro_campo == 'encargadoPresupuesto':
            ingeniero = User.objects.get(username=filtro_valor)
            presupuestos = presupuestos.filter(encargado=ingeniero)
        elif filtro_campo == 'estadoPresupuesto':
            estado_codigo = {value: key for key, value in dict(Presupuesto.ESTADOS).items()}[filtro_valor]
            presupuestos = presupuestos.filter(estado=estado_codigo)
        elif filtro_campo == 'estadoAnticipo':
            tiene_anticipo = True if filtro_valor == 'Sí' else False
            presupuestos = presupuestos.filter(anticipo=tiene_anticipo)

    # Lógica de paginación
    paginator = Paginator(presupuestos, 10)  # 10 presupuestos por página
    page = request.GET.get('page')

    try:
        presupuestos_paginados = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, muestra la primera página.
        presupuestos_paginados = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, muestra la última página de resultados.
        presupuestos_paginados = paginator.page(paginator.num_pages)

    context = {
        'page_obj': presupuestos_paginados,  # Usa 'page_obj' en lugar de 'presupuestos' en el template
        'campo_seleccionado': filtro_campo,
        'valor_seleccionado': filtro_valor,
        'presupuestos': presupuestos
    }

    return render(request, 'pantallas_adm/ver_presupuestos_adm.html', context)



@csrf_exempt
def actualizar_anticipo(request, presupuesto_id):
    if request.method == "POST":
        try:
            presupuesto = Presupuesto.objects.get(pk=presupuesto_id)
            presupuesto.anticipo = request.POST.get('anticipo') == 'true'

            # Si se ha enviado un archivo de comprobante, lo guardamos
            comprobante = request.FILES.get('comprobante')
            if comprobante:
                presupuesto.comprobante_anticipo = comprobante

            if presupuesto.estado == 'S' and presupuesto.anticipo is True:
                presupuesto.estado = 'A'
            if presupuesto.anticipo is True:
                presupuesto.fecha_pago_anticipo = date.today()
            presupuesto.save()

            return JsonResponse({
                'status': 'success',
                'nuevo_estado': presupuesto.get_estado_display(),
                'fecha_pago_anticipo': presupuesto.fecha_pago_anticipo.strftime('%d/%m/%Y') if presupuesto.fecha_pago_anticipo else None
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


def ver_obras_adm(request):
    obras = Obra.objects.filter(encargado__isnull=False)
    presupuestos_con_anticipo = Presupuesto.objects.filter(anticipo=True)
    # Filtramos aquellos presupuestos cuyo proyecto no tiene una obra con encargado asignado
    presupuestos_a_asignar = [presupuesto for presupuesto in presupuestos_con_anticipo if
                              not presupuesto.proyecto.obra.encargado]

    # Obtenemos los ingenieros disponibles
    group_ingeniero = Group.objects.get(name='INGENIERO')
    ingenieros = group_ingeniero.user_set.all()

    # Obtenemos los meses de las fechas de inicio y fin
    meses_inicio = list(set(obras.values_list('fecha_inicio__month', flat=True)))
    meses_fin = list(set(obras.values_list('fecha_fin__month', flat=True)))
    paginator = Paginator(obras, 10)  # Muestra 10 obras por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'obras': obras,
        'presupuestos': presupuestos_a_asignar,
        'ingenieros': ingenieros,
        'meses_inicio': meses_inicio,
        'meses_fin': meses_fin,
        'page_obj': page_obj
    }
    return render(request, 'pantallas_adm/ver_obras_adm.html', context)


def ver_obra_adm(request, obra_id):
    obra = get_object_or_404(Obra, id=obra_id)
    return render(request, 'pantallas_adm/ver_obra_adm.html', {'obra': obra})


def buscar_obras(request):
    q = request.GET.get('q', '')
    obras = Obra.objects.filter(proyecto__nombre__icontains=q).values('id', 'proyecto__nombre')
    return JsonResponse(list(obras), safe=False)


def obtener_estados_obra(request):
    # Obtenemos los estados distintos del modelo Obra
    estados_distintos = Obra.objects.values_list('estado', flat=True).distinct()

    # Creamos una instancia ficticia de Obra para poder usar el método get_estado_display()
    obra_dummy = Obra()

    # Obtenemos la representación legible para cada estado
    estados_legibles = [obra_dummy.get_estado_display() for obra_dummy.estado in estados_distintos]

    return JsonResponse(estados_legibles, safe=False)


def obtener_ingenieros_obra(request):
    # Obtener ingenieros de las obras
    ingenieros = Obra.objects.exclude(encargado=None).values_list('encargado__first_name',
                                                                  'encargado__last_name').distinct()

    # Convertir la tupla (first_name, last_name) a la cadena "first_name last_name"
    formatted_ingenieros = [f"{ingeniero[0]} {ingeniero[1]}" for ingeniero in ingenieros]

    return JsonResponse(formatted_ingenieros, safe=False)


def obtener_fechas_inicio(request):
    fechas = Obra.objects.exclude(fecha_inicio=None).dates('fecha_inicio', 'month').distinct()
    fechas_formateadas = ["{} {}".format(traducir_mes(fecha.strftime('%B')), fecha.year) for fecha in fechas]
    return JsonResponse(fechas_formateadas, safe=False)


def obtener_fechas_fin(request):
    fechas = Obra.objects.exclude(fecha_fin=None).dates('fecha_fin', 'month').distinct()
    fechas_formateadas = ["{} {}".format(traducir_mes(fecha.strftime('%B')), fecha.year) for fecha in fechas]
    return JsonResponse(fechas_formateadas, safe=False)


def traducir_mes(mes_ingles):
    """Traduce un mes de inglés a español."""
    traducciones = {
        'January': 'Enero',
        'February': 'Febrero',
        'March': 'Marzo',
        'April': 'Abril',
        'May': 'Mayo',
        'June': 'Junio',
        'July': 'Julio',
        'August': 'Agosto',
        'September': 'Septiembre',
        'October': 'Octubre',
        'November': 'Noviembre',
        'December': 'Diciembre',
    }
    return traducciones.get(mes_ingles, mes_ingles)


def traducir_mes_inverso(mes_espanol):
    """Traduce un mes de español a inglés."""
    traducciones = {
        'Enero': 'January',
        'Febrero': 'February',
        'Marzo': 'March',
        'Abril': 'April',
        'Mayo': 'May',
        'Junio': 'June',
        'Julio': 'July',
        'Agosto': 'August',
        'Septiembre': 'September',
        'Octubre': 'October',
        'Noviembre': 'November',
        'Diciembre': 'December',
    }
    return traducciones.get(mes_espanol, mes_espanol)


def estado_legible_a_codigo(estado_legible):
    # Usamos el diccionario invertido para obtener el código a partir de la representación legible
    estado_codigo = dict((v, k) for k, v in Obra.ESTADOS).get(estado_legible)
    return estado_codigo


def ver_obras_filtradas(request):
    campo = request.GET.get('campo')
    valor = request.GET.get('valor')

    if campo == 'estado':
        # Convertimos el estado legible a su código correspondiente
        estado_codigo = estado_legible_a_codigo(valor)
        obras = Obra.objects.filter(estado=estado_codigo, encargado__isnull=False)
    elif campo == 'encargado':
        # Divide el valor en nombre y apellido
        first_name, last_name = valor.split(' ', 1)

        # Obtiene el usuario por nombre y apellido
        ingeniero = User.objects.get(first_name=first_name, last_name=last_name)

        # Filtra las obras por el ID del ingeniero
        obras = Obra.objects.filter(encargado=ingeniero)
    elif campo == 'fechaInicio':
        if valor == 'No iniciada':
            obras = Obra.objects.filter(fecha_inicio__isnull=True, encargado__isnull=False)
        else:
            # Convertir el mes en formato textual a un valor numérico
            month_es, year = valor.split()
            month_en = traducir_mes_inverso(month_es)
            month_num = datetime.strptime(month_en, '%B').month
            obras = Obra.objects.filter(fecha_inicio__month=month_num, fecha_inicio__year=year, encargado__isnull=False)
    elif campo == 'fechaFin':
        if valor == 'No finalizada':
            obras = Obra.objects.filter(fecha_fin__isnull=True, encargado__isnull=False)
        else:
            # Convertir el mes en formato textual a un valor numérico
            month_es, year = valor.split()
            month_en = traducir_mes_inverso(month_es)
            month_num = datetime.datetime.strptime(month_en, '%B').month
            obras = Obra.objects.filter(fecha_fin__month=month_num, fecha_fin__year=year, encargado__isnull=False)
    else:
        obras = Obra.objects.filter(encargado__isnull=False)

    presupuestos_con_anticipo = Presupuesto.objects.filter(anticipo=True)
    presupuestos_a_asignar = [presupuesto for presupuesto in presupuestos_con_anticipo if
                              not presupuesto.proyecto.obra.encargado]

    group_ingeniero = Group.objects.get(name='INGENIERO')
    ingenieros = group_ingeniero.user_set.all()

    meses_inicio = list(set(obras.values_list('fecha_inicio__month', flat=True)))
    meses_fin = list(set(obras.values_list('fecha_fin__month', flat=True)))
    paginator = Paginator(obras, 10)  # Muestra 10 obras por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'obras': obras,
        'presupuestos': presupuestos_a_asignar,
        'ingenieros': ingenieros,
        'meses_inicio': meses_inicio,
        'meses_fin': meses_fin,
        'campo_seleccionado': campo,
        'valor_seleccionado': valor,
        'page_obj': page_obj
    }

    return render(request, 'pantallas_adm/ver_obras_adm.html', context)


def asignar_obras(request):
    # Buscamos los presupuestos que tienen anticipo pagado
    presupuestos_con_anticipo = Presupuesto.objects.filter(anticipo=True)
    # Filtramos aquellos presupuestos cuyo proyecto no tiene una obra con encargado asignado
    presupuestos_a_asignar = [presupuesto for presupuesto in presupuestos_con_anticipo if
                              not presupuesto.proyecto.obra.encargado]
    group_ingeniero = Group.objects.get(name='INGENIERO')
    ingenieros = group_ingeniero.user_set.all()
    context = {'presupuestos': presupuestos_a_asignar,
               'ingenieros': ingenieros}
    return render(request, 'pantallas_adm/asignar_obras.html', context)


@csrf_exempt
def asignar_ingeniero_a_obra(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            presupuesto_id = data.get('presupuesto_id')
            ingeniero_id = data.get('ingeniero_id')
            print(presupuesto_id)
            # Obtener el presupuesto
            presupuesto = Presupuesto.objects.get(pk=presupuesto_id)
            print(presupuesto)
            # Obtener la obra relacionada con el proyecto del presupuesto
            obra = Obra.objects.get(proyecto=presupuesto.proyecto)

            # Asignar el ingeniero a la obra
            obra.encargado = User.objects.get(pk=ingeniero_id)
            obra.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


def buscar_presupuestos(request):
    query = request.GET.get('q', '')
    presupuestos = Presupuesto.objects.filter(
        Q(proyecto__nombre__icontains=query)
    )
    data = [
        {
            'id': presupuesto.id,
            'proyecto_nombre': presupuesto.proyecto.nombre,
            'cliente_nombre': presupuesto.proyecto.cliente.nombre
        }
        for presupuesto in presupuestos
    ]
    return JsonResponse(data, safe=False)


def buscar_presupuestos_terminados(request):
    query = request.GET.get('q', '')
    presupuestos = Presupuesto.objects.filter(
        Q(proyecto__nombre__icontains=query),
        Q(estado__in=['S', 'A']),
        Q(anticipo=False)
    )
    data = [
        {
            'id': presupuesto.id,
            'proyecto_nombre': presupuesto.proyecto.nombre,
            'cliente_nombre': presupuesto.proyecto.cliente.nombre,
            'monto_total': str(presupuesto.monto_total)  # Convertir a string para serialización JSON
        }
        for presupuesto in presupuestos
    ]
    return JsonResponse(data, safe=False)


def ver_presupuesto_adm(request, presupuesto_id):
    presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id)

    try:
        # Intenta obtener el ArchivoPresupuesto asociado al presupuesto.
        archivo_presupuesto = ArchivoPresupuesto.objects.get(presupuesto=presupuesto)
        # Si existe, obtener las categorías asociadas a dicho archivo.
        categorias = Categoria.objects.filter(archivo=archivo_presupuesto).order_by('pk')
    except ObjectDoesNotExist:
        archivo_presupuesto = None
        categorias = []

    context = {
        'presupuesto': presupuesto,
        'archivo_presupuesto': archivo_presupuesto,
        'categorias': categorias
    }
    return render(request, 'pantallas_adm/ver_presupuesto_adm.html', context)


def obtener_estados_anticipo(request):
    estados = ['Sí', 'No']
    return JsonResponse(list(estados), safe=False)


def ver_proyectos_estado_anticipo(request, anticipo):
    if anticipo == 'Sí':
        presupuestos = Presupuesto.objects.filter(anticipo=True)
    else:
        presupuestos = Presupuesto.objects.filter(anticipo=False)
    return render(request, 'pantallas_adm/ver_presupuestos_filtrados.html', {'presupuestos': presupuestos})


def ver_presupuestos_cliente(request, cliente_nombre):
    presupuestos = Presupuesto.objects.filter(proyecto__cliente__nombre=cliente_nombre)
    return render(request, 'pantallas_adm/ver_presupuestos_filtrados.html', {'presupuestos': presupuestos})


def ver_presupuestos_encargado_presupuesto(request, ingeniero_user):
    ingeniero = User.objects.filter(username=ingeniero_user)
    presupuestos = Presupuesto.objects.filter(encargado__in=ingeniero)
    return render(request, 'pantallas_adm/ver_presupuestos_filtrados.html', {'presupuestos': presupuestos})


def ver_presupuestos_estado_presupuesto(request, estado):
    # Convertir el nombre legible del estado a su código correspondiente
    estado_codigo = {value: key for key, value in dict(Presupuesto.ESTADOS).items()}[estado]

    # Filtrar los proyectos basándose en el código del estado
    presupuestos = Presupuesto.objects.filter(estado=estado_codigo)

    return render(request, 'pantallas_adm/ver_presupuestos_filtrados.html', {'presupuestos': presupuestos})


def verificar_obras_agendadas():
    # Obtener todas las obras que deberían haber empezado pero aún están en estado "No Iniciada"
    obras_a_iniciar = Obra.objects.filter(estado='NI', fecha_inicio__lte=date.today())

    for obra in obras_a_iniciar:
        obra.estado = 'E'  # Cambiar el estado a "En ejecución"
        obra.save()


def iniciar_obra(request, obra_id):
    obra = get_object_or_404(Obra, id=obra_id)

    if obra.estado == 'NI':
        obra.fecha_inicio = date.today()
        obra.estado = 'E'  # 'E' es el estado para "En ejecución"
        obra.save()

        return JsonResponse({'status': 'success', 'message': 'Obra iniciada con éxito'})

    return JsonResponse({'status': 'error', 'message': 'No se pudo iniciar la obra'})


def agendar_inicio_obra(request, obra_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        fecha_inicio = data.get('fecha_inicio')
        try:
            obra = Obra.objects.get(id=obra_id)
            obra.fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            obra.save()
            print('ya')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


def finalizar_obra(request, obra_id):
    if request.method == 'POST':
        try:
            obra = Obra.objects.get(id=obra_id)
            obra.fecha_fin = date.today()
            obra.estado = 'F'  # F para Finalizada
            obra.save()
            return JsonResponse({'status': 'success', 'message': 'Obra finalizada con éxito', 'fecha_fin': obra.fecha_fin.strftime('%Y-%m-%d')})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


def elaborar_certificado(request):
    obras = Obra.objects.filter(encargado=request.user, estado='E')

    # Extraemos los proyectos relacionados con las obras
    proyectos = [obra.proyecto for obra in obras]

    # Filtramos los presupuestos usando esos proyectos
    presupuestos = Presupuesto.objects.filter(proyecto__in=proyectos)
    presupuestos_dict = {presupuesto.proyecto.id: presupuesto for presupuesto in presupuestos}
    presupuestos_serializados = serialize('json', presupuestos)

    # Obtener el archivo_presupuesto
    archivos_presupuesto = ArchivoPresupuesto.objects.filter(presupuesto__in=presupuestos)

    # Obtener las categorías para cada archivo_presupuesto
    categorias = {archivo.id: Categoria.objects.filter(archivo=archivo).order_by('pk') for archivo in archivos_presupuesto}

    context = {
        'obras': obras,
        'presupuestos': presupuestos_serializados,
        'archivos_presupuesto': archivos_presupuesto,
        'categorias': categorias
    }

    return render(request, 'pantallas_ing/elaborar_certificado.html', context)


def guardar_certificado(request):
    # Lógica para crear el certificado y agregar todos los subitems.
    # ...
    return JsonResponse({"status": "success"})


def obtener_presupuesto_detalle(request, proyecto_id):
    try:
        # Buscamos el presupuesto basado en el proyecto_id
        presupuesto = Presupuesto.objects.get(proyecto_id=proyecto_id)

        # Obtenemos el archivo_presupuesto relacionado
        archivo_presupuesto = ArchivoPresupuesto.objects.get(presupuesto=presupuesto)

        # Recuperamos las categorías y los subitems
        categorias = Categoria.objects.filter(archivo=archivo_presupuesto).order_by('pk')

        data = []
        for categoria in categorias:
            items_data = []
            for item in categoria.item_set.all():
                subitems_data = []
                for subitem in item.subitem_set.all():
                    subitems_data.append({
                        'id': subitem.id,
                        'rubro': subitem.rubro,
                        'unidad_medida': subitem.unidad_medida,
                        'cantidad': float(subitem.cantidad),
                        'precio_unitario': float(subitem.precio_unitario),
                        'precio_total': float(subitem.precio_total),
                        'itemId': subitem.item.id,
                        'categoriaId': subitem.item.categoria.id
                    })
                items_data.append({
                    'id': item.id,
                    'nombre': item.nombre,
                    'subitems': subitems_data,
                    'categoriaId': item.categoria.id
                })
            data.append({
                'id': categoria.id,
                'nombre': categoria.nombre,
                'items': items_data
            })

        return JsonResponse(data, safe=False)
    except (Presupuesto.DoesNotExist, ArchivoPresupuesto.DoesNotExist):
        return JsonResponse({'error': 'Presupuesto no encontrado'}, status=404)


def registrar_anticipo(request):
    presupuestos = Presupuesto.objects.filter(estado__in=['S', 'A']).filter(anticipo=False)
    return render(request, 'pantallas_adm/registrar_anticipo.html', {'presupuestos': presupuestos})


def obtener_filtro_valores(request):
    tipo = request.GET.get('tipo')
    presupuestos = Presupuesto.objects.filter(estado__in=['S', 'A']).filter(anticipo=False)
    if tipo == 'cliente':
        proyectos = [presupuesto.proyecto for presupuesto in presupuestos]
        clientes = Cliente.objects.filter(proyecto__in=proyectos).distinct()
        data = [{'id': cliente.id, 'nombre': cliente.nombre} for cliente in clientes]
    elif tipo == 'encargadoPresupuesto':
        ingenieros = User.objects.filter(presupuesto__in=presupuestos).distinct()
        data = [{'id': ingeniero.id, 'nombre': f"{ingeniero.first_name} {ingeniero.last_name}"} for ingeniero in ingenieros]
    elif tipo == 'estadoPresupuesto':
        data = [
            {'id': 'S', 'nombre': 'Enviado'},
            {'id': 'A', 'nombre': 'Aprobado'}
        ]
    else:
        data = []

    return JsonResponse(data, safe=False)


def obtener_presupuestos_filtrados(request):
    campo = request.GET.get('campo')
    valor = request.GET.get('valor')

    if campo == 'cliente':
        presupuestos = Presupuesto.objects.filter(proyecto__cliente_id=valor, estado__in=['S', 'A'], anticipo=False)
    elif campo == 'encargadoPresupuesto':
        presupuestos = Presupuesto.objects.filter(encargado_id=valor, estado__in=['S', 'A'], anticipo=False)
    elif campo == 'estadoPresupuesto':
        presupuestos = Presupuesto.objects.filter(estado=valor)
    else:
        presupuestos = []

    data = [
        {
            'id': presupuesto.id,
            'nombre': presupuesto.proyecto.nombre
        }
        for presupuesto in presupuestos
    ]

    return JsonResponse(data, safe=False)


def obtener_monto_presupuesto(request):
    presupuesto_id = request.GET.get('id')
    presupuesto = Presupuesto.objects.get(id=presupuesto_id)
    data = {
        'monto_total': str(presupuesto.monto_total)  # Convertir a string para que sea serializable
    }
    return JsonResponse(data)


def ver_certificados_ing(request):
    # Asumimos que el usuario que está iniciando sesión es el ingeniero
    certificados = Certificado.objects.filter(ingeniero=request.user)
    return render(request, 'pantallas_ing/ver_certificados.html', {
        'certificados': certificados,
        'title': 'Mis Certificados'
    })


def buscar_presupuestos_ingeniero(request):
    query = request.GET.get('q', '')
    # Filtra los presupuestos basándose en el nombre del proyecto y el ingeniero asignado
    presupuestos = Presupuesto.objects.filter(
        Q(proyecto__nombre__icontains=query) & Q(encargado=request.user)
    )
    data = [
        {
            'id': presupuesto.id,
            'proyecto_nombre': presupuesto.proyecto.nombre,
            'cliente_nombre': presupuesto.proyecto.cliente.nombre
        }
        for presupuesto in presupuestos
    ]
    return JsonResponse(data, safe=False)


def obtener_clientes_presupuestos_ing(request):
    clientes = Proyecto.objects.values_list('cliente__nombre', flat=True).distinct()
    return JsonResponse(list(clientes), safe=False)