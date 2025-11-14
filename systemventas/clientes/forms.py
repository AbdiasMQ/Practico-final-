from django import forms
from .models import Cliente
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit
from crispy_forms.layout import Layout, Row , Column, Submit , Reset , ButtonHolder , Field , Div , HTML
from .crispy import BaseFormHelper

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'dni', 'email', 'telefono', 'direccion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.layout = Layout(
            Field('nombre'),
            Field('apellido'),
            Field('dni'),
            Field('email'),
            Field('telefono'),
            Field('direccion'),
            ButtonHolder(
                Submit('submit', 'Guardar', css_class='btn btn-success'),
                HTML('<a href="{% url \'clientes:cliente_list\' %}" class="btn btn-secondary">Cancelar</a>')
                )
        )
        
    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if Cliente.objects.filter(dni=dni).exclude(pk=self.instance.pk).exists():
             raise forms.ValidationError("Ya existe un cliente con este DNI.")
        return dni