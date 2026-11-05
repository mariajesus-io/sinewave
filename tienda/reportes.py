from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from types import SimpleNamespace

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from .models import Categoria, DetallePedido, Pedido, Producto, Usuario

VENTAS_VALIDAS = [Pedido.Estado.PAGADO, Pedido.Estado.ENVIADO, Pedido.Estado.ENTREGADO]


def _ventas():
    return Pedido.objects.filter(estado__in=VENTAS_VALIDAS)


PREGUNTAS = [
    'Productos disponibles en la tienda',
    'Productos de una categoría seleccionada',
    'Productos dentro de un rango de precios',
    'Los 10 productos más caros',
    'Cantidad de clientes registrados',
    'Compras de un cliente específico',
    'Productos adquiridos en una venta de un cliente',
    'Ventas realizadas durante un período',
    'Productos con menos de cinco unidades',
    'Monto total vendido durante un día',
    'Cinco productos más vendidos por unidades',
    'Cinco clientes con más compras',
    'Monto total comprado por cada cliente',
    'Productos que nunca se han vendido',
    'Promedio gastado por venta',
    'Categoría con mayor monto de ventas',
    'Unidades vendidas por producto en los últimos 30 días',
    'Cliente que más ha gastado durante el año',
    'Montos de ventas por mes en el año seleccionado',
    'Diez productos que generan mayores ingresos',
]

FILTROS = {
    2: ['categoria'], 3: ['precio_min', 'precio_max'], 6: ['cliente'],
    7: ['cliente', 'pedido'], 8: ['fecha_inicio', 'fecha_fin'],
    10: ['fecha'], 18: ['anio'], 19: ['anio'],
}


def _tabla(queryset, campos, columnas, limite=100):
    registros = list(queryset.values(*campos)[:limite])
    return columnas, [[registro[c] for c in campos] for registro in registros], limite


