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
    path('inicio_adm/', views.inicio_adm, name='inicio_adm'),
    path('inicio_deposito/', views.inicio_deposito, name='inicio_deposito'),
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
    path('get_ingeniero_data/<int:ingeniero_id>/', views.get_ingeniero_data, name='get_ingeniero_data'),
    path('editar_ingeniero/<int:pk>/', views.editar_ingeniero, name='editar_ingeniero'),
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
    path('ver_certificados_adm', views.ver_certificados_adm, name='ver_certificados_adm'),
    path('materiales/editar/<int:pk>/', views.editar_material, name='editar_material'),
    path('buscar_materiales/', views.buscar_materiales, name='buscar_materiales'),
    path('ver_material/<int:id_material>/', views.ver_material, name='ver_material'),
    path('ABM/usuarios/login/', views.loguear_usuario, name='login'),
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
    path('ver_pedidos_adm/<int:obra_id>/', views.ver_pedidos_adm, name='ver_pedidos_adm'),
    path('obtener_clientes_con_proyectos/', views.obtener_clientes_con_proyectos, name='obtener_clientes_con_proyectos'),
    path('obtener_clientes_con_obras/', views.obtener_clientes_con_obras, name='obtener_clientes_con_obras'),
    path('obtener_ingenieros_presupuesto/', views.obtener_ingenieros_presupuesto, name='obtener_ingenieros_presupuesto'),
    path('obtener_estados_presupuesto/', views.obtener_estados_presupuesto, name='obtener_estados_presupuesto'),
    path('obtener_estados_anticipo/', views.obtener_estados_anticipo, name='obtener_estados_anticipo'),
    path('obtener_ingenieros_obra/', views.obtener_ingenieros_obra, name='obtener_ingenieros_obra'),
    path('obtener_estados_obra/', views.obtener_estados_obra, name='obtener_estados_obra'),
    path('obtener_estados_obras_ing/', views.obtener_estados_obras_ing, name='obtener_estados_obras_ing'),
    path('obtener_ciudades_con_proyectos/', views.obtener_ciudades_con_proyectos, name='obtener_ciudades_con_proyectos'),
    path('ver_proyectos_cliente/<str:cliente_nombre>/', views.ver_proyectos_cliente,name='ver_proyectos_cliente'),
    path('ver_proyectos_encargado_presupuesto/<str:ingeniero_user>/',views.ver_proyectos_encargado_presupuesto, name='ver_proyectos_encargado_presupuesto'),
    path('ver_proyectos_encargado_obra/<str:ingeniero_user>/', views.ver_proyectos_encargado_obra,name='ver_proyectos_encargado_obra'),
    path('ver_proyectos_estado_presupuesto/<str:estado>/', views.ver_proyectos_estado_presupuesto,name='ver_proyectos_estado_presupuesto'),
    path('ver_proyectos_estado_obra/<str:estado>/', views.ver_proyectos_estado_obra,name='ver_proyectos_estado_obra'),
    path('ver_proyectos_estado_anticipo/<str:anticipo>/', views.ver_proyectos_estado_anticipo,name='ver_proyectos_estado_anticipo'),
    path('ver_proyectos_ciudad/<str:ciudad>/', views.ver_proyectos_ciudad, name='ver_proyectos_ciudad'),
    path('exportar_excel/', views.exportar_excel, name='exportar_excel'),
    path('exportar_pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('obtener_materiales_marca/', views.obtener_materiales_marca, name='obtener_materiales_marca'),
    path('obtener_materiales_proveedor/', views.obtener_materiales_proveedor, name='obtener_materiales_proveedor'),
    path('obtener_materiales_stock/', views.obtener_materiales_stock, name='obtener_materiales_stock'),
    path('ver_materiales_marca/<str:marca_nombre>/', views.ver_materiales_marca, name='ver_materiales_marca'),
    path('ver_materiales_proveedor/<str:proveedor>/', views.ver_materiales_proveedores, name='ver_materiales_proveedores'),
    path('ver_materiales_stock/<str:cantidad>/', views.ver_materiales_stock, name='ver_materiales_stock'),
    path('cargar_presupuesto/<int:pk>', views.cargar_presupuesto, name='cargar_presupuesto'),
    path('ver_archivo_presupuesto/<int:pk>', views.ver_archivo_presupuesto, name='ver_archivo_presupuesto'),
    path('modificar_presupuesto/<int:pk>', views.modificar_presupuesto, name='modificar_presupuesto'),
    path('editar_subitem/<int:subitem_id>/', views.editar_subitem, name='editar_subitem'),
    path('eliminar_subitem/<int:subitem_id>/', views.eliminar_subitem, name='eliminar_subitem'),
    path('actualizar_estado/<int:presupuesto_id>/', views.actualizar_estado, name='actualizar_estado'),
    path('pantallas_adm/ver_presupuestos_adm/', views.ver_presupuestos_adm, name='ver_presupuestos_adm'),
    path('actualizar_anticipo/<int:presupuesto_id>/', views.actualizar_anticipo, name='actualizar_anticipo'),
    path('actualizar_monto_total/', views.actualizar_monto_total, name='actualizar_monto_total'),
    path('pantallas_adm/ver_obras_adm', views.ver_obras_adm, name='ver_obras_adm'),
    path('pantallas_adm/ver_obras_filtradas/', views.ver_obras_filtradas, name='ver_obras_filtradas'),
    path('pantallas_adm/ver_obra_adm/<int:obra_id>/', views.ver_obra_adm, name='ver_obra_adm'),
    path('buscar_obras/', views.buscar_obras, name='buscar_obras'),
    path('obtener_estados_obra/', views.obtener_estados_obra, name='obtener_estados_obra'),
    path('obtener_ingenieros_obra/', views.obtener_ingenieros_obra, name='obtener_ingenieros_obra'),
    path('obtener_fechas_inicio/', views.obtener_fechas_inicio, name='obtener_fechas_inicio'),
    path('obtener_fechas_fin/', views.obtener_fechas_fin, name='obtener_fechas_fin'),
    path('pantallas_adm/asignar_obras', views.asignar_obras, name='asignar_obras'),
    path('asignar_ingeniero_a_obra/', views.asignar_ingeniero_a_obra, name='asignar_ingeniero_a_obra'),
    path('buscar_presupuestos/', views.buscar_presupuestos, name='buscar_presupuestos'),
    path('buscar_presupuestos_ingeniero/', views.buscar_presupuestos_ingeniero, name='buscar_presupuestos_ingeniero'),
    path('buscar_presupuestos_terminados/', views.buscar_presupuestos_terminados, name='buscar_presupuestos_terminados'),
    path('ver_presupuesto_adm/<int:presupuesto_id>/', views.ver_presupuesto_adm, name='ver_presupuesto_adm'),
    path('ver_presupuestos_cliente/<str:cliente_nombre>/', views.ver_presupuestos_cliente,name='ver_presupuestos_cliente'),
    path('ver_presupuestos_encargado_presupuesto/<str:ingeniero_user>/', views.ver_presupuestos_encargado_presupuesto, name='ver_presupuestos_encargado_presupuesto'),
    path('ver_presupuestos_estado_presupuesto/<str:estado>/', views.ver_presupuestos_estado_presupuesto, name='ver_presupuestos_estado_presupuesto'),
    path('iniciar_obra/<int:obra_id>/', views.iniciar_obra, name='iniciar_obra'),
    path('agendar_inicio_obra/<int:obra_id>/', views.agendar_inicio_obra, name='agendar_inicio_obra'),
    path('finalizar_obra/<int:obra_id>/', views.finalizar_obra, name='finalizar_obra'),
    path('elaborar_certificado', views.elaborar_certificado, name='elaborar_certificado'),
    path('ver_certificados_ing', views.ver_certificados_ing, name='ver_certificados_ing'),
    path('obtener_presupuesto_detalle/<int:proyecto_id>/', views.obtener_presupuesto_detalle, name='obtener_presupuesto_detalle'),
    path('registrar_anticipo/', views.registrar_anticipo, name='registrar_anticipo'),
    path('obtener_filtro_valores/', views.obtener_filtro_valores, name='obtener_filtro_valores'),
    path('obtener_presupuestos_filtrados/', views.obtener_presupuestos_filtrados, name='obtener_presupuestos_filtrados'),
    path('obtener_monto_presupuesto/', views.obtener_monto_presupuesto, name='obtener_monto_presupuesto'),
    path('cargar_detalles_certificado/', views.cargar_detalles_certificado, name='cargar_detalles_certificado'),
    path('cargar_distritos/', views.cargar_distritos, name='cargar_distritos'),
    path('crear_presupuesto/<int:presupuesto_id>/', views.crear_presupuesto, name='crear_presupuesto'),
    path('cambiar_password/', views.cambiar_password, name='cambiar_password'),
    path('obtener_subsecciones', views.obtener_subsecciones, name='obtener_subsecciones'),
    path('obtener_secciones', views.obtener_secciones, name='obtener_secciones'),
    path('obtener_detalles', views.obtener_detalles, name='obtener_detalles'),
    path('get_subsecciones_detalles/', views.get_subsecciones_detalles, name='get_subsecciones_detalles'),
    path('get_detalles/', views.get_detalles, name='get_detalles'),
    path('get_subseccion_name/', views.get_subseccion_name, name='get_subseccion_name'),
    path('crear_seccion/', views.crear_seccion, name='crear_seccion'),
    path('crear_detalle/', views.crear_detalle, name='crear_detalle'),
    path('crear_subseccion/', views.crear_subseccion, name='crear_subseccion'),
    path('get_detalle_data/', views.get_detalle_data, name='get_detalle_data'),
    path('associate_subseccion/', views.associate_subseccion, name='associate_subseccion'),
    path('get_unidad_medida/', views.get_unidad_medida, name='get_unidad_medida'),
    path('guardar_presupuesto/', views.guardar_presupuesto, name='guardar_presupuesto'),
    path('exportar_presupuesto/<int:presupuesto_id>/<int:archivo_presupuesto_id>/<str:tipo>/', views.exportar_presupuesto, name='exportar_presupuesto'),
    path('exportar_a_excel/<int:archivo_presupuesto_id>/<int:presupuesto_id>/', views.exportar_a_excel, name='exportar_a_excel'),
    path('exportar_a_pdf/<int:archivo_presupuesto_id>/<int:presupuesto_id>/', views.exportar_a_pdf, name='exportar_a_pdf'),
    path('armar_cronograma/<int:obra_id>/', views.armar_cronograma, name='armar_cronograma'),
    path('ver_pedido/<int:pedido_id>/', views.ver_pedido, name='ver_pedido'),
    path('ver_pedido_adm/<int:pedido_id>/', views.ver_pedido_adm, name='ver_pedido_adm'),
    path('guardar_cronograma/', views.guardar_cronograma, name='guardar_cronograma'),
    path('guardar_certificado/', views.guardar_certificado, name='guardar_certificado'),
    path('ver_proyectos_filtrados/', views.ver_proyectos_filtrados, name='ver_proyectos_filtrados'),
    path('ver_presupuestos_filtrados/', views.ver_presupuestos_filtrados, name='ver_presupuestos_filtrados'),
    path('ver_obras_filtrados/', views.ver_obras_filtrados, name='ver_obras_filtrados'),
    path('vista_redireccion/<str:campo>/<str:valor>/', views.vista_redireccion, name='vista_redireccion'),
    path('vista_redireccion_obra/<str:campo>/<str:valor>/', views.vista_redireccion_obra, name='vista_redireccion_obra'),
    path('buscar_materiales/', views.buscar_materiales, name='buscar_materiales'),
    path('ver_cronograma/<int:obra_id>/<int:cronograma_id>/', views.ver_cronograma, name='ver_cronograma'),
    path('ver_cronograma_adm/<int:obra_id>/', views.ver_cronograma_adm, name='ver_cronograma_adm'),
    path('presupuestos_pendientes/', views.presupuestos_pendientes, name='presupuestos_pendientes'),
    path('obras_pendientes/', views.obras_pendientes, name='obras_pendientes'),
    path('proximas_actividades/', views.proximas_actividades, name='proximas_actividades'),
    path('marcar_como_realizado/', views.marcar_como_realizado, name='marcar_como_realizado'),
    path('presupuestos_enviados_sin_anticipo/', views.presupuestos_enviados_sin_anticipo, name='presupuestos_enviados_sin_anticipo'),
    path('presupuestos_en_elaboracion/', views.presupuestos_en_elaboracion, name='presupuestos_en_elaboracion'),
    path('obras-pendientes-asignacion/', views.obras_pendientes_de_asignacion, name='obras_pendientes_asignacion'),
    path('registrar_pago_certificado/<int:certificado_id>/', views.registrar_pago_certificado, name='registrar_pago_certificado'),
    path('marcar-enviado/<int:certificado_id>/', views.marcar_certificado_enviado, name='marcar_certificado_enviado'),
    path('ver_obras_terminadas', views.ver_obras_terminadas, name='ver_obras_terminadas'),
    path('ver_pedidos_obra/<int:obra_id>/', views.ver_pedidos_obra, name='ver_pedidos_obra'),
    path('ver_pedido_a_devolver/<int:pedido_id>/', views.ver_pedido_a_devolver, name='ver_pedido_a_devolver'),
    path('confirmar_devolucion/', views.confirmar_devolucion, name='confirmar_devolucion'),
    path('ver_devolucion/<int:devolucion_id>/', views.ver_devolucion, name='ver_devolucion'),
    path('ver_devoluciones', views.ver_devoluciones, name='ver_devoluciones'),
    path('ver_archivo_certificado/<int:pk>', views.ver_archivo_certificado, name='ver_archivo_certificado'),
    path('ver_certificado_adm/<int:pk>', views.ver_certificado_adm, name='ver_certificado_adm'),
    path('ver_certificado_gerente/<int:pk>', views.ver_certificado_gerente, name='ver_certificado_gerente'),
    path('ver_proveedores_dep', views.ver_proveedores, name='ver_proveedores_dep'),
    path('ver_devoluciones_dep', views.ver_devoluciones, name='ver_devoluciones_dep'),
    path('devoluciones_pedidos_pendientes', views.devoluciones_pedidos_pendientes, name='devoluciones_pedidos_pendientes'),
    path('ver_devolucion_dep/<int:devolucion_id>/', views.ver_devolucion, name='ver_devolucion_dep'),
    path('aceptar_devolucion_dep/<int:devolucion_id>/', views.aceptar_devolucion, name='aceptar_devolucion_dep'),
    path('rechazar_devolucion/<int:devolucion_id>/', views.rechazar_devolucion, name='rechazar_devolucion'),
    path('ver_pedidos_dep/', views.ver_pedidos_deposito, name='ver_pedidos_dep'),
    path('ver_pedido_dep/<int:pedido_id>', views.ver_pedido_deposito, name='ver_pedido_dep'),
    path('ver_pedido_gerente/<int:pedido_id>', views.ver_pedido_gerente, name='ver_pedido_gerente'),
    path('entregar_pedido/<int:pedido_id>', views.entregar_pedido, name='entregar_pedido'),
    path('ver_materiales_faltantes', views.ver_materiales_faltantes, name='ver_materiales_faltantes'),
    path('agregar_pedido_compra', views.agregar_pedido_compra, name='agregar_pedido_compra'),
    path('obtener_marcas_y_unidades/', views.obtener_marcas_y_unidades, name='obtener_marcas_y_unidades'),
    path('ver_pedidos_compras', views.ver_pedidos_compras, name='ver_pedidos_compras'),
    path('ver_pedido_compras/<int:pedido_id>', views.ver_pedido_compras, name='ver_pedido_compras'),
    path('pedido_compra/', views.pedido_compra, name='pedido_compra'),
    path('confirmar_pedido_compra', views.confirmar_pedido_compra, name='confirmar_pedido_compra'),
    path('ver_pedidos_compras_adm', views.ver_pedidos_compras_adm, name='ver_pedidos_compras_adm'),
    path('actualizar_pedido_compra/<int:pedido_id>/', views.actualizar_pedido_compra,name='actualizar_pedido_compra'),
    path('ver_inventario', views.ver_inventario, name='ver_inventario'),
    path('ver_resumen_obra/<int:obra_id>', views.ver_resumen_obra,name='ver_resumen_obra'),
    path('get_obras_activas/', views.get_obras_activas, name='get_obras_activas'),
    path('get_presupuestos_elaboracion/', views.get_presupuestos_elaboracion, name='get_presupuestos_elaboracion'),
    path('get_obras/', views.get_obras, name='get_obras'),
    path('ver_ing_gerente/', views.ver_ing_gerente, name='ver_ing_gerente'),
    path('ver_ing_gerente/<int:ingeniero_id>/', views.ver_ing_gerente, name='ver_ing_gerente_con_id'),
    path('get_gestion_obras_presupuestos/', views.get_gestion_obras_presupuestos, name='get_gestion_obras_presupuestos'),
    path('get_estados_por_tipo/', views.get_estados_por_tipo, name='get_estados_por_tipo'),
    path('get_gestion_pedidos_devoluciones/', views.get_gestion_pedidos_devoluciones, name='get_gestion_pedidos_devoluciones'),
    path('get_estados_por_tipo_pedido_devolucion/', views.get_estados_por_tipo_pedido_devolucion, name='get_estados_por_tipo_pedido_devolucion'),
    path('pantallas_gerente/ver_obras_gerente', views.ver_obras_gerente, name='ver_obras_gerente'),
    path('obtener_montos_obra', views.obtener_montos_obra, name='obtener_montos_obra'),
    path('obtener_datos_progreso', views.obtener_datos_progreso, name='obtener_datos_progreso'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
