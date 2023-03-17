from django import forms
from .models import Cliente, Ingeniero, Proveedor

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'


class IngenieroForm(forms.ModelForm):
    class Meta:
        model = Ingeniero
        fields = ['nombre', 'apellido', 'fecha_nacimiento', 'telefono', 'email', 'estado']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }


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


