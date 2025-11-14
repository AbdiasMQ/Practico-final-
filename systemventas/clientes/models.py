from django.db import models
import os #importar el modulo os sirve para manejar rutas de archivos
import uuid #importar el modulo uuid que sirve para generar identificadores únicos
# Create your models here.
from django.core.exceptions import ValidationError #importar ValidationError para manejar errores de validacion

class Cliente(models.Model):
    nombre = models.CharField('Nombre',max_length=100,blank=False,null=False,)
    apellido = models.CharField('Apellido',max_length=100,blank=False,null=False,)
    email = models.EmailField('Email',max_length=100,blank=False,null=False,)
    telefono = models.CharField('Telefono',max_length=20,blank=False,null=False,)
    direccion = models.CharField('Direccion',max_length=200,blank=False,null=False,)
    dni = models.CharField('DNI',max_length=20,blank=False,null=False,unique=True)
    
    class Meta:
        """Meta definition for Cliente."""

        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def clean(self):
        """Custom validation for Cliente."""
        if not self.email.endswith('@example.com'):
            raise ValidationError('El email debe ser de la domain @example.com')
    def clean(self):
        # Validación personalizada para asegurar que el número de documento sea único
        if Cliente.objects.filter(dni=self.dni).exclude(pk=self.pk).exists():
            raise ValidationError({
                'dni': _('Ya existe un cliente con este DNI.')
            })
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def clean(self):
        if Cliente.objects.filter(nombre=self.nombre, apellido=self.apellido).exists():
            raise ValidationError('Ya existe un cliente con este nombre y apellido.')
    
        
    def __str__(self):
        """Unicode representation of Cliente."""
        return f"{self.nombre} {self.apellido}"

