from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.core.paginator import Paginator
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Categoria, Marca, Producto, Rol, Usuario

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


# El carrito continúa en el navegador. El login y el registro sí usan Django y la BD.

def nosotros(request):
    return render(request, 'nosotros.html')


def terminos(request):
    return render(request, 'terminos.html')


def privacidad(request):
    return render(request, 'privacidad.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('panel_inicio' if request.user.is_staff else 'inicio')
    error = ''
    if request.method == 'POST':
        usuario = request.POST.get('username', '').strip()
        contrasena = request.POST.get('password', '')
        cuenta = authenticate(request, username=usuario, password=contrasena)
        if cuenta is not None:
            auth_login(request, cuenta)
            destino = request.POST.get('next', '')
            if not url_has_allowed_host_and_scheme(destino, {request.get_host()}, require_https=request.is_secure()):
                destino = 'panel_inicio' if cuenta.is_staff else 'inicio'
            return redirect(destino)
        error = 'Usuario o contraseña incorrectos, o cuenta desactivada.'
    return render(request, 'login.html', {
        'error': error, 'next': request.POST.get('next', request.GET.get('next', '')),
        'usuario': request.POST.get('username', ''),
    })


def registro(request):
    error = ''
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        correo = request.POST.get('correo', '').strip().lower()
        telefono = request.POST.get('telefono', '').strip()
        clave = request.POST.get('password1', '')
        confirmacion = request.POST.get('password2', '')

        if not nombre or not correo or not clave:
            error = 'Completa el nombre, correo y contraseña.'
        elif len(nombre) > 150 or len(correo) > 150 or len(telefono) > 20:
            error = 'Uno de los datos supera el largo permitido.'
        else:
            try:
                validate_email(correo)
                validate_password(clave)
            except ValidationError as exc:
                error = ' '.join(exc.messages)
        if not error and clave != confirmacion:
            error = 'Las contraseñas no coinciden.'
        if not error and (Usuario.objects.filter(correo__iexact=correo).exists()
                          or get_user_model().objects.filter(email__iexact=correo).exists()
                          or get_user_model().objects.filter(username__iexact=correo).exists()):
            error = 'Este correo ya está registrado.'

        if not error:
            try:
                with transaction.atomic():
                    cuenta = get_user_model().objects.create_user(
                        username=correo, email=correo, password=clave, first_name=nombre,
                    )
                    rol, _ = Rol.objects.get_or_create(nombre='Cliente')
                    Usuario.objects.create(
                        nombre_completo=nombre, correo=correo, telefono=telefono,
                        rol=rol, cuenta=cuenta,
                    )
                messages.success(request, 'Cuenta creada. Ya puedes iniciar sesión.')
                return redirect('login')
            except IntegrityError:
                error = 'Este correo ya está registrado.'
    return render(request, 'registro.html', {'error': error, 'datos': request.POST})


@require_POST
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')


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
