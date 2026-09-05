import re

with open('/home/maria/sinewave/tienda/views.py', 'r') as f:
    content = f.read()

# Batería Tama Imperialstar stock: 2 -> 24
content = content.replace('"stock": 2, "imagen": "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7', '"stock": 24, "imagen": "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7')

# Sintetizador Korg Kross stock: 3 -> 15
content = content.replace('"stock": 3, "imagen": "/static/img/prod_korg_kross.png"', '"stock": 15, "imagen": "/static/img/prod_korg_kross.png"')

# Pioneer DDJ-200 stock: 3 -> 18
content = content.replace('"stock": 3, "imagen": "https://images.unsplash.com/photo-1593697821252-0c9137d9fc45', '"stock": 18, "imagen": "https://images.unsplash.com/photo-1593697821252-0c9137d9fc45')

# Audifonos M50x stock: 10 -> 35
content = content.replace('"stock": 10, "imagen": "https://images.unsplash.com/photo-1599669454699-248893623440', '"stock": 35, "imagen": "https://images.unsplash.com/photo-1599669454699-248893623440')

# KRK Rokit 5 stock: 4 -> 20
content = content.replace('"stock": 4, "imagen": "/static/img/prod_krk_rokit.png"', '"stock": 20, "imagen": "/static/img/prod_krk_rokit.png"')

with open('/home/maria/sinewave/tienda/views.py', 'w') as f:
    f.write(content)

print("Stock updated")
