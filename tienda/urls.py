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
]

