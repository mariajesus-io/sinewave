# Demostración de las 20 consultas ORM en la terminal

Estas consultas **solo leen datos**. Ejecútalas desde la raíz del proyecto. La
primera línea carga la configuración local de MySQL; la segunda abre la consola
de Django:

```bash
cd /home/andres/Projects/sinewave
source .env.local
.venv/bin/python manage.py shell
```

Cuando aparezca `>>>`, pega este bloque **una vez** y pulsa Enter. Las variables
`venta`, `fecha` y `anio` se obtienen de una venta existente para que las
consultas con filtros tengan un ejemplo real:

```python
from datetime import timedelta
from decimal import Decimal
from django.db import connection
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from tienda.models import Categoria, DetallePedido, Pedido, Producto, Usuario

VALIDOS = [Pedido.Estado.PAGADO, Pedido.Estado.ENVIADO, Pedido.Estado.ENTREGADO]
venta = Pedido.objects.filter(estado__in=VALIDOS).order_by('-fecha_creacion').first()
categoria = Categoria.objects.order_by('id').first()
fecha = timezone.localtime(venta.fecha_creacion).date()
anio = fecha.year
print(connection.vendor, 'venta:', venta.id, 'cliente:', venta.usuario_id, 'categoría:', categoria.id, 'fecha:', fecha)
```

Debe decir `mysql`. Esta preparación requiere al menos una categoría y una venta
pagada, enviada o entregada. En esta instalación ya existen. Si cambias los datos,
ejecuta de nuevo el bloque. En las consultas siguientes pega **una línea completa
por número** en el indicador `>>>`; Enter muestra el resultado.

## 1. Todos los productos disponibles

```python
list(Producto.objects.filter(stock__gt=0).order_by('nombre').values('codigo_sku', 'nombre', 'categoria__nombre', 'precio', 'stock'))
```

## 2. Productos de una categoría seleccionada

Usa la categoría elegida en la variable `categoria`. Puedes cambiarla, por
ejemplo, con `categoria = Categoria.objects.get(id=1)`.

```python
list(Producto.objects.filter(categoria=categoria).order_by('nombre').values('codigo_sku', 'nombre', 'precio', 'stock'))
```

## 3. Productos dentro de un rango de precios

Cambia `10000` y `100000` por los límites que quieras mostrar.

```python
list(Producto.objects.filter(precio__gte=10000, precio__lte=100000).order_by('precio').values('nombre', 'precio', 'stock'))
```

## 4. Los 10 productos más caros

```python
list(Producto.objects.order_by('-precio').values('nombre', 'precio', 'stock')[:10])
```

## 5. Cantidad de clientes registrados

```python
Usuario.objects.count()
```

## 6. Compras de un cliente específico

La variable `venta.usuario_id` elige un cliente que tiene una venta válida.

```python
list(Pedido.objects.filter(usuario_id=venta.usuario_id, estado__in=VALIDOS).order_by('-fecha_creacion').values('id', 'fecha_creacion', 'estado', 'total'))
```

## 7. Productos adquiridos por ese cliente en una venta

La variable `venta` contiene tanto el número de venta como su cliente.

```python
list(DetallePedido.objects.filter(pedido_id=venta.id, pedido__usuario_id=venta.usuario_id, pedido__estado__in=VALIDOS).values('producto__nombre', 'cantidad', 'precio_unitario', 'subtotal'))
```

## 8. Cantidad de ventas durante un período

Este ejemplo cuenta desde 30 días antes de `fecha` hasta `fecha`, inclusive.

```python
Pedido.objects.filter(estado__in=VALIDOS, fecha_creacion__date__range=(fecha - timedelta(days=30), fecha)).count()
```

## 9. Productos con menos de cinco unidades disponibles

```python
list(Producto.objects.filter(stock__lt=5).order_by('stock', 'nombre').values('nombre', 'categoria__nombre', 'stock'))
```

## 10. Monto total vendido durante un día

```python
Pedido.objects.filter(estado__in=VALIDOS, fecha_creacion__date=fecha).aggregate(total=Sum('total'))
```

## 11. Cinco productos más vendidos por unidades

```python
list(Producto.objects.annotate(unidades=Sum('detalles__cantidad', filter=Q(detalles__pedido__estado__in=VALIDOS), default=0)).order_by('-unidades', 'nombre').values('nombre', 'unidades')[:5])
```

## 12. Cinco clientes con más compras

```python
list(Usuario.objects.annotate(compras=Count('pedidos', filter=Q(pedidos__estado__in=VALIDOS))).order_by('-compras', 'nombre_completo').values('nombre_completo', 'compras')[:5])
```

## 13. Monto total comprado por cada cliente

```python
list(Usuario.objects.annotate(monto=Sum('pedidos__total', filter=Q(pedidos__estado__in=VALIDOS), default=0)).order_by('-monto').values('nombre_completo', 'monto'))
```

## 14. Productos que nunca se han vendido

```python
list(Producto.objects.exclude(detalles__pedido__estado__in=VALIDOS).order_by('nombre').values('nombre', 'categoria__nombre', 'stock'))
```

## 15. Promedio gastado por venta

```python
Pedido.objects.filter(estado__in=VALIDOS).aggregate(promedio=Avg('total'))
```

## 16. Categoría con el mayor monto de ventas

```python
list(Categoria.objects.annotate(ingresos=Sum('productos__detalles__subtotal', filter=Q(productos__detalles__pedido__estado__in=VALIDOS))).filter(ingresos__isnull=False).order_by('-ingresos').values('nombre', 'ingresos')[:1])
```

## 17. Unidades vendidas por producto en los últimos 30 días

```python
list(Producto.objects.annotate(unidades=Sum('detalles__cantidad', filter=Q(detalles__pedido__fecha_creacion__gte=timezone.now() - timedelta(days=30), detalles__pedido__estado__in=VALIDOS), default=0)).order_by('-unidades', 'nombre').values('nombre', 'unidades'))
```

## 18. Cliente que más ha gastado durante el año

`anio` corresponde al año de la venta elegida. Puedes cambiarlo con `anio = 2026`.

```python
list(Usuario.objects.filter(pedidos__fecha_creacion__year=anio, pedidos__estado__in=VALIDOS).annotate(monto=Sum('pedidos__total')).order_by('-monto').values('nombre_completo', 'monto')[:1])
```

## 19. Montos de ventas por mes en el año seleccionado

```python
list(Pedido.objects.filter(estado__in=VALIDOS, fecha_creacion__year=anio).annotate(mes=TruncMonth('fecha_creacion')).values('mes').annotate(monto=Sum('total')).order_by('mes'))
```

## 20. Diez productos que generan mayores ingresos

```python
list(Producto.objects.annotate(ingresos=Sum('detalles__subtotal', filter=Q(detalles__pedido__estado__in=VALIDOS), default=0)).order_by('-ingresos', 'nombre').values('nombre', 'ingresos')[:10])
```

Para terminar, escribe `exit()` y pulsa Enter. `filter()` aplica condiciones,
`values()` elige columnas, `order_by()` ordena, `Count`/`Sum`/`Avg` calculan y
`list()` fuerza a Django a ejecutar la consulta y mostrar las filas en pantalla.
El código que utiliza el panel para estos reportes está en `tienda/reportes.py`.
