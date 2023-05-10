from django import forms
from .models import Cliente, Proveedor, Material, Proyecto, User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


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


class CustomUserChangeForm(UserChangeForm):
    password = forms.CharField(widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField(label=_("Nombre"), max_length=150)
    last_name = forms.CharField(label=_("Apellido"), max_length=150)
    email = forms.EmailField(label=_("Email"), max_length=254)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ClienteForm(forms.ModelForm):
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
        fields = ['nombre', 'ruc', 'nombre_contacto', 'numero_contacto', 'email']


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
    encargado = forms.ModelChoiceField(queryset=User.objects.filter(perfil__rol__nombre='INGENIERO'), label='Encargado de presupuesto')

    class Meta:
        model = Proyecto
        fields = ['nombre']


