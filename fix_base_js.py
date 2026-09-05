with open('/home/maria/sinewave/tienda/templates/base.html', 'r') as f:
    content = f.read()

new_script = """
<script>
  function addToCart(nombre, precio, imagen, redirectUrl) {
    let cart = JSON.parse(localStorage.getItem('sinewave_cart')) || [];
    
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
    
    // Optional: show a toast or alert, but redirecting to cart is easiest
    if (redirectUrl) {
      window.location.href = redirectUrl;
    }
  }
</script>
</body>
"""

content = content.replace("</body>", new_script)

with open('/home/maria/sinewave/tienda/templates/base.html', 'w') as f:
    f.write(content)
print("Base JS updated")
