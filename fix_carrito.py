html_content = """{% extends 'base.html' %}

{% block title %}Carrito - Sinewave{% endblock %}

{% block content %}
<div class="container py-5">
  <h2 class="text-center mb-4 text-light">Carrito de Compras</h2>
  
  <div class="row">
    <div class="col-md-8" id="cart-items-container">
      <!-- Items will be injected here via JS -->
      <div class="text-center py-5 text-muted d-none" id="empty-cart-msg">
        <i class="bi bi-cart-x mb-3 d-block" style="font-size: 3rem;"></i>
        <h5>Tu carrito está vacío</h5>
        <a href="{% url 'inicio' %}" class="btn btn-outline-light mt-3">Volver a la tienda</a>
      </div>
    </div>
    
    <div class="col-md-4">
      <div class="card bg-dark text-light border-secondary position-sticky" style="top: 20px;">
        <div class="card-header border-secondary">
          <h5 class="mb-0">Resumen del Pedido</h5>
        </div>
        <div class="card-body">
          <div class="d-flex justify-content-between mb-2">
            <span>Subtotal</span>
            <span id="subtotal">$0</span>
          </div>
          <div class="d-flex justify-content-between mb-3">
            <span>Descuento</span>
            <span>$0</span>
          </div>
          <hr class="border-secondary">
          <div class="d-flex justify-content-between mb-4">
            <strong class="fs-5">Total</strong>
            <strong class="fs-5" style="color: var(--accent);" id="total">$0</strong>
          </div>
          
          <a href="{% url 'login' %}?next={% url 'checkout' %}" class="btn btn-primary w-100 mb-2" id="btn-checkout">Proceder al Pago</a>
          <a href="{% url 'inicio' %}" class="btn btn-outline-secondary w-100 text-light">Seguir Comprando</a>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('cart-items-container');
    const emptyMsg = document.getElementById('empty-cart-msg');
    const subtotalDisplay = document.getElementById('subtotal');
    const totalDisplay = document.getElementById('total');
    const btnCheckout = document.getElementById('btn-checkout');
    
    let cart = JSON.parse(localStorage.getItem('sinewave_cart')) || [];

    function saveCart() {
      localStorage.setItem('sinewave_cart', JSON.stringify(cart));
    }

    function formatMoney(amount) {
      return '$' + amount.toLocaleString('es-CL');
    }

    function renderCart() {
      container.innerHTML = '';
      
      if (cart.length === 0) {
        emptyMsg.classList.remove('d-none');
        container.appendChild(emptyMsg);
        subtotalDisplay.textContent = '$0';
        totalDisplay.textContent = '$0';
        btnCheckout.classList.add('disabled');
        return;
      }
      
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
{% endblock %}
"""

with open('/home/maria/sinewave/tienda/templates/carrito.html', 'w') as f:
    f.write(html_content)

print("Carrito updated")
