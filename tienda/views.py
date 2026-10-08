from django.core.paginator import Paginator
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.shortcuts import get_object_or_404, render

from .models import Categoria, Marca, Producto


def inicio(request):
    contexto = {
        "categorias": Categoria.objects.filter(activa=True).order_by("id"),
        "mas_vistos": Producto.objects.filter(destacado=True).select_related("categoria")[:6],
        "marcas": Marca.objects.order_by("id"),
    }
    return render(request, 'index.html', contexto)


def categoria(request, slug):
    cat = get_object_or_404(Categoria, slug=slug, activa=True)
    # Los productos sin foto ni imagen (los que crea poblar_datos con Faker) quedan al final.
    tiene_imagen = ExpressionWrapper(~Q(foto="") | ~Q(imagen=""), output_field=BooleanField())
    productos = cat.productos.select_related("marca").order_by(tiene_imagen.desc(), "nombre")
    # Con 1 millón de productos de prueba no se pueden mostrar todos: se muestran de a 12.
    pagina = Paginator(productos, 12).get_page(request.GET.get("page"))
    return render(request, 'categoria.html', {"cat": cat, "slug": slug, "pagina": pagina})


def nosotros(request):
    return render(request, 'nosotros.html')


def terminos(request):
    return render(request, 'terminos.html')


def privacidad(request):
    return render(request, 'privacidad.html')


def login_view(request):
    return render(request, 'login.html')


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
