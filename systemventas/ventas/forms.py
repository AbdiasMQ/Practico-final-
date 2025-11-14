from django import forms
from django.forms import inlineformset_factory
from .models import Venta, ItemVenta
from .crispy import BaseFormHelper
from crispy_forms.layout import Layout, Row , Column, Submit , Reset , ButtonHolder , Field , Div , HTML


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'codigo']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: V001'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.layout = Layout(
            'cliente',
            'codigo',
            ButtonHolder(
                Submit('submit', 'Guardar Venta', css_class='btn btn-success'),
                HTML('<a href="{% url "venta:venta_list" %}" class="btn btn-secondary">Cancelar</a>')
            )
        )
class ItemVentaForm(forms.ModelForm):
    class Meta:
        model = ItemVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control select-producto'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control cantidad',
                'min': '1',
                'value': '1'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control precio-unitario',  # ← QUITAR readonly
                'step': '0.01'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es una instancia existente, mostrar el precio
        if self.instance and self.instance.pk:
            self.fields['precio_unitario'].initial = self.instance.precio_unitario

# FormSet para items de venta
ItemVentaFormSet = inlineformset_factory(
    Venta,
    ItemVenta,
    form=ItemVentaForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
    fields=['producto', 'cantidad', 'precio_unitario'],
    max_num=20
)