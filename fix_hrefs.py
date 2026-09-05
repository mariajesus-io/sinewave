with open('/home/maria/sinewave/tienda/templates/index.html', 'r') as f:
    content = f.read()

content = content.replace('href="#mas-visto"', 'href="#categorias-grid"')

with open('/home/maria/sinewave/tienda/templates/index.html', 'w') as f:
    f.write(content)

print("Hrefs fixed")
