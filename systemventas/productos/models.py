from django.db import models
import os #importar el modulo os sirve para manejar rutas de archivos
import uuid #importar el modulo uuid que sirve para generar identificadores únicos
# Create your models here.
from django.core.exceptions import ValidationError #importar ValidationError para manejar errores de validacion
from PIL import Image #importar la clase Image del modulo PIL para manejar imagenes
from django.utils import timezone #importar timezone para manejar fechas y horas

def validate_image_size(image):#funcion para validar el tamaño de la imagen
    file_size = image.file.size
    megabytes_limit = 5.0
    if file_size > megabytes_limit * 1024 * 1024:
        raise ValidationError(f"La imagen no debe superar los {megabytes_limit}MB")

def get_image_path(instance, filename):#funcion para generar una ruta unica para cada imagen subida
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}" #para subir dos archivos aunque se llamen igual
    return os.path.join('productos/', filename)      

class Producto(models.Model):
    sku = models.CharField("SKU", max_length=20, unique=True ,blank = True)
    nombre = models.CharField("Nombre", max_length=50)
    descripcion = models.CharField("Descripción", max_length=255)
    precio = models.DecimalField("Precio", max_digits=10, decimal_places=2)
    stock = models.IntegerField("Stock", default=0)
    stock_minimo = models.IntegerField("Stock mínimo", default=5)#stock minimo para alerta es de 5 unidades
    imagen = models.ImageField(
        "Imagen",
        upload_to=get_image_path,
        validators=[validate_image_size],#ponemos la validacion del tamaño de la imagen que definimos arriba
        blank=True,#permitimos que la imagen sea opcional
        null=True, #permitimos que la imagen sea opcional
        help_text="formatos permitidos: jpg, png. Tamaño máximo: 5MB"
    )
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        """Unicode representation of Producto."""
        return f"{self.nombre} (SKU: {self.sku})"

    def save(self, *args, **kwargs):
        if not self.sku:
        # Genera un SKU único de 8 caracteres
            self.sku = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    # Redimensionar imagen si es muy grande
        try:
            if self.imagen:
                img = Image.open(self.imagen.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.imagen.path)
        except Exception as e:
             print(f'No se pudo procesar la imagen del producto {self.nombre}: {e}')
    
    @property
    def necesita_reposicion(self):
        """Retorna True si el stock es menor al stock minimo."""
        return self.stock < self.stock_minimo

class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')#relacionar el movimiento de stock con el producto correspondiente
    tipo = models.CharField("Tipo de movimiento", max_length=10, choices=TIPO_CHOICES)
    cantidad = models.IntegerField("Cantidad")
    motivo = models.CharField("Motivo", max_length=255, blank=True, null=True)
    usuario = models.CharField("Usuario", max_length=50)
    fecha = models.DateTimeField("Fecha y hora", default=timezone.now)
    class Meta:
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-fecha']

    def __str__(self):
        """Unicode representation of MovimientoStock."""
        return f"{self.tipo} - {self.producto.nombre} - {self.cantidad}"

        