import re

with open('/home/maria/sinewave/tienda/views.py', 'r') as f:
    content = f.read()

# Update Fender Precision Bass
content = content.replace(
    '{"nombre": "Bajo Fender Precision Bass", "precio": 980000, "stock": 2, "imagen": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=500&q=80"}',
    '{"nombre": "Bajo Fender Precision Bass", "precio": 980000, "stock": 2, "imagen": "/static/img/prod_fender_pbass.png"}'
)

with open('/home/maria/sinewave/tienda/views.py', 'w') as f:
    f.write(content)

print("Fender P-Bass updated successfully")
