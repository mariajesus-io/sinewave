import json
import secrets
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.core.paginator import Paginator
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Categoria, DetallePedido, Marca, Pago, Pedido, Producto, Rol, Usuario

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
        destino = request.GET.get('next', '')
        if url_has_allowed_host_and_scheme(destino, {request.get_host()}, require_https=request.is_secure()):
            return redirect(destino)
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


def cantidades_del_carrito(raw):
    try:
        items = json.loads(raw)
    except (TypeError, ValueError):
        raise ValidationError('El carrito no es válido. Vuelve a agregar los productos.')
    if not isinstance(items, list) or not 0 < len(items) <= 100:
        raise ValidationError('El carrito está vacío o contiene demasiados productos.')
    cantidades = {}
    for item in items:
        if not isinstance(item, dict) or type(item.get('id')) is not int or type(item.get('qty')) is not int:
            raise ValidationError('El carrito no es válido. Vuelve a agregar los productos.')
        producto_id, cantidad = item['id'], item['qty']
        if producto_id < 1 or not 1 <= cantidad <= 1000:
            raise ValidationError('La cantidad de un producto no es válida.')
        cantidades[producto_id] = cantidades.get(producto_id, 0) + cantidad
        if cantidades[producto_id] > 1000:
            raise ValidationError('La cantidad de un producto no es válida.')
    return cantidades


@login_required
def checkout(request):
    error = ''
    if request.method == 'POST':
        try:
            token = request.POST.get('checkout_token', '')
            if token != request.session.get('checkout_token') or not token:
                anterior = Pedido.objects.filter(checkout_token=token, usuario__cuenta=request.user).first() if token else None
                if anterior:
                    return redirect('pedido_confirmado', pk=anterior.pk)
                raise ValidationError('La confirmación venció. Actualiza la página e intenta nuevamente.')
            cantidades = cantidades_del_carrito(request.POST.get('carrito'))
            entrega = request.POST.get('despacho', '')
            direccion = request.POST.get('direccion', '').strip()
            metodo = request.POST.get('pago', '')
            if entrega not in Pedido.Entrega.values:
                raise ValidationError('Selecciona un tipo de entrega válido.')
            if entrega == Pedido.Entrega.DESPACHO and not direccion:
                raise ValidationError('Indica la dirección de envío.')
            if len(direccion) > 255:
                raise ValidationError('La dirección no puede superar 255 caracteres.')
            if metodo not in Pago.Metodo.values:
                raise ValidationError('Selecciona un método de pago válido.')
            cliente = Usuario.objects.filter(cuenta=request.user, activo=True).first()
            if cliente is None:
                raise ValidationError('Tu cuenta no tiene un perfil de cliente activo.')

            with transaction.atomic():
                productos = list(Producto.objects.select_for_update().filter(
                    pk__in=cantidades,
                ).order_by('pk'))
                if len(productos) != len(cantidades):
                    raise ValidationError('Uno de los productos ya no está disponible. Revisa tu carrito.')
                for producto in productos:
                    if producto.stock < cantidades[producto.pk]:
                        raise ValidationError(f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}.')
                subtotal = sum((producto.precio * cantidades[producto.pk] for producto in productos), Decimal(0))
                envio = Decimal(5000) if entrega == Pedido.Entrega.DESPACHO and subtotal < 100000 else Decimal(0)
                if subtotal + envio > 999999999999:
                    raise ValidationError('El total del pedido supera el máximo permitido.')
                pedido = Pedido.objects.create(
                    usuario=cliente, estado=Pedido.Estado.PENDIENTE,
                    tipo_entrega=entrega,
                    direccion_entrega=direccion if entrega == Pedido.Entrega.DESPACHO else '',
                    costo_envio=envio, total=subtotal + envio, checkout_token=token,
                )
                for producto in productos:
                    cantidad = cantidades[producto.pk]
                    DetallePedido.objects.create(
                        pedido=pedido, producto=producto, cantidad=cantidad,
                        precio_unitario=producto.precio,
                    )
                    producto.stock -= cantidad
                    producto.save(update_fields=['stock'])
                Pago.objects.create(pedido=pedido, metodo=metodo, estado=Pago.Estado.PENDIENTE)
            request.session.pop('checkout_token', None)
            request.session['checkout_clear_cart_for'] = pedido.pk
            return redirect('pedido_confirmado', pk=pedido.pk)
        except ValidationError as exc:
            error = ' '.join(exc.messages)
        except IntegrityError:
            anterior = Pedido.objects.filter(checkout_token=token, usuario__cuenta=request.user).first()
            if anterior:
                return redirect('pedido_confirmado', pk=anterior.pk)
            error = 'No se pudo registrar el pedido. Intenta nuevamente.'
    if not request.session.get('checkout_token'):
        request.session['checkout_token'] = secrets.token_hex(24)
    return render(request, 'checkout.html', {
        'error': error, 'datos': request.POST,
        'checkout_token': request.session['checkout_token'],
    })


@login_required
def pedido_confirmado(request, pk):
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related('detalles__producto', 'pagos'),
        pk=pk, usuario__cuenta=request.user,
    )
    clear_cart = request.session.get('checkout_clear_cart_for') == pedido.pk
    if clear_cart:
        request.session.pop('checkout_clear_cart_for', None)
    return render(request, 'pedido_confirmado.html', {'pedido': pedido, 'clear_cart': clear_cart})


@login_required
def historial(request):
    pedidos = Pedido.objects.filter(usuario__cuenta=request.user).prefetch_related(
        'detalles__producto', 'pagos',
    )
    pagina = Paginator(pedidos, 20).get_page(request.GET.get('page'))
    return render(request, 'historial.html', {'pagina': pagina})


def cajas_sorpresa(request):
    cajas = Producto.objects.filter(es_caja_sorpresa=True, stock__gt=0).order_by('precio', 'nombre')
    pagina = Paginator(cajas, 12).get_page(request.GET.get('page'))
    return render(request, 'cajas_sorpresa.html', {'pagina': pagina})
