import re

with open('/home/maria/sinewave/tienda/views.py', 'r') as f:
    content = f.read()

# Update Pioneer DDJ-200
content = content.replace(
    'https://images.unsplash.com/photo-1593697821252-0c9137d9fc45?auto=format&fit=crop&w=500&q=80',
    '/static/img/prod_pioneer_ddj200.png'
)

with open('/home/maria/sinewave/tienda/views.py', 'w') as f:
    f.write(content)

print("Pioneer updated successfully")
