"""Panel propio: cada formulario HTML envía datos por POST y usa el ORM."""

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Categoria, DetallePedido, Marca, Pago, Pedido, Producto, Rol, Usuario


User = get_user_model()


def comprobar_staff(request):
    if not request.user.is_staff:
        raise PermissionDenied('Se requiere una cuenta administrativa.')


def comprobar_cuentas(request):
    if not request.user.is_superuser:
        raise PermissionDenied('Solo el administrador principal gestiona cuentas de acceso.')


def mensaje_error(exc):
    if isinstance(exc, ValidationError):
        if hasattr(exc, 'message_dict'):
            return ' '.join('; '.join(errores) for errores in exc.message_dict.values())
        return ' '.join(exc.messages)
    return 'Revisa los datos ingresados.'


@login_required
def inicio(request):
    comprobar_staff(request)
    ventas = Pedido.objects.filter(estado__in=[Pedido.Estado.PAGADO, Pedido.Estado.ENVIADO,
                                              Pedido.Estado.ENTREGADO])
    return render(request, 'panel/inicio.html', {
        'cuentas': User.objects.count(),
        'clientes': Usuario.objects.count(),
        'productos': Producto.objects.count(),
        'pedidos': ventas.count(),
        'ventas': ventas.aggregate(total=Sum('total'))['total'] or 0,
        'ultimos': Pedido.objects.select_related('usuario').order_by('-fecha_creacion')[:5],
    })


@login_required
def listado(request, seccion):
    comprobar_staff(request)
    buscar = request.GET.get('q', '').strip()

    # CONSULTAR: una consulta ORM diferente para cada tabla del panel.
    if seccion == 'cuentas':
        comprobar_cuentas(request)
        titulo = 'Cuentas de acceso'
        headers = ['Usuario', 'Correo', 'Panel', 'Activa']
        registros = User.objects.all().order_by('username')
        if buscar:
            registros = registros.filter(Q(username__icontains=buscar) | Q(email__icontains=buscar))
    elif seccion == 'clientes':
        titulo = 'Clientes'
        headers = ['Nombre', 'Correo', 'Rol', 'Activo']
        registros = Usuario.objects.select_related('rol').order_by('-fecha_registro')
        if buscar:
            registros = registros.filter(Q(nombre_completo__icontains=buscar) | Q(correo__icontains=buscar))
    elif seccion == 'roles':
        titulo = 'Roles comerciales'
        headers = ['Nombre', 'Descripción']
        registros = Rol.objects.order_by('nombre')
        if buscar:
            registros = registros.filter(nombre__icontains=buscar)
    elif seccion == 'categorias':
        titulo = 'Categorías'
        headers = ['Nombre', 'Slug', 'Activa']
        registros = Categoria.objects.order_by('nombre')
        if buscar:
            registros = registros.filter(nombre__icontains=buscar)
    elif seccion == 'marcas':
        titulo = 'Marcas'
        headers = ['Nombre']
        registros = Marca.objects.order_by('nombre')
        if buscar:
            registros = registros.filter(nombre__icontains=buscar)
    elif seccion == 'productos':
        titulo = 'Productos'
        headers = ['SKU', 'Nombre', 'Categoría', 'Precio', 'Stock']
        registros = Producto.objects.select_related('categoria').order_by('nombre')
        if buscar:
            registros = registros.filter(Q(nombre__icontains=buscar) | Q(codigo_sku__icontains=buscar))
    elif seccion == 'pedidos':
        titulo = 'Ventas y pedidos'
        headers = ['Número', 'Cliente', 'Fecha', 'Estado', 'Total']
        registros = Pedido.objects.select_related('usuario').order_by('-fecha_creacion')
        if buscar:
            registros = registros.filter(Q(usuario__nombre_completo__icontains=buscar) | Q(usuario__correo__icontains=buscar))
    else:
        raise Http404('Sección inexistente')

    pagina = Paginator(registros, 20).get_page(request.GET.get('page'))
    rows = []
    for obj in pagina:
        if seccion == 'cuentas':
            cells = [obj.username, obj.email, 'Sí' if obj.is_staff else 'No', 'Sí' if obj.is_active else 'No']
        elif seccion == 'clientes':
            cells = [obj.nombre_completo, obj.correo, obj.rol.nombre, 'Sí' if obj.activo else 'No']
        elif seccion == 'roles':
            cells = [obj.nombre, obj.descripcion]
        elif seccion == 'categorias':
            cells = [obj.nombre, obj.slug, 'Sí' if obj.activa else 'No']
        elif seccion == 'marcas':
            cells = [obj.nombre]
        elif seccion == 'productos':
            cells = [obj.codigo_sku, obj.nombre, obj.categoria.nombre, obj.precio, obj.stock]
        else:
            cells = [obj.pk, obj.usuario.nombre_completo, obj.fecha_creacion, obj.get_estado_display(), obj.total]
        rows.append({'pk': obj.pk, 'cells': cells})

    return render(request, 'panel/listado.html', {
        'seccion': seccion, 'titulo': titulo, 'headers': headers, 'rows': rows,
        'pagina': pagina, 'q': buscar, 'puede_eliminar': seccion not in ('cuentas', 'clientes'),
    })


