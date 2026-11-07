# Changelog

## [1.1.0] — 2026-11-07

- CRUD completo de categorías; no se puede eliminar una categoría con productos.
- Mensajes flotantes de confirmación y error.
- Regla de stock crítico centralizada en el modelo.
- Login con retorno seguro a la página pedida, cierre de sesión por POST y panel de administración solo para staff.
- "Familia" renombrado a "Categoría".
- Limpieza de código y configuración; `check` sin advertencias.
- Pruebas automatizadas: de 16 a 35.

## [1.0.0] — 2026-11-05

- Adaptación del ejemplo `simple-crud-django` a la ferretería: productos y categorías.
- Corrección de defectos del ejemplo: borrado por GET, `objects.get()`, imagen al editar, borrado en cascada, `requierements.txt`, clave secreta en el código y zona horaria.
- Búsqueda, filtro por categoría e indicadores de stock.
- Validaciones de precio, stock y SKU único.
- 16 pruebas automatizadas.

## Pendiente

- SKU y nombre de categoría únicos sin distinguir mayúsculas.
- Borrar del disco las fotos reemplazadas.
- Pasar los estilos en línea a la hoja de estilos.
