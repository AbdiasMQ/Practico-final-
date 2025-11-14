from django.shortcuts import render
from django.views.generic import ListView , CreateView, UpdateView, DeleteView # estas son las vistas genericas basadas en clases
from django.urls import reverse_lazy # reverse_lazy se usa para redirigir despues de una operacion
from django.contrib import messages # para mostrar mensajes al usuario
from django.shortcuts import get_object_or_404, redirect # para obtener objetos o redirigir
from django.db.models import Q, F # Q se usa para consultas complejas y F para referenciar campos del modelo
from django.views.generic import DetailView, FormView
from .models import Cliente
from .forms import ClienteForm
from django.contrib.auth.mixins import LoginRequiredMixin , PermissionRequiredMixin # para restringir el acceso a las vistas
from django.core.paginator import Paginator

class ClienteListView(ListView):
    model = Cliente
    template_name = "clientes/clientes_list.html"
    context_object_name = "clientes"
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q")
        
        if query:
            # Buscar por nombre o DNI
            clientes = Cliente.objects.filter(
                Q(nombre__icontains=query) |
                Q(dni__icontains=query)
            )
            
            # Si encuentra algún resultado, ir al detalle del PRIMERO
            if clientes.exists():
                return redirect('clientes:cliente_detail', pk=clientes.first().pk)
        
        # Si no hay búsqueda o no encuentra, mostrar lista normal
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        
        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) |
                Q(dni__icontains=query)
            )
        return queryset.order_by('nombre')

class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_form.html"
    success_url = reverse_lazy("clientes:cliente_list")
    permission_required = 'clientes.add_cliente'

    def has_permission(self):
        return (self.request.user.groups.filter(name='ventas').exists() 
            or self.request.user.is_superuser)
    def form_valid(self, form):
        messages.success(self.request, "Cliente creado exitosamente.")
        return super().form_valid(form)

class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_form.html"
    success_url = reverse_lazy("clientes:cliente_list")
    permission_required = 'clientes.change_cliente'
    def has_permission(self):
        return (self.request.user.groups.filter(name='ventas').exists() 
            or self.request.user.is_superuser)

    def form_valid(self, form):
        messages.success(self.request, "Cliente actualizado exitosamente.")
        return super().form_valid(form)
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if dni and Cliente.objects.filter(dni=dni).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un cliente con este DNI.")
        return dni
        
class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Cliente
    template_name = "clientes/cliente_confirm_delete.html"
    success_url = reverse_lazy("clientes:cliente_list")
    permission_required = 'clientes.delete_cliente'

    def has_permission(self):
        return (self.request.user.groups.filter(name='ventas').exists() 
            or self.request.user.is_superuser)

    def form_valid(self, form):
        cliente = self.get_object()
        nombre = cliente.nombre
        messages.success(self.request, f'El cliente "{nombre}" fue eliminado correctamente.')
        return super().form_valid(form)

class ClienteDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Cliente
    template_name = "clientes/cliente_detail.html"
    context_object_name = "cliente"
    permission_required = 'clientes.view_cliente'

    def has_permission(self):
        return (self.request.user.groups.filter(name='ventas').exists() 
            or self.request.user.is_superuser)