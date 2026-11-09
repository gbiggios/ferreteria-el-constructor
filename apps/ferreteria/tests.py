import io
import shutil
import tempfile

from PIL import Image

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Categoria, Producto, STOCK_CRITICO


MEDIA_PRUEBAS = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_PRUEBAS)
class FerreteriaTestCase(TestCase):
    """Pruebas del CRUD de insumos. Usan una base de datos y una carpeta de imágenes temporales."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_PRUEBAS, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user('vendedor', password='clave-segura-123')
        self.categoria = Categoria.objects.create(nombre='Materiales Básicos')
        self.producto = Producto.objects.create(
            codigo='CEM-25', nombre='Cemento Especial 25 kg', categoria=self.categoria,
            descripcion='Saco de cemento', precio=6490, stock=40,
        )

    def login(self):
        self.client.login(username='vendedor', password='clave-segura-123')

    def datos_producto(self, **cambios):
        datos = {
            'codigo': 'POL-ES-01', 'nombre': 'Pintura Látex', 'categoria': self.categoria.pk,
            'descripcion': 'Galón blanco', 'precio': 15990, 'stock': 12,
            'unidad_medida': 'Galón / Litro', 'ubicacion_bodega': 'Pasillo 3', 'disponible': 'on',
        }
        datos.update(cambios)
        return datos

    # RF1: autenticación y control de acceso
    def test_login_valido_redirige_al_catalogo(self):
        res = self.client.post(reverse('ferreteria:log-in'),
                               {'username': 'vendedor', 'password': 'clave-segura-123'})
        self.assertRedirects(res, reverse('ferreteria:home'))

    def test_login_invalido_muestra_mensaje(self):
        res = self.client.post(reverse('ferreteria:log-in'),
                               {'username': 'vendedor', 'password': 'incorrecta'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Credenciales inválidas')

    def test_rutas_protegidas_exigen_sesion(self):
        for url in [reverse('ferreteria:home'), reverse('ferreteria:producto-create'),
                    reverse('ferreteria:producto-edit', args=[self.producto.pk]),
                    reverse('ferreteria:category-list')]:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 302, url)
            self.assertIn('next=', res['Location'])

    def test_no_existe_ruta_de_acceso_sin_clave(self):
        res = self.client.get('/autologin/')
        self.assertEqual(res.status_code, 404)

    def test_login_vuelve_a_la_pagina_pedida(self):
        destino = reverse('ferreteria:category-list')
        res = self.client.get(destino)  # sin sesión: redirige al login con ?next=
        res = self.client.post(res['Location'], {'username': 'vendedor', 'password': 'clave-segura-123'})
        self.assertRedirects(res, destino)

    def test_login_ignora_next_hacia_otro_sitio(self):
        res = self.client.post(reverse('ferreteria:log-in') + '?next=https://sitio-malicioso.com/',
                               {'username': 'vendedor', 'password': 'clave-segura-123'})
        self.assertRedirects(res, reverse('ferreteria:home'))

    def test_usuario_con_sesion_que_entra_al_login_va_al_catalogo(self):
        self.login()
        self.assertRedirects(self.client.get(reverse('ferreteria:log-in')), reverse('ferreteria:home'))

    def test_logout_sin_sesion_no_deja_next_hacia_logout(self):
        res = self.client.get(reverse('ferreteria:log-out'))
        self.assertRedirects(res, reverse('ferreteria:log-in'), fetch_redirect_response=False)

    def test_logout_solo_por_post(self):
        self.login()
        self.client.get(reverse('ferreteria:log-out'))  # un GET (enlace, imagen) no cierra la sesión
        self.assertEqual(self.client.get(reverse('ferreteria:home')).status_code, 200)
        self.client.post(reverse('ferreteria:log-out'))
        self.assertEqual(self.client.get(reverse('ferreteria:home')).status_code, 302)

    def test_enlace_al_admin_solo_para_staff(self):
        self.login()
        self.assertNotContains(self.client.get(reverse('ferreteria:home')), 'Panel de administración')
        self.user.is_staff = True
        self.user.save()
        self.assertContains(self.client.get(reverse('ferreteria:home')), 'Panel de administración')

    # RF2: catálogo, búsqueda y ficha
    def test_catalogo_lista_productos_y_kpis(self):
        self.login()
        res = self.client.get(reverse('ferreteria:home'))
        self.assertContains(res, 'CEM-25')
        self.assertEqual(res.context['total_items'], 1)

    def test_busqueda_filtra_por_texto(self):
        self.login()
        res = self.client.get(reverse('ferreteria:home'), {'q': 'inexistente'})
        self.assertEqual(res.context['total_items'], 0)

    def test_ficha_tecnica(self):
        self.login()
        res = self.client.get(reverse('ferreteria:producto-detail', args=[self.producto.pk]))
        self.assertContains(res, 'Cemento Especial 25 kg')

    # RF7: alta, ajuste y baja de insumos
    def test_crear_producto(self):
        self.login()
        res = self.client.post(reverse('ferreteria:producto-create'), self.datos_producto())
        self.assertRedirects(res, reverse('ferreteria:home'))
        self.assertTrue(Producto.objects.filter(codigo='POL-ES-01').exists())

    def test_rechaza_sku_duplicado(self):
        self.login()
        res = self.client.post(reverse('ferreteria:producto-create'), self.datos_producto(codigo='CEM-25'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Producto.objects.filter(codigo='CEM-25').count(), 1)

    def test_rechaza_stock_negativo_y_precio_cero(self):
        self.login()
        res = self.client.post(reverse('ferreteria:producto-create'),
                               self.datos_producto(stock=-5, precio=0))
        self.assertEqual(res.status_code, 200)
        self.assertIn('stock', res.context['form'].errors)
        self.assertIn('precio', res.context['form'].errors)

    def test_ajustar_stock(self):
        self.login()
        datos = self.datos_producto(codigo='CEM-25', stock=15)
        self.client.post(reverse('ferreteria:producto-edit', args=[self.producto.pk]), datos)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 15)

    def test_eliminar_requiere_post(self):
        self.login()
        url = reverse('ferreteria:producto-delete', args=[self.producto.pk])
        self.client.get(url)
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())
        self.client.post(url)
        self.assertFalse(Producto.objects.filter(pk=self.producto.pk).exists())

    # Integridad referencial
    def test_no_se_borra_categoria_con_productos(self):
        with self.assertRaises(ProtectedError):
            self.categoria.delete()

    def test_crear_categoria(self):
        self.login()
        self.client.post(reverse('ferreteria:category-list'), {'nombre': 'Gasfitería', 'descripcion': ''})
        self.assertTrue(Categoria.objects.filter(nombre='Gasfitería').exists())

    # CRUD completo de categorías
    def test_rutas_de_categoria_exigen_sesion(self):
        for nombre in ('category-detail', 'category-edit', 'category-delete'):
            res = self.client.get(reverse(f'ferreteria:{nombre}', args=[self.categoria.pk]))
            self.assertEqual(res.status_code, 302, nombre)

    def test_detalle_categoria_lista_sus_productos(self):
        self.login()
        res = self.client.get(reverse('ferreteria:category-detail', args=[self.categoria.pk]))
        self.assertContains(res, 'Materiales Básicos')
        self.assertContains(res, 'CEM-25')
        self.assertEqual(self.client.get(reverse('ferreteria:category-detail', args=[999])).status_code, 404)

    def test_editar_categoria(self):
        self.login()
        res = self.client.post(reverse('ferreteria:category-edit', args=[self.categoria.pk]),
                               {'nombre': 'Obra Gruesa', 'descripcion': 'Cemento y áridos'})
        self.assertRedirects(res, reverse('ferreteria:category-detail', args=[self.categoria.pk]))
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.nombre, 'Obra Gruesa')

    def test_editar_categoria_con_nombre_repetido_se_rechaza(self):
        Categoria.objects.create(nombre='Gasfitería')
        self.login()
        res = self.client.post(reverse('ferreteria:category-edit', args=[self.categoria.pk]),
                               {'nombre': 'Gasfitería', 'descripcion': ''})
        self.assertEqual(res.status_code, 200)
        self.assertIn('nombre', res.context['form'].errors)

    def test_eliminar_categoria_vacia(self):
        vacia = Categoria.objects.create(nombre='Electricidad')
        self.login()
        url = reverse('ferreteria:category-delete', args=[vacia.pk])
        self.assertContains(self.client.get(url), '¿Eliminar esta categoría?')
        self.assertTrue(Categoria.objects.filter(pk=vacia.pk).exists())
        self.assertRedirects(self.client.post(url), reverse('ferreteria:category-list'))
        self.assertFalse(Categoria.objects.filter(pk=vacia.pk).exists())

    def test_eliminar_categoria_con_productos_se_bloquea(self):
        self.login()
        url = reverse('ferreteria:category-delete', args=[self.categoria.pk])
        self.assertContains(self.client.get(url), 'No se puede eliminar esta categoría')
        res = self.client.post(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'todavía tiene insumos asociados')
        self.assertTrue(Categoria.objects.filter(pk=self.categoria.pk).exists())
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    # Imagen del producto
    def imagen_png(self):
        buffer = io.BytesIO()
        Image.new('RGB', (10, 10), 'red').save(buffer, 'PNG')
        return SimpleUploadedFile('foto.png', buffer.getvalue(), content_type='image/png')

    def test_crear_con_imagen_la_guarda_y_la_muestra(self):
        self.login()
        res = self.client.post(reverse('ferreteria:producto-create'),
                               self.datos_producto(imagen=self.imagen_png()))
        self.assertRedirects(res, reverse('ferreteria:home'))
        producto = Producto.objects.get(codigo='POL-ES-01')
        self.assertTrue(producto.imagen.name.startswith('productos/'))
        self.assertContains(self.client.get(reverse('ferreteria:home')), producto.imagen.url)

    def test_archivo_que_no_es_imagen_se_rechaza(self):
        self.login()
        falso = SimpleUploadedFile('virus.png', b'no soy una imagen', content_type='image/png')
        res = self.client.post(reverse('ferreteria:producto-create'), self.datos_producto(imagen=falso))
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Producto.objects.filter(codigo='POL-ES-01').exists())

    # Mensajes de feedback
    def test_mensaje_tras_crear_producto(self):
        self.login()
        res = self.client.post(reverse('ferreteria:producto-create'), self.datos_producto(), follow=True)
        self.assertContains(res, 'Insumo &quot;Pintura Látex&quot; (POL-ES-01) registrado correctamente.')
        self.assertContains(res, 'mensaje-success')

    def test_mensaje_de_error_con_formulario_invalido(self):
        self.login()
        res = self.client.post(reverse('ferreteria:producto-create'), self.datos_producto(precio=0))
        self.assertContains(res, 'No se pudo registrar el insumo')
        self.assertContains(res, 'mensaje-error')

    def test_mensaje_tras_editar_y_eliminar_producto(self):
        self.login()
        res = self.client.post(reverse('ferreteria:producto-edit', args=[self.producto.pk]),
                               self.datos_producto(codigo='CEM-25', nombre='Cemento 25 kg'), follow=True)
        self.assertContains(res, 'actualizado correctamente')
        res = self.client.post(reverse('ferreteria:producto-delete', args=[self.producto.pk]), follow=True)
        self.assertContains(res, 'dado de baja')

    def test_mensajes_de_categoria(self):
        self.login()
        res = self.client.post(reverse('ferreteria:category-list'), {'nombre': 'Gasfitería'}, follow=True)
        self.assertContains(res, 'registrada correctamente')
        nueva = Categoria.objects.get(nombre='Gasfitería')
        res = self.client.post(reverse('ferreteria:category-edit', args=[nueva.pk]), {'nombre': 'Gasfitería y PVC'}, follow=True)
        self.assertContains(res, 'actualizada correctamente')
        res = self.client.post(reverse('ferreteria:category-delete', args=[nueva.pk]), follow=True)
        self.assertContains(res, 'eliminada')

    def test_mensaje_tras_logout(self):
        self.login()
        res = self.client.post(reverse('ferreteria:log-out'), follow=True)
        self.assertContains(res, 'Sesión cerrada correctamente.')

    # Regla de stock en un solo lugar (STOCK_CRITICO)
    def crear_con_stock(self, codigo, stock):
        return Producto.objects.create(codigo=codigo, nombre=codigo, categoria=self.categoria,
                                       descripcion='d', precio=1000, stock=stock)

    def test_estado_stock_en_los_bordes_del_umbral(self):
        casos = [(0, 'agotado'), (1, 'critico'), (STOCK_CRITICO, 'critico'), (STOCK_CRITICO + 1, 'disponible')]
        for stock, esperado in casos:
            self.assertEqual(Producto(stock=stock).estado_stock, esperado, f'stock={stock}')

    def test_queryset_kpis_e_insignias_usan_la_misma_regla(self):
        agotado = self.crear_con_stock('AGO-1', 0)
        critico = self.crear_con_stock('CRI-1', STOCK_CRITICO)
        disponible = self.crear_con_stock('DIS-1', STOCK_CRITICO + 1)
        self.assertEqual(list(Producto.objects.agotados()), [agotado])
        self.assertEqual(list(Producto.objects.criticos()), [critico])
        self.assertNotIn(disponible, Producto.objects.criticos())

        self.login()
        res = self.client.get(reverse('ferreteria:home'))
        self.assertEqual(res.context['items_agotados'], 1)
        self.assertEqual(res.context['items_criticos'], 1)
        self.assertContains(res, f'Con stock crítico ({STOCK_CRITICO} o menos)')
        self.assertContains(res, '<span class="stock stock-agotado">Agotado</span>', html=True)
        self.assertContains(res, f'<span class="stock stock-critico">{STOCK_CRITICO} en stock</span>', html=True)
        self.assertContains(res, f'<span class="stock stock-disponible">{STOCK_CRITICO + 1} en stock</span>', html=True)

        ficha = self.client.get(reverse('ferreteria:producto-detail', args=[critico.pk]))
        self.assertContains(ficha, '<span class="stock stock-critico">Stock crítico</span>', html=True)
