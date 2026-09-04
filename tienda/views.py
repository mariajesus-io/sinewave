from django.shortcuts import render

from django.shortcuts import render

def inicio(request):

    categorias_productos = {
        "Guitarras y Bajos": [
            {"nombre": "Guitarra Eléctrica Fender Stratocaster", "precio": 850000, "stock": 5, "imagen": "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Bajo Eléctrico Ibanez SR300", "precio": 450000, "stock": 4, "imagen": "https://images.unsplash.com/photo-1550993473-f61b0c036329?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Guitarra Acústica Yamaha F310", "precio": 180000, "stock": 12, "imagen": "https://images.unsplash.com/photo-1550291652-6ea9114a47b1?auto=format&fit=crop&w=500&q=80"}
        ],
        "Teclados": [
            {"nombre": "Sintetizador Korg Kross 2", "precio": 650000, "stock": 3, "imagen": "https://images.unsplash.com/photo-1595069906974-f370baae6bd5?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Piano Digital Yamaha P-45", "precio": 550000, "stock": 1, "imagen": "https://images.unsplash.com/photo-1552422535-c45813c61732?auto=format&fit=crop&w=500&q=80"}
        ],
        "Baterías y Percusión": [
            {"nombre": "Batería Acústica Tama Imperialstar", "precio": 1200000, "stock": 2, "imagen": "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Batería Electrónica Roland TD-1K", "precio": 750000, "stock": 5, "imagen": "https://images.unsplash.com/photo-1543791959-12b3f54308ed?auto=format&fit=crop&w=500&q=80"}
        ],
        "Audio Profesional": [
            {"nombre": "Micrófono Dinámico Shure SM58", "precio": 95000, "stock": 0, "imagen": "https://images.unsplash.com/photo-1525926477800-7a3aa30eb2ab?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Audífonos de Estudio Audio-Technica M50x", "precio": 150000, "stock": 10, "imagen": "https://images.unsplash.com/photo-1599669454699-248893623440?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Interfaz de Audio Focusrite Scarlett", "precio": 180000, "stock": 0, "imagen": "https://images.unsplash.com/photo-1610931580956-620579e00661?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Monitores de Estudio KRK Rokit 5", "precio": 350000, "stock": 4, "imagen": "https://images.unsplash.com/photo-1565576771691-0d3ee77bbdd1?auto=format&fit=crop&w=500&q=80"}
        ]
    }
   
    contexto = {
        "categorias_productos": categorias_productos
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


