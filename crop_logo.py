from PIL import Image

def crop_transparent(image_path, output_path):
    img = Image.open(image_path).convert("RGBA")
    
    # Get the bounding box of non-transparent pixels
    bbox = img.getbbox()
    
    if bbox:
        cropped_img = img.crop(bbox)
        cropped_img.save(output_path, "PNG")
        print(f"Cropped successfully. Original size: {img.size}, New size: {cropped_img.size}")
    else:
        print("Image is entirely transparent.")

crop_transparent("/home/maria/sinewave/tienda/static/img/logo_final.png", "/home/maria/sinewave/tienda/static/img/logo_cropped.png")
