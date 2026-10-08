from django.core.paginator import Paginator
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.shortcuts import get_object_or_404, render

from .models import Categoria, Marca, Producto

# Una VISTA es una función que recibe la petición del navegador (request) y devuelve una página.
# render(request, plantilla, contexto) toma el HTML de tienda/templates/ y le pasa los datos
# del diccionario "contexto", que en la plantilla se usan con {{ variable }} y {% for %}.


def inicio(request):
    """Página principal: categorías, productos destacados y carrusel de marcas, todo desde la BD."""
    contexto = {
        "categorias": Categoria.objects.filter(activa=True).order_by("id"),
        "mas_vistos": Producto.objects.filter(destacado=True).select_related("categoria")[:6],
        "marcas": Marca.objects.order_by("id"),
    }
    return render(request, 'index.html', contexto)


def categoria(request, slug):
    """Productos de una categoría. El slug viene de la URL: /categoria/<slug>/"""
    # get_object_or_404: si no existe la categoría (o está inactiva) muestra la página de error 404.
    cat = get_object_or_404(Categoria, slug=slug, activa=True)
    # Los productos sin foto ni imagen (los que crea poblar_datos con Faker) quedan al final.
    tiene_imagen = ExpressionWrapper(~Q(foto="") | ~Q(imagen=""), output_field=BooleanField())
    productos = cat.productos.select_related("marca").order_by(tiene_imagen.desc(), "nombre")
    # Con 1 millón de productos de prueba no se pueden mostrar todos: se muestran de a 12.
    pagina = Paginator(productos, 12).get_page(request.GET.get("page"))
    return render(request, 'categoria.html', {"cat": cat, "slug": slug, "pagina": pagina})


# Las vistas de abajo solo muestran una plantilla, sin datos de la BD.
# El carrito, el login y el registro funcionan con JavaScript en el navegador (localStorage),
# no guardan nada en la base de datos.

def nosotros(request):
    return render(request, 'nosotros.html')


def terminos(request):
    return render(request, 'terminos.html')


def privacidad(request):
    return render(request, 'privacidad.html')


def login_view(request):
    return render(request, 'login.html')


# Alias: login también apunta a login_view.
login = login_view


def registro(request):
    return render(request, 'registro.html')


def olvide_contrasena(request):
    return render(request, 'olvide-contrasena.html')

def carrito(request):
    return render(request, 'carrito.html')

def checkout(request):
    return render(request, 'checkout.html')

def pago_exitoso(request):
    return render(request, 'pago_exitoso.html')

def historial(request):
    return render(request, 'historial.html')


def cajas_sorpresa(request):
    return render(request, 'cajas_sorpresa.html')
