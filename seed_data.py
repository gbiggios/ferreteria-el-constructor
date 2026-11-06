import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crud.settings")
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from apps.ferreteria.models import Categoria, Producto

# 1. Crear Superusuario / Administrador para pruebas
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@elconstructor.cl", "admin123")
    print("Usuario admin creado exitosamente (admin / admin123).")
else:
    print("Usuario admin ya existe.")

# 2. Categorías del Negocio Ferretero
categorias_data = [
    {
        "nombre": "Herramientas y Maquinaria",
        "descripcion": "Herramientas manuales, eléctricas y neumáticas para obra y taller."
    },
    {
        "nombre": "Materiales Básicos y Obra Gruesa",
        "descripcion": "Cemento, mortero, áridos en saco y mallas para construcción."
    },
    {
        "nombre": "Pinturas y Adhesivos",
        "descripcion": "Látex interior, esmaltes al agua, siliconas y selladores."
    },
    {
        "nombre": "Fijaciones y Tornillería",
        "descripcion": "Tarugos, tornillos vulcanita, pernos de anclaje y remaches."
    },
    {
        "nombre": "Gasfitería y Tuberías",
        "descripcion": "Tubos PVC, terminales cobre, llaves de paso y fitting."
    },
    {
        "nombre": "Electricidad e Iluminación",
        "descripcion": "Cables conductores, automáticos monofásicos y canaletas."
    }
]

cat_map = {}
for c_data in categorias_data:
    cat, created = Categoria.objects.get_or_create(nombre=c_data["nombre"], defaults={"descripcion": c_data["descripcion"]})
    cat_map[c_data["nombre"]] = cat
    if created:
        print(f"Categoría creada: {cat.nombre}")

# 3. Productos representativos del caso "El Constructor"
productos_data = [
    {
        "codigo": "POL-ES-01",
        "nombre": "Cemento Especial 25 kg Melón",
        "categoria": cat_map["Materiales Básicos y Obra Gruesa"],
        "descripcion": "Cemento de alta resistencia para hormigón y pegado de ladrillos en obra general.",
        "precio": 6490,
        "stock": 48,
        "unidad_medida": "Saco",
        "ubicacion_bodega": "Patio Techado - Zona Cemento",
        "disponible": True
    },
    {
        "codigo": "ARI-GR-25",
        "nombre": "Arena Gruesa Seleccionada 25 kg",
        "categoria": cat_map["Materiales Básicos y Obra Gruesa"],
        "descripcion": "Arena limpia harneada lista para mezclas de mortero y afinados de piso.",
        "precio": 2500,
        "stock": 40,
        "unidad_medida": "Saco",
        "ubicacion_bodega": "Patio Techado - Pallet 3",
        "disponible": True
    },
    {
        "codigo": "PIN-LAT-01",
        "nombre": "Látex Interior Blanco Mate 1 Galón",
        "categoria": cat_map["Pinturas y Adhesivos"],
        "descripcion": "Pintura lavable antihongos para muros interiores y cielos rasos.",
        "precio": 18990,
        "stock": 12,
        "unidad_medida": "Galón / Litro",
        "ubicacion_bodega": "Pasillo 4 - Estante B",
        "disponible": True
    },
    {
        "codigo": "PIN-ESM-04",
        "nombre": "Esmalte al Agua Satinado 1 Galón",
        "categoria": cat_map["Pinturas y Adhesivos"],
        "descripcion": "Alta durabilidad y lavabilidad para zonas húmedas (baños y cocinas).",
        "precio": 24990,
        "stock": 5,  # Stock Crítico
        "unidad_medida": "Galón / Litro",
        "ubicacion_bodega": "Pasillo 4 - Estante C",
        "disponible": True
    },
    {
        "codigo": "FIJ-TAR-100",
        "nombre": "Kit Tarugos y Tornillos 100 piezas",
        "categoria": cat_map["Fijaciones y Tornillería"],
        "descripcion": "Juego surtido de tarugos plásticos Nº 6 y 8 con tornillos cincados correspondientes.",
        "precio": 9990,
        "stock": 35,
        "unidad_medida": "Caja / Set",
        "ubicacion_bodega": "Mesón Central - Gaveta 12",
        "disponible": True
    },
    {
        "codigo": "HER-TAL-18V",
        "nombre": "Taladro Percutor Inalámbrico 18V Bosch",
        "categoria": cat_map["Herramientas y Maquinaria"],
        "descripcion": "Mandril 13mm, 2 baterías de litio y maletín de transporte para trabajo pesado.",
        "precio": 129990,
        "stock": 8,  # Stock Crítico
        "unidad_medida": "Unidad",
        "ubicacion_bodega": "Vitrina Seguridad Mesón",
        "disponible": True
    },
    {
        "codigo": "HER-ESM-750",
        "nombre": "Esmeril Angular 4 1/2' 750W Dewalt",
        "categoria": cat_map["Herramientas y Maquinaria"],
        "descripcion": "Velocidad de 11.000 RPM, traba de eje y mango lateral de dos posiciones.",
        "precio": 34990,
        "stock": 15,
        "unidad_medida": "Unidad",
        "ubicacion_bodega": "Bodega Central - Estante 2",
        "disponible": True
    },
    {
        "codigo": "GAS-TUB-110",
        "nombre": "Tubo Sanitario PVC 110 mm x 6 m",
        "categoria": cat_map["Gasfitería y Tuberías"],
        "descripcion": "Tubería sanitaria clase 4 para descargas domiciliarias y alcantarillado.",
        "precio": 14990,
        "stock": 0,  # Agotado (para probar alertas de stock)
        "unidad_medida": "Tira / Barra",
        "ubicacion_bodega": "Patio Exterior - Racks Tuberías",
        "disponible": True
    },
    {
        "codigo": "ELE-DIS-16A",
        "nombre": "Disyuntor Termomagnético 1P 16A Legrand",
        "categoria": cat_map["Electricidad e Iluminación"],
        "descripcion": "Protección para circuitos de alumbrado y enchufes según norma SEC.",
        "precio": 4590,
        "stock": 28,
        "unidad_medida": "Unidad",
        "ubicacion_bodega": "Pasillo 1 - Vitrina Eléctrica",
        "disponible": True
    }
]

for p_data in productos_data:
    prod, created = Producto.objects.get_or_create(
        codigo=p_data["codigo"],
        defaults=p_data
    )
    if created:
        print(f"Producto cargado: [{prod.codigo}] {prod.nombre} | Stock: {prod.stock}")
    # Fotos incluidas en media/productos/ (créditos en CREDITOS.md), nombradas por SKU
    foto = f"productos/{prod.codigo.lower()}.jpg"
    if not prod.imagen and (settings.MEDIA_ROOT / foto).exists():
        Producto.objects.filter(pk=prod.pk).update(imagen=foto)

print("\n--- CARGA DE DATOS DE PRUEBA COMPLETADA CON ÉXITO ---")
