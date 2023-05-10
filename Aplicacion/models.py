from django.core.validators import RegexValidator, EmailValidator
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


class Cliente(models.Model):
    nombre = models.CharField(max_length=50, validators=[
        RegexValidator(r'^[\w\s]*$', message='Introduzca solo letras, números y espacios en blanco')])
    ruc = models.CharField(max_length=20, validators=[RegexValidator(r'^[\d\-]*$', message='Introduzca solo numeros y un guion, sin puntos')])
    nombre_contacto = models.CharField(max_length=50, validators=[RegexValidator(r'^[a-zA-Z ]*$', message='Introduzca solo letras o espacios en blanco')])
    numero_contacto = models.CharField(max_length=20, validators=[RegexValidator(r'^[\d]*$', message='Introduzca solo numeros')])
    email = models.EmailField()

    def __str__(self):
        return self.nombre


def validate_fecha_nacimiento(value):
    if value > date.today():
        raise ValidationError('La fecha de nacimiento no puede ser mayor a la fecha actual')


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=20, validators=[RegexValidator(r'^[\d\-]*$', message='Introduzca solo numeros y un guion, sin puntos')])
    nombre_contacto = models.CharField(max_length=50, validators=[RegexValidator(r'^[a-zA-Z ]*$', message='Introduzca solo letras o espacios en blanco')])
    numero_contacto = models.CharField(max_length=20, validators=[RegexValidator(r'^[\d]*$', message='Introduzca solo numeros')])
    email = models.EmailField(max_length=254, validators=[EmailValidator()])

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
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'perfil__rol__nombre': 'INGENIERO'}, null=True)
    fecha_inicio = models.DateField(_('fecha de inicio'), null=True)
    fecha_fin = models.DateField(_('fecha de fin'), null=True)
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

    def __str__(self):
        return f'{self.id}'


class Presupuesto(models.Model):
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'perfil__rol__nombre': 'INGENIERO'})
    monto_total = models.DecimalField(_('monto total'), max_digits=10, decimal_places=0, null=True)
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

    def __str__(self):
        return f'{self.obra} - {self.estado}'


class Proyecto(models.Model):
    nombre = models.CharField(_('nombre'), max_length=100)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name=_('cliente'))
    presupuesto = models.OneToOneField(Presupuesto, on_delete=models.CASCADE, verbose_name=_('presupuesto'))
    obra = models.OneToOneField(Obra, on_delete=models.CASCADE, verbose_name=_('obra'))

    class Meta:
        verbose_name = _('proyecto')


class Pedido(models.Model):
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'perfil__rol__nombre': 'INGENIERO'})
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE, verbose_name=_('obra'))
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name=_('material'))
    fecha_solicitud = models.DateField(_('fecha de solicitud'))
    fecha_entrega = models.DateField(_('fecha de entrega'))
    ESTADOS = (
        ('P', _('Pendiente')),
        ('E', _('Entregado')),
    )
    estado = models.CharField(_('estado'), max_length=1, choices=ESTADOS, default='P')

    class Meta:
        verbose_name = _('pedido')
        verbose_name_plural = _('pedidos')

    def __str__(self):
        return f'{self.material} - {self.obra} - {self.estado}'