def _resultado(numero, f):
    """Cada caso ejecuta exclusivamente consultas ORM sobre los modelos de la tienda."""
    if numero == 1:
        return _tabla(Producto.objects.filter(stock__gt=0).order_by('nombre'),
                      ['codigo_sku', 'nombre', 'categoria__nombre', 'precio', 'stock'],
                      ['SKU', 'Producto', 'Categoría', 'Precio', 'Stock'])
    if numero == 2:
        return _tabla(Producto.objects.filter(categoria=f['categoria']).order_by('nombre'),
                      ['codigo_sku', 'nombre', 'precio', 'stock'], ['SKU', 'Producto', 'Precio', 'Stock'])
    if numero == 3:
        q = Producto.objects.all()
        if f.get('precio_min') is not None:
            q = q.filter(precio__gte=f['precio_min'])
        if f.get('precio_max') is not None:
            q = q.filter(precio__lte=f['precio_max'])
        return _tabla(q.order_by('precio'), ['nombre', 'precio', 'stock'], ['Producto', 'Precio', 'Stock'])
    if numero == 4:
        return _tabla(Producto.objects.order_by('-precio'), ['nombre', 'precio', 'stock'],
                      ['Producto', 'Precio', 'Stock'], 10)
    if numero == 5:
        return ['Clientes registrados'], [[Usuario.objects.count()]], 1
    if numero == 6:
        return _tabla(_ventas().filter(usuario_id=f['cliente']).order_by('-fecha_creacion'),
                      ['id', 'fecha_creacion', 'estado', 'total'], ['Venta', 'Fecha', 'Estado', 'Total'])
    if numero == 7:
        return _tabla(DetallePedido.objects.filter(pedido_id=f['pedido'], pedido__usuario_id=f['cliente'],
                                                  pedido__estado__in=VENTAS_VALIDAS),
                      ['producto__nombre', 'cantidad', 'precio_unitario', 'subtotal'],
                      ['Producto', 'Cantidad', 'Precio unitario', 'Subtotal'])
    if numero == 8:
        return ['Ventas realizadas'], [[_ventas().filter(
            fecha_creacion__date__range=(f['fecha_inicio'], f['fecha_fin'])).count()]], 1
    if numero == 9:
        return _tabla(Producto.objects.filter(stock__lt=5).order_by('stock', 'nombre'),
                      ['nombre', 'categoria__nombre', 'stock'], ['Producto', 'Categoría', 'Stock'])
    if numero == 10:
        total = _ventas().filter(fecha_creacion__date=f['fecha']).aggregate(total=Sum('total'))['total'] or Decimal(0)
        return ['Total vendido'], [[total]], 1
    if numero == 11:
        q = Producto.objects.annotate(unidades=Sum('detalles__cantidad',
            filter=Q(detalles__pedido__estado__in=VENTAS_VALIDAS), default=0)).order_by('-unidades', 'nombre')
        return _tabla(q, ['nombre', 'unidades'], ['Producto', 'Unidades'], 5)
    if numero == 12:
        q = Usuario.objects.annotate(compras=Count('pedidos',
            filter=Q(pedidos__estado__in=VENTAS_VALIDAS))).order_by('-compras', 'nombre_completo')
        return _tabla(q, ['nombre_completo', 'compras'], ['Cliente', 'Compras'], 5)
    if numero == 13:
        q = Usuario.objects.annotate(monto=Sum('pedidos__total',
            filter=Q(pedidos__estado__in=VENTAS_VALIDAS), default=0)).order_by('-monto')
        return _tabla(q, ['nombre_completo', 'monto'], ['Cliente', 'Monto total'])
    if numero == 14:
        return _tabla(Producto.objects.exclude(detalles__pedido__estado__in=VENTAS_VALIDAS).order_by('nombre'),
                      ['nombre', 'categoria__nombre', 'stock'], ['Producto', 'Categoría', 'Stock'])
    if numero == 15:
        promedio = _ventas().aggregate(valor=Avg('total'))['valor'] or Decimal(0)
        return ['Promedio por venta'], [[promedio]], 1
    if numero == 16:
        q = Categoria.objects.annotate(ingresos=Sum('productos__detalles__subtotal',
            filter=Q(productos__detalles__pedido__estado__in=VENTAS_VALIDAS))).filter(
            ingresos__isnull=False).order_by('-ingresos')
        return _tabla(q, ['nombre', 'ingresos'], ['Categoría', 'Ingresos'], 1)
    if numero == 17:
        desde = timezone.now() - timedelta(days=30)
        q = Producto.objects.annotate(unidades=Sum('detalles__cantidad',
            filter=Q(detalles__pedido__fecha_creacion__gte=desde,
                     detalles__pedido__estado__in=VENTAS_VALIDAS), default=0))
        return _tabla(q.order_by('-unidades', 'nombre'), ['nombre', 'unidades'], ['Producto', 'Unidades'])
    if numero == 18:
        q = Usuario.objects.filter(pedidos__fecha_creacion__year=f['anio'],
            pedidos__estado__in=VENTAS_VALIDAS).annotate(
            monto=Sum('pedidos__total')).order_by('-monto')
        return _tabla(q, ['nombre_completo', 'monto'], ['Cliente', 'Monto'], 1)
    if numero == 19:
        q = _ventas().filter(fecha_creacion__year=f['anio']).annotate(
            mes=TruncMonth('fecha_creacion')).values('mes').annotate(monto=Sum('total')).order_by('mes')
        return _tabla(q, ['mes', 'monto'], ['Mes', 'Monto'], 12)
    q = Producto.objects.annotate(ingresos=Sum('detalles__subtotal',
        filter=Q(detalles__pedido__estado__in=VENTAS_VALIDAS), default=0)).order_by('-ingresos', 'nombre')
    return _tabla(q, ['nombre', 'ingresos'], ['Producto', 'Ingresos'], 10)


