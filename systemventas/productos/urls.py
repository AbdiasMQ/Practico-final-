from django.urls import path, include
from . import views
from django.urls import path
app_name = 'producto'
urlpatterns = [
    # Listado de productos
    path('', views.ProductoListView.as_view(), name='producto_list'),
    # Crear producto (la vista que mencionás)
    path('nuevo/', views.ProductoCreateView.as_view(), name='producto_create'),
    # Detalle de un producto
    path('<int:pk>/', views.ProductoDetailView.as_view(), name='producto_detail'),
    # Editar producto
    path('<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto_update'),
    # Eliminar producto
    path('<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto_delete'),
    # Crear movimiento de stock para un producto
    path('<int:pk>/movimiento/', views.MovimientoStockCreateView.as_view(), name='movimiento_create'),
    # Ajustar stock de un producto
    path('<int:pk>/ajuste/', views.AjusteStockView.as_view(), name='ajuste_stock'),
    # Listar productos con stock bajo
    path('stock-bajo/', views.StockBajoListView.as_view(), name='stock_bajo_list'),
]