from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Sum, Count
from .models import Producto, Categoria
from .forms import ProductoForm, LoginForm, CategoriaForm


def log_in(request):
    form = LoginForm(request.POST or None)
    context = {'message': None, 'form': form}
    if request.POST and form.is_valid():
        user = authenticate(**form.cleaned_data)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('ferreteria:home')
            else:
                context['message'] = 'El usuario ha sido desactivado en el sistema.'
        else:
            context['message'] = 'Credenciales inválidas. Verifique usuario o contraseña.'
    return render(request, 'ferreteria/login.html', context)


@login_required
def log_out(request):
    logout(request)
    return redirect('ferreteria:log-in')


@login_required
def producto_list(request):
    query = request.GET.get('q', '').strip()
    cat_id = request.GET.get('categoria', '').strip()

    productos = Producto.objects.select_related('categoria').all()

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(codigo__icontains=query) |
            Q(descripcion__icontains=query)
        )

    if cat_id and cat_id.isdigit():
        productos = productos.filter(categoria_id=int(cat_id))

    categorias = Categoria.objects.annotate(total_prod=Count('productos'))

    # Métricas clave del inventario para la toma de decisiones
    total_items = productos.count()
    items_agotados = productos.filter(stock__lte=0).count()
    items_criticos = productos.filter(stock__gt=0, stock__lte=10).count()

    context = {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categoria_seleccionada': int(cat_id) if cat_id.isdigit() else None,
        'total_items': total_items,
        'items_agotados': items_agotados,
        'items_criticos': items_criticos,
    }
    return render(request, 'ferreteria/index.html', context)


@login_required
def producto_detail(request, pk):
    producto = get_object_or_404(Producto.objects.select_related('categoria'), pk=pk)
    return render(request, 'ferreteria/detail.html', {'producto': producto})


@login_required
def producto_create(request):
    form = ProductoForm(request.POST or None, request.FILES or None)
    if request.POST and form.is_valid():
        nuevo_producto = form.save()
        return redirect('ferreteria:home')
    return render(request, 'ferreteria/form.html', {
        'form': form,
        'titulo': 'Registrar insumo',
        'subtitulo': 'Ingresa el SKU, la familia, el precio y el stock inicial del producto.'
    })


@login_required
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)
    if request.POST and form.is_valid():
        form.save()
        return redirect('ferreteria:home')
    return render(request, 'ferreteria/form.html', {
        'form': form,
        'producto': producto,
        'titulo': f'Editar {producto.nombre}',
        'subtitulo': 'Ajusta el stock después de una recepción o un conteo, o corrige el precio y la ubicación.'
    })


@login_required
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('ferreteria:home')
    return render(request, 'ferreteria/confirm_delete.html', {'producto': producto})


@login_required
def categoria_list(request):
    categorias = Categoria.objects.annotate(total_prod=Count('productos')).order_by('nombre')
    form = CategoriaForm(request.POST or None)
    if request.POST and form.is_valid():
        form.save()
        return redirect('ferreteria:category-list')
    return render(request, 'ferreteria/category/category_list.html', {
        'categorias': categorias,
        'form': form
    })
