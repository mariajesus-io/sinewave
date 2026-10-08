from django.contrib import admin

from .models import Categoria, DetallePedido, Pago, Pedido, Producto, Rol, Usuario

# Personalización general del administrador
admin.site.site_header = "Sinewave Music Pro - Administración"
admin.site.site_title = "Sinewave Admin"
admin.site.index_title = "Panel de la tienda"


# @admin.register(Modelo) es lo mismo que admin.site.register(Modelo, ModeloAdmin)
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ["nombre", "descripcion"]   # columnas que se ven en la lista
    search_fields = ["nombre"]                 # caja de búsqueda


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ["nombre_completo", "correo", "telefono", "rol", "activo", "fecha_registro"]
    list_filter = ["rol", "activo", "fecha_registro"]          # filtros de la barra derecha
    search_fields = ["nombre_completo", "correo", "telefono"]
    list_select_related = ["rol"]   # trae el rol en la misma consulta (más rápido)
    list_per_page = 25
    actions = ["activar", "desactivar"]

    @admin.action(description="Activar usuarios seleccionados")
    def activar(self, request, queryset):
        queryset.update(activo=True)

    @admin.action(description="Desactivar usuarios seleccionados")
    def desactivar(self, request, queryset):
        queryset.update(activo=False)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "activa"]
    list_filter = ["activa"]
    search_fields = ["nombre"]


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["codigo_sku", "nombre", "categoria", "precio", "stock", "es_caja_sorpresa"]
    list_filter = ["categoria", "es_caja_sorpresa"]
    search_fields = ["codigo_sku", "nombre"]
    list_editable = ["precio", "stock"]   # se editan directo desde la lista
    list_select_related = ["categoria"]
    list_per_page = 25
    # Organiza el formulario de edición en secciones
    fieldsets = [
        ("Datos básicos", {"fields": ["codigo_sku", "nombre", "descripcion", "categoria"]}),
        ("Precio e inventario", {"fields": ["precio", "stock", "es_caja_sorpresa"]}),
    ]


# Los "inlines" muestran los detalles y pagos DENTRO del formulario del pedido
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    autocomplete_fields = ["producto"]   # buscador en vez de una lista con todos los productos
    readonly_fields = ["subtotal"]


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ["id", "usuario", "fecha_creacion", "estado", "total"]
    list_filter = ["estado", "fecha_creacion"]
    search_fields = ["id", "usuario__nombre_completo", "usuario__correo"]   # "__" busca en el modelo relacionado
    autocomplete_fields = ["usuario"]
    list_select_related = ["usuario"]
    # Navegación por año/mes/día arriba de la lista.
    # Ojo: con 1 millón de pedidos en SQLite tarda ~2 s, porque revisa todas las fechas.
    date_hierarchy = "fecha_creacion"
    list_per_page = 25
    inlines = [DetallePedidoInline, PagoInline]
    readonly_fields = ["total"]
    actions = ["marcar_enviado"]

    def save_related(self, request, form, formsets, change):
        # Después de guardar los detalles, el total se recalcula sumando los subtotales.
        super().save_related(request, form, formsets, change)
        pedido = form.instance
        pedido.total = sum(d.subtotal for d in pedido.detalles.all())
        pedido.save(update_fields=["total"])

    @admin.action(description="Marcar como enviado")
    def marcar_enviado(self, request, queryset):
        queryset.update(estado=Pedido.Estado.ENVIADO)


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ["pedido", "producto", "cantidad", "precio_unitario", "subtotal"]
    search_fields = ["producto__nombre", "producto__codigo_sku"]
    autocomplete_fields = ["pedido", "producto"]
    list_select_related = ["pedido", "producto"]
    readonly_fields = ["subtotal"]
    list_per_page = 25


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ["id", "pedido", "metodo", "estado", "fecha_transaccion"]
    list_filter = ["metodo", "estado", "fecha_transaccion"]
    search_fields = ["pedido__id", "pedido__usuario__correo"]
    autocomplete_fields = ["pedido"]
    list_select_related = ["pedido"]
    list_per_page = 25
