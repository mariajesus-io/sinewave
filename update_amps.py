import re

with open('/home/maria/sinewave/tienda/views.py', 'r') as f:
    content = f.read()

# Update Fender Amp
content = content.replace(
    '{"nombre": "Amplificador Fender Champion 20", "precio": 185000, "stock": 7, "imagen": "https://images.unsplash.com/photo-1558098329-a11cff621064?auto=format&fit=crop&w=500&q=80"}',
    '{"nombre": "Amplificador Fender Champion 20", "precio": 185000, "stock": 7, "imagen": "/static/img/prod_fender_amp.jpg"}'
)

# Update Marshall Amp
content = content.replace(
    '{"nombre": "Amplificador Marshall MG15", "precio": 160000, "stock": 4, "imagen": "https://images.unsplash.com/photo-1588678697769-c48e44a4b3a3?auto=format&fit=crop&w=500&q=80"}',
    '{"nombre": "Amplificador Marshall MG15", "precio": 160000, "stock": 4, "imagen": "/static/img/prod_marshall.jpg"}'
)

with open('/home/maria/sinewave/tienda/views.py', 'w') as f:
    f.write(content)

print("Amps updated successfully")
