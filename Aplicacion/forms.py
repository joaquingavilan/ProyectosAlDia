from django import forms
from .models import Cliente, Ingeniero, Proveedor, Material

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


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['nombre', 'marca', 'id_proveedor', 'medida', 'minimo', 'unidades_stock', 'fotografia']

    labels = {
        'id_proveedor': 'Proveedor',
    }

class BuscadorMaterialForm(forms.Form):
    termino_busqueda = forms.CharField(label='Buscar material', max_length=100)
