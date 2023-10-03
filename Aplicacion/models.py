from django.core.validators import RegexValidator, EmailValidator, URLValidator
from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Rol(models.Model):

    ROL_CHOICES = [
        ('', ''),
        ('GERENTE', 'Gerente'),
        ('ADMINISTRADOR', 'Administrador'),
        ('INGENIERO', 'Ingeniero'),
        ('ENCARGADO_DEPOSITO', 'Encargado de Depósito'),
    ]

    nombre = models.CharField(choices=ROL_CHOICES, max_length=20)

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, default='', blank=True, null=True)

    def __str__(self):
        return self.user.username


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

    nombre = models.CharField(max_length=50, validators=[
        RegexValidator(r'^[\w\s]*$', message='Introduzca solo letras, números y espacios en blanco')])
    ruc = models.CharField(max_length=20, validators=[RegexValidator(r'^[\d\-]*$', message='Introduzca solo numeros y un guion, sin puntos')])
    email = models.EmailField()
    tipo_persona = models.CharField(max_length=8, choices=TIPO_PERSONA_CHOICES, default='Fisica')
    direccion = models.CharField(max_length=200, default='', blank=True)
    ciudad = models.CharField(max_length=20, default='', blank=True)

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
    ciudad = models.CharField(max_length=20, default='', blank=True)
    pagina_web = models.CharField(max_length=255, validators=[
        RegexValidator(r'^[\w\-]+\.[\w\-]+(\.[\w\-]+)?$',
                       message='La URL debe tener el formato "texto.texto" o "texto.texto.texto"')
    ], blank=True, null=True)

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class Material(models.Model):
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    medida = models.CharField(max_length=50)
    minimo = models.PositiveIntegerField()
    unidades_stock = models.PositiveIntegerField()
    fotografia = models.ImageField(upload_to='imagenes/', blank=True, null=True)

    def __str__(self):
        return self.nombre


class Obra(models.Model):
    proyecto = models.OneToOneField('Proyecto', on_delete=models.CASCADE)
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'perfil__rol__nombre': 'INGENIERO'}, null=True)
    fecha_inicio = models.DateField(_('fecha de inicio'), null=True)
    fecha_fin = models.DateField(_('fecha de fin'), null=True)
    plazo = models.PositiveIntegerField(null=True)
    ESTADOS = (
        ('NI', _('No iniciada')),
        ('E', _('En ejecución')),
        ('F', _('Finalizada')),
    )
    estado = models.CharField(_('estado'), max_length=2, choices=ESTADOS, default='NI')

    def get_estado_display(self):
        return dict(self.ESTADOS)[self.estado]

    class Meta:
        verbose_name = _('obra')
        verbose_name_plural = _('obras')


class Presupuesto(models.Model):
    proyecto = models.OneToOneField('Proyecto', on_delete=models.CASCADE)
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'perfil__rol__nombre': 'INGENIERO'})
    monto_total = models.DecimalField(_('monto total'), max_digits=15, decimal_places=0, null=True)
    anticipo = models.BooleanField(_('anticipo'), default=False)
    monto_anticipo = models.DecimalField(_('monto anticipo'), max_digits=15, decimal_places=0, null=True)
    fecha_pago_anticipo = models.DateField(_('fecha de pago del anticipo'), null=True, blank=True)
    ESTADOS = (
        ('E', _('En elaboración')),
        ('S', _('Enviado')),
        ('A', _('Aprobado')),
    )
    estado = models.CharField(_('estado'), max_length=1, choices=ESTADOS, default='E')

    def get_estado_display(self):
        return dict(Presupuesto.ESTADOS)[self.estado]

    class Meta:
        verbose_name = _('presupuesto')
        verbose_name_plural = _('presupuestos')


class Proyecto(models.Model):
    nombre = models.CharField(_('nombre'), max_length=100)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name=_('cliente'))
    ciudad = models.CharField(max_length=100)

    class Meta:
        verbose_name = _('proyecto')

    def __str__(self):
        return f'{self.nombre}'


class Pedido(models.Model):
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'perfil__rol__nombre': 'INGENIERO'})
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


class MaterialPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    class Meta:
        verbose_name = _('material en pedido')
        verbose_name_plural = _('materiales en pedido')

    def __str__(self):
        return f'{self.material} - {self.pedido}'


class ArchivoPresupuesto(models.Model):
    presupuesto = models.OneToOneField('Presupuesto', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    fecha_carga = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to='presupuestos/')  # campo para almacenar el archivo
    # Otros campos que quieras agregar...


class Categoria(models.Model):
    archivo = models.ForeignKey(ArchivoPresupuesto, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.nombre}'


class Item(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    archivo = models.ForeignKey(ArchivoPresupuesto, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.nombre}'


class SubItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rubro = models.CharField(max_length=255)
    unidad_medida = models.CharField(max_length=50)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    precio_total = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f'{self.rubro}'


class Certificado(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE)
    ingeniero = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()
    ESTADOS = (
        ('P', 'Presentado'),
        ('G', 'Pagado'),
    )
    estado = models.CharField(max_length=1, choices=ESTADOS, default='P')


class CategoriaCertificado(models.Model):
    certificado = models.ForeignKey(Certificado, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return f'{self.nombre}'


class ItemCertificado(models.Model):
    categoria = models.ForeignKey(CategoriaCertificado, on_delete=models.CASCADE, null=True, blank=True)
    certificado = models.ForeignKey(Certificado, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return f'{self.nombre}'


class SubItemCertificado(models.Model):
    item = models.ForeignKey(ItemCertificado, on_delete=models.CASCADE)
    certificado = models.ForeignKey(Certificado, on_delete=models.CASCADE)
    subitem = models.ForeignKey(SubItem, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    unidad_medida = models.CharField(max_length=50)
    precio_total = models.DecimalField(max_digits=10, decimal_places=0)
    def __str__(self):
        return f'{self.nombre}'