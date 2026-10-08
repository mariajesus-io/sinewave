from django.db import models
from django.utils import timezone

# Nota: Django crea automáticamente la clave primaria "id" en cada modelo,
# por eso no la escribimos. Y cada ForeignKey se guarda en la tabla como
# "<nombre>_id" (por ejemplo: rol -> rol_id).


class Rol(models.Model):
    """Tipo de usuario: Cliente, Vendedor, Administrador..."""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "rol"
        verbose_name_plural = "roles"

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    """Cliente de la tienda (no es el usuario que entra al admin)."""
    nombre_completo = models.CharField(max_length=150)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    # Campos agregados después (migración 0002) para mostrar cómo se modifica un modelo.
    # db_index (migración 0003) hace que ordenar y filtrar por fecha sea rápido con muchos datos.
    fecha_registro = models.DateTimeField(default=timezone.now, db_index=True)
    activo = models.BooleanField(default=True)
    # Un rol tiene muchos usuarios (1 a N). PROTECT: no deja borrar un rol en uso.
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name="usuarios")

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ["-fecha_registro"]

    def __str__(self):
        return self.nombre_completo


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    codigo_sku = models.CharField("código SKU", max_length=30, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0)  # pesos chilenos, sin decimales
    stock = models.PositiveIntegerField(default=0)
    es_caja_sorpresa = models.BooleanField(default=False)
    # Una categoría tiene muchos productos (1 a N).
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="productos")

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def __str__(self):
        return f"{self.nombre} ({self.codigo_sku})"


class Pedido(models.Model):
    # "choices" limita los valores posibles y en el admin aparece como lista desplegable.
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        PAGADO = "pagado", "Pagado"
        ENVIADO = "enviado", "Enviado"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    fecha_creacion = models.DateTimeField(default=timezone.now, db_index=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    total = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    # Un usuario tiene muchos pedidos (1 a N). CASCADE: si se borra el usuario, se borran sus pedidos.
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="pedidos")

    class Meta:
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Pedido #{self.pk}"


class DetallePedido(models.Model):
    """Cada línea del carrito/pedido: qué producto, cuántos y a qué precio."""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="detalles")
    cantidad = models.PositiveIntegerField(default=1)
    # Se guarda el precio del momento de la compra, porque el precio del producto puede cambiar.
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, editable=False)

    class Meta:
        verbose_name = "detalle de pedido"
        verbose_name_plural = "detalles de pedido"

    def save(self, *args, **kwargs):
        # El subtotal siempre se calcula solo, así nunca queda mal.
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class Pago(models.Model):
    class Metodo(models.TextChoices):
        DEBITO = "debito", "Débito"
        CREDITO = "credito", "Crédito"
        TRANSFERENCIA = "transferencia", "Transferencia"

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        APROBADO = "aprobado", "Aprobado"
        RECHAZADO = "rechazado", "Rechazado"

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="pagos")
    metodo = models.CharField(max_length=20, choices=Metodo.choices)
    fecha_transaccion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)

    class Meta:
        verbose_name = "pago"
        verbose_name_plural = "pagos"

    def __str__(self):
        return f"Pago #{self.pk} - {self.get_estado_display()}"
