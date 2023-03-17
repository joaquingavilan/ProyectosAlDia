from django.core.validators import RegexValidator, EmailValidator
from django.db import models
from datetime import date
from django.core.exceptions import ValidationError

class Cliente(models.Model):
    nombre = models.CharField(max_length=50, validators=[
        RegexValidator(r'^[\w\s]*$', message='Introduzca solo letras, números y espacios en blanco')])
    ruc = models.CharField(max_length=20, validators=[RegexValidator(r'^[\d\-]*$', message='Introduzca solo numeros y un guion, sin puntos')])
    nombre_contacto = models.CharField(max_length=50, validators=[RegexValidator(r'^[a-zA-Z ]*$', message='Introduzca solo letras o espacios en blanco')])
    numero_contacto = models.CharField(max_length=20, validators=[RegexValidator(r'^[\d]*$', message='Introduzca solo numeros')])
    email = models.EmailField()


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




