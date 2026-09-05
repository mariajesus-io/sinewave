import re

with open('/home/maria/sinewave/tienda/views.py', 'r') as f:
    content = f.read()

# Update Shure SM58
content = content.replace(
    '{"nombre": "Micrófono Dinámico Shure SM58", "precio": 95000, "stock": 0, "imagen": "https://images.unsplash.com/photo-1525926477800-7a3aa30eb2ab?auto=format&fit=crop&w=500&q=80"}',
    '{"nombre": "Micrófono Dinámico Shure SM58", "precio": 95000, "stock": 25, "imagen": "/static/img/prod_shure_sm58.png"}'
)

# Update Focusrite Scarlett
content = content.replace(
    '{"nombre": "Interfaz de Audio Focusrite Scarlett", "precio": 180000, "stock": 0, "imagen": "https://images.unsplash.com/photo-1610931580956-620579e00661?auto=format&fit=crop&w=500&q=80"}',
    '{"nombre": "Interfaz de Audio Focusrite Scarlett", "precio": 180000, "stock": 12, "imagen": "/static/img/prod_focusrite.png"}'
)

with open('/home/maria/sinewave/tienda/views.py', 'w') as f:
    f.write(content)

print("Audio products updated successfully")
