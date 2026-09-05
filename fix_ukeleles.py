import re

with open('/home/maria/sinewave/tienda/templates/index.html', 'r') as f:
    content = f.read()

target_block = """      <!-- Ukeleles -->
      <div class="col-6 col-md-4 col-lg-2">
        <a href="{% url 'categoria' 'ukeleles' %}" class="text-decoration-none">
          <div class="card border-0 text-center h-100 categoria-tile" style="background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border) !important; transition: all 0.3s;">
            <div class="card-body py-4 px-2">
              <div class="mb-3 mx-auto" style="width: 75px; height: 75px; border-radius: 50%; overflow: hidden; border: 2px solid var(--border); box-shadow: 0 4px 8px rgba(0,0,0,0.5);"><img src="https://images.unsplash.com/photo-1512404550810-754f0aeb5a21?auto=format&fit=crop&w=300&q=80" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>
              <h6 class="fw-bold text-light mb-0" style="font-size: 0.9rem;">Ukeleles</h6>
            </div>
          </div>
        </a>"""

correct_block = """      <!-- Ukeleles -->
      <div class="col-6 col-md-4 col-lg-2">
        <a href="{% url 'categoria' 'ukeleles' %}" class="text-decoration-none">
          <div class="card border-0 text-center h-100 categoria-tile" style="background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border) !important; transition: all 0.3s;">
            <div class="card-body py-4 px-2">
              <div class="mb-3 mx-auto" style="width: 75px; height: 75px; border-radius: 50%; overflow: hidden; border: 2px solid var(--border); box-shadow: 0 4px 8px rgba(0,0,0,0.5);"><img src="{% static 'img/cat_ukeleles.png' %}" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>
              <h6 class="fw-bold text-light mb-0" style="font-size: 0.9rem;">Ukeleles</h6>
            </div>
          </div>
        </a>"""

if target_block in content:
    content = content.replace(target_block, correct_block)
    with open('/home/maria/sinewave/tienda/templates/index.html', 'w') as f:
        f.write(content)
    print("Fixed Ukeleles block")
else:
    print("Block not found precisely")

