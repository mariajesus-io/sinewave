"""Consultas y funciones auxiliares del panel administrativo."""

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, render

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


def mover_stock(cambios):
    """Aplica cambios de stock con bloqueo; un valor negativo reserva unidades."""
    cambios = {pk: cantidad for pk, cantidad in cambios.items() if cantidad}
    productos = list(Producto.objects.select_for_update().filter(pk__in=cambios).order_by('pk'))
    if len(productos) != len(cambios):
        raise ValidationError('Uno de los productos ya no está disponible.')
    for producto in productos:
        nuevo_stock = producto.stock + cambios[producto.pk]
        if nuevo_stock < 0:
            raise ValidationError(f'Stock insuficiente para {producto.nombre}.')
        producto.stock = nuevo_stock
        producto.save(update_fields=['stock'])


def cantidades_pedido(pedido, signo):
    return {
        item['producto_id']: signo * item['cantidad']
        for item in pedido.detalles.values('producto_id').annotate(cantidad=Sum('cantidad'))
    }


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
def pedido(request, pk):
    comprobar_staff(request)
    obj = get_object_or_404(Pedido.objects.select_related('usuario'), pk=pk)
    return render(request, 'panel/pedido.html', {
        'pedido': obj,
        'detalles': obj.detalles.select_related('producto').all(),
        'pagos': obj.pagos.all(),
    })


def recalcular_total(pedido):
    pedido.total = (pedido.detalles.aggregate(total=Sum('subtotal'))['total'] or 0) + pedido.costo_envio
    pedido.save(update_fields=['total'])
