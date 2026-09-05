from django.shortcuts import render

from django.shortcuts import render

CATALOGO = {
    "guitarras": {
        "nombre": "Guitarras",
        "icono": "bi-music-note",
        "productos": [
            {"nombre": "Guitarra Eléctrica Fender Stratocaster", "precio": 850000, "stock": 5, "imagen": "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Guitarra Acústica Yamaha F310", "precio": 180000, "stock": 12, "imagen": "https://images.unsplash.com/photo-1550291652-6ea9114a47b1?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Guitarra Clásica Takamine GN10", "precio": 220000, "stock": 6, "imagen": "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=500&q=80"},
        ]
    },
    "bajos": {
        "nombre": "Bajos",
        "icono": "bi-soundwave",
        "productos": [
            {"nombre": "Bajo Eléctrico Ibanez SR300", "precio": 450000, "stock": 4, "imagen": "https://images.unsplash.com/photo-1550993473-f61b0c036329?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Bajo Fender Precision Bass", "precio": 980000, "stock": 2, "imagen": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=500&q=80"},
        ]
    },
    "ukeleles": {
        "nombre": "Ukeleles",
        "icono": "bi-music-note-beamed",
        "productos": [
            {"nombre": "Ukelele Soprano Kala MK-S", "precio": 55000, "stock": 15, "imagen": "https://images.unsplash.com/photo-1574093581484-89c6f5a7b6e0?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Ukelele Tenor Fender Venice", "precio": 120000, "stock": 8, "imagen": "https://images.unsplash.com/photo-1501612780327-45045538702b?auto=format&fit=crop&w=500&q=80"},
        ]
    },
    "pianos": {
        "nombre": "Pianos",
        "icono": "bi-piano",
        "productos": [
            {"nombre": "Piano Digital Yamaha P-45", "precio": 550000, "stock": 1, "imagen": "https://images.unsplash.com/photo-1552422535-c45813c61732?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Piano Digital Roland FP-30X", "precio": 720000, "stock": 3, "imagen": "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=500&q=80"},
        ]
    },
    "teclados": {
        "nombre": "Teclados",
        "icono": "bi-keyboard",
        "productos": [
            {"nombre": "Sintetizador Korg Kross 2", "precio": 650000, "stock": 15, "imagen": "/static/img/prod_korg_kross.png"},
            {"nombre": "Teclado Arranger Casio CT-S300", "precio": 80000, "stock": 20, "imagen": "/static/img/prod_casio_cts300.png"},
        ]
    },
    "bateria": {
        "nombre": "Batería y Percusión",
        "icono": "bi-grid",
        "productos": [
            {"nombre": "Batería Acústica Tama Imperialstar", "precio": 1200000, "stock": 24, "imagen": "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Batería Electrónica Roland TD-1K", "precio": 750000, "stock": 5, "imagen": "/static/img/prod_roland.png"},
            {"nombre": "Cajón Flamenco Meinl", "precio": 95000, "stock": 10, "imagen": "/static/img/prod_cajon.jpg"},
        ]
    },
    "amplificadores": {
        "nombre": "Amplificadores",
        "icono": "bi-speaker",
        "productos": [
            {"nombre": "Amplificador Fender Champion 20", "precio": 185000, "stock": 7, "imagen": "https://images.unsplash.com/photo-1558098329-a11cff621064?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Amplificador Marshall MG15", "precio": 160000, "stock": 4, "imagen": "https://images.unsplash.com/photo-1588678697769-c48e44a4b3a3?auto=format&fit=crop&w=500&q=80"},
        ]
    },
    "audio-profesional": {
        "nombre": "Audio Profesional",
        "icono": "bi-mic",
        "productos": [
            {"nombre": "Micrófono Dinámico Shure SM58", "precio": 95000, "stock": 25, "imagen": "/static/img/prod_shure_sm58.png"},
            {"nombre": "Interfaz de Audio Focusrite Scarlett", "precio": 180000, "stock": 12, "imagen": "/static/img/prod_focusrite.png"},
            {"nombre": "Monitores de Estudio KRK Rokit 5", "precio": 350000, "stock": 20, "imagen": "/static/img/prod_krk_rokit.png"},
        ]
    },
    "audio-hogar": {
        "nombre": "Audio Hogar y Estudio",
        "icono": "bi-house",
        "productos": [
            {"nombre": "Audífonos de Estudio Audio-Technica M50x", "precio": 150000, "stock": 35, "imagen": "https://images.unsplash.com/photo-1599669454699-248893623440?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Parlante JBL Flip 6", "precio": 95000, "stock": 18, "imagen": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=500&q=80"},
        ]
    },
    "dj": {
        "nombre": "DJ",
        "icono": "bi-disc",
        "productos": [
            {"nombre": "Controladora DJ Pioneer DDJ-200", "precio": 450000, "stock": 18, "imagen": "https://images.unsplash.com/photo-1593697821252-0c9137d9fc45?auto=format&fit=crop&w=500&q=80"},
            {"nombre": "Auriculares DJ Sennheiser HD 25", "precio": 210000, "stock": 6, "imagen": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=500&q=80"},
        ]
    },
}

MAS_VISTOS = [
    {"nombre": "Guitarra Eléctrica Fender Stratocaster", "imagen": "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=500&q=80", "categoria": "guitarras"},
    {"nombre": "Batería Acústica Tama Imperialstar", "imagen": "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=500&q=80", "categoria": "bateria"},
    {"nombre": "Sintetizador Korg Kross 2", "imagen": "/static/img/prod_korg_kross.png", "categoria": "teclados"},
    {"nombre": "Controladora DJ Pioneer DDJ-200", "imagen": "https://images.unsplash.com/photo-1593697821252-0c9137d9fc45?auto=format&fit=crop&w=500&q=80", "categoria": "dj"},
    {"nombre": "Audífonos Audio-Technica M50x", "imagen": "https://images.unsplash.com/photo-1599669454699-248893623440?auto=format&fit=crop&w=500&q=80", "categoria": "audio-hogar"},
    {"nombre": "Monitores KRK Rokit 5", "imagen": "/static/img/prod_krk_rokit.png", "categoria": "audio-profesional"},
]

MARCAS = [
    "Fender", "Yamaha", "Gibson", "Shure", "Roland", "Korg", "Ibanez", 
    "Marshall", "Pioneer", "Audio-Technica", "Tama", "Casio", "JBL", 
    "Focusrite", "Meinl", "Sennheiser", "KRK", "Takamine", "Kala", "Boss"
]

def inicio(request):
    contexto = {
        "categorias_productos": {v["nombre"]: v["productos"] for v in CATALOGO.values()},
        "categorias": CATALOGO,
        "mas_vistos": MAS_VISTOS,
        "marcas": MARCAS,
    }
    return render(request, 'index.html', contexto)


def categoria(request, slug):
    cat = CATALOGO.get(slug)
    if not cat:
        from django.http import Http404
        raise Http404("Categoría no encontrada")
    return render(request, 'categoria.html', {"cat": cat, "slug": slug})


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


