from django.core.validators import RegexValidator, EmailValidator, URLValidator
from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models import Q


class Ciudad(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre


class Personal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    must_change_password = models.BooleanField(default=True)


class Contacto(models.Model):
    nombre = models.CharField(
        max_length=50,
        validators=[RegexValidator(r'^[a-zA-Z ]*$', message='Introduzca solo letras o espacios en blanco')]
    )
    numero = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^[\d]*$', message='Introduzca solo numeros')]
    )
    email = models.EmailField(validators=[EmailValidator()], null=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, null=True, blank=True)
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.numero}"


class Cliente(models.Model):
    TIPO_PERSONA_CHOICES = [
        ('Juridica', 'Jurídica'),
        ('Fisica', 'Física'),
    ]

    nombre = models.CharField(max_length=50, validators=[RegexValidator(r'^[\w\s]*$', message='Introduzca solo letras, números y espacios en blanco')])
    ruc = models.CharField(max_length=20, validators=[RegexValidator(r'^[\d\-]*$', message='Introduzca solo números y un guion, sin puntos')])
    email = models.EmailField()
    tipo_persona = models.CharField(max_length=8, choices=TIPO_PERSONA_CHOICES, default='Fisica')
    direccion = models.CharField(max_length=200, default='', blank=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, validators=[RegexValidator(r'^\d{6,20}$', message='Introduzca un teléfono válido (solo números entre 6 a 20 dígitos)')])  # Añadido
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


def validate_fecha_nacimiento(value):
    if value > date.today():
        raise ValidationError('La fecha de nacimiento no puede ser mayor a la fecha actual')


class Proveedor(models.Model):
    nombre = models.CharField(max_length=50, validators=[
        RegexValidator(r'^[\w\s]*$', message='Introduzca solo letras, números y espacios en blanco')])
    ruc = models.CharField(max_length=20, validators=[
        RegexValidator(r'^[\d\-]*$', message='Introduzca solo numeros y un guion, sin puntos')])
    email = models.EmailField(max_length=254, validators=[EmailValidator()])
    direccion = models.CharField(max_length=200, default='', blank=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, blank=True, null=True)
    pagina_web = models.CharField(max_length=255, validators=[
        RegexValidator(r'^[\w\-]+\.[\w\-]+(\.[\w\-]+)?$',
                       message='La URL debe tener el formato "texto.texto" o "texto.texto.texto"')
    ], blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, validators=[RegexValidator(r'^\d{6,20}$',
                                                                                      message='Introduzca un teléfono válido (solo números entre 6 a 20 dígitos)')])  # Añadido
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class UnidadMedida(models.Model):
    descripcion = models.CharField(max_length=50)
    nombre = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    nombre = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre


class Material(models.Model):
    nombre = models.CharField(max_length=100)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    medida = models.ForeignKey(UnidadMedida, on_delete=models.CASCADE)
    minimo = models.PositiveIntegerField()
    unidades_stock = models.PositiveIntegerField()
    fotografia = models.ImageField(upload_to='imagenes/', blank=True, null=True)
    precio = models.PositiveIntegerField()  # Añadido campo precio

    def __str__(self):
        return self.nombre


class Obra(models.Model):
    proyecto = models.OneToOneField('Proyecto', on_delete=models.CASCADE)
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to=Q(groups__name='INGENIERO'), null=True)
    fecha_inicio = models.DateField(_('fecha de inicio'), null=True)
    fecha_fin = models.DateField(_('fecha de fin'), null=True)
    plazo = models.PositiveIntegerField(null=True)
    ESTADOS = (
        ('NI', _('No iniciada')),
        ('E', _('En ejecución')),
        ('F', _('Finalizada')),
    )
    estado = models.CharField(_('estado'), max_length=2, choices=ESTADOS, default='NI')

    @property
    def monto_total(self):
        total = sum(item.monto_total for item in self.pedido_set.all())
        return total
    class Meta:
        verbose_name = _('obra')
        verbose_name_plural = _('obras')


