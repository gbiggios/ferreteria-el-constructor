import io
import shutil
import tempfile

from PIL import Image

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Categoria, Producto


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
