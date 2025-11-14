from django import forms
from django.core.exceptions import ValidationError
from .models import Producto , MovimientoStock
from crispy_forms.layout import Layout, Row , Column, Submit , Reset , ButtonHolder , Field , Div , HTML
from .crispy import BaseFormHelper

class ProductoForm(forms.ModelForm): # formulario para el modelo Producto
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'stock_minimo', 'imagen'] # campos del modelo a incluir en el formulario
        
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}), # widget para el campo descripcion
            'sku': forms.TextInput(attrs={'class': 'form-control'}), # hacemos el campo sku de solo lectura
        }
        labels = {
            'stock_minimo': 'Stock Mínimo', # etiqueta personalizada para el campo stock_minimo
        }
        help_texts = {
            'stock_minimo' : 'se mostrara una alerta cuando el stock sea menor a este valor'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = BaseFormHelper()

        self.helper.layout = Layout( # diseño del formulario con crispy forms
            Field('nombre'),
            Field('descripcion'),

            Field('precio', placeholder='0.00', css_class='input-precio'),
            Field('stock'),
            Field('stock_minimo'),
            Field('imagen'),
            ButtonHolder(
                Submit('submit', 'Guardar', css_class='btn btn-success'),
                Reset('reset', 'Limpiar', css_class='btn btn-outline-secondary'),
                HTML('<a href="{% url "producto:producto_list" %}" class="btn btn-secondary">Cancelar</a>')

            )
        )

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio and precio <= 0:
            raise ValidationError('El precio debe ser mayor a 0.')
        return precio

    def clean_stock(self): # definimos el metodo clean para el campo stock
        stock = self.cleaned_data.get('stock')
        if stock and stock < 0:
            raise ValidationError('El stock no puede ser negativo.')
        return stock

    def clean_stock_minimo(self): # definimos el metodo clean para el campo stock_minimo
        stock_minimo = self.cleaned_data.get('stock_minimo')
        if stock_minimo and stock_minimo < 0:
            raise ValidationError('El stock mínimo no puede ser negativo.')
        return stock_minimo
    
class MovimientoStockForm(forms.ModelForm):
    class Meta:
        model = MovimientoStock
        fields = ['tipo', 'cantidad', 'motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'tipo': 'Tipo de Movimiento',
            'cantidad': 'Cantidad',
            'motivo': 'Motivo (opcional)',
        }

    def __init__(self, *args, **kwargs):
        self.producto = kwargs.pop('producto', None)  # obtenemos el producto pasado
        super().__init__(*args, **kwargs)
        self.helper = BaseFormHelper()

        stock_info = ''
        if self.producto:
            stock_info = f"""
            <div class="alert alert-info">
                <strong>Producto:</strong> {self.producto.nombre} <br>
                <strong>Stock Actual:</strong> {self.producto.stock}
            </div>
            """

        self.helper.layout = Layout(
            HTML(stock_info),
            Field('tipo'),
            Field('cantidad'),
            Field('motivo'),
            ButtonHolder(
                Submit('submit', 'Registrar Movimiento', css_class='btn btn-success'),
                Reset('reset', 'Limpiar', css_class='btn btn-outline-secondary'),
                HTML('<a href="{{ request.META.HTTP_REFERER }}" class="btn btn-secondary">Cancelar</a>')
            )
        )

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a 0.')
        if self.producto and self.cleaned_data.get('tipo') == 'salida':
            if cantidad > self.producto.stock:
                raise ValidationError(f"No hay suficiente stock. Stock actual: {self.producto.stock}.")
        return cantidad

class AjusteStockForm(forms.Form): # formulario para ajustar el stock de un producto
    cantidad = forms.IntegerField(label='Nueva Cantidad de Stock', min_value=0)
    motivo = forms.CharField(label='Motivo (opcional)', widget=forms.Textarea(attrs={'rows': 3}), required=False)

    def __init__(self, *args, **kwargs):
        self.producto = kwargs.pop('producto', None) # obtenemos el producto pasado como argumento
        super().__init__(*args, **kwargs)
        self.helper = BaseFormHelper()

        stock_info = ''
        if self.producto:
            stock_info = f"""
            <div class="alert alert-info">
                <strong>Producto:</strong> {self.producto.nombre} <br>
                <strong>Stock Actual:</strong> {self.producto.stock}
            </div>
            """
        
        self.helper.layout = Layout( # diseño del formulario con crispy forms
            HTML(stock_info),
            Field('cantidad'),
            Field('motivo'),
            ButtonHolder(
                Submit('submit', 'Ajustar Stock', css_class='btn btn-success'),
                Reset('reset', 'Limpiar', css_class='btn btn-outline-secondary'),
                HTML('<a href="{{ request.META.HTTP_REFERER }}" class="btn btn-secondary">Cancelar</a>')
            )
        )