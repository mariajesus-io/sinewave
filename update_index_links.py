with open('/home/maria/sinewave/tienda/templates/index.html', 'r') as f:
    content = f.read()

old_banners = """<!-- BENEFICIOS / PROMOCIONES -->
<section class="container py-5">
  <div class="row g-4 text-center">
    <div class="col-md-4">
      <div class="card text-light border-0 h-100 shadow" style="border-radius: 14px; background: linear-gradient(145deg, var(--primary-light), var(--primary)); border: 1px solid var(--border) !important;">
        <div class="card-body p-4">
          <i class="bi bi-credit-card mb-3 d-block" style="font-size: 2.8rem; color: var(--accent);"></i>
          <h5 class="fw-bold">Paga hasta en 12 pagos</h5>
          <p class="small mb-0" style="color: #cbd5e1;">Sin interés con tarjetas de crédito seleccionadas.</p>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card text-light border-0 h-100 shadow" style="border-radius: 14px; background: linear-gradient(145deg, var(--primary-light), var(--primary)); border: 1px solid var(--border) !important;">
        <div class="card-body p-4">
          <i class="bi bi-truck mb-3 d-block" style="font-size: 2.8rem; color: var(--accent);"></i>
          <h5 class="fw-bold">Envíos Gratis a Todo Chile</h5>
          <p class="small mb-0" style="color: #cbd5e1;">Por compras superiores a $100.000.</p>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card text-light border-0 h-100 shadow" style="border-radius: 14px; background: linear-gradient(145deg, var(--primary-light), var(--primary)); border: 1px solid var(--border) !important;">
        <div class="card-body p-4">
          <i class="bi bi-box-seam mb-3 d-block" style="font-size: 2.8rem; color: var(--accent);"></i>
          <h5 class="fw-bold">Cajas Sorpresa</h5>
          <p class="small mb-0" style="color: #cbd5e1;">Accesorios aleatorios increíbles en cada caja misteriosa.</p>
        </div>
      </div>
    </div>
  </div>
</section>"""

new_banners = """<!-- BENEFICIOS / PROMOCIONES -->
<section class="container py-5">
  <div class="row g-4 text-center">
    <div class="col-md-4">
      <a href="#mas-visto" class="text-decoration-none">
        <div class="card text-light border-0 h-100 shadow promo-card" style="border-radius: 14px; background: linear-gradient(145deg, var(--primary-light), var(--primary)); border: 1px solid var(--border) !important; transition: transform 0.3s, box-shadow 0.3s;" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 10px 20px rgba(0,0,0,0.5)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='';">
          <div class="card-body p-4">
            <i class="bi bi-credit-card mb-3 d-block" style="font-size: 2.8rem; color: var(--accent);"></i>
            <h5 class="fw-bold">Paga hasta en 12 pagos</h5>
            <p class="small mb-0" style="color: #cbd5e1;">Sin interés con tarjetas de crédito seleccionadas.</p>
          </div>
        </div>
      </a>
    </div>
    <div class="col-md-4">
      <a href="#mas-visto" class="text-decoration-none">
        <div class="card text-light border-0 h-100 shadow promo-card" style="border-radius: 14px; background: linear-gradient(145deg, var(--primary-light), var(--primary)); border: 1px solid var(--border) !important; transition: transform 0.3s, box-shadow 0.3s;" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 10px 20px rgba(0,0,0,0.5)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='';">
          <div class="card-body p-4">
            <i class="bi bi-truck mb-3 d-block" style="font-size: 2.8rem; color: var(--accent);"></i>
            <h5 class="fw-bold">Envíos Gratis a Todo Chile</h5>
            <p class="small mb-0" style="color: #cbd5e1;">Aprovecha hoy en todo nuestro catálogo disponible.</p>
          </div>
        </div>
      </a>
    </div>
    <div class="col-md-4">
      <a href="{% url 'cajas_sorpresa' %}" class="text-decoration-none">
        <div class="card text-light border-0 h-100 shadow promo-card" style="border-radius: 14px; background: linear-gradient(145deg, var(--primary-light), var(--primary)); border: 1px solid var(--border) !important; transition: transform 0.3s, box-shadow 0.3s;" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 10px 20px rgba(0,0,0,0.5)'; this.style.borderColor='var(--accent) !important';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow=''; this.style.borderColor='var(--border) !important';">
          <div class="card-body p-4">
            <i class="bi bi-box-seam mb-3 d-block" style="font-size: 2.8rem; color: var(--accent);"></i>
            <h5 class="fw-bold">Cajas Sorpresa</h5>
            <p class="small mb-0" style="color: #cbd5e1;">Accesorios aleatorios increíbles en cada caja misteriosa.</p>
          </div>
        </div>
      </a>
    </div>
  </div>
</section>"""

content = content.replace(old_banners, new_banners)

with open('/home/maria/sinewave/tienda/templates/index.html', 'w') as f:
    f.write(content)

print("Index updated")
