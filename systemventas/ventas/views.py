from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from .models import Venta, ItemVenta
from .forms import VentaForm, ItemVentaFormSet
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin # para restringir el acceso a las vistas
from django.core.paginator import Paginator
from django.db.models import Q
# Para vistas basadas en clases
from django.views import View
# Para buscar objetos o devolver 404
from django.shortcuts import get_object_or_404
# Para devolver la respuesta PDF
from django.http import HttpResponse
# Para renderizar plantilla a HTML
from django.template.loader import render_to_string
# Para generar PDF desde HTML
from xhtml2pdf import pisa


class VentaListView(ListView):
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q")
        if query:
            venta = Venta.objects.filter(codigo__icontains=query)
            if venta.exists():
                # Redirige al detalle de la primera venta encontrada
                return redirect('ventas:venta_detail', pk=venta.first().pk)
        
        # Si no hay búsqueda o no encuentra, mostrar lista normal
        return super().get(request, *args, **kwargs)

class VentaDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'
    permission_required = 'ventas.view_venta'

    def has_permission(self):
        return (self.request.user.groups.filter(name='ventas').exists()
            or self.request.user.is_superuser)
           
    def get_queryset(self):
        return Venta.objects.prefetch_related('items__producto')

class VentaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta_list')
    permission_required = 'ventas.add_venta'

    def has_permission(self):
        return (self.request.user.groups.filter(name='ventas').exists() 
            or self.request.user.is_superuser)

    def get(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = ItemVentaFormSet()
        return render(request, self.template_name, {'form': form, 'formset': formset})

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = ItemVentaFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # Guardar la venta
            venta = form.save(commit=False)
            venta.total = 0
            venta.save()
            
            total = 0
            # Guardar los items de venta
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    item = item_form.save(commit=False)
                    item.venta = venta
                    
                    # Obtener el precio del producto si no se proporcionó
                    if not item.precio_unitario:
                        item.precio_unitario = item.producto.precio
                    
                    # Calcular subtotal
                    item.subtotal = item.cantidad * item.precio_unitario
                    item.save()
                    total += item.subtotal
                    
                    # Descontar stock del producto
                    producto = item.producto
                    producto.stock -= item.cantidad
                    producto.save()
            
            # Actualizar total de la venta
            venta.total = total
            venta.save()
            
            return redirect(self.success_url)
        
        # Si el formulario no es válido, mostrar errores
        return render(request, self.template_name, {
            'form': form, 
            'formset': formset
        })
           
class VentaDeleteView(LoginRequiredMixin, PermissionRequiredMixin , DeleteView):
    model = Venta
    template_name = 'ventas/venta_confirm_delete.html'
    success_url = reverse_lazy('ventas:venta_list')
    permission_required = 'ventas.delete_venta'

    def has_permission(self):
        return (self.request.user.groups.filter(name='ventas').exists() 
            or self.request.user.is_superuser)

    def delete(self, request, *args, **kwargs):
        venta = self.get_object()
        for item in venta.items.all():
            producto = item.producto
            producto.stock += item.cantidad
            producto.save()
        return super().delete(request, *args, **kwargs)

class VentaPDFView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'ventas.view_venta'

    def get(self, request, pk, *args, **kwargs):
        # Trae la venta con todos los items y sus productos
        venta = get_object_or_404(Venta.objects.prefetch_related('items__producto'), pk=pk)

        # Renderizar plantilla PDF
        html = render_to_string('ventas/ventas_pdf.html', {'venta': venta})

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=Venta_{venta.codigo}.pdf'

        # Generar PDF
        pisa_status = pisa.CreatePDF(html, dest=response, encoding='UTF-8')
        if pisa_status.err:
            return HttpResponse("Ocurrió un error generando el PDF", status=500)

        return response