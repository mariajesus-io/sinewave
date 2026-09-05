import re

with open('/home/maria/sinewave/tienda/templates/pago_exitoso.html', 'r') as f:
    content = f.read()

js = """
{% block extra_js %}
<script>
  // El pago se ha procesado correctamente
  // Limpiamos el carrito local
  localStorage.removeItem('sinewave_cart');
</script>
{% endblock %}
"""

if "{% block extra_js %}" not in content:
    content += js

with open('/home/maria/sinewave/tienda/templates/pago_exitoso.html', 'w') as f:
    f.write(content)
print("Pago exitoso patched")
