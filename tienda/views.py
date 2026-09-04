from django.shortcuts import render

from django.shortcuts import render

def inicio(request):

    productos_tienda = [
        {"nombre": "Guitarra Eléctrica Fender", "precio": 850000, "stock": 5},
        {"nombre": "Batería Acústica Tama", "precio": 1200000, "stock": 2},
        {"nombre": "Micrófono Shure SM58", "precio": 95000, "stock": 0},
        {"nombre": "Teclado Korg Kross", "precio": 650000, "stock": 3},
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

