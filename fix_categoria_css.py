with open('/home/maria/sinewave/tienda/templates/categoria.html', 'r') as f:
    content = f.read()

# Fix the product image container in categoria.html
old_div = """<div style="height: 200px; overflow: hidden; background: #000;">
              <img src="{{ producto.imagen }}" class="w-100 h-100" style="object-fit: cover; opacity: 0.9;" alt="{{ producto.nombre }}">
            </div>"""
new_div = """<div style="height: 200px; overflow: hidden; background: #fff; display: flex; align-items: center; justify-content: center; padding: 10px;">
              <img src="{{ producto.imagen }}" style="max-width: 100%; max-height: 100%; object-fit: contain;" alt="{{ producto.nombre }}">
            </div>"""
content = content.replace(old_div, new_div)

with open('/home/maria/sinewave/tienda/templates/categoria.html', 'w') as f:
    f.write(content)

with open('/home/maria/sinewave/tienda/templates/index.html', 'r') as f:
    content2 = f.read()

# Fix the mas-vistos image container in index.html
old_mv = """<img src="{{ item.imagen }}" alt="{{ item.nombre }}" style="width: 100%; height: 100%; object-fit: cover; opacity: 0.7; transition: opacity 0.3s;">"""
new_mv = """<div style="width: 100%; height: 100%; background: #fff; display: flex; align-items: center; justify-content: center; padding: 15px;"><img src="{{ item.imagen }}" alt="{{ item.nombre }}" style="width: 100%; height: 100%; object-fit: contain; transition: transform 0.3s;"></div>"""
content2 = content2.replace(old_mv, new_mv)

with open('/home/maria/sinewave/tienda/templates/index.html', 'w') as f:
    f.write(content2)

print("CSS Fixed")
