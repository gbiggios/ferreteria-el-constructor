# Ferretería "El Constructor" — CRUD de inventario (Django)

Adaptación del ejemplo `simple-crud-django` (catálogo de películas) a la gestión de insumos de una ferretería.
Grupo 6 — APTC106 Taller de Desarrollo Web y Móvil (UNAB).

## Requisitos

- Python 3.12 o superior
- Las dependencias de `requirements.txt` (Django 6.1)

## Despliegue local

```bash
python -m venv venv
venv\Scripts\activate            # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python seed_data.py              # crea el usuario admin y el catálogo de ejemplo
python manage.py runserver
```

Abrir http://127.0.0.1:8000/ e ingresar con `admin` / `admin123` (solo para el entorno local).

## Pruebas

```bash
python manage.py test apps.ferreteria.tests
```

Las pruebas usan una base de datos temporal, no modifican `db.sqlite3`.

## Variables de entorno

| Variable | Uso | Valor por defecto |
|---|---|---|
| `DJANGO_SECRET_KEY` | clave de firma de sesiones | clave de desarrollo |
| `DJANGO_DEBUG` | `0` desactiva el modo depuración | `1` |
