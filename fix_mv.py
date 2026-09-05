with open('/home/maria/sinewave/tienda/templates/index.html', 'r') as f:
    content = f.read()

# Replace the white box with a clean cover or contain
old_mv = """<div style="width: 100%; height: 100%; background: #fff; display: flex; align-items: center; justify-content: center; padding: 15px;"><img src="{{ item.imagen }}" alt="{{ item.nombre }}" style="width: 100%; height: 100%; object-fit: contain; transition: transform 0.3s;"></div>"""
new_mv = """<img src="{{ item.imagen }}" alt="{{ item.nombre }}" style="width: 100%; height: 100%; object-fit: cover; background-color: #fff; transition: transform 0.3s;">"""

content = content.replace(old_mv, new_mv)

with open('/home/maria/sinewave/tienda/templates/index.html', 'w') as f:
    f.write(content)
print("Restored cover for mas vistos")
