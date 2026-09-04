import re

with open('/home/maria/sinewave/tienda/templates/index.html', 'r') as f:
    content = f.read()

replacements = {
    'Bajos': 'https://images.unsplash.com/photo-1485030056468-3820ff9e6e90?auto=format&fit=crop&w=300&q=80',
    'Amplificadores': 'https://images.unsplash.com/photo-1524311583133-705a61bbcc47?auto=format&fit=crop&w=300&q=80',
    'Audio Hogar y Estudio': 'https://images.unsplash.com/photo-1542728928-1413d1894ed1?auto=format&fit=crop&w=300&q=80',
    'Ukeleles': 'https://images.unsplash.com/photo-1512404550810-754f0aeb5a21?auto=format&fit=crop&w=300&q=80',
    'Teclados': 'https://images.unsplash.com/photo-1579737482811-3841a0e70db6?auto=format&fit=crop&w=300&q=80',
    'DJ': 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=300&q=80'
}

for name, url in replacements.items():
    # Find the block for this category:
    # 1. We know it ends with <h6 ...>NAME</h6>
    # 2. It contains <img src="...">
    # We can replace the img src for the block that matches the name.
    
    # regex matches: <img src="[url]" style="..." alt="Categoría"></div>\n              <h6 class="...">NAME</h6>
    pattern = r'(<img src=")[^"]+(" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>\s*<h6 class="[^"]+">)' + re.escape(name) + r'(</h6>)'
    
    def repl(m):
        return m.group(1) + url + m.group(2) + name + m.group(3)
        
    content = re.sub(pattern, repl, content)

with open('/home/maria/sinewave/tienda/templates/index.html', 'w') as f:
    f.write(content)
