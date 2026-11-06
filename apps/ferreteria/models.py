from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse_lazy


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    updated = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    class Meta:
        abstract = True


class Categoria(BaseModel):
    nombre = models.CharField(max_length=120, unique=True, verbose_name='Nombre de la Categoría')
    descripcion = models.CharField(max_length=255, blank=True, verbose_name='Descripción')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(BaseModel):
    UNIDADES_CHOICES = [
        ('Unidad', 'Unidad'),
        ('Saco', 'Saco (25kg/40kg)'),
        ('Bolsa', 'Bolsa / Paquete'),
        ('Galón / Litro', 'Galón / Litro'),
        ('Metro lineal', 'Metro lineal'),
        ('Tira / Barra', 'Tira / Barra (6m)'),
        ('Caja / Set', 'Caja / Set'),
    ]

    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código / SKU')
    nombre = models.CharField(max_length=150, verbose_name='Nombre del Insumo')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos', verbose_name='Categoría')
    descripcion = models.TextField(verbose_name='Descripción / Especificaciones Técnicas')
    precio = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name='Precio de Venta ($ CLP)')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock Disponible (Bodega / Mesón)')
    unidad_medida = models.CharField(max_length=50, choices=UNIDADES_CHOICES, default='Unidad', verbose_name='Unidad de Medida')
    ubicacion_bodega = models.CharField(max_length=100, default='Bodega Central - Estante 1', verbose_name='Ubicación en Bodega')
    disponible = models.BooleanField(default=True, verbose_name='Disponible para Venta')
    imagen = models.ImageField(upload_to='productos/', blank=True, verbose_name='Imagen del producto')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-updated']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def get_edit_url(self):
        return reverse_lazy('ferreteria:producto-edit', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse_lazy('ferreteria:producto-delete', kwargs={'pk': self.pk})

    def get_detail_url(self):
        return reverse_lazy('ferreteria:producto-detail', kwargs={'pk': self.pk})

    @property
    def estado_stock(self):
        if self.stock <= 0:
            return 'Agotado'
        elif self.stock <= 10:
            return 'Crítico'
        return 'Disponible'
