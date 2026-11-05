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
