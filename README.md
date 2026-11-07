# Ferretería "El Constructor" — Inventario

Sistema web para gestionar los productos y categorías de una ferretería: stock, precios, búsqueda e indicadores de reposición.
Basado en el ejemplo `simple-crud-django`. Grupo 6 — APTC106 Taller de Desarrollo Web y Móvil (UNAB).

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.12+ | Lenguaje |
| Django 6.1 | Framework web (MVT, ORM, autenticación, admin) |
| SQLite | Base de datos local |
| Pillow 13 | Validación y manejo de imágenes |
| django-widget-tweaks 1.5 | Estilos en los campos de formulario |
| HTML, CSS y JavaScript | Plantillas de Django, hoja de estilos propia y avisos flotantes |

## Estructura del proyecto

```
crud/                    configuración (settings, urls)
apps/ferreteria/
  models.py              modelos Categoria y Producto
  views.py               vistas del CRUD y del login
  forms.py               formularios
  urls.py                rutas
  admin.py               panel de administración
  templates/ferreteria/  plantillas HTML
  static/ferreteria/     CSS y JavaScript
  tests.py               pruebas automatizadas
media/productos/         fotos de ejemplo
seed_data.py             carga de datos de ejemplo
```

## Instalación

```powershell
python -m venv venv
venv\Scripts\Activate.ps1          # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python seed_data.py                # usuario admin y datos de ejemplo
python manage.py runserver
```

Abrir http://127.0.0.1:8000 con usuario `admin` y clave `admin123`.

## Pruebas

```powershell
python manage.py test apps.ferreteria.tests
```

## Funcionalidades

- CRUD de productos (con foto) y de categorías.
- Búsqueda, filtro por categoría e indicadores de stock crítico y agotado.
- Inicio de sesión obligatorio y panel de administración.

## Cambios

Ver [CHANGELOG.md](CHANGELOG.md).
