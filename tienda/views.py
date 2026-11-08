import json
import secrets
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.core.paginator import Paginator
from django.db.models import BooleanField, ExpressionWrapper, ProtectedError, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (url_has_allowed_host_and_scheme, urlsafe_base64_decode,
                               urlsafe_base64_encode)
from django.views.decorators.http import require_POST

from .models import Categoria, DetallePedido, Marca, Pago, Pedido, Producto, Rol, Usuario
from .panel import (comprobar_cuentas, comprobar_staff, datos_iniciales, mensaje_error,
                    mover_stock, objeto_de_seccion, cantidades_pedido, recalcular_total)

User = get_user_model()

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
    error = ''
    enviado = False
    email = request.POST.get('email', '').strip().lower() if request.method == 'POST' else ''
    if request.method == 'POST':
        try:
            validate_email(email)
            if len(email) > 254:
                raise ValidationError('El correo es demasiado largo.')
        except ValidationError:
            error = 'Ingresa un correo electrónico válido.'
        else:
            usuario = User.objects.filter(email__iexact=email, is_active=True).first()
            if usuario and usuario.has_usable_password():
                url = request.build_absolute_uri(reverse('restablecer_contrasena', args=[
                    urlsafe_base64_encode(force_bytes(usuario.pk)),
                    default_token_generator.make_token(usuario),
                ]))
                send_mail(
                    'Restablecer contraseña de Sinewave',
                    f'Para cambiar tu contraseña, abre este enlace:\n\n{url}\n',
                    None, [usuario.email],
                )
            enviado = True
    return render(request, 'olvide-contrasena.html', {
        'error': error, 'enviado': enviado, 'email': email,
    })


def restablecer_contrasena(request, uidb64, token):
    try:
        usuario = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        usuario = None
    valido = usuario is not None and default_token_generator.check_token(usuario, token)
    error = ''
    if request.method == 'POST' and valido:
        clave = request.POST.get('password1', '')
        if clave != request.POST.get('password2', ''):
            error = 'Las contraseñas no coinciden.'
        else:
            try:
                validate_password(clave, usuario)
            except ValidationError as exc:
                error = ' '.join(exc.messages)
            else:
                usuario.set_password(clave)
                usuario.save(update_fields=['password'])
                messages.success(request, 'Contraseña actualizada. Ya puedes iniciar sesión.')
                return redirect('login')
    return render(request, 'restablecer-contrasena.html', {
        'valido': valido, 'error': error,
    })

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