@login_required
def reportes(request):
    if not request.user.is_staff:
        raise PermissionDenied('Se requiere una cuenta administrativa.')
    now = timezone.localdate()
    numero_raw = request.GET.get('reporte', '')
    numero = int(numero_raw) if numero_raw.isdigit() and 1 <= int(numero_raw) <= 20 else None
    columnas, filas, limite, aviso = [], [], None, ''
    if numero:
        filtros = {}
        try:
            if numero == 2:
                categoria_id = request.GET.get('categoria', '')
                if not categoria_id.isdigit() or not Categoria.objects.filter(pk=categoria_id).exists():
                    raise ValueError('Selecciona una categoría.')
                filtros['categoria'] = int(categoria_id)
            elif numero == 3:
                minimo = request.GET.get('precio_min', '')
                maximo = request.GET.get('precio_max', '')
                if not minimo or not maximo:
                    raise ValueError('Indica ambos precios.')
                filtros['precio_min'] = Decimal(minimo)
                filtros['precio_max'] = Decimal(maximo)
                if filtros['precio_min'] < 0 or filtros['precio_min'] > filtros['precio_max']:
                    raise ValueError('El rango de precios no es válido.')
            elif numero in (6, 7):
                cliente_id = request.GET.get('cliente', '')
                if not cliente_id.isdigit() or int(cliente_id) < 1:
                    raise ValueError('Indica el ID del cliente.')
                filtros['cliente'] = int(cliente_id)
                if numero == 7:
                    pedido_id = request.GET.get('pedido', '')
                    if not pedido_id.isdigit() or int(pedido_id) < 1:
                        raise ValueError('Indica el número de venta.')
                    filtros['pedido'] = int(pedido_id)
            elif numero == 8:
                filtros['fecha_inicio'] = date.fromisoformat(request.GET.get('fecha_inicio', ''))
                filtros['fecha_fin'] = date.fromisoformat(request.GET.get('fecha_fin', ''))
                if filtros['fecha_inicio'] > filtros['fecha_fin']:
                    raise ValueError('La fecha final debe ser posterior a la inicial.')
            elif numero == 10:
                filtros['fecha'] = date.fromisoformat(request.GET.get('fecha', ''))
            elif numero in (18, 19):
                anio = request.GET.get('anio', '')
                filtros['anio'] = int(anio) if anio else now.year
                if not 2000 <= filtros['anio'] <= 2100:
                    raise ValueError('El año debe estar entre 2000 y 2100.')
            columnas, filas, limite = _resultado(numero, filtros)
        except (ValueError, InvalidOperation) as exc:
            aviso = str(exc) if str(exc) and not isinstance(exc, InvalidOperation) else 'Revisa los filtros ingresados.'
    dashboard = {
        'ventas': _ventas().count(),
        'clientes': Usuario.objects.count(),
        'productos': Producto.objects.filter(stock__gt=0).count(),
        'ingresos': _ventas().aggregate(total=Sum('total'))['total'] or 0,
        'top_productos': list(Producto.objects.annotate(unidades=Sum('detalles__cantidad',
            filter=Q(detalles__pedido__estado__in=VENTAS_VALIDAS), default=0)).filter(
            unidades__gt=0).order_by('-unidades', 'nombre')[:5]),
        'top_clientes': list(Usuario.objects.annotate(compras=Count('pedidos',
            filter=Q(pedidos__estado__in=VENTAS_VALIDAS)), monto=Sum('pedidos__total',
            filter=Q(pedidos__estado__in=VENTAS_VALIDAS), default=0)).filter(
            monto__gt=0).order_by('-monto', 'nombre_completo')[:5]),
        'stock_bajo': list(Producto.objects.select_related('categoria').filter(stock__lt=5).order_by('stock', 'nombre')[:5]),
        'categorias': list(Categoria.objects.annotate(ingresos=Sum('productos__detalles__subtotal',
            filter=Q(productos__detalles__pedido__estado__in=VENTAS_VALIDAS), default=0)).filter(
            ingresos__gt=0).order_by('-ingresos')),
        'meses': list(_ventas().annotate(mes=TruncMonth('fecha_creacion')).values('mes').annotate(
            monto=Sum('total')).order_by('-mes')[:6]),
    }
    if len(dashboard['categorias']) > 5:
        otras = sum(c.ingresos for c in dashboard['categorias'][4:])
        dashboard['categorias'] = dashboard['categorias'][:4] + [SimpleNamespace(nombre='Otras', ingresos=otras)]
    dashboard['max_unidades'] = max([p.unidades for p in dashboard['top_productos']] + [1])
    dashboard['max_ingresos_categoria'] = max([c.ingresos for c in dashboard['categorias']] + [1])
    dashboard['max_mes'] = max([m['monto'] for m in dashboard['meses']] + [1])
    colores = ['#2585fa', '#8759ec', '#ffc72e', '#21ca90', '#b9c2d1']
    total_categorias = sum(c.ingresos for c in dashboard['categorias'])
    dashboard['ingresos_categorias'] = total_categorias
    tramos = []
    acumulado = 0
    for color, categoria in zip(colores, dashboard['categorias']):
        categoria.color = color
        categoria.porcentaje = round(categoria.ingresos * 100 / total_categorias) if total_categorias else 0
        siguiente = acumulado + (categoria.ingresos * 100 / total_categorias if total_categorias else 0)
        tramos.append(f'{color} {acumulado:.2f}% {siguiente:.2f}%')
        acumulado = siguiente
    dashboard['donut_background'] = 'conic-gradient(' + ', '.join(tramos) + ')' if tramos and total_categorias else '#e2e8f0'
    dashboard['meses'].reverse()
    puntos = []
    for i, mes in enumerate(dashboard['meses']):
        x = 20 + i * 320 / max(len(dashboard['meses']) - 1, 1)
        y = 125 - float(mes['monto']) * 105 / float(dashboard['max_mes'])
        puntos.append(f'{x:.1f},{y:.1f}')
    dashboard['linea_puntos'] = ' '.join(puntos)
    return render(request, 'panel/reportes.html', {
        'preguntas': list(enumerate(PREGUNTAS, 1)), 'numero': numero,
        'pregunta_seleccionada': PREGUNTAS[numero - 1] if numero else None,
        'filtros': request.GET, 'categorias_filtro': Categoria.objects.order_by('nombre'),
        'mostrar_filtros': numero in FILTROS,
        'columnas': columnas, 'filas': filas, 'limite': limite, 'aviso': aviso,
        'dashboard': dashboard,
    })
