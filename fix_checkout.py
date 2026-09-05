with open('/home/maria/sinewave/tienda/templates/checkout.html', 'r') as f:
    content = f.read()

new_html = """
{% extends 'base.html' %}

{% block title %}Checkout - Sinewave{% endblock %}

{% block content %}
<div class="container py-5">
  <h2 class="text-center mb-4 text-light">Checkout</h2>
  
  <div class="row">
    <div class="col-md-8">
      <div class="card bg-dark text-light border-secondary mb-4 shadow-sm">
        <div class="card-header border-secondary">
          <h5 class="mb-0">1. Opciones de Despacho y Entrega</h5>
        </div>
        <div class="card-body">
          <div class="form-check mb-2">
            <input class="form-check-input bg-dark border-secondary" type="radio" name="despacho" id="despacho1" checked>
            <label class="form-check-label" for="despacho1">
              Despacho a Domicilio (Starken / Chilexpress) - $5.000
            </label>
          </div>
          <div class="form-check">
            <input class="form-check-input bg-dark border-secondary" type="radio" name="despacho" id="despacho2">
            <label class="form-check-label" for="despacho2">
              Retiro en Tienda (Providencia) - Gratis
            </label>
          </div>
          <hr class="border-secondary">
          <div class="mb-3">
            <label class="form-label">Dirección de Envío</label>
            <input type="text" class="form-control bg-dark text-light border-secondary" placeholder="Ej. Av. Providencia 1234" required>
          </div>
        </div>
      </div>

      <div class="card bg-dark text-light border-secondary shadow-sm">
        <div class="card-header border-secondary">
          <h5 class="mb-0">2. Opciones de Pago</h5>
        </div>
        <div class="card-body">
          <div class="form-check mb-2">
            <input class="form-check-input bg-dark border-secondary" type="radio" name="pago" id="pago1" checked>
            <label class="form-check-label" for="pago1">
              Tarjeta de Crédito / Débito (Webpay)
            </label>
          </div>
          <div class="form-check mb-2">
            <input class="form-check-input bg-dark border-secondary" type="radio" name="pago" id="pago2">
            <label class="form-check-label" for="pago2">
              Transferencia Bancaria
            </label>
          </div>
        </div>
      </div>
    </div>
    
    <div class="col-md-4">
      <div class="card bg-dark text-light border-secondary position-sticky shadow-sm" style="top: 20px;">
        <div class="card-header border-secondary">
          <h5 class="mb-0">Resumen</h5>
        </div>
        <div class="card-body">
          <div id="checkout-items-list" class="mb-3 small">
            <!-- items via JS -->
          </div>
          <hr class="border-secondary">
          <div class="d-flex justify-content-between mb-2">
            <span>Subtotal</span>
            <span id="checkout-subtotal">$0</span>
          </div>
          <div class="d-flex justify-content-between mb-3 text-success">
            <span id="checkout-envio-label">Envío</span>
            <span id="checkout-envio">$5.000</span>
          </div>
          <hr class="border-secondary">
          <div class="d-flex justify-content-between mb-4">
            <strong class="fs-5">Total</strong>
            <strong class="fs-5" style="color: var(--accent);" id="checkout-total">$0</strong>
          </div>
          
          <a href="{% url 'pago_exitoso' %}" class="btn btn-success w-100 mb-2 fw-bold shadow">Confirmar y Realizar Pago</a>
          <button class="btn btn-outline-danger w-100 mt-2" onclick="alert('Pago rechazado por el banco. Intente nuevamente.')">Simular Pago Fallido</button>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
  document.addEventListener('DOMContentLoaded', function() {
    let rawCart = localStorage.getItem('sinewave_cart');
    let cart = [];
    try {
      cart = JSON.parse(rawCart) || [];
      if (!Array.isArray(cart)) cart = [];
    } catch (e) {
      cart = [];
    }
    
    if (cart.length === 0) {
      window.location.href = "{% url 'carrito' %}";
      return;
    }

    const itemsList = document.getElementById('checkout-items-list');
    const subtotalDisplay = document.getElementById('checkout-subtotal');
    const totalDisplay = document.getElementById('checkout-total');
    const envioDisplay = document.getElementById('checkout-envio');
    
    const radioEnvio = document.getElementById('despacho1');
    const radioRetiro = document.getElementById('despacho2');

    function formatMoney(amount) {
      return '$' + amount.toLocaleString('es-CL');
    }

    let subtotal = 0;
    cart.forEach(item => {
      subtotal += (item.precio * item.qty);
      let div = document.createElement('div');
      div.className = 'd-flex justify-content-between text-muted mb-1';
      div.innerHTML = `<span>${item.qty}x ${item.nombre}</span><span>${formatMoney(item.precio * item.qty)}</span>`;
      itemsList.appendChild(div);
    });

    function updateTotal() {
      let envio = radioEnvio.checked ? 5000 : 0;
      // Envíos gratis por más de 100.000
      if (subtotal >= 100000 && radioEnvio.checked) {
        envio = 0;
        envioDisplay.innerHTML = '<span class="badge bg-success">Gratis</span>';
      } else {
        envioDisplay.textContent = formatMoney(envio);
      }
      subtotalDisplay.textContent = formatMoney(subtotal);
      totalDisplay.textContent = formatMoney(subtotal + envio);
    }

    radioEnvio.addEventListener('change', updateTotal);
    radioRetiro.addEventListener('change', updateTotal);
    
    updateTotal();
  });
</script>
{% endblock %}
"""

with open('/home/maria/sinewave/tienda/templates/checkout.html', 'w') as f:
    f.write(new_html)

print("Checkout patched")
