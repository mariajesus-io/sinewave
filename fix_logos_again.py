import re

html_files = [
    '/home/maria/sinewave/tienda/templates/login.html',
    '/home/maria/sinewave/tienda/templates/registro.html',
    '/home/maria/sinewave/tienda/templates/olvide-contrasena.html'
]

for fpath in html_files:
    with open(fpath, 'r') as f:
        content = f.read()
    
    content = content.replace("img/logo2.jpg", "img/logo_wordmark.png")
    content = content.replace("width: 100px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 0 15px rgba(0, 162, 255, 0.2);", "width: 250px; height: auto; margin-bottom: 10px; border-radius: 8px;")
    
    with open(fpath, 'w') as f:
        f.write(content)
        
with open('/home/maria/sinewave/tienda/templates/base.html', 'r') as f:
    content = f.read()

content = content.replace("img/logo2.jpg", "img/logo_wordmark.png")
content = content.replace('style="width: 30px; border-radius: 4px; margin-right: 5px;"> SineWave', 'style="width: 150px; height: auto; border-radius: 4px;">')

with open('/home/maria/sinewave/tienda/templates/base.html', 'w') as f:
    f.write(content)