class Presupuesto(models.Model):
    proyecto = models.OneToOneField('Proyecto', on_delete=models.CASCADE)
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to=Q(groups__name='INGENIERO'))
    subtotal = models.DecimalField(_('subtotal'), max_digits=15, decimal_places=0, null=True, blank=True)
    iva = models.DecimalField(_('IVA'), max_digits=15, decimal_places=0, null=True, blank=True)
    monto_total = models.DecimalField(_('monto total'), max_digits=15, decimal_places=0, null=True)
    anticipo = models.BooleanField(_('anticipo'), default=False)
    monto_anticipo = models.DecimalField(_('monto anticipo'), max_digits=15, decimal_places=0, null=True)
    fecha_pago_anticipo = models.DateField(_('fecha de pago del anticipo'), null=True, blank=True)
    comprobante_anticipo = models.FileField(upload_to='comprobantes/', blank=True, null=True)
    ESTADOS = (
        ('E', _('En elaboración')),
        ('S', _('Enviado')),
        ('A', _('Aprobado')),
    )
    estado = models.CharField(_('estado'), max_length=1, choices=ESTADOS, default='E')
    fecha_asignacion = models.DateField(_('fecha de asignación'), auto_now_add=True, null=True, blank=True)

    def get_estado_display(self):
        return dict(Presupuesto.ESTADOS)[self.estado]

    class Meta:
        verbose_name = _('presupuesto')
        verbose_name_plural = _('presupuestos')


class Proyecto(models.Model):
    nombre = models.CharField(_('nombre'), max_length=100)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name=_('cliente'))
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = _('proyecto')

    def __str__(self):
        return f'{self.nombre}'


class Pedido(models.Model):
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to=Q(groups__name='INGENIERO'))
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE, verbose_name=_('obra'))
    fecha_solicitud = models.DateField(_('fecha de solicitud'))
    fecha_entrega = models.DateField(_('fecha de entrega'), null=True, blank=True)
    ESTADOS = (
        ('P', _('Pendiente')),
        ('E', _('Entregado')),
    )
    estado = models.CharField(_('estado'), max_length=1, choices=ESTADOS, default='P')
    materiales = models.ManyToManyField(Material, through='MaterialPedido')

    class Meta:
        verbose_name = _('pedido')
        verbose_name_plural = _('pedidos')

    def __str__(self):
        return f'{self.obra} - {self.estado}'
    @property
    def monto_total(self):
        total = sum(item.monto for item in self.materialpedido_set.all())
        return total

class MaterialPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    class Meta:
        verbose_name = _('material en pedido')
        verbose_name_plural = _('materiales en pedido')

    def __str__(self):
        return f'{self.material} - {self.pedido}'
    @property
    def monto(self):
        return self.material.precio * self.cantidad

class Seccion(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


class SubSeccion(models.Model):
    secciones = models.ManyToManyField('Seccion', blank=True)  # 'Seccion' es el nombre de tu modelo de sección
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


class Detalle(models.Model):
    subseccion = models.ForeignKey(SubSeccion, on_delete=models.CASCADE)
    rubro = models.CharField(max_length=255)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    precio_total = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return self.rubro


class ArchivoPresupuesto(models.Model):
    presupuesto = models.OneToOneField(Presupuesto, on_delete=models.CASCADE)
    secciones = models.ManyToManyField(Seccion)
    subsecciones = models.ManyToManyField(SubSeccion)
    detalles = models.ManyToManyField(Detalle)


class Cronograma(models.Model):
    archivo_presupuesto = models.OneToOneField(ArchivoPresupuesto, on_delete=models.CASCADE)


class DetalleCronograma(models.Model):
    cronograma = models.ForeignKey(Cronograma, on_delete=models.CASCADE, related_name='detalles_cronograma')
    detalle = models.ForeignKey(Detalle, on_delete=models.CASCADE)
    fecha_programada = models.DateField(null=True, blank=True)
    fecha_culminacion = models.DateField(null=True, blank=True)
    realizado = models.BooleanField(default=False)  # Campo booleano para indicar si la actividad fue realizada

    def __str__(self):
        return f"{self.detalle} - {self.fecha_programada}"


class Devolucion(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, default=1)
    ingeniero = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to=Q(groupsname='INGENIERO'))
    obra = models.ForeignKey('Obra', on_delete=models.CASCADE, verbose_name=_('obra'))
    fecha_solicitud = models.DateField(_('fecha de solicitud'))
    fecha_devolucion = models.DateField(_('fecha de devolucion'), null=True, blank=True)
    observaciones = models.TextField(blank=True)
    ESTADOS = (
        ('P', _('Pendiente')),
        ('D', _('Devuelto')),
        ('R', _('Rechazado')),
    )
    estado = models.CharField(_('estado'), max_length=1, choices=ESTADOS, default='P')
    materiales = models.ManyToManyField('Material', through='MaterialDevuelto', null=True)

    @property
    def monto_total(self):
        total = sum(item.monto for item in self.materialdevuelto_set.all())
        return total
    class Meta:
        verbose_name = _('devolución')
        verbose_name_plural = _('devoluciones')

    def str(self):
        return f'{self.obra} - {self.estado}'


