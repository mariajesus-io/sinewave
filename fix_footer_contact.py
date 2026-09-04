import re

with open('/home/maria/sinewave/tienda/templates/base.html', 'r') as f:
    content = f.read()

# The original contacto block
old_contacto = """          <div class="col-md-3 mb-3">
            <h6 class="text-white mb-3">Contacto</h6>
            <p class="mb-1 small text-muted">
              <i class="bi bi-envelope me-2"></i>info@sinewave.cl
            </p>
            <p class="small text-muted"><i class="bi bi-telephone me-2"></i>+56 9 1234 5678</p>
          </div>"""

new_contacto = """          <div class="col-md-3 mb-3">
            <h6 class="text-white mb-3">Contacto</h6>
            <p class="mb-1 small text-white">
              <i class="bi bi-envelope me-2"></i>info@sinewave.cl
            </p>
            <p class="mb-1 small text-white">
              <i class="bi bi-telephone me-2"></i>+56 9 1234 5678
            </p>
            <p class="small text-white mb-4">
              <a href="https://instagram.com" target="_blank" class="text-white text-decoration-none hover-accent">
                <i class="bi bi-instagram me-2"></i>@sinewave.music
              </a>
            </p>
            
            <!-- Caja de ayuda rápida WhatsApp -->
            <div class="p-3 rounded" style="background: rgba(37, 211, 102, 0.1); border: 1px solid rgba(37, 211, 102, 0.3);">
              <p class="small text-white mb-2 fw-bold lh-sm">¿No encuentras lo que buscabas?</p>
              <a href="https://wa.me/56912345678" target="_blank" class="btn btn-sm w-100 fw-bold d-flex align-items-center justify-content-center" style="background-color: #25D366; color: white; border-radius: 8px; transition: all 0.3s;">
                <i class="bi bi-whatsapp me-2 fs-5"></i> Escríbenos directo
              </a>
            </div>
          </div>"""

content = content.replace(old_contacto, new_contacto)

# Now inject floating whatsapp button before </body>
floating_wsp = """
    <!-- Botón Flotante WhatsApp -->
    <a href="https://wa.me/56912345678" target="_blank" class="shadow-lg d-flex align-items-center justify-content-center" style="position: fixed; bottom: 30px; right: 30px; width: 60px; height: 60px; background-color: #25D366; color: white; border-radius: 50%; text-decoration: none; z-index: 1000; transition: transform 0.3s;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
      <i class="bi bi-whatsapp" style="font-size: 2rem;"></i>
    </a>
</body>"""

content = content.replace('</body>', floating_wsp)

with open('/home/maria/sinewave/tienda/templates/base.html', 'w') as f:
    f.write(content)

