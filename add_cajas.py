import re

# 1. Update views.py
with open('/home/maria/sinewave/tienda/views.py', 'r') as f:
    views_content = f.read()

new_view = """
def cajas_sorpresa(request):
    return render(request, 'cajas_sorpresa.html')
"""
if "def cajas_sorpresa" not in views_content:
    views_content += new_view
    with open('/home/maria/sinewave/tienda/views.py', 'w') as f:
        f.write(views_content)

# 2. Update urls.py
with open('/home/maria/sinewave/tienda/urls.py', 'r') as f:
    urls_content = f.read()

if "name='cajas_sorpresa'" not in urls_content:
    urls_content = urls_content.replace(
        "path('historial/', views.historial, name='historial'),",
        "path('historial/', views.historial, name='historial'),\n    path('cajas-sorpresa/', views.cajas_sorpresa, name='cajas_sorpresa'),"
    )
    with open('/home/maria/sinewave/tienda/urls.py', 'w') as f:
        f.write(urls_content)

print("urls and views updated")
