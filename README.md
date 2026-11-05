# Sinewave Music Pro

Tienda Django con panel administrativo propio en `/panel/`, autenticación de Django,
CRUD de clientes, productos, categorías, marcas y ventas, y 20 reportes hechos con ORM.
La ruta `/admin/` de Django no está habilitada.

## Preparar MySQL local

Instala MySQL 8.4+ o MariaDB 10.11+ y deja el servicio iniciado. En el cliente MySQL,
con una cuenta que pueda crear bases y usuarios, ejecuta:

```sql
CREATE DATABASE sinewave CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sinewave'@'127.0.0.1' IDENTIFIED BY 'elige_una_clave_local';
GRANT ALL PRIVILEGES ON sinewave.* TO 'sinewave'@'127.0.0.1';
FLUSH PRIVILEGES;
```

Copia `.env.example` a `.env.local`, cambia `MYSQL_PASSWORD` y carga las variables
en la terminal. El archivo local está excluido de Git. En esta instalación ya se creó
una `.env.local` con credenciales locales.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
source .env.local
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

`createsuperuser` solo crea la cuenta de acceso; el sitio no usa Django Admin.
Entra a `http://127.0.0.1:8000/login/` y luego a `/panel/`. Las cuentas normales
pueden entrar a la tienda; solo las cuentas con `is_staff=True` acceden al panel.
La cuenta inicial de esta instalación se guarda en `.env.local` como
`SINEWAVE_ADMIN_USERNAME` y `SINEWAVE_ADMIN_PASSWORD`.

En esta instalación, MariaDB guarda sus datos locales en `.mysql-data/`. Si el
servidor local se detiene, puedes iniciarlo desde la raíz del proyecto en una
terminal aparte:

```bash
mariadbd --no-defaults --datadir="$PWD/.mysql-data" --socket=/tmp/sinewave-mysql.sock --port=3306 --bind-address=127.0.0.1 --pid-file=/tmp/sinewave-mysql.pid --tmpdir=/tmp
```

Para los reportes mensuales con zona horaria de Chile, MySQL debe tener cargadas
sus tablas de zonas horarias. En MariaDB local se puede ejecutar:

```bash
mariadb-tzinfo-to-sql /usr/share/zoneinfo | mariadb -u root -p mysql
```

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
en MySQL y calcula el precio y el despacho desde la base de datos. Guarda el
pedido, sus detalles y un pago pendiente en una transacción, y descuenta el
stock. Un identificador único evita pedidos duplicados al repetir el envío.
`/historial/` muestra únicamente los pedidos de la cuenta autenticada.
No hay pasarela de pago conectada: el pedido se registra pendiente y el pago
debe confirmarse después desde el panel.
Al cancelar o eliminar un pedido creado por el checkout, el panel devuelve sus
unidades al stock; también ajusta la reserva al modificar sus detalles.

## Verificar

```bash
source .env.local
python manage.py check
python manage.py test tienda
```

Las pruebas usan una base temporal `test_sinewave`; otorga a la cuenta de desarrollo
permiso sobre ella si MySQL lo solicita. Para probar sin MySQL:

```bash
SINEWAVE_DB_ENGINE=sqlite python manage.py test tienda
```

La explicación de las consultas se encuentra en [GUIA_EVALUACION_3.md](GUIA_EVALUACION_3.md).
