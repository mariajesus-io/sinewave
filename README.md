# Sinewave Music Pro

Tienda Django con panel administrativo propio en `/panel/`, autenticación de Django,
CRUD de clientes, productos, categorías, marcas y ventas, y 20 reportes hechos con ORM.
La ruta `/admin/` de Django no está habilitada.

## Preparar SQLite

La base de datos se guarda en `db.sqlite3`, en la raíz del proyecto. No necesitas
instalar ni iniciar un servidor de base de datos. El proyecto incluye una base con
datos de ejemplo; `migrate` aplica las migraciones pendientes sin borrar esos datos.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Si necesitas una cuenta de acceso nueva, ejecuta `python manage.py createsuperuser`.
Este comando crea la cuenta, aunque el sitio no usa Django Admin.
Entra a `http://127.0.0.1:8000/login/` y luego a `/panel/`. Las cuentas normales
pueden entrar a la tienda; solo las cuentas con `is_staff=True` acceden al panel.

## Usar el panel

- `/panel/`: resumen.
- `/panel/productos/`, `/panel/categorias/`, `/panel/marcas/`: catálogo.
- `/panel/clientes/`: clientes comerciales. Desactiva clientes desde el formulario
  para conservar el historial de ventas.
- `/panel/pedidos/`: ventas. Al abrir una venta se agregan productos y pagos;
  el total se recalcula al guardar o eliminar detalles.
- `/panel/cuentas/`: cuentas de acceso, solo para superusuarios. La contraseña se
  guarda con el hash de Django.
- `/panel/reportes/`: indicadores y tabla de 20 consultas ORM del caso Tienda.

Los formularios son HTML sencillo. Las vistas leen `request.POST` y guardan con
el ORM de Django, sin `forms.py`. Todos tienen CSRF; la eliminación y el cierre
de sesión requieren POST.
Un usuario sin sesión vuelve a `/login/` al entrar a cualquier ruta protegida.

## Pedidos desde la tienda

El carrito permanece en el navegador hasta confirmar. Al enviar `/checkout/`,
Django exige una cuenta con perfil de cliente activo, comprueba productos y stock
en SQLite y calcula el precio y el despacho desde la base de datos. Guarda el
pedido, sus detalles y un pago pendiente en una transacción, y descuenta el
stock. Un identificador único evita pedidos duplicados al repetir el envío.
`/historial/` muestra únicamente los pedidos de la cuenta autenticada.
No hay pasarela de pago conectada: el pedido se registra pendiente y el pago
debe confirmarse después desde el panel.
Al cancelar o eliminar un pedido creado por el checkout, el panel devuelve sus
unidades al stock; también ajusta la reserva al modificar sus detalles.

## Verificar

```bash
python manage.py check
python manage.py showmigrations tienda
```

La explicación de las consultas se encuentra en [GUIA_EVALUACION_3.md](GUIA_EVALUACION_3.md).
