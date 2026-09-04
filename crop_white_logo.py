from PIL import Image

def crop_transparent(image_path, output_path):
    img = Image.open(image_path).convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        cropped_img = img.crop(bbox)
        cropped_img.save(output_path, "PNG")
        print(f"Cropped successfully. Original size: {img.size}, New size: {cropped_img.size}")
    else:
        print("Image is entirely transparent.")

crop_transparent("/home/maria/sinewave/tienda/static/img/logo_white.png", "/home/maria/sinewave/tienda/static/img/logo_white_cropped.png")
