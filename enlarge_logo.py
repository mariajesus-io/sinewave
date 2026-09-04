with open('/home/maria/sinewave/tienda/templates/base.html', 'r') as f:
    content = f.read()

# Increase navbar logo from 60px to 75px
content = content.replace('style="height: 60px; width: auto; object-fit: contain; margin-top: -5px; margin-bottom: -5px;"', 'style="height: 75px; width: auto; object-fit: contain; margin-top: -5px; margin-bottom: -5px;"')
# Increase footer logo from 50px to 60px
content = content.replace('style="height: 50px; width: auto;"', 'style="height: 60px; width: auto;"')

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
    # Increase auth forms logo from 100px to 120px
    c = c.replace('height: 100px; width: auto; margin-bottom: 15px;', 'height: 125px; width: auto; margin-bottom: 20px;')
    with open(fpath, 'w') as f:
        f.write(c)

