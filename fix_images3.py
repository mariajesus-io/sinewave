with open('/home/maria/sinewave/tienda/templates/index.html', 'r') as f:
    c = f.read()

c = c.replace(
    '<img src="https://images.unsplash.com/photo-1596526131083-e8c633c948d2?auto=format&fit=crop&w=300&q=80" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>\n              <h6 class="fw-bold text-light mb-0" style="font-size: 0.9rem;">Ukeleles</h6>',
    '<img src="https://images.unsplash.com/photo-1512404550810-754f0aeb5a21?auto=format&fit=crop&w=300&q=80" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>\n              <h6 class="fw-bold text-light mb-0" style="font-size: 0.9rem;">Ukeleles</h6>'
)

c = c.replace(
    '<img src="https://images.unsplash.com/photo-1592652684826-b8162d3a39e8?auto=format&fit=crop&w=300&q=80" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>\n              <h6 class="fw-bold text-light mb-0" style="font-size: 0.9rem;">Teclados</h6>',
    '<img src="https://images.unsplash.com/photo-1579737482811-3841a0e70db6?auto=format&fit=crop&w=300&q=80" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>\n              <h6 class="fw-bold text-light mb-0" style="font-size: 0.9rem;">Teclados</h6>'
)

c = c.replace(
    '<img src="https://images.unsplash.com/photo-1577714578130-1011eb7c52d8?auto=format&fit=crop&w=300&q=80" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>\n              <h6 class="fw-bold text-light mb-0" style="font-size: 0.9rem;">Amplificadores</h6>',
    '<img src="https://images.unsplash.com/photo-1524311583133-705a61bbcc47?auto=format&fit=crop&w=300&q=80" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>\n              <h6 class="fw-bold text-light mb-0" style="font-size: 0.9rem;">Amplificadores</h6>'
)

c = c.replace(
    '<img src="https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?auto=format&fit=crop&w=300&q=80" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>\n              <h6 class="fw-bold text-light mb-0" style="font-size: 0.9rem;">Audio Hogar y Estudio</h6>',
    '<img src="https://images.unsplash.com/photo-1542728928-1413d1894ed1?auto=format&fit=crop&w=300&q=80" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>\n              <h6 class="fw-bold text-light mb-0" style="font-size: 0.9rem;">Audio Hogar y Estudio</h6>'
)

c = c.replace(
    '<img src="https://images.unsplash.com/photo-1571266028243-3716f02d2d2e?auto=format&fit=crop&w=300&q=80" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>\n              <h6 class="fw-bold text-light mb-0" style="font-size: 0.9rem;">DJ</h6>',
    '<img src="https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=300&q=80" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>\n              <h6 class="fw-bold text-light mb-0" style="font-size: 0.9rem;">DJ</h6>'
)

with open('/home/maria/sinewave/tienda/templates/index.html', 'w') as f:
    f.write(c)

