import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, DetallePedido, Marca, Pago, Pedido, Producto, Rol, Usuario


class PanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser('admin', 'admin@example.com', 'ClaveSegura123!')
        cls.normal = get_user_model().objects.create_user('cliente', 'cliente@example.com', 'ClaveSegura123!')
        cls.rol = Rol.objects.create(nombre='Cliente')
        cls.cliente = Usuario.objects.create(nombre_completo='Ana Pérez', correo='ana@example.com', rol=cls.rol)
        cls.categoria, _ = Categoria.objects.get_or_create(slug='guitarras', defaults={'nombre': 'Guitarras'})
        cls.producto = Producto.objects.create(codigo_sku='G-1', nombre='Guitarra', precio=10000,
                                               stock=3, categoria=cls.categoria)

    def test_login_logout_y_proteccion_de_urls(self):
        for url in [reverse('panel_inicio'), reverse('panel_reportes'),
                    reverse('panel_listado', args=['productos']), reverse('panel_formulario_nuevo', args=['productos'])]:
            self.assertRedirects(self.client.get(url), reverse('login') + '?next=' + url)
        self.assertEqual(self.client.get('/admin/').status_code, 404)
        self.assertEqual(self.client.post(reverse('login'), {'username': 'admin', 'password': 'mal'}).status_code, 200)
        self.assertRedirects(self.client.post(reverse('login'), {'username': 'admin', 'password': 'ClaveSegura123!'}),
                             reverse('panel_inicio'))
        self.assertEqual(self.client.get(reverse('panel_reportes')).status_code, 200)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.client.post(reverse('logout'))
        self.assertRedirects(self.client.get(reverse('panel_reportes')),
                             reverse('login') + '?next=' + reverse('panel_reportes'))

    def test_cliente_autenticado_no_puede_administrar(self):
        self.client.force_login(self.normal)
        self.assertEqual(self.client.get(reverse('panel_inicio')).status_code, 403)
        self.assertEqual(self.client.post(reverse('panel_formulario_nuevo', args=['productos']), {}).status_code, 403)

    def test_registro_crea_cuenta_segura_y_cliente(self):
        response = self.client.post(reverse('registro'), {
            'nombre': 'Luis López', 'correo': 'luis@example.com', 'telefono': '123456',
            'password1': 'NuevaClaveSegura123!', 'password2': 'NuevaClaveSegura123!',
        })
        self.assertRedirects(response, reverse('login'))
        cuenta = get_user_model().objects.get(username='luis@example.com')
        self.assertTrue(cuenta.check_password('NuevaClaveSegura123!'))
        self.assertNotEqual(cuenta.password, 'NuevaClaveSegura123!')
        cliente = Usuario.objects.get(correo='luis@example.com')
        self.assertEqual(cliente.cuenta, cuenta)
        self.assertFalse(cuenta.is_staff)
        self.client.force_login(self.admin)
        self.client.post(reverse('panel_formulario_editar', args=['clientes', cliente.pk]), {
            'nombre_completo': 'Luis López', 'correo': 'luis@example.com', 'rol': cliente.rol_id,
        })
        cuenta.refresh_from_db()
        self.assertFalse(cuenta.is_active)

    def test_crud_y_persistencia_de_producto_y_venta(self):
        self.client.force_login(self.admin)
        create = self.client.post(reverse('panel_formulario_nuevo', args=['productos']), {
            'codigo_sku': 'G-2', 'nombre': 'Bajo', 'precio': '15000', 'stock': '8',
            'categoria': self.categoria.pk,
        })
        self.assertEqual(create.status_code, 302)
        bajo = Producto.objects.get(codigo_sku='G-2')
        self.client.post(reverse('panel_formulario_editar', args=['productos', bajo.pk]), {
            'codigo_sku': 'G-2', 'nombre': 'Bajo eléctrico', 'precio': '16000', 'stock': '7',
            'categoria': self.categoria.pk,
        })
        bajo.refresh_from_db()
        self.assertEqual(bajo.nombre, 'Bajo eléctrico')
        venta = self.client.post(reverse('panel_formulario_nuevo', args=['pedidos']), {
            'usuario': self.cliente.pk, 'estado': 'pagado',
        })
        self.assertEqual(venta.status_code, 302)
        pedido = Pedido.objects.get(usuario=self.cliente)
        self.client.post(reverse('panel_hijo_nuevo', args=[pedido.pk, 'detalles']), {
            'producto': bajo.pk, 'cantidad': 2, 'precio_unitario': '16000',
        })
        pedido.refresh_from_db()
        self.assertEqual(pedido.total, Decimal('32000'))
        detalle = DetallePedido.objects.get(pedido=pedido)
        self.client.post(reverse('panel_hijo_eliminar', args=[pedido.pk, 'detalles', detalle.pk]))
        pedido.refresh_from_db()
        self.assertEqual(pedido.total, 0)
        self.client.post(reverse('panel_eliminar', args=['productos', bajo.pk]))
        self.assertFalse(Producto.objects.filter(pk=bajo.pk).exists())

    def test_cuentas_y_clientes_desactivados(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('panel_formulario_nuevo', args=['cuentas']), {
            'username': 'operador', 'email': 'operador@example.com', 'first_name': 'Operador',
            'last_name': 'Tienda', 'is_staff': 'on', 'is_active': 'on',
            'password1': 'OtraClaveSegura123!', 'password2': 'OtraClaveSegura123!',
        })
        self.assertEqual(response.status_code, 302)
        operador = get_user_model().objects.get(username='operador')
        self.assertTrue(operador.check_password('OtraClaveSegura123!'))
        self.assertTrue(operador.is_staff)
        self.client.post(reverse('panel_formulario_editar', args=['cuentas', operador.pk]), {
            'username': 'operador', 'email': 'operador@example.com', 'first_name': 'Operador',
            'last_name': 'Tienda', 'is_staff': 'on',
        })
        operador.refresh_from_db()
        self.assertFalse(operador.is_active)
        self.client.post(reverse('panel_formulario_editar', args=['clientes', self.cliente.pk]), {
            'nombre_completo': self.cliente.nombre_completo, 'correo': self.cliente.correo,
            'rol': self.rol.pk,
        })
        self.cliente.refresh_from_db()
        self.assertFalse(self.cliente.activo)
        self.assertEqual(self.client.get(reverse('panel_listado', args=['cuentas'])).status_code, 200)
        self.client.force_login(self.normal)
        self.assertEqual(self.client.get(reverse('panel_listado', args=['cuentas'])).status_code, 403)

    def test_todos_los_reportes_y_cifras_orm(self):
        pedido = Pedido.objects.create(usuario=self.cliente, estado='pagado', total=20000)
        DetallePedido.objects.create(pedido=pedido, producto=self.producto, cantidad=2, precio_unitario=10000)
        self.client.force_login(self.admin)
        for n in range(1, 21):
            params = {'reporte': n, 'categoria': self.categoria.pk, 'cliente': self.cliente.pk,
                      'pedido': pedido.pk, 'fecha_inicio': '2020-01-01', 'fecha_fin': '2100-01-01',
                      'fecha': pedido.fecha_creacion.date().isoformat(), 'anio': pedido.fecha_creacion.year,
                      'precio_min': 0, 'precio_max': 1000000}
            response = self.client.get(reverse('panel_reportes'), params)
            self.assertEqual(response.status_code, 200, f'Reporte {n}')
            self.assertTrue(response.context['columnas'], f'Reporte {n} sin columnas')
        response = self.client.get(reverse('panel_reportes'), {'reporte': 10,
            'fecha': pedido.fecha_creacion.date().isoformat()})
        self.assertEqual(response.context['filas'], [[Decimal('20000')]])

    def test_formularios_html_y_filtros_invalidos(self):
        self.client.force_login(self.admin)
        campos = {
            'cuentas': 'username', 'clientes': 'nombre_completo', 'roles': 'nombre',
            'categorias': 'slug', 'marcas': 'nombre', 'productos': 'codigo_sku',
            'pedidos': 'usuario',
        }
        for seccion, campo in campos.items():
            respuesta = self.client.get(reverse('panel_formulario_nuevo', args=[seccion]))
            self.assertEqual(respuesta.status_code, 200)
            self.assertContains(respuesta, f'name="{campo}"')
        pedido = Pedido.objects.create(usuario=self.cliente)
        for tipo, campo in [('detalles', 'cantidad'), ('pagos', 'metodo')]:
            respuesta = self.client.get(reverse('panel_hijo_nuevo', args=[pedido.pk, tipo]))
            self.assertEqual(respuesta.status_code, 200)
            self.assertContains(respuesta, f'name="{campo}"')
        respuesta = self.client.get(reverse('panel_reportes'), {
            'reporte': 3, 'precio_min': '200', 'precio_max': '100',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'El rango de precios no es válido.')

    def test_crud_simple_de_roles_categorias_marcas_y_pagos(self):
        self.client.force_login(self.admin)
        casos = [
            ('roles', Rol, {'nombre': 'Mayorista', 'descripcion': 'Venta por volumen'},
             {'nombre': 'Mayorista VIP', 'descripcion': 'Venta por volumen'}),
            ('categorias', Categoria, {'nombre': 'Categoría prueba 912', 'slug': 'categoria-prueba-912', 'activa': 'on'},
             {'nombre': 'Categoría actualizada 912', 'slug': 'categoria-prueba-912', 'activa': 'on'}),
            ('marcas', Marca, {'nombre': 'Marca demo'}, {'nombre': 'Marca actualizada'}),
        ]
        for seccion, modelo, datos_crear, datos_editar in casos:
            respuesta = self.client.post(reverse('panel_formulario_nuevo', args=[seccion]), datos_crear)
            self.assertEqual(respuesta.status_code, 302, f"{seccion}: {respuesta.context.get('error') if respuesta.context else ''}")
            objeto = modelo.objects.get(nombre=datos_crear['nombre'])
            self.assertEqual(self.client.get(reverse('panel_formulario_editar', args=[seccion, objeto.pk])).status_code, 200)
            respuesta = self.client.post(reverse('panel_formulario_editar', args=[seccion, objeto.pk]), datos_editar)
            self.assertEqual(respuesta.status_code, 302, seccion)
            objeto.refresh_from_db()
            self.assertEqual(objeto.nombre, datos_editar['nombre'])
            self.client.post(reverse('panel_eliminar', args=[seccion, objeto.pk]))
            self.assertFalse(modelo.objects.filter(pk=objeto.pk).exists())
        pedido = Pedido.objects.create(usuario=self.cliente)
        respuesta = self.client.post(reverse('panel_hijo_nuevo', args=[pedido.pk, 'pagos']), {
            'metodo': 'debito', 'estado': 'pendiente',
        })
        self.assertEqual(respuesta.status_code, 302)
        pago = Pago.objects.get(pedido=pedido)
        respuesta = self.client.post(reverse('panel_hijo_editar', args=[pedido.pk, 'pagos', pago.pk]), {
            'metodo': 'credito', 'estado': 'aprobado',
        })
        self.assertEqual(respuesta.status_code, 302)
        pago.refresh_from_db()
        self.assertEqual(pago.estado, 'aprobado')
        self.client.post(reverse('panel_hijo_eliminar', args=[pedido.pk, 'pagos', pago.pk]))
        self.assertFalse(Pago.objects.filter(pk=pago.pk).exists())


class CheckoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cuenta = get_user_model().objects.create_user(
            'compradora', 'compradora@example.com', 'ClaveSegura123!',
        )
        cls.otra_cuenta = get_user_model().objects.create_user(
            'otra', 'otra@example.com', 'ClaveSegura123!',
        )
        rol = Rol.objects.create(nombre='Cliente')
        cls.cliente = Usuario.objects.create(
            nombre_completo='Compradora', correo='compradora@example.com',
            rol=rol, cuenta=cls.cuenta,
        )
        cls.otra_cliente = Usuario.objects.create(
            nombre_completo='Otra', correo='otra@example.com',
            rol=rol, cuenta=cls.otra_cuenta,
        )
        categoria = Categoria.objects.create(nombre='Audio', slug='audio')
        cls.producto = Producto.objects.create(
            codigo_sku='A-1', nombre='Micrófono', precio=10000,
            stock=3, categoria=categoria, es_caja_sorpresa=True,
        )

    def datos_compra(self, token, **cambios):
        datos = {
            'checkout_token': token,
            'carrito': json.dumps([{'id': self.producto.pk, 'qty': 2, 'precio': 1}]),
            'despacho': 'despacho',
            'direccion': 'Av. Providencia 1234',
            'pago': 'transferencia',
        }
        datos.update(cambios)
        return datos

    def test_checkout_persiste_precio_real_stock_entrega_y_pago_pendiente(self):
        self.client.force_login(self.cuenta)
        token = self.client.get(reverse('checkout')).context['checkout_token']
        datos = self.datos_compra(token)
        respuesta = self.client.post(reverse('checkout'), datos)
        pedido = Pedido.objects.get(usuario=self.cliente)
        self.assertRedirects(respuesta, reverse('pedido_confirmado', args=[pedido.pk]),
                             fetch_redirect_response=False)
        self.assertEqual(pedido.total, Decimal('25000'))
        self.assertEqual(pedido.costo_envio, Decimal('5000'))
        self.assertEqual(pedido.direccion_entrega, 'Av. Providencia 1234')
        self.assertEqual(pedido.estado, Pedido.Estado.PENDIENTE)
        detalle = DetallePedido.objects.get(pedido=pedido)
        self.assertEqual(detalle.precio_unitario, Decimal('10000'))
        self.assertEqual(detalle.subtotal, Decimal('20000'))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 1)
        self.assertEqual(Pago.objects.get(pedido=pedido).estado, Pago.Estado.PENDIENTE)
        self.assertContains(self.client.get(reverse('pedido_confirmado', args=[pedido.pk])),
                            "localStorage.removeItem('sinewave_cart')")
        self.assertNotContains(self.client.get(reverse('pedido_confirmado', args=[pedido.pk])),
                               "localStorage.removeItem('sinewave_cart')")

        historial = self.client.get(reverse('historial'))
        self.assertContains(historial, 'Micrófono')
        self.assertContains(historial, '#%s' % pedido.pk)
        self.assertNotContains(historial, '#SW-10294')
        self.assertRedirects(self.client.post(reverse('checkout'), datos),
                             reverse('pedido_confirmado', args=[pedido.pk]))
        self.assertEqual(Pedido.objects.filter(usuario=self.cliente).count(), 1)

    def test_checkout_rechaza_stock_y_datos_invalidos_sin_escribir(self):
        self.client.force_login(self.cuenta)
        token = self.client.get(reverse('checkout')).context['checkout_token']
        respuesta = self.client.post(reverse('checkout'), self.datos_compra(
            token, carrito=json.dumps([{'id': self.producto.pk, 'qty': 4}]),
        ))
        self.assertContains(respuesta, 'Stock insuficiente')
        respuesta = self.client.post(reverse('checkout'), self.datos_compra(
            token, direccion='',
        ))
        self.assertContains(respuesta, 'Indica la dirección')
        respuesta = self.client.post(reverse('checkout'), self.datos_compra(
            token, carrito=json.dumps([{'id': self.producto.pk, 'qty': 1.5}]),
        ))
        self.assertContains(respuesta, 'carrito no es válido')
        self.assertEqual(Pedido.objects.count(), 0)
        self.assertEqual(Pago.objects.count(), 0)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)

    def test_historial_y_confirmacion_solo_muestran_pedidos_propios(self):
        pedido = Pedido.objects.create(usuario=self.otra_cliente, total=10000)
        self.assertRedirects(self.client.get(reverse('historial')),
                             reverse('login') + '?next=' + reverse('historial'))
        self.assertRedirects(self.client.get(reverse('checkout')),
                             reverse('login') + '?next=' + reverse('checkout'))
        self.client.force_login(self.cuenta)
        self.assertEqual(self.client.get(reverse('pedido_confirmado', args=[pedido.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse('historial')).context['pagina'].paginator.count, 0)

    def test_retiro_guarda_total_sin_envio(self):
        self.client.force_login(self.cuenta)
        token = self.client.get(reverse('checkout')).context['checkout_token']
        respuesta = self.client.post(reverse('checkout'), self.datos_compra(
            token, despacho='retiro', direccion='Dirección descartada',
            carrito=json.dumps([{'id': self.producto.pk, 'qty': 1}]),
        ))
        self.assertEqual(respuesta.status_code, 302)
        pedido = Pedido.objects.get(usuario=self.cliente)
        self.assertEqual(pedido.total, Decimal('10000'))
        self.assertEqual(pedido.costo_envio, Decimal('0'))
        self.assertEqual(pedido.direccion_entrega, '')

    def test_catalogo_envia_identificador_real_al_carrito(self):
        for url in (reverse('categoria', args=['audio']), reverse('cajas_sorpresa')):
            respuesta = self.client.get(url)
            self.assertEqual(respuesta.status_code, 200)
            self.assertContains(respuesta, 'addToCart(%s,' % self.producto.pk)

    def test_panel_ajusta_stock_de_pedido_publico_al_cancelar_editar_y_eliminar(self):
        self.client.force_login(self.cuenta)
        token = self.client.get(reverse('checkout')).context['checkout_token']
        self.client.post(reverse('checkout'), self.datos_compra(token))
        pedido = Pedido.objects.get(usuario=self.cliente)
        detalle = DetallePedido.objects.get(pedido=pedido)
        admin = get_user_model().objects.create_superuser(
            'admin_checkout', 'admin_checkout@example.com', 'ClaveSegura123!',
        )
        self.client.force_login(admin)
        self.client.post(reverse('panel_formulario_editar', args=['pedidos', pedido.pk]), {
            'usuario': self.cliente.pk, 'estado': Pedido.Estado.CANCELADO,
        })
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.client.post(reverse('panel_formulario_editar', args=['pedidos', pedido.pk]), {
            'usuario': self.cliente.pk, 'estado': Pedido.Estado.PENDIENTE,
        })
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 1)
        self.client.post(reverse('panel_hijo_editar', args=[pedido.pk, 'detalles', detalle.pk]), {
            'producto': self.producto.pk, 'cantidad': 1, 'precio_unitario': 10000,
        })
        self.producto.refresh_from_db()
        pedido.refresh_from_db()
        self.assertEqual(self.producto.stock, 2)
        self.assertEqual(pedido.total, Decimal('15000'))
        self.client.post(reverse('panel_eliminar', args=['pedidos', pedido.pk]))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.assertFalse(Pedido.objects.filter(pk=pedido.pk).exists())
