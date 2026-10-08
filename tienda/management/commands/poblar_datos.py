"""
Genera datos de prueba con Faker.

Uso:
    python manage.py poblar_datos 100
    python manage.py poblar_datos 1000000 --limpiar

Crea la cantidad indicada de usuarios, productos, pedidos, detalles y pagos
(cada pedido trae 1 detalle y 1 pago). Los roles, categorías y marcas son fijos.
Los productos de prueba usan SKU "SKU-...", así --limpiar no borra el catálogo
real de la tienda (SKU "SW-...", cargado por la migración 0005).
"""
import random
import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from faker import Faker

from tienda.models import Categoria, DetallePedido, Marca, Pago, Pedido, Producto, Rol, Usuario

ROLES = ["Cliente", "Vendedor", "Administrador"]
CATEGORIAS = ["Guitarras", "Bajos", "Ukeleles", "Pianos", "Teclados", "Batería y Percusión",
              "Amplificadores", "Audio Profesional", "Audio Hogar y Estudio", "DJ"]
MARCAS = ["Fender", "Yamaha", "Gibson", "Shure", "Roland", "Korg", "Ibanez", "Marshall",
          "Pioneer", "Audio-Technica", "Tama", "Casio", "JBL", "Focusrite", "Meinl"]

LOTE = 5000  # cuántas filas se insertan por consulta


class Command(BaseCommand):
    help = "Llena la base de datos con datos ficticios usando Faker"

    def add_arguments(self, parser):
        parser.add_argument("cantidad", type=int, help="Cantidad de registros por tabla")
        parser.add_argument("--limpiar", action="store_true", help="Borra los datos anteriores antes de cargar")

    def handle(self, *args, **opciones):
        cantidad = opciones["cantidad"]
        self.fake = Faker("es_CL")
        inicio = time.time()

        if opciones["limpiar"]:
            self.limpiar()

        # Roles y categorías: pocos y fijos. get_or_create no los duplica si ya existen.
        roles = [Rol.objects.get_or_create(nombre=n)[0] for n in ROLES]
        categorias = [Categoria.objects.get_or_create(nombre=n)[0] for n in CATEGORIAS]
        marcas = [Marca.objects.get_or_create(nombre=n)[0] for n in MARCAS]

        self.crear_usuarios(cantidad, roles)
        self.crear_productos(cantidad, categorias, marcas)
        self.crear_pedidos(cantidad)

        segundos = time.time() - inicio
        self.stdout.write(self.style.SUCCESS(f"Listo en {segundos:.1f} s"))
        self.stdout.write(
            f"Totales en la BD -> usuarios: {Usuario.objects.count()}, productos: {Producto.objects.count()}, "
            f"pedidos: {Pedido.objects.count()}, detalles: {DetallePedido.objects.count()}, "
            f"pagos: {Pago.objects.count()}"
        )

    def limpiar(self):
        self.stdout.write("Borrando datos anteriores...")
        # Se borra de "hijo" a "padre" para respetar las claves foráneas.
        for qs in [Pago.objects.all(), DetallePedido.objects.all(), Pedido.objects.all(),
                   Producto.objects.filter(codigo_sku__startswith="SKU-"), Usuario.objects.all()]:
            qs._raw_delete(qs.db)  # DELETE directo, rápido con millones de filas

    def siguiente_numero(self, modelo):
        # Número desde donde seguir, para que correos y SKU no se repitan entre cargas.
        return (modelo.objects.aggregate(Max("id"))["id__max"] or 0) + 1

    def fecha_aleatoria(self):
        return timezone.now() - timedelta(days=random.randint(0, 730), seconds=random.randint(0, 86400))

    def crear_usuarios(self, cantidad, roles):
        fake = self.fake
        n = self.siguiente_numero(Usuario)
        for desde in range(0, cantidad, LOTE):
            lote = []
            for _ in range(min(LOTE, cantidad - desde)):
                lote.append(Usuario(
                    nombre_completo=fake.name(),
                    # el número n al final garantiza que el correo sea único
                    correo=f"{fake.user_name()}.{n}@{fake.free_email_domain()}",
                    telefono=fake.phone_number(),
                    fecha_registro=self.fecha_aleatoria(),
                    activo=random.random() < 0.9,
                    rol=random.choices(roles, weights=[90, 8, 2])[0],
                ))
                n += 1
            Usuario.objects.bulk_create(lote)
            self.progreso("Usuarios", desde + len(lote), cantidad)

    def crear_productos(self, cantidad, categorias, marcas):
        fake = self.fake
        n = self.siguiente_numero(Producto)
        for desde in range(0, cantidad, LOTE):
            lote = []
            for _ in range(min(LOTE, cantidad - desde)):
                categoria = random.choice(categorias)
                marca = random.choice(marcas)
                lote.append(Producto(
                    codigo_sku=f"SKU-{n:08d}",
                    nombre=f"{categoria.nombre.split()[0]} {marca.nombre} {fake.bothify('??-###').upper()}",
                    descripcion=fake.sentence(nb_words=12),
                    precio=random.randint(10, 1500) * 1000,
                    stock=random.randint(0, 50),
                    es_caja_sorpresa=random.random() < 0.05,
                    categoria=categoria,
                    marca=marca,
                ))
                n += 1
            Producto.objects.bulk_create(lote)
            self.progreso("Productos", desde + len(lote), cantidad)

    def crear_pedidos(self, cantidad):
        # Se cargan solo los id (y precios) para elegir al azar sin traer objetos completos.
        usuarios_ids = list(Usuario.objects.values_list("id", flat=True))
        productos = list(Producto.objects.values_list("id", "precio"))

        for desde in range(0, cantidad, LOTE):
            tam = min(LOTE, cantidad - desde)
            with transaction.atomic():
                pedidos, detalles, pagos = [], [], []
                for _ in range(tam):
                    producto_id, precio = random.choice(productos)
                    cant = random.randint(1, 5)
                    fecha = self.fecha_aleatoria()
                    pedido = Pedido(
                        usuario_id=random.choice(usuarios_ids),
                        fecha_creacion=fecha,
                        estado=random.choice(Pedido.Estado.values),
                        total=precio * cant,
                    )
                    pedidos.append(pedido)
                    # bulk_create no llama a save(), por eso el subtotal se calcula aquí
                    detalles.append(DetallePedido(pedido=pedido, producto_id=producto_id, cantidad=cant,
                                                  precio_unitario=precio, subtotal=precio * cant))
                    pagos.append(Pago(pedido=pedido, metodo=random.choice(Pago.Metodo.values),
                                      estado=random.choice(Pago.Estado.values), fecha_transaccion=fecha))
                # Primero los pedidos (así obtienen su id), después lo que depende de ellos
                Pedido.objects.bulk_create(pedidos)
                DetallePedido.objects.bulk_create(detalles)
                Pago.objects.bulk_create(pagos)
            self.progreso("Pedidos (+detalle +pago)", desde + tam, cantidad)

    def progreso(self, nombre, hechos, total):
        if hechos == total or hechos % 50000 == 0:
            self.stdout.write(f"  {nombre}: {hechos}/{total}")
