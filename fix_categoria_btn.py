with open('/home/maria/sinewave/tienda/templates/categoria.html', 'r') as f:
    content = f.read()

old_btn = """<a href="{% url 'carrito' %}" class="btn btn-outline-light w-100 mt-auto" style="border-radius: 8px;">Agregar al Carrito</a>"""
new_btn = """<button type="button" onclick="addToCart('{{ producto.nombre|escapejs }}', {{ producto.precio }}, '{{ producto.imagen|escapejs }}', '{% url 'carrito' %}')" class="btn btn-outline-light w-100 mt-auto" style="border-radius: 8px;">Agregar al Carrito</button>"""

content = content.replace(old_btn, new_btn)

with open('/home/maria/sinewave/tienda/templates/categoria.html', 'w') as f:
    f.write(content)

print("Categoria button updated")