@login_required
def formulario(request, seccion, pk=None):
    comprobar_staff(request)
    if seccion not in ('cuentas', 'clientes', 'roles', 'categorias', 'marcas', 'productos', 'pedidos'):
        raise Http404('Sección inexistente')
    if seccion == 'cuentas':
        comprobar_cuentas(request)
    obj = objeto_de_seccion(seccion, pk) if pk else None
    datos = request.POST if request.method == 'POST' else datos_iniciales(seccion, obj)
    error = ''

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # CREAR o MODIFICAR: los datos vienen del formulario HTML.
                if seccion == 'cuentas':
                    saved = obj or User()
                    username = request.POST.get('username', '').strip()
                    email = request.POST.get('email', '').strip().lower()
                    clave = request.POST.get('password1', '')
                    if not email:
                        raise ValidationError('El correo es obligatorio.')
                    if clave != request.POST.get('password2', ''):
                        raise ValidationError('Las contraseñas no coinciden.')
                    if obj is None and not clave:
                        raise ValidationError('Indica una contraseña.')
                    if clave:
                        validate_password(clave, saved)
                    if User.objects.filter(email__iexact=email).exclude(pk=saved.pk).exists():
                        raise ValidationError('Este correo ya está registrado.')
                    if obj == request.user and 'is_active' not in request.POST:
                        raise ValidationError('No puedes desactivar tu propia cuenta.')
                    saved.username = username
                    saved.email = email
                    saved.first_name = request.POST.get('first_name', '').strip()
                    saved.last_name = request.POST.get('last_name', '').strip()
                    saved.is_staff = 'is_staff' in request.POST
                    saved.is_active = 'is_active' in request.POST
                    if clave:
                        saved.set_password(clave)
                    saved.full_clean()
                    saved.save()
                    if hasattr(saved, 'cliente'):
                        cliente = saved.cliente
                        cliente.activo = saved.is_active
                        cliente.save(update_fields=['activo'])
                elif seccion == 'clientes':
                    saved = obj or Usuario()
                    correo = request.POST.get('correo', '').strip().lower()
                    if User.objects.filter(email__iexact=correo).exclude(pk=saved.cuenta_id).exists():
                        raise ValidationError('Este correo ya pertenece a una cuenta de acceso.')
                    rol = Rol.objects.filter(pk=request.POST.get('rol')).first()
                    if rol is None:
                        raise ValidationError('Selecciona un rol.')
                    correo_anterior = saved.correo if obj else ''
                    saved.nombre_completo = request.POST.get('nombre_completo', '').strip()
                    saved.correo = correo
                    saved.telefono = request.POST.get('telefono', '').strip()
                    saved.rol = rol
                    saved.activo = 'activo' in request.POST
                    saved.full_clean()
                    saved.save()
                    if saved.cuenta_id:
                        cuenta = saved.cuenta
                        if cuenta.username == correo_anterior:
                            cuenta.username = correo
                        cuenta.email = correo
                        cuenta.is_active = saved.activo
                        cuenta.full_clean()
                        cuenta.save()
                elif seccion == 'roles':
                    saved = obj or Rol()
                    saved.nombre = request.POST.get('nombre', '').strip()
                    saved.descripcion = request.POST.get('descripcion', '').strip()
                    saved.full_clean()
                    saved.save()
                elif seccion == 'categorias':
                    saved = obj or Categoria()
                    saved.nombre = request.POST.get('nombre', '').strip()
                    saved.slug = request.POST.get('slug', '').strip()
                    saved.icono = request.POST.get('icono', '').strip()
                    saved.imagen = request.POST.get('imagen', '').strip()
                    saved.activa = 'activa' in request.POST
                    saved.full_clean()
                    saved.save()
                elif seccion == 'marcas':
                    saved = obj or Marca()
                    saved.nombre = request.POST.get('nombre', '').strip()
                    saved.full_clean()
                    saved.save()
                elif seccion == 'productos':
                    saved = obj or Producto()
                    saved.codigo_sku = request.POST.get('codigo_sku', '').strip()
                    saved.nombre = request.POST.get('nombre', '').strip()
                    saved.descripcion = request.POST.get('descripcion', '').strip()
                    saved.precio = Decimal(request.POST.get('precio', ''))
                    saved.stock = int(request.POST.get('stock', ''))
                    if saved.precio < 0 or saved.stock < 0:
                        raise ValidationError('El precio y el stock no pueden ser negativos.')
                    categoria = Categoria.objects.filter(pk=request.POST.get('categoria')).first()
                    if categoria is None:
                        raise ValidationError('Selecciona una categoría.')
                    saved.categoria = categoria
                    marca_id = request.POST.get('marca')
                    saved.marca = Marca.objects.filter(pk=marca_id).first() if marca_id else None
                    if marca_id and saved.marca is None:
                        raise ValidationError('Selecciona una marca válida.')
                    saved.imagen = request.POST.get('imagen', '').strip()
                    saved.destacado = 'destacado' in request.POST
                    saved.es_caja_sorpresa = 'es_caja_sorpresa' in request.POST
                    if request.FILES.get('foto'):
                        saved.foto = request.FILES['foto']
                    saved.full_clean()
                    saved.save()
                else:
                    saved = Pedido.objects.select_for_update().get(pk=obj.pk) if obj else Pedido()
                    usuario = Usuario.objects.filter(pk=request.POST.get('usuario')).first()
                    if usuario is None:
                        raise ValidationError('Selecciona un cliente.')
                    estado_anterior = saved.estado
                    estado_nuevo = request.POST.get('estado', '')
                    if saved.checkout_token and estado_anterior != estado_nuevo:
                        if estado_nuevo == Pedido.Estado.CANCELADO:
                            mover_stock(cantidades_pedido(saved, 1))
                        elif estado_anterior == Pedido.Estado.CANCELADO:
                            mover_stock(cantidades_pedido(saved, -1))
                    saved.usuario = usuario
                    saved.estado = estado_nuevo
                    saved.full_clean()
                    saved.save()
            messages.success(request, 'Registro guardado correctamente.')
            if seccion == 'pedidos':
                return redirect('panel_pedido', pk=saved.pk)
            return redirect('panel_listado', seccion=seccion)
        except (ValidationError, ValueError, InvalidOperation, IntegrityError) as exc:
            error = mensaje_error(exc)

    titulos = {'cuentas': 'Cuentas de acceso', 'clientes': 'Clientes', 'roles': 'Roles comerciales',
               'categorias': 'Categorías', 'marcas': 'Marcas', 'productos': 'Productos',
               'pedidos': 'Ventas y pedidos'}
    return render(request, 'panel/formulario.html', {
        'seccion': seccion, 'titulo': titulos[seccion], 'obj': obj, 'datos': datos, 'error': error,
        'roles': Rol.objects.order_by('nombre'), 'categorias': Categoria.objects.order_by('nombre'),
        'marcas': Marca.objects.order_by('nombre'), 'clientes': Usuario.objects.order_by('nombre_completo'),
        'estados': Pedido.Estado.choices, 'puede_eliminar': seccion not in ('cuentas', 'clientes'),
    })


