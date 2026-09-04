with open('/home/maria/sinewave/tienda/templates/base.html', 'r') as f:
    content = f.read()

content = content.replace("img/logo_final.png", "img/logo_cropped.png")
content = content.replace('style="width: 180px; height: auto; object-fit: contain;"', 'style="height: 38px; width: auto; object-fit: contain; margin-top: -5px; margin-bottom: -5px;"')

with open('/home/maria/sinewave/tienda/templates/base.html', 'w') as f:
    f.write(content)

html_files = [
    '/home/maria/sinewave/tienda/templates/login.html',
    '/home/maria/sinewave/tienda/templates/registro.html',
    '/home/maria/sinewave/tienda/templates/olvide-contrasena.html'
]

for fpath in html_files:
    with open(fpath, 'r') as f:
        c = f.read()
    c = c.replace("img/logo_final.png", "img/logo_cropped.png")
    c = c.replace('width: 250px; height: auto; margin-bottom: 10px; border-radius: 8px;', 'height: 60px; width: auto; margin-bottom: 15px;')
    with open(fpath, 'w') as f:
        f.write(c)