def objeto_de_seccion(seccion, pk):
    if seccion == 'cuentas':
        return get_object_or_404(User, pk=pk)
    if seccion == 'clientes':
        return get_object_or_404(Usuario, pk=pk)
    if seccion == 'roles':
        return get_object_or_404(Rol, pk=pk)
    if seccion == 'categorias':
        return get_object_or_404(Categoria, pk=pk)
    if seccion == 'marcas':
        return get_object_or_404(Marca, pk=pk)
    if seccion == 'productos':
        return get_object_or_404(Producto, pk=pk)
    if seccion == 'pedidos':
        return get_object_or_404(Pedido, pk=pk)
    raise Http404('Sección inexistente')


def datos_iniciales(seccion, obj):
    if obj is None:
        return {'is_active': True, 'activo': True, 'activa': True}
    if seccion == 'cuentas':
        return {'username': obj.username, 'email': obj.email, 'first_name': obj.first_name,
                'last_name': obj.last_name, 'is_staff': obj.is_staff, 'is_active': obj.is_active}
    if seccion == 'clientes':
        return {'nombre_completo': obj.nombre_completo, 'correo': obj.correo,
                'telefono': obj.telefono, 'rol': str(obj.rol_id), 'activo': obj.activo}
    if seccion == 'roles':
        return {'nombre': obj.nombre, 'descripcion': obj.descripcion}
    if seccion == 'categorias':
        return {'nombre': obj.nombre, 'slug': obj.slug, 'icono': obj.icono,
                'imagen': obj.imagen, 'activa': obj.activa}
    if seccion == 'marcas':
        return {'nombre': obj.nombre}
    if seccion == 'productos':
        return {'codigo_sku': obj.codigo_sku, 'nombre': obj.nombre, 'descripcion': obj.descripcion,
                'precio': obj.precio, 'stock': obj.stock, 'categoria': str(obj.categoria_id),
                'marca': str(obj.marca_id or ''), 'imagen': obj.imagen,
                'destacado': obj.destacado, 'es_caja_sorpresa': obj.es_caja_sorpresa}
    return {'usuario': str(obj.usuario_id), 'estado': obj.estado}


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
                    saved.imagen = request.POST.get('imagen', '').strip()
                    saved.destacado = 'destacado' in request.POST
                    saved.es_caja_sorpresa = 'es_caja_sorpresa' in request.POST
                    if request.FILES.get('foto'):
                        saved.foto = request.FILES['foto']
                    saved.full_clean()
                    saved.save()
                else:
                    saved = obj or Pedido()
                    usuario = Usuario.objects.filter(pk=request.POST.get('usuario')).first()
                    if usuario is None:
                        raise ValidationError('Selecciona un cliente.')
                    saved.usuario = usuario
                    saved.estado = request.POST.get('estado', '')
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
            # ELIMINAR: se requiere POST para no borrar al abrir un enlace.
            obj.delete()
            messages.success(request, 'Registro eliminado.')
            return redirect('panel_listado', seccion=seccion)
        except ProtectedError:
            messages.error(request, 'No se puede eliminar porque existen registros relacionados.')
            return redirect('panel_formulario_editar', seccion=seccion, pk=pk)
    return render(request, 'panel/eliminar.html', {'obj': obj, 'seccion': seccion, 'titulo': seccion})


@login_required
def pedido(request, pk):
    comprobar_staff(request)
    obj = get_object_or_404(Pedido.objects.select_related('usuario'), pk=pk)
    return render(request, 'panel/pedido.html', {
        'pedido': obj,
        'detalles': obj.detalles.select_related('producto').all(),
        'pagos': obj.pagos.all(),
    })


def recalcular_total(pedido):
    pedido.total = pedido.detalles.aggregate(total=Sum('subtotal'))['total'] or 0
    pedido.save(update_fields=['total'])


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
                if tipo == 'detalles':
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
            obj.delete()
            if tipo == 'detalles':
                recalcular_total(parent)
        messages.success(request, 'Registro eliminado.')
        return redirect('panel_pedido', pk=pedido_id)
    return render(request, 'panel/eliminar.html', {
        'obj': obj, 'titulo': 'Detalle de venta' if tipo == 'detalles' else 'Pago',
        'volver': reverse('panel_pedido', kwargs={'pk': pedido_id}),
    })
