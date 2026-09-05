with open('/home/maria/sinewave/tienda/templates/categoria.html', 'r') as f:
    content = f.read()

old_img_div = """<div style="height: 200px; overflow: hidden; background: #fff;">
              <img src="{{ producto.imagen }}" class="w-100 h-100" style="object-fit: cover;" alt="{{ producto.nombre }}">
            </div>"""

new_img_div = """<div style="height: 200px; overflow: hidden; background: #fff; position: relative;">
              <img src="{{ producto.imagen }}" class="w-100 h-100" style="object-fit: cover;" alt="{{ producto.nombre }}">
              <button onclick="toggleFavorite('{{ producto.nombre|escapejs }}', this)" class="btn btn-sm btn-light shadow-sm position-absolute rounded-circle" style="top: 10px; right: 10px; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; z-index: 10;">
                <i class="bi bi-heart fav-icon" data-name="{{ producto.nombre|escapejs }}" style="color: #dc3545; font-size: 1.1rem;"></i>
              </button>
            </div>"""

content = content.replace(old_img_div, new_img_div)

# Now add the script block at the end
js_script = """
{% block extra_js %}
<script>
  function toggleFavorite(nombre, btnElement) {
    let favs = JSON.parse(localStorage.getItem('sinewave_favs')) || [];
    let icon = btnElement.querySelector('.fav-icon');
    
    if (favs.includes(nombre)) {
      // Remove from favorites
      favs = favs.filter(item => item !== nombre);
      icon.classList.remove('bi-heart-fill');
      icon.classList.add('bi-heart');
    } else {
      // Add to favorites
      favs.push(nombre);
      icon.classList.remove('bi-heart');
      icon.classList.add('bi-heart-fill');
    }
    
    localStorage.setItem('sinewave_favs', JSON.stringify(favs));
  }

  // Set initial state of hearts on page load
  document.addEventListener('DOMContentLoaded', function() {
    let favs = JSON.parse(localStorage.getItem('sinewave_favs')) || [];
    document.querySelectorAll('.fav-icon').forEach(icon => {
      let nombre = icon.getAttribute('data-name');
      if (favs.includes(nombre)) {
        icon.classList.remove('bi-heart');
        icon.classList.add('bi-heart-fill');
      }
    });
  });
</script>
{% endblock %}
"""

if "{% block extra_js %}" not in content:
    content += js_script

with open('/home/maria/sinewave/tienda/templates/categoria.html', 'w') as f:
    f.write(content)

print("Favorites added")
