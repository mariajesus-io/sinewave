# Evaluación 3: panel propio y consultas con Django ORM

## Qué se implementó

El panel `/panel/` usa formularios HTML sencillos. Las vistas que procesan sus
envíos están en `tienda/views.py`; `tienda/panel.py` conserva consultas y funciones auxiliares.
No se usa `forms.py` ni Django Admin. Cada vista administrativa tiene
`@login_required` y además comprueba `is_staff`. Si no hay sesión, Django redirige
al login; si la cuenta está autenticada pero no es administrativa, devuelve 403.
El formulario de acceso usa `authenticate()`, `login()` y `logout()` de Django.
La sesión identifica al usuario mediante `request.user`.

Las cuentas de acceso están en `django.contrib.auth.models.User`. El modelo
`tienda.Usuario` representa al cliente comercial y conserva sus ventas. Cuando
un cliente se registra, ambos registros se vinculan por `Usuario.cuenta`.
Las cuentas se desactivan con `is_active=False`; los clientes con `activo=False`.
Las contraseñas siempre se guardan mediante `set_password()` o `create_user()`.

Las operaciones de crear, modificar y eliminar están en `tienda/views.py`.
Las consultas del panel están en `tienda/panel.py`.
La eliminación de clientes se reemplaza por desactivación para conservar ventas.
Las tablas y reportes consultan los modelos de `tienda/models.py`. Los filtros y
consultas de los 20 reportes están en `tienda/reportes.py`.

## Cómo hacer una consulta ORM

Abre la consola de Django con la base SQLite del proyecto:

```bash
python manage.py shell
```

Importa los modelos y funciones que necesites:

```python
from tienda.models import Categoria, Producto, Pedido, DetallePedido, Usuario
from django.db.models import Count, Sum, Q
from django.utils import timezone
```

Cada modelo tiene un administrador `objects`. `filter()` construye un `QuerySet`
con condiciones; Django lo convierte en SQL cuando lo evalúas. El doble guion
bajo (`__`) permite seguir relaciones y aplicar operadores como `lt`, `gte` e
`icontains`.

```python
Producto.objects.all()                                  # todos los productos
Producto.objects.filter(stock__lt=5)                    # stock menor que 5
Producto.objects.filter(categoria__slug='guitarras')     # relación con Categoría
Producto.objects.filter(precio__gte=10000, precio__lte=50000)
Producto.objects.filter(nombre__icontains='fender')     # búsqueda sin distinguir mayúsculas
```

Para obtener un registro, usa `get()` con una clave única o `first()` si puede no
existir. `get()` lanza `DoesNotExist` cuando no encuentra nada.

```python
producto = Producto.objects.get(codigo_sku='SW-001')
producto = Producto.objects.filter(nombre__icontains='fender').first()
```

Para contar, agrupar y sumar, usa `count()`, `annotate()` y `aggregate()`:

```python
Usuario.objects.count()
Categoria.objects.annotate(cantidad=Count('productos')).values('nombre', 'cantidad')
Pedido.objects.aggregate(total_vendido=Sum('total'))
Producto.objects.annotate(unidades=Sum('detalles__cantidad', default=0)).order_by('-unidades')[:5]
```

`annotate()` agrega un cálculo a cada fila; `aggregate()` devuelve un único
diccionario con el cálculo global. `values()` selecciona las columnas que quieres
mostrar. Un corte `[:5]` limita el resultado en la base de datos.

Para crear, actualizar y borrar con ORM:

```python
categoria = Categoria.objects.get(slug='guitarras')
producto = Producto.objects.create(
    codigo_sku='DEMO-001', nombre='Guitarra demo', precio=120000,
    stock=4, categoria=categoria,
)
producto.stock = 3
producto.save(update_fields=['stock'])
producto.delete()
```

En la web, el formulario HTML envía datos con `method="post"` y `{% csrf_token %}`.
La vista lee `request.POST`, comprueba los datos, llama a `full_clean()` para
validar el modelo y luego usa `save()`. Para eliminar se utiliza `delete()` con
una petición POST. Las listas usan `objects.all()` o `filter()` para consultar.
Por ejemplo, en el CRUD de productos se leen `request.POST['nombre']`, `precio`,
`stock` y `categoria`; después se crea o modifica un objeto `Producto` y se guarda.
Las escrituras de una venta y sus detalles están dentro de `transaction.atomic()`:
si falla una operación, el grupo completo se revierte. Al guardar un detalle,
su `subtotal` se calcula en `DetallePedido.save()` y el total del pedido se
recalcula con `Sum('subtotal')`.

## Consultas para mostrar en la defensa

1. En `/panel/reportes/`, abre el reporte 9: muestra `Producto.objects.filter(stock__lt=5)`.
2. Abre el reporte 11: usa `Sum('detalles__cantidad')` y ordena para obtener el top 5.
3. Abre el reporte 13: usa `Sum('pedidos__total')` para cada cliente.
4. Crea un producto desde `/panel/productos/` y vuelve al reporte 1 o 9.
5. Abre `/panel/` sin iniciar sesión y demuestra la redirección a `/login/`.
6. Inicia sesión, abre reportes, cierra sesión y repite la URL para demostrar
   que la sesión ya no permite el acceso.

Para comprobar la base utilizada desde el shell:

```python
from django.db import connection
connection.vendor             # 'sqlite'
Producto.objects.count()      # datos persistidos
```
