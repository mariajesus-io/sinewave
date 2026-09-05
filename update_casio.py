import re

with open('/home/maria/sinewave/tienda/views.py', 'r') as f:
    content = f.read()

# Update Casio CT-S300
content = content.replace(
    '{"nombre": "Teclado Arranger Casio CT-S300", "precio": 80000, "stock": 20, "imagen": "https://images.unsplash.com/photo-1617471346061-5d329ab9c574?auto=format&fit=crop&w=500&q=80"}',
    '{"nombre": "Teclado Arranger Casio CT-S300", "precio": 80000, "stock": 20, "imagen": "/static/img/prod_casio_cts300.png"}'
)

with open('/home/maria/sinewave/tienda/views.py', 'w') as f:
    f.write(content)

print("Casio updated successfully")
