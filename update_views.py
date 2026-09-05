import re

with open('/home/maria/sinewave/tienda/views.py', 'r') as f:
    content = f.read()

# Update Korg Kross 2
content = content.replace(
    'https://images.unsplash.com/photo-1595069906974-f370baae6bd5?auto=format&fit=crop&w=500&q=80',
    '/static/img/prod_korg_kross.png'
)

# Update KRK Rokit 5
content = content.replace(
    'https://images.unsplash.com/photo-1565576771691-0d3ee77bbdd1?auto=format&fit=crop&w=500&q=80',
    '/static/img/prod_krk_rokit.png'
)

with open('/home/maria/sinewave/tienda/views.py', 'w') as f:
    f.write(content)

print("Views updated successfully")
