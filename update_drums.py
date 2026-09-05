import re

with open('/home/maria/sinewave/tienda/views.py', 'r') as f:
    content = f.read()

# Cajon
content = content.replace(
    '{"nombre": "Cajón Flamenco Meinl", "precio": 95000, "stock": 10, "imagen": "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=500&q=80"}',
    '{"nombre": "Cajón Flamenco Meinl", "precio": 95000, "stock": 10, "imagen": "/static/img/prod_cajon.jpg"}'
)

# Roland
content = content.replace(
    '{"nombre": "Batería Electrónica Roland TD-1K", "precio": 750000, "stock": 5, "imagen": "https://images.unsplash.com/photo-1543791959-12b3f54308ed?auto=format&fit=crop&w=500&q=80"}',
    '{"nombre": "Batería Electrónica Roland TD-1K", "precio": 750000, "stock": 5, "imagen": "/static/img/prod_roland.png"}'
)

with open('/home/maria/sinewave/tienda/views.py', 'w') as f:
    f.write(content)

print("Drums updated successfully")
