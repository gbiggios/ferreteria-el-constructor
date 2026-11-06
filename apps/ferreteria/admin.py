from django.contrib import admin
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'created')
    search_fields = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio', 'stock', 'unidad_medida', 'disponible', 'updated')
    list_filter = ('categoria', 'disponible', 'unidad_medida')
    search_fields = ('codigo', 'nombre', 'descripcion')
    list_editable = ('precio', 'stock', 'disponible')