@login_required
def eliminar(request, seccion, pk):
    comprobar_staff(request)
    if seccion in ('cuentas', 'clientes'):
        raise PermissionDenied('Este registro se desactiva desde el formulario de edición.')
    obj = objeto_de_seccion(seccion, pk)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # ELIMINAR: se requiere POST para no borrar al abrir un enlace.
                if seccion == 'pedidos':
                    obj = Pedido.objects.select_for_update().get(pk=obj.pk)
                    if obj.checkout_token and obj.estado != Pedido.Estado.CANCELADO:
                        mover_stock(cantidades_pedido(obj, 1))
                obj.delete()
            messages.success(request, 'Registro eliminado.')
            return redirect('panel_listado', seccion=seccion)
        except ProtectedError:
            messages.error(request, 'No se puede eliminar porque existen registros relacionados.')
            return redirect('panel_formulario_editar', seccion=seccion, pk=pk)
    return render(request, 'panel/eliminar.html', {'obj': obj, 'seccion': seccion, 'titulo': seccion})


@login_required
def hijo_formulario(request, tipo, pedido_id, pk=None):
    comprobar_staff(request)
    parent = get_object_or_404(Pedido, pk=pedido_id)
    if tipo == 'detalles':
        obj = get_object_or_404(DetallePedido, pk=pk, pedido=parent) if pk else None
        titulo = 'Detalle de venta'
    elif tipo == 'pagos':
        obj = get_object_or_404(Pago, pk=pk, pedido=parent) if pk else None
        titulo = 'Pago'
    else:
        raise Http404('Sección inexistente')
    datos = request.POST if request.method == 'POST' else {}
    if obj and request.method != 'POST':
        if tipo == 'detalles':
            datos = {'producto': str(obj.producto_id), 'cantidad': obj.cantidad,
                     'precio_unitario': obj.precio_unitario}
        else:
            datos = {'metodo': obj.metodo, 'estado': obj.estado}
    error = ''
    if request.method == 'POST':
        try:
            with transaction.atomic():
                parent = Pedido.objects.select_for_update().get(pk=pedido_id)
                if tipo == 'detalles':
                    viejo_producto_id = obj.producto_id if obj else None
                    vieja_cantidad = obj.cantidad if obj else 0
                    saved = obj or DetallePedido()
                    producto = Producto.objects.filter(pk=request.POST.get('producto')).first()
                    if producto is None:
                        raise ValidationError('Selecciona un producto.')
                    saved.pedido = parent
                    saved.producto = producto
                    saved.cantidad = int(request.POST.get('cantidad', ''))
                    saved.precio_unitario = Decimal(request.POST.get('precio_unitario', ''))
                    if saved.cantidad < 1 or saved.precio_unitario < 0:
                        raise ValidationError('La cantidad debe ser positiva y el precio no puede ser negativo.')
                    saved.full_clean()
                    if parent.checkout_token and parent.estado != Pedido.Estado.CANCELADO:
                        cambios = {saved.producto_id: -saved.cantidad}
                        if viejo_producto_id:
                            cambios[viejo_producto_id] = cambios.get(viejo_producto_id, 0) + vieja_cantidad
                        mover_stock(cambios)
                    saved.save()
                    recalcular_total(parent)
                else:
                    saved = obj or Pago()
                    saved.pedido = parent
                    saved.metodo = request.POST.get('metodo', '')
                    saved.estado = request.POST.get('estado', '')
                    saved.full_clean()
                    saved.save()
            messages.success(request, 'Registro guardado correctamente.')
            return redirect('panel_pedido', pk=pedido_id)
        except (ValidationError, ValueError, InvalidOperation, IntegrityError) as exc:
            error = mensaje_error(exc)
    return render(request, 'panel/formulario.html', {
        'seccion': tipo, 'titulo': titulo, 'obj': obj, 'datos': datos, 'error': error,
        'productos': Producto.objects.order_by('nombre'),
        'metodos': Pago.Metodo.choices, 'estados_pago': Pago.Estado.choices,
        'volver': reverse('panel_pedido', kwargs={'pk': pedido_id}), 'puede_eliminar': False,
    })


@login_required
def hijo_eliminar(request, tipo, pedido_id, pk):
    comprobar_staff(request)
    parent = get_object_or_404(Pedido, pk=pedido_id)
    if tipo == 'detalles':
        obj = get_object_or_404(DetallePedido, pk=pk, pedido=parent)
    elif tipo == 'pagos':
        obj = get_object_or_404(Pago, pk=pk, pedido=parent)
    else:
        raise Http404('Sección inexistente')
    if request.method == 'POST':
        with transaction.atomic():
            parent = Pedido.objects.select_for_update().get(pk=pedido_id)
            if tipo == 'detalles' and parent.checkout_token and parent.estado != Pedido.Estado.CANCELADO:
                mover_stock({obj.producto_id: obj.cantidad})
            obj.delete()
            if tipo == 'detalles':
                recalcular_total(parent)
        messages.success(request, 'Registro eliminado.')
        return redirect('panel_pedido', pk=pedido_id)
    return render(request, 'panel/eliminar.html', {
        'obj': obj, 'titulo': 'Detalle de venta' if tipo == 'detalles' else 'Pago',
        'volver': reverse('panel_pedido', kwargs={'pk': pedido_id}),
    })
