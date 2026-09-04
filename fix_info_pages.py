import re

html_files = [
    '/home/maria/sinewave/tienda/templates/nosotros.html',
    '/home/maria/sinewave/tienda/templates/terminos.html',
    '/home/maria/sinewave/tienda/templates/privacidad.html'
]

for fpath in html_files:
    with open(fpath, 'r') as f:
        content = f.read()
    
    # Replace text-muted and lead with text-white
    content = content.replace('class="text-muted"', 'class="text-white"')
    content = content.replace('class="text-muted mb-4"', 'class="text-white mb-4"')
    content = content.replace('class="lead"', 'class="text-white"')
    
    # Add text-white to plain <p> and <li> tags if not already there
    # It's safer to just inject a CSS block at the top of these pages overriding p, li to be white
    
    # Let's add the block extra_css
    css_override = """{% block extra_css %}
<style>
  p, li, small {
    color: #FFFFFF !important;
  }
</style>
{% endblock %}
"""
    
    # If {% block extra_css %} is not in the file, append it after {% block title %}...
    if "{% block extra_css %}" not in content:
        content = re.sub(r'({% block title %}.*?{% endblock %})', r'\1\n' + css_override, content, flags=re.DOTALL)
    
    with open(fpath, 'w') as f:
        f.write(content)

