from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('terminos/', views.terminos, name='terminos'),
    path('privacidad/', views.privacidad, name='privacidad'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('olvide-contrasena/', views.olvide_contrasena, name='olvide_contrasena'),
    path('carrito/', views.carrito, name='carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('pago-exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('historial/', views.historial, name='historial'),
    path('categoria/<str:slug>/', views.categoria, name='categoria'),
]

