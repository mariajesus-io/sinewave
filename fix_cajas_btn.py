with open('/home/maria/sinewave/tienda/templates/cajas_sorpresa.html', 'r') as f:
    content = f.read()

# Box basico
content = content.replace(
    """<a href="{% url 'carrito' %}" class="btn w-100 fw-bold" style="background-color: var(--border); color: #fff; border-radius: 50px;">Agregar Box</a>""",
    """<button onclick="addToCart('Box Básico', 19990, '', '{% url 'carrito' %}')" class="btn w-100 fw-bold" style="background-color: var(--border); color: #fff; border-radius: 50px;">Agregar Box</button>"""
)

# Box Intermedio
content = content.replace(
    """<a href="{% url 'carrito' %}" class="btn btn-primary w-100 fw-bold" style="border-radius: 50px; box-shadow: 0 0 15px rgba(0,162,255,0.4);">Agregar Box</a>""",
    """<button onclick="addToCart('Box Intermedio', 49990, '', '{% url 'carrito' %}')" class="btn btn-primary w-100 fw-bold" style="border-radius: 50px; box-shadow: 0 0 15px rgba(0,162,255,0.4);">Agregar Box</button>"""
)

# Box Premium
content = content.replace(
    """<a href="{% url 'carrito' %}" class="btn w-100 fw-bold" style="background-color: #ffd700; color: #000; border-radius: 50px;">Agregar Box</a>""",
    """<button onclick="addToCart('Box Premium', 99990, '', '{% url 'carrito' %}')" class="btn w-100 fw-bold" style="background-color: #ffd700; color: #000; border-radius: 50px;">Agregar Box</button>"""
)

with open('/home/maria/sinewave/tienda/templates/cajas_sorpresa.html', 'w') as f:
    f.write(content)

print("Cajas buttons updated")
