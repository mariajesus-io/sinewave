"""
Migración de DATOS (no cambia tablas, solo inserta filas).

Carga el catálogo real de la tienda, que antes estaba escrito a mano en views.py:
categorías (con slug, ícono e imagen), marcas y productos.

Se usa update_or_create / get_or_create, así que se puede aplicar sobre una BD
que ya tiene las categorías creadas por poblar_datos sin duplicar nada.
"""
from django.db import migrations
from django.utils.text import slugify

UNSPLASH = "https://images.unsplash.com/photo-{}?auto=format&fit=crop&w={}&q=80"

# (slug, nombre, icono, imagen)
CATEGORIAS = [
    ("guitarras", "Guitarras", "bi-music-note", "/static/img/cat_guitarras.png"),
    ("bajos", "Bajos", "bi-soundwave", "/static/img/cat_bajos.png"),
    ("ukeleles", "Ukeleles", "bi-music-note-beamed", "/static/img/cat_ukeleles.png"),
    ("pianos", "Pianos", "bi-piano", "/static/img/cat_pianos.png"),
    ("teclados", "Teclados", "bi-keyboard", "/static/img/cat_teclados.png"),
    ("bateria", "Batería y Percusión", "bi-grid", UNSPLASH.format("1519892300165-cb5542fb47c7", 300)),
    ("amplificadores", "Amplificadores", "bi-speaker", "/static/img/cat_amplificadores.png"),
    ("audio-profesional", "Audio Profesional", "bi-mic", UNSPLASH.format("1598488035139-bdbb2231ce04", 300)),
    ("audio-hogar", "Audio Hogar y Estudio", "bi-house", UNSPLASH.format("1542728928-1413d1894ed1", 300)),
    ("dj", "DJ", "bi-disc", UNSPLASH.format("1470225620780-dba8ba36b745", 300)),
]

MARCAS = [
    "Fender", "Yamaha", "Gibson", "Shure", "Roland", "Korg", "Ibanez",
    "Marshall", "Pioneer", "Audio-Technica", "Tama", "Casio", "JBL",
    "Focusrite", "Meinl", "Sennheiser", "KRK", "Takamine", "Kala", "Boss",
]

