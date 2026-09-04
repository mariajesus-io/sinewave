from django.shortcuts import render

from django.shortcuts import render

def inicio(request):

    productos_tienda = [
        {"nombre": "Guitarra Eléctrica Fender Stratocaster", "precio": 850000, "stock": 5},
        {"nombre": "Batería Acústica Tama Imperialstar", "precio": 1200000, "stock": 2},
        {"nombre": "Micrófono Dinámico Shure SM58", "precio": 95000, "stock": 0},
        {"nombre": "Sintetizador Korg Kross 2", "precio": 650000, "stock": 3},
        {"nombre": "Bajo Eléctrico Ibanez SR300", "precio": 450000, "stock": 4},
        {"nombre": "Audífonos de Estudio Audio-Technica M50x", "precio": 150000, "stock": 10},
        {"nombre": "Interfaz de Audio Focusrite Scarlett", "precio": 180000, "stock": 0},
        {"nombre": "Piano Digital Yamaha P-45", "precio": 550000, "stock": 1},
    ]

   
    contexto = {
        "productos": productos_tienda
    }

    return render(request, 'index.html', contexto)


def nosotros(request):
    return render(request, 'nosotros.html')


def terminos(request):
    return render(request, 'terminos.html')


def privacidad(request):
    return render(request, 'privacidad.html')


def login_view(request):
    return render(request, 'login.html')


login = login_view


def registro(request):
    return render(request, 'registro.html')


def olvide_contrasena(request):
    return render(request, 'olvide-contrasena.html')

def carrito(request):
    return render(request, 'carrito.html')

def checkout(request):
    return render(request, 'checkout.html')

def pago_exitoso(request):
    return render(request, 'pago_exitoso.html')

def historial(request):
    return render(request, 'historial.html')


