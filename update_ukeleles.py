import re

with open('/home/maria/sinewave/tienda/views.py', 'r') as f:
    content = f.read()

# Update Ukelele Soprano Kala
content = content.replace(
    '{"nombre": "Ukelele Soprano Kala MK-S", "precio": 55000, "stock": 15, "imagen": "https://images.unsplash.com/photo-1574093581484-89c6f5a7b6e0?auto=format&fit=crop&w=500&q=80"}',
    '{"nombre": "Ukelele Soprano Kala MK-S", "precio": 55000, "stock": 15, "imagen": "/static/img/prod_ukelele_soprano.png"}'
)

# Update Ukelele Tenor Fender
content = content.replace(
    '{"nombre": "Ukelele Tenor Fender Venice", "precio": 120000, "stock": 8, "imagen": "https://images.unsplash.com/photo-1501612780327-45045538702b?auto=format&fit=crop&w=500&q=80"}',
    '{"nombre": "Ukelele Tenor Fender Venice", "precio": 120000, "stock": 8, "imagen": "/static/img/prod_ukelele_tenor.png"}'
)

with open('/home/maria/sinewave/tienda/views.py', 'w') as f:
    f.write(content)

print("Ukeleles updated successfully")
