from django import forms
from .models import Cliente, Ingeniero

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
