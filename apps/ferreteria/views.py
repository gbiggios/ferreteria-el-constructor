from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Count, ProtectedError
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
                messages.success(request, f'Bienvenido, {user.username}.')
                return redirect('ferreteria:home')
            else:
                context['message'] = 'El usuario ha sido desactivado en el sistema.'
        else:
            context['message'] = 'Credenciales inválidas. Verifique usuario o contraseña.'
    return render(request, 'ferreteria/login.html', context)


@login_required
def log_out(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
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
    if request.POST:
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Insumo "{producto.nombre}" ({producto.codigo}) registrado correctamente.')
            return redirect('ferreteria:home')
        messages.error(request, 'No se pudo registrar el insumo. Revisa los campos marcados en rojo.')
    return render(request, 'ferreteria/form.html', {
        'form': form,
        'titulo': 'Registrar insumo',
        'subtitulo': 'Ingresa el SKU, la categoría, el precio y el stock inicial del producto.'
    })


@login_required
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)
    if request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, f'Insumo "{producto.nombre}" actualizado correctamente.')
            return redirect('ferreteria:home')
        messages.error(request, 'No se pudieron guardar los cambios. Revisa los campos marcados en rojo.')
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
        messages.success(request, f'Insumo "{producto.nombre}" ({producto.codigo}) dado de baja.')
        return redirect('ferreteria:home')
    return render(request, 'ferreteria/confirm_delete.html', {'producto': producto})


@login_required
def categoria_list(request):
    categorias = Categoria.objects.annotate(total_prod=Count('productos')).order_by('nombre')
    form = CategoriaForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" registrada correctamente.')
            return redirect('ferreteria:category-list')
        messages.error(request, 'No se pudo registrar la categoría. Revisa el formulario.')
    return render(request, 'ferreteria/category/category_list.html', {
        'categorias': categorias,
        'form': form
    })


@login_required
def categoria_detail(request, pk):
    categoria = get_object_or_404(Categoria.objects.annotate(total_prod=Count('productos')), pk=pk)
    return render(request, 'ferreteria/category/category_detail.html', {
        'categoria': categoria,
        'productos': categoria.productos.all(),
    })


@login_required
def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada correctamente.')
            return redirect(categoria.get_detail_url())
        messages.error(request, 'No se pudieron guardar los cambios. Revisa el formulario.')
    return render(request, 'ferreteria/category/category_form.html', {
        'form': form,
        'categoria': categoria,
    })


@login_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria.objects.annotate(total_prod=Count('productos')), pk=pk)
    if request.method == 'POST':
        try:
            categoria.delete()
            messages.success(request, f'Categoría "{categoria.nombre}" eliminada.')
            return redirect('ferreteria:category-list')
        except ProtectedError:
            # on_delete=PROTECT: una categoría con insumos no se puede borrar
            messages.error(request, 'No se puede eliminar: la categoría todavía tiene insumos asociados.')
    return render(request, 'ferreteria/category/category_confirm_delete.html', {'categoria': categoria})
