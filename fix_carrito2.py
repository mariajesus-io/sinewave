with open('/home/maria/sinewave/tienda/templates/carrito.html', 'r') as f:
    content = f.read()

# Make sure cart is an array and logic is robust
new_js = """
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('cart-items-container');
    const emptyMsg = document.getElementById('empty-cart-msg');
    const subtotalDisplay = document.getElementById('subtotal');
    const totalDisplay = document.getElementById('total');
    const btnCheckout = document.getElementById('btn-checkout');
    
    let rawCart = localStorage.getItem('sinewave_cart');
    let cart = [];
    try {
      cart = JSON.parse(rawCart) || [];
      if (!Array.isArray(cart)) cart = [];
    } catch (e) {
      cart = [];
    }

    function saveCart() {
      localStorage.setItem('sinewave_cart', JSON.stringify(cart));
    }

    function formatMoney(amount) {
      return '$' + amount.toLocaleString('es-CL');
    }

    function renderCart() {
      // Clear dynamic items, but keep emptyMsg out of it by separating logic
      // First, remove all cards
      const cards = container.querySelectorAll('.card.shadow-sm');
      cards.forEach(c => c.remove());
      
      if (cart.length === 0) {
        emptyMsg.classList.remove('d-none');
        subtotalDisplay.textContent = '$0';
        totalDisplay.textContent = '$0';
        btnCheckout.classList.add('disabled');
        return;
      }
      
      emptyMsg.classList.add('d-none');
      btnCheckout.classList.remove('disabled');
      let total = 0;
      
      cart.forEach((item, index) => {
        total += (item.precio * item.qty);
        
        let itemDiv = document.createElement('div');
        itemDiv.className = 'card bg-dark text-light border-secondary mb-3 shadow-sm';
        itemDiv.innerHTML = `
          <div class="card-body p-3 p-md-4">
            <div class="row align-items-center">
              <div class="col-3 col-md-2 text-center">
                ${item.imagen ? 
                  `<img src="${item.imagen}" class="img-fluid rounded" style="max-height: 80px; object-fit: contain;">` : 
                  `<i class="bi bi-box-seam" style="font-size: 2.5rem; color: var(--accent);"></i>`
                }
              </div>
              <div class="col-9 col-md-4 mb-3 mb-md-0">
                <h6 class="mb-1 fw-bold">${item.nombre}</h6>
                <small class="text-muted">Unidad: ${formatMoney(item.precio)}</small>
              </div>
              <div class="col-6 col-md-3">
                <div class="input-group input-group-sm">
                  <button class="btn btn-outline-secondary btn-minus" data-index="${index}" type="button">-</button>
                  <input type="text" class="form-control text-center bg-dark text-light border-secondary" value="${item.qty}" readonly>
                  <button class="btn btn-outline-secondary btn-plus" data-index="${index}" type="button">+</button>
                </div>
              </div>
              <div class="col-4 col-md-2 text-end">
                <span class="fw-bold" style="color: var(--accent);">${formatMoney(item.precio * item.qty)}</span>
              </div>
              <div class="col-2 col-md-1 text-end">
                <button class="btn btn-sm btn-outline-danger btn-delete" data-index="${index}"><i class="bi bi-trash"></i></button>
              </div>
            </div>
          </div>
        `;
        container.appendChild(itemDiv);
      });
      
      subtotalDisplay.textContent = formatMoney(total);
      totalDisplay.textContent = formatMoney(total);
      
      // Attach events
      document.querySelectorAll('.btn-plus').forEach(btn => {
        btn.addEventListener('click', function() {
          let idx = parseInt(this.getAttribute('data-index'));
          cart[idx].qty += 1;
          saveCart();
          renderCart();
        });
      });
      
      document.querySelectorAll('.btn-minus').forEach(btn => {
        btn.addEventListener('click', function() {
          let idx = parseInt(this.getAttribute('data-index'));
          if (cart[idx].qty > 1) {
            cart[idx].qty -= 1;
          } else {
            cart.splice(idx, 1);
          }
          saveCart();
          renderCart();
        });
      });
      
      document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', function() {
          let idx = parseInt(this.getAttribute('data-index'));
          cart.splice(idx, 1);
          saveCart();
          renderCart();
        });
      });
    }

    renderCart();
  });
</script>
"""

import re
# Replace old script with new script
content = re.sub(r'<script>.*?</script>', new_js, content, flags=re.DOTALL)

with open('/home/maria/sinewave/tienda/templates/carrito.html', 'w') as f:
    f.write(content)

print("Carrito logic patched")