class MaterialDevuelto(models.Model):
    devolucion = models.ForeignKey('Devolucion', on_delete=models.CASCADE, default=1)
    material = models.ForeignKey('Material', on_delete=models.CASCADE, null=True, default=None)
    cantidad = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('material devuelto')
        verbose_name_plural = _('materiales devueltos')

    @property
    def monto(self):
        return self.material.precio * self.cantidad
    def str__(self):
        return f'{self.material} - {self.pedido}'


class Certificado(models.Model):
    presupuesto = models.ForeignKey('Presupuesto', on_delete=models.CASCADE)
    ingeniero = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to=Q(groups__name='INGENIERO'))
    subtotal = models.DecimalField(_('subtotal'), max_digits=15, decimal_places=0, null=True, blank=True)
    iva = models.DecimalField(_('IVA'), max_digits=15, decimal_places=0, null=True, blank=True)
    monto_total = models.DecimalField(_('monto total'), max_digits=15, decimal_places=0, null=True)
    fecha_pago = models.DateField(_('fecha de pago del certificado'), null=True, blank=True)
    fecha_envio = models.DateField(_('fecha de envio del certificado'), null=True, blank=True)
    fecha_creacion = models.DateTimeField(_('fecha de creación del certificado'), null=True, blank=True)
    comprobante_pago = models.FileField(upload_to='comprobantes/', blank=True, null=True)
    ESTADOS = (
        ('P', _('Pendiente de envio')),
        ('S', _('Enviado')),
        ('A', _('Aprobado')),
    )
    estado = models.CharField(_('estado'), max_length=1, choices=ESTADOS, default='P')

    def get_estado_display(self):
        return dict(Certificado.ESTADOS)[self.estado]

    class Meta:
        verbose_name = _('certificado')
        verbose_name_plural = _('certificados')


class ArchivoCertificado(models.Model):
    certificado = models.OneToOneField(Certificado, on_delete=models.CASCADE)
    secciones = models.ManyToManyField(Seccion)
    subsecciones = models.ManyToManyField(SubSeccion)
    detalles = models.ManyToManyField(Detalle)


class PedidoCompra(models.Model):
    fecha_solicitud = models.DateField(_('fecha de solicitud'))
    fecha_entrega = models.DateField(_('fecha de entrega'), null=True, blank=True)
    comprobante = models.ImageField(upload_to='comprobantes/compra', blank=True, null=True)
    ESTADOS = (
        ('P', _('Pendiente')),
        ('R', _('Recibido')),
    )
    estado = models.CharField(_('estado'), max_length=1, choices=ESTADOS, default='P')
    materiales = models.ManyToManyField(Material, through='MaterialPedidoCompra')

    class Meta:
        verbose_name = _('pedido')
        verbose_name_plural = _('pedidos')

    @property
    def monto_total(self):
        total = sum(item.monto for item in self.materialpedidocompra_set.all())
        return total
    def str(self):
        return f'{self.estado}'


class MaterialPedidoCompra(models.Model):
    pedido_compra = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    class Meta:
        verbose_name = _('material en pedido de compra')
        verbose_name_plural = _('materiales en pedido de compra')

    @property
    def monto(self):
        return self.material.precio * self.cantidad
    def str(self):
        return f'{self.material} - {self.pedido_compra}'



