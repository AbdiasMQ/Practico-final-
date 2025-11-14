from django.urls import path
from .views import VentaListView, VentaDetailView, VentaCreateView, VentaDeleteView , VentaPDFView

app_name = 'ventas'

urlpatterns = [
    path('', VentaListView.as_view(), name='venta_list'),
    path('alta/', VentaCreateView.as_view(), name='venta_create'),
    path('<int:pk>/', VentaDetailView.as_view(), name='venta_detail'),
    path('<int:pk>/eliminar/', VentaDeleteView.as_view(), name='venta_delete'),
    path('venta/<int:pk>/pdf/', VentaPDFView.as_view(), name='venta_pdf'),

]
