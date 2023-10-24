from django import forms
from .models import Cliente, Proveedor, Material, Proyecto, User, Contacto, Ciudad
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label=_('Nombre'), max_length=150)
    last_name = forms.CharField(label=_('Apellido'), max_length=150)
    email = forms.EmailField(label=_('Correo electrónico'), max_length=254)

    username = forms.CharField(
        label=_('Nombre de usuario'),
        max_length=150,
        help_text='',
        error_messages={'required': ''},
        widget=forms.TextInput(attrs={'autocomplete': 'username'})
    )
    password1 = forms.CharField(
        label=_('Contraseña'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='',
        error_messages={
            'required': '',
            'password_mismatch': _('Las dos contraseñas no coinciden.'),
            'password_too_short': _('La contraseña es muy corta.'),
            'password_common': _('La contraseña es muy común.'),
            'password_entirely_numeric': _('La contraseña no puede ser totalmente numérica.'),
        }
    )
    password2 = forms.CharField(
        label=_("Confirmar contraseña"),
        strip=False,
        widget=forms.PasswordInput,
        error_messages={
            'required': '',
            'password_mismatch': _('Las dos contraseñas no coinciden.'),
            'password_too_short': _('La contraseña es muy corta.'),
            'password_common': _('La contraseña es muy común.'),
            'password_entirely_numeric': _('La contraseña no puede ser totalmente numérica.'),
        }
    )

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')
        labels = {
            'username': _('Nombre de usuario'),
            'password1': _('Contraseña'),
            'password2': _('Confirmar contraseña'),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('El email ya está registrado.')
        return email


class CustomUserChangeForm(UserChangeForm):
    password = forms.CharField(widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField(label=_("Nombre"), max_length=150)
    last_name = forms.CharField(label=_("Apellido"), max_length=150)
    email = forms.EmailField(label=_("Email"), max_length=254)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ClienteForm(forms.ModelForm):
    direccion = forms.CharField(required=False, max_length=200)
    ciudad = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'autocomplete-ciudad'}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ciudades = list(Ciudad.objects.values_list('nombre', flat=True))
        self.fields['ciudad'].widget.attrs.update({
            'data-list': ','.join(ciudades)
        })

    class Meta:
        model = Cliente
        fields = '__all__'


class BuscadorIngenieroForm(forms.Form):
    termino_busqueda = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={'placeholder': 'Ingrese el nombre o apellido'}))


class BuscadorClienteForm(forms.Form):
    termino_busqueda = forms.CharField(label='Buscar Cliente', max_length=100, required=False)


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'


class BuscadorProveedorForm(forms.Form):
    termino_busqueda = forms.CharField(required=False, max_length=100, label='Buscar proveedor')


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['nombre', 'marca', 'id_proveedor', 'medida', 'minimo', 'unidades_stock', 'fotografia']

    labels = {
        'id_proveedor': 'Proveedor',
    }


class BuscadorMaterialForm(forms.Form):
    termino_busqueda = forms.CharField(label='Buscar material', max_length=100)


class ProyectoForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), label=_('cliente'))
    encargado = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='INGENIERO'), label='Encargado de presupuesto')

    class Meta:
        model = Proyecto
        fields = ['nombre']


class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['nombre', 'numero']

        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del contacto'}),
            'numero': forms.TextInput(attrs={'placeholder': 'Número de teléfono'}),
        }
