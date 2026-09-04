with open('/home/maria/sinewave/tienda/templates/base.html', 'r') as f:
    content = f.read()

content = content.replace("img/logo_cropped.png", "img/logo_white_cropped.png")
# Update navbar logo style
content = content.replace('style="height: 38px; width: auto; object-fit: contain; margin-top: -5px; margin-bottom: -5px;"', 'style="height: 60px; width: auto; object-fit: contain; margin-top: -5px; margin-bottom: -5px;"')
# Update footer logo style
content = content.replace('style="width: 150px; height: auto; border-radius: 4px;"', 'style="height: 50px; width: auto;"')

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
    c = c.replace("img/logo_cropped.png", "img/logo_white_cropped.png")
    c = c.replace('height: 60px; width: auto; margin-bottom: 15px;', 'height: 100px; width: auto; margin-bottom: 15px;')
    with open(fpath, 'w') as f:
        f.write(c)

