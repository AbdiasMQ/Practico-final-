from django.shortcuts import render
from django.views.generic import ListView , CreateView, UpdateView, DeleteView # estas son las vistas genericas basadas en clases
from django.urls import reverse_lazy # reverse_lazy se usa para redirigir despues de una operacion
from django.contrib import messages # para mostrar mensajes al usuario
from django.shortcuts import get_object_or_404, redirect # para obtener objetos o redirigir
from django.db.models import Q , F # Q se usa para consultas complejas y F para referenciar campos del modelo
from django.utils import timezone # para manejar fechas y horas
from .models import Producto , MovimientoStock # importamos los modelos Producto y MovimientoStock
from .forms import ProductoForm  , MovimientoStockForm , AjusteStockForm# importamos el formulario personalizado para Producto
from django.views.generic import DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin , PermissionRequiredMixin # para restringir el acceso a las vistas
from django.core.paginator import Paginator

class ProductoListView(ListView):
    model = Producto
    template_name = "producto/producto_list.html"
    context_object_name = "producto"
    paginate_by= 10
    
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q")
    
        if query:
            productos = Producto.objects.filter(Q(nombre__icontains=query))
            if productos.count() == 1:
                return redirect('producto:producto_detail', pk=productos.first().pk)
    
        return super().get(request, *args, **kwargs) 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) #
        context['stock_bajo'] = self.request.GET.get('stock_bajo') #mantenemos el filtro en el contexto
        return context


class ProductoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Producto
    template_name = "producto/producto_detail.html"
    permission_required = 'productos.view_producto' # permiso necesario para ver los detalles del producto
    context_object_name = "producto"

    def has_permission(self):
        # Solo usuarios en el grupo 'stock' o superusuario pueden ver
        return (self.request.user.groups.filter(name='stock').exists() 
            or self.request.user.is_superuser)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movimientos'] = self.object.movimientos.all()[:10]  # Obtenemos los movimientos de stock del producto
        context['form_ajuste'] = AjusteStockForm()  # Formulario para ajustes de stock
        return context

class ProductoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Producto
    template_name = "producto/producto_form.html"
    form_class = ProductoForm # usamos el formulario personalizado
    success_url = reverse_lazy("producto:producto_list") # redirigimos a la lista de productos al crear uno nuevo
    permission_required = 'productos.add_producto' # permiso necesario para crear un producto

    def has_permission(self):
        # Solo usuarios en el grupo 'stock' o superusuario pueden crear
        return (self.request.user.groups.filter(name='stock').exists() 
                or self.request.user.is_superuser)
    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data['stock'] > 0:
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
    
          
class ProductoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Producto
    template_name = "producto/producto_form.html"
    form_class = ProductoForm # usamos el formulario personalizado
    success_url = reverse_lazy("producto:producto_list") # redirigimos a la lista de productos al actualizar uno
    permission_required = 'productos.change_producto' # permiso necesario para actualizar un producto

    def has_permission(self):
        # Solo usuarios en el grupo 'stock' o superusuario pueden actualizar
        return (self.request.user.groups.filter(name='stock').exists() 
                or self.request.user.is_superuser)
    def form_valid(self, form): # definimos el metodo form_valid para registrar el movimiento de stock si se actualiza el stock
        response = super().form_valid(form)
        messages.success(self.request, "Producto actualizado exitosamente.")
        return response

class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):# vista para eliminar un producto
    model = Producto
    template_name = "producto/producto_confirm_delete.html"
    success_url = reverse_lazy("producto:producto_list")
    permission_required = 'productos.delete_producto' # permiso necesario para eliminar un producto

    def has_permission(self):
        # Solo usuarios en el grupo 'stock' o superusuario pueden eliminar
        return (self.request.user.groups.filter(name='stock').exists() 
                or self.request.user.is_superuser)
    
    def form_valid(self, form):
        producto = self.get_object()   # obtener el objeto antes de eliminarlo
        nombre = producto.nombre       # acceder al nombre
        messages.success(self.request, f'El producto "{nombre}" fue eliminado correctamente.')
        return super().form_valid(form)
        
class MovimientoStockCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = MovimientoStock
    template_name = "producto/movimiento_form.html"
    form_class = MovimientoStockForm # usamos un formulario personalizado para movimientos de stock
    permission_required = 'productos.add_movimientostock' # permiso necesario para crear un movimiento de stock

    def has_permission(self):
        # Solo usuarios en el grupo 'stock' o superusuario pueden crear movimientos de stock
        return (self.request.user.groups.filter(name='stock').exists() 
                or self.request.user.is_superuser)
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

class AjusteStockView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = AjusteStockForm
    template_name = "producto/ajuste_stock_form.html"
    permission_required = 'productos.change_producto' 
    
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


class StockBajoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Producto
    template_name = "producto/stock_bajo_list.html"
    context_object_name = "producto"
    permission_required = 'productos.view_producto' # permiso necesario para ver los productos con stock bajo
    def has_permission(self):
        # Solo usuarios en el grupo 'stock' o superusuario pueden ver
        return (self.request.user.groups.filter(name='stock').exists() 
            or self.request.user.is_superuser)

    def get_queryset(self):
        return Producto.objects.filter(stock__lt=F('stock_minimo')).order_by('stock')
