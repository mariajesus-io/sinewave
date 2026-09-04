import re

html_files = [
    '/home/maria/sinewave/tienda/templates/login.html',
    '/home/maria/sinewave/tienda/templates/registro.html',
    '/home/maria/sinewave/tienda/templates/olvide-contrasena.html'
]

for fpath in html_files:
    with open(fpath, 'r') as f:
        content = f.read()
    
    # Update image source
    content = content.replace("img/logo_wordmark.png", "img/logo_final.png")
    
    with open(fpath, 'w') as f:
        f.write(content)
        
with open('/home/maria/sinewave/tienda/templates/base.html', 'r') as f:
    content = f.read()

# Replace image source globally in base.html
content = content.replace("img/logo_wordmark.png", "img/logo_final.png")

# The navbar logo has style="width: 280px; height: auto; object-fit: contain;"
content = content.replace('style="width: 280px; height: auto; object-fit: contain;"', 'style="width: 180px; height: auto; object-fit: contain;"')

with open('/home/maria/sinewave/tienda/templates/base.html', 'w') as f:
    f.write(content)