# (sku, nombre, marca, categoria_slug, precio, stock, imagen, destacado)
PRODUCTOS = [
    ("SW-001", "Guitarra Eléctrica Fender Stratocaster", "Fender", "guitarras", 850000, 5, UNSPLASH.format("1564186763535-ebb21ef5277f", 500), True),
    ("SW-002", "Guitarra Acústica Yamaha F310", "Yamaha", "guitarras", 180000, 12, UNSPLASH.format("1550291652-6ea9114a47b1", 500), False),
    ("SW-003", "Guitarra Clásica Takamine GN10", "Takamine", "guitarras", 220000, 6, UNSPLASH.format("1510915361894-db8b60106cb1", 500), False),
    ("SW-004", "Bajo Eléctrico Ibanez SR300", "Ibanez", "bajos", 450000, 4, "/static/img/prod_ibanez_sr300.png", False),
    ("SW-005", "Bajo Fender Precision Bass", "Fender", "bajos", 980000, 2, "/static/img/prod_fender_pbass.png", False),
    ("SW-006", "Ukelele Soprano Kala MK-S", "Kala", "ukeleles", 55000, 15, "/static/img/prod_ukelele_soprano.png", False),
    ("SW-007", "Ukelele Tenor Fender Venice", "Fender", "ukeleles", 120000, 8, "/static/img/prod_ukelele_tenor.png", False),
    ("SW-008", "Piano Digital Yamaha P-45", "Yamaha", "pianos", 550000, 1, UNSPLASH.format("1552422535-c45813c61732", 500), False),
    ("SW-009", "Piano Digital Roland FP-30X", "Roland", "pianos", 720000, 3, UNSPLASH.format("1520523839897-bd0b52f945a0", 500), False),
    ("SW-010", "Sintetizador Korg Kross 2", "Korg", "teclados", 650000, 15, "/static/img/prod_korg_kross.png", True),
    ("SW-011", "Teclado Arranger Casio CT-S300", "Casio", "teclados", 80000, 20, "/static/img/prod_casio_cts300.png", False),
    ("SW-012", "Batería Acústica Tama Imperialstar", "Tama", "bateria", 1200000, 24, UNSPLASH.format("1519892300165-cb5542fb47c7", 500), True),
    ("SW-013", "Batería Electrónica Roland TD-1K", "Roland", "bateria", 750000, 5, "/static/img/prod_roland.png", False),
    ("SW-014", "Cajón Flamenco Meinl", "Meinl", "bateria", 95000, 10, "/static/img/prod_cajon.jpg", False),
    ("SW-015", "Amplificador Fender Champion 20", "Fender", "amplificadores", 185000, 7, "/static/img/prod_fender_amp.jpg", False),
    ("SW-016", "Amplificador Marshall MG15", "Marshall", "amplificadores", 160000, 4, "/static/img/prod_marshall.jpg", False),
    ("SW-017", "Micrófono Dinámico Shure SM58", "Shure", "audio-profesional", 95000, 25, "/static/img/prod_shure_sm58.png", False),
    ("SW-018", "Interfaz de Audio Focusrite Scarlett", "Focusrite", "audio-profesional", 180000, 12, "/static/img/prod_focusrite.png", False),
    ("SW-019", "Monitores de Estudio KRK Rokit 5", "KRK", "audio-profesional", 350000, 20, "/static/img/prod_krk_rokit.png", True),
    ("SW-020", "Audífonos de Estudio Audio-Technica M50x", "Audio-Technica", "audio-hogar", 150000, 35, UNSPLASH.format("1599669454699-248893623440", 500), True),
    ("SW-021", "Parlante JBL Flip 6", "JBL", "audio-hogar", 95000, 18, UNSPLASH.format("1608043152269-423dbba4e7e1", 500), False),
    ("SW-022", "Controladora DJ Pioneer DDJ-200", "Pioneer", "dj", 450000, 18, "/static/img/prod_pioneer_ddj200.png", True),
    ("SW-023", "Auriculares DJ Sennheiser HD 25", "Sennheiser", "dj", 210000, 6, UNSPLASH.format("1505740420928-5e560c06d30e", 500), False),
]


def cargar_catalogo(apps, schema_editor):
    # En las migraciones se usa apps.get_model (la versión del modelo en ESTE punto
    # del historial), no se importa desde models.py.
    Categoria = apps.get_model("tienda", "Categoria")
    Marca = apps.get_model("tienda", "Marca")
    Producto = apps.get_model("tienda", "Producto")

    categorias = {}
    for slug, nombre, icono, imagen in CATEGORIAS:
        categorias[slug], _ = Categoria.objects.update_or_create(
            nombre=nombre, defaults={"slug": slug, "icono": icono, "imagen": imagen},
        )
    # Si alguien creó otra categoría en el admin, también necesita un slug
    # (la migración 0006 lo vuelve único).
    for cat in Categoria.objects.filter(slug=""):
        cat.slug = slugify(cat.nombre)
        cat.save(update_fields=["slug"])

    marcas = {nombre: Marca.objects.get_or_create(nombre=nombre)[0] for nombre in MARCAS}

    for sku, nombre, marca, cat, precio, stock, imagen, destacado in PRODUCTOS:
        Producto.objects.update_or_create(
            codigo_sku=sku,
            defaults={
                "nombre": nombre, "marca": marcas[marca], "categoria": categorias[cat],
                "precio": precio, "stock": stock, "imagen": imagen, "destacado": destacado,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("tienda", "0004_catalogo_campos"),
    ]

    operations = [
        # noop al revertir: los datos se quedan, solo se "desmarca" la migración.
        migrations.RunPython(cargar_catalogo, migrations.RunPython.noop),
    ]
