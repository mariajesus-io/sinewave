import re

with open('/home/maria/sinewave/tienda/templates/index.html', 'r') as f:
    content = f.read()

# Replace Guitarras
content = content.replace('src="https://images.unsplash.com/photo-1516924962500-2b4b3b99ea02?auto=format&fit=crop&w=300&q=80"', 'src="{% static \'img/cat_guitarras.png\' %}"')

# Replace Pianos
content = content.replace('src="https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=300&q=80"', 'src="{% static \'img/cat_pianos.png\' %}"')

# Replace Amplificadores
content = content.replace('src="https://images.unsplash.com/photo-1524311583133-705a61bbcc47?auto=format&fit=crop&w=300&q=80"', 'src="{% static \'img/cat_amplificadores.png\' %}"')

with open('/home/maria/sinewave/tienda/templates/index.html', 'w') as f:
    f.write(content)

print("Images updated successfully")
