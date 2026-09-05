with open('/home/maria/sinewave/tienda/templates/categoria.html', 'r') as f:
    content = f.read()

old_div = """<div style="height: 200px; overflow: hidden; background: #fff; display: flex; align-items: center; justify-content: center; padding: 10px;">
              <img src="{{ producto.imagen }}" style="max-width: 100%; max-height: 100%; object-fit: contain;" alt="{{ producto.nombre }}">
            </div>"""
new_div = """<div style="height: 200px; overflow: hidden; background: #fff;">
              <img src="{{ producto.imagen }}" class="w-100 h-100" style="object-fit: cover;" alt="{{ producto.nombre }}">
            </div>"""

content = content.replace(old_div, new_div)

with open('/home/maria/sinewave/tienda/templates/categoria.html', 'w') as f:
    f.write(content)
print("Restored cover for categoria")
