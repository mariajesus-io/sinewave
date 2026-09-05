with open('/home/maria/sinewave/tienda/templates/index.html', 'r') as f:
    content = f.read()

content = content.replace(
    '<p class="small mb-0" style="color: #cbd5e1;">Aprovecha hoy en todo nuestro catálogo disponible.</p>',
    '<p class="small mb-0" style="color: #cbd5e1;">Por compras superiores a $100.000.</p>'
)

with open('/home/maria/sinewave/tienda/templates/index.html', 'w') as f:
    f.write(content)

print("Envios text fixed")
