# URLs de la app "tienda". Cada path() une una dirección del navegador con una función de views.py.
# El "name" permite usar {% url 'nombre' %} en las plantillas sin escribir la dirección a mano.
from django.urls import path
from . import panel, reportes, views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('terminos/', views.terminos, name='terminos'),
    path('privacidad/', views.privacidad, name='privacidad'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro, name='registro'),
    path('olvide-contrasena/', views.olvide_contrasena, name='olvide_contrasena'),
    path('carrito/', views.carrito, name='carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('pago-exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('historial/', views.historial, name='historial'),
    path('cajas-sorpresa/', views.cajas_sorpresa, name='cajas_sorpresa'),
    path('categoria/<str:slug>/', views.categoria, name='categoria'),
    path('panel/', panel.inicio, name='panel_inicio'),
    path('panel/reportes/', reportes.reportes, name='panel_reportes'),
    path('panel/pedidos/<int:pk>/', panel.pedido, name='panel_pedido'),
    path('panel/pedidos/<int:pedido_id>/<str:tipo>/nuevo/', panel.hijo_formulario, name='panel_hijo_nuevo'),
    path('panel/pedidos/<int:pedido_id>/<str:tipo>/<int:pk>/editar/', panel.hijo_formulario, name='panel_hijo_editar'),
    path('panel/pedidos/<int:pedido_id>/<str:tipo>/<int:pk>/eliminar/', panel.hijo_eliminar, name='panel_hijo_eliminar'),
    path('panel/<str:seccion>/', panel.listado, name='panel_listado'),
    path('panel/<str:seccion>/nuevo/', panel.formulario, name='panel_formulario_nuevo'),
    path('panel/<str:seccion>/<int:pk>/editar/', panel.formulario, name='panel_formulario_editar'),
    path('panel/<str:seccion>/<int:pk>/eliminar/', panel.eliminar, name='panel_eliminar'),
]

