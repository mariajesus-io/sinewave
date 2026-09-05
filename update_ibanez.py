import re

with open('/home/maria/sinewave/tienda/views.py', 'r') as f:
    content = f.read()

# Update Ibanez SR300
content = content.replace(
    '{"nombre": "Bajo Eléctrico Ibanez SR300", "precio": 450000, "stock": 4, "imagen": "https://images.unsplash.com/photo-1550993473-f61b0c036329?auto=format&fit=crop&w=500&q=80"}',
    '{"nombre": "Bajo Eléctrico Ibanez SR300", "precio": 450000, "stock": 4, "imagen": "/static/img/prod_ibanez_sr300.png"}'
)

with open('/home/maria/sinewave/tienda/views.py', 'w') as f:
    f.write(content)

print("Ibanez updated successfully")
