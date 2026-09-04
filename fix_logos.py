import re
import glob

html_files = [
    '/home/maria/sinewave/tienda/templates/login.html',
    '/home/maria/sinewave/tienda/templates/registro.html',
    '/home/maria/sinewave/tienda/templates/olvide-contrasena.html'
]

replacement = """        <a href="{% url 'inicio' %}" class="text-decoration-none">
          <img src="{% static 'img/logo2.jpg' %}" alt="SineWave Logo" style="width: 100px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 0 15px rgba(0, 162, 255, 0.2);">
        </a>"""

for fpath in html_files:
    with open(fpath, 'r') as f:
        content = f.read()
    
    # We want to replace everything from <a href="{% url 'inicio' %}" class="text-decoration-none"> to </a> before <p class="text-muted">
    # regex: <a href="{% url 'inicio' %}" class="text-decoration-none">.*?</a>\s*<p class="text-muted">
    pattern = r'<a href="{% url \'inicio\' %}" class="text-decoration-none">.*?</a>\s*(?=<p class="text-muted">)'
    content = re.sub(pattern, replacement + '\n        ', content, flags=re.DOTALL)
    
    with open(fpath, 'w') as f:
        f.write(content)