class DimMaterial(models.Model):
    material_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    marca_id = models.IntegerField()
    medida_id = models.IntegerField()
    minimo = models.IntegerField()
    unidades_stock = models.IntegerField()
    fotografia = models.CharField(max_length=255)
    id_proveedor_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'dim_material'


class DimCliente(models.Model):
    cliente_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    ciudad_id = models.IntegerField()
    direccion = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'dim_cliente'


class DimCiudad(models.Model):
    ciudad_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'dim_ciudad'


class DimUsuario(models.Model):
    usuario_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateField()

    class Meta:
        managed = False
        db_table = 'dim_usuario'


class DimProveedor(models.Model):
    proveedor_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    ciudad_id = models.IntegerField()
    direccion = models.CharField(max_length=255)
    pagina_web = models.CharField(max_length=255)
    observaciones = models.TextField()
    telefono = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'dim_proveedor'


class DimProyecto(models.Model):
    proyecto_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    cliente_id = models.IntegerField()
    ciudad_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'dim_proyecto'



class HechoCertificado(models.Model):
    id = models.AutoField(primary_key=True)
    ingeniero_id = models.IntegerField()
    presupuesto_id = models.IntegerField()
    estado = models.CharField(max_length=50)
    fecha_creacion = models.DateField()
    fecha_envio = models.DateField()
    fecha_pago = models.DateField()
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'hecho_certificado'


class HechoMaterialPedido(models.Model):
    id = models.AutoField(primary_key=True)
    pedido_id = models.IntegerField()
    material_id = models.IntegerField()
    cantidad = models.IntegerField()
    fecha_solicitud = models.DateField()
    fecha_entrega = models.DateField()
    estado = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'hecho_materialpedido'


class HechoDevolucion(models.Model):
    id = models.AutoField(primary_key=True)
    ingeniero_id = models.IntegerField()
    obra_id = models.IntegerField()
    pedido_id = models.IntegerField()
    fecha_solicitud = models.DateField()
    fecha_devolucion = models.DateField()
    observaciones = models.TextField()
    estado = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'hecho_devolucion'


class HechoPedido(models.Model):
    id = models.AutoField(primary_key=True)
    obra_id = models.IntegerField()
    solicitante_id = models.IntegerField()
    fecha_solicitud = models.DateField()
    fecha_entrega = models.DateField()
    estado = models.CharField(max_length=50)
    monto_total = models.PositiveIntegerField()  # Nuevo campo

    class Meta:
        managed = False
        db_table = 'hecho_pedido'


class HechoPresupuesto(models.Model):
    id = models.AutoField(primary_key=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50)
    encargado_id = models.IntegerField()
    proyecto_id = models.IntegerField()
    anticipo = models.BooleanField()
    monto_anticipo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago_anticipo = models.DateField()
    comprobante_anticipo = models.CharField(max_length=255)
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'hecho_presupuesto'


class HechoEstadoIngeniero(models.Model):
    ingeniero_id = models.IntegerField()
    nombre_ingeniero = models.CharField(max_length=100)
    cantidad_obras_ejecucion = models.IntegerField()
    cantidad_presupuestos_elaboracion = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'hecho_estado_ingeniero'


class HechoMaterialPorObra(models.Model):
    id = models.AutoField(primary_key=True)
    obra_id = models.IntegerField()
    material_id = models.IntegerField()
    cantidad_total = models.IntegerField(default=0)
    obra_nombre = models.CharField(max_length=255)
    material_nombre = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'hechomaterialporobra'


class HechoCronograma(models.Model):
    cronograma_id = models.IntegerField()
    detalle_id = models.IntegerField()
    fecha_programada = models.DateField(null=True, blank=True)
    fecha_culminacion = models.DateField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'hechocronograma'


class HechoObra(models.Model):
    id = models.AutoField(primary_key=True)
    id_obra = models.IntegerField()
    id_encargado = models.IntegerField(null=True)
    estado = models.CharField(max_length=2)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    plazo = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'hecho_obra'