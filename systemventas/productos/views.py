from django.shortcuts import render
from django.views.generic import ListView , CreateView, UpdateView, DeleteView # estas son las vistas genericas basadas en clases
from django.urls import reverse_lazy # reverse_lazy se usa para redirigir despues de una operacion
from django.contrib import messages # para mostrar mensajes al usuario
from django.shortcuts import get_object_or_404, redirect # para obtener objetos o redirigir
from django.db.models import Q , F # Q se usa para consultas complejas y F para referenciar campos del modelo
from django.utils import timezone # para manejar fechas y horas
from .models import Producto , MovimientoStock # importamos los modelos Producto y MovimientoStock
from .forms import ProductoForm # importamos el formulario personalizado para Producto


class ProductoListView(ListView):
    model = Producto
    template_name = "producto/producto_list.html"
    context_object_name = "producto"

    def get_queryset(self):
        queryset = super().get_queryset()
        stock_bajo = self.request.GET.get('stock_bajo')
        if stock_bajo:
            queryset = queryset.filter(stock__lt=F('stock_minimo'))#filtramos los productos con stock menor al stock minimo
        return queryset.order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) #
        context['stock_bajo'] = self.request.GET.get('stock_bajo') #mantenemos el filtro en el contexto
        return context


class ProductosDetailView(DetailView):
    model = Productos
    template_name = "producto/producto_detail.html"
    context_object_name = "producto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movimientos'] = self.object.movimientos.all()[:10]  # Obtenemos los movimientos de stock del producto
        context['form_ajuste'] = AjusteStockForm()  # Formulario para ajustes de stock
        return context


class ProductoCreateView(CreateView):
    model = Producto
    template_name = "producto/producto_form.html"
    form_class = ProductoForm # usamos el formulario personalizado
    success_url = reverse_lazy("producto:producto_list") # redirigimos a la lista de productos al crear uno nuevo

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data > 0:
            MovimientoStock.objects.create(
                producto=self.object,
                tipo='entrada', # los tipos de moviemitos los definimos en la models
                cantidad=form.cleaned_data['stock'],
                motivo='Stock inicial',
                fecha=timezone.now(),
                usuario=self.request.user.username if self.request.user.is_authenticated else 'Sistema' # obtenemos el usuario autenticado o 'Sistema' si no hay usuario

            )
        messages.success(self.request, "Producto creado exitosamente.")
        return response

class ProductoUpdateView(UpdateView):
    model = Producto
    template_name = "producto/producto_form.html"
    form_class = ProductoForm # usamos el formulario personalizado
    success_url = reverse_lazy("producto:producto_list") # redirigimos a la lista de productos al actualizar uno

    def form_valid(self, form): # definimos el metodo form_valid para registrar el movimiento de stock si se actualiza el stock
        response = super().form_valid(form)
        messages.success(self.request, "Producto actualizado exitosamente.")
        return response


class ProductoDeleteView(DeleteView):# vista para eliminar un producto
    model = Producto
    template_name = "producto/producto_confirm_delete.html"
    success_url = reverse_lazy("producto:producto_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Producto eliminado exitosamente.")# mostramos un mensaje de exito
        return super().delete(request, *args, **kwargs)


class MovimientoStockCreateView(CreateView):
    model = MovimientoStock
    template_name = "producto/movimiento_form.html"
    form_class = MovimientoStockForm # usamos un formulario personalizado para movimientos de stock
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['producto'] = get_object_or_404(Producto, pk=self.kwargs['pk'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producto'] = get_object_or_404(Producto, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        movimiento = form.save(commit=False)
        movimiento.producto = get_object_or_404(Producto, pk=self.kwargs['pk'])
        movimiento.usuario = self.request.user.username if self.request.user.is_authenticated else 'Sistema'
        if movimiento.tipo == 'entrada' :
            movimiento.producto.stock += movimiento.cantidad # actualizamos el stock del producto
        elif movimiento.tipo == 'salida':
            if movimiento.producto.stock >= movimiento.cantidad:
                movimiento.producto.stock -= movimiento.cantidad # actualizamos el stock del producto
            else:
                form.add_error('cantidad', 'No hay suficiente stock para realizar esta salida.')
                return self.form_invalid(form)
        
        movimiento.producto.save()
        movimiento.save()
        messages.success(self.request, "Movimiento de stock registrado exitosamente.")
        return redirect('producto:producto_detail', pk=movimiento.producto.pk)

class AjusteStockView(FormView):
    form_class = AjusteStockForm
    template_name = "producto/ajuste_stock_form.html"
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['producto'] = get_object_or_404(Producto, pk=self.kwargs['pk'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producto'] = get_object_or_404(Producto, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        producto = get_object_or_404(Producto, pk=self.kwargs['pk'])
        nueva_cantidad = form.cleaned_data['cantidad']
        motivo = form.cleaned_data['motivo'] or 'Ajuste de stock'
        diferencia = nueva_cantidad - producto.stock

        if diferencia != 0:
            tipo = 'entrada' if diferencia > 0 else 'salida'
            MovimientoStock.objects.create(  #la parte de orm de django nos permite crear un nuevo registro en la tabla de movimientos de stock
                producto=producto,
                tipo=tipo,
                cantidad=abs(diferencia),
                motivo=motivo,
                fecha=timezone.now(),
                usuario=self.request.user.username if self.request.user.is_authenticated else 'Sistema'
            )

            producto.stock = nueva_cantidad
            producto.save()
            messages.success(self.request,f"Ajuste de stock realizado exitosamente.")

        else:
            messages.info(self.request,f"El stock no ha cambiado.")
        
        return redirect('producto:producto_detail', pk=producto.pk)


class StockBajoListView(ListView):
    model = Producto
    template_name = "producto/stock_bajo_list.html"
    context_object_name = "producto"

    def get_queryset(self):
        return Producto.objects.filter(stock__lt=F('stock_minimo')).order_by('stock')



        