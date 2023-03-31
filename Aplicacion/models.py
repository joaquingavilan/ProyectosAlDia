from django.core.validators import RegexValidator, EmailValidator
from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


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


class Ingeniero(models.Model):
    nombre = models.CharField(max_length=50, validators=[RegexValidator(r'^[a-zA-Z]*$', 'Solo se permiten letras en el nombre.')])
    apellido = models.CharField(max_length=50, validators=[RegexValidator(r'^[a-zA-Z]*$', 'Solo se permiten letras en el apellido.')])
    fecha_nacimiento = models.DateField(validators=[validate_fecha_nacimiento])
    telefono = models.CharField(max_length=15, validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'El formato de teléfono no es válido. Ejemplo: +541155555555.')])
    email = models.EmailField()

    ESTADO_CHOICES = (
        ('L', 'Libre'),
        ('O', 'Ocupado'),
    )
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='L')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


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

