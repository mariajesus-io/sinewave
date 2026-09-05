with open('/home/maria/sinewave/tienda/templates/base.html', 'r') as f:
    content = f.read()

messages_block = """
    <main class="flex-shrink-0">
      <div class="container mt-3">
        {% if messages %}
          {% for message in messages %}
            <div class="alert alert-{{ message.tags|default:'info' }} alert-dismissible fade show shadow-sm" role="alert">
              {{ message }}
              <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
          {% endfor %}
        {% endif %}
      </div>
"""

content = content.replace('<main class="flex-shrink-0">', messages_block)

with open('/home/maria/sinewave/tienda/templates/base.html', 'w') as f:
    f.write(content)
