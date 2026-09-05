import re

with open('/home/maria/sinewave/tienda/templates/base.html', 'r') as f:
    content = f.read()

new_js = """
<script>
  function addToCart(nombre, precio, imagen, redirectUrl) {
    let rawCart = localStorage.getItem('sinewave_cart');
    let cart = [];
    try {
      cart = JSON.parse(rawCart) || [];
      if (!Array.isArray(cart)) cart = [];
    } catch (e) {
      cart = [];
    }
    
    // Check if item exists
    let existingItem = cart.find(item => item.nombre === nombre);
    if (existingItem) {
      existingItem.qty += 1;
    } else {
      cart.push({
        nombre: nombre,
        precio: precio,
        imagen: imagen,
        qty: 1
      });
    }
    
    localStorage.setItem('sinewave_cart', JSON.stringify(cart));
    
    if (redirectUrl) {
      window.location.href = redirectUrl;
    }
  }
</script>
</body>
"""

content = re.sub(r'<script>\s*function addToCart.*?</body>', new_js, content, flags=re.DOTALL)

with open('/home/maria/sinewave/tienda/templates/base.html', 'w') as f:
    f.write(content)

print("Base patched")
