import re

with open('/home/maria/sinewave/tienda/templates/index.html', 'r') as f:
    content = f.read()

images = {
    '🎸': 'https://images.unsplash.com/photo-1516924962500-2b4b3b99ea02?auto=format&fit=crop&w=300&q=80',
    '🎵': 'https://images.unsplash.com/photo-1559703248-dcaaec9fac92?auto=format&fit=crop&w=300&q=80',
    '🪗': 'https://images.unsplash.com/photo-1596526131083-e8c633c948d2?auto=format&fit=crop&w=300&q=80',
    '🎹': 'https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=300&q=80',
    '🎼': 'https://images.unsplash.com/photo-1592652684826-b8162d3a39e8?auto=format&fit=crop&w=300&q=80',
    '🥁': 'https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=300&q=80',
    '🔊': 'https://images.unsplash.com/photo-1577714578130-1011eb7c52d8?auto=format&fit=crop&w=300&q=80',
    '🎙️': 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=300&q=80',
    '🎧': 'https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?auto=format&fit=crop&w=300&q=80',
    '🎛️': 'https://images.unsplash.com/photo-1571266028243-3716f02d2d2e?auto=format&fit=crop&w=300&q=80'
}

for emoji, url in images.items():
    pattern = r'<div class="mb-3"[^>]*>' + re.escape(emoji) + r'</div>'
    replacement = f'<div class="mb-3 mx-auto" style="width: 75px; height: 75px; border-radius: 50%; overflow: hidden; border: 2px solid var(--border); box-shadow: 0 4px 8px rgba(0,0,0,0.5);"><img src="{url}" style="width: 100%; height: 100%; object-fit: cover;" alt="Categoría"></div>'
    content = re.sub(pattern, replacement, content)

with open('/home/maria/sinewave/tienda/templates/index.html', 'w') as f:
    f.write(content)

