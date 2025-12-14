from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

def process_image(image_file, size=(300, 500), target_kb=100, format="WEBP"):
    img = Image.open(image_file)
    img = img.convert("RGBA")
    target_w, target_h = size
    target_ratio = target_w / target_h
    w, h = img.size
    img_ratio = w / h
    if img_ratio > target_ratio:
        new_w = int(target_ratio * h)
        offset = (w - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, h))
    else:
        new_h = int(w / target_ratio)
        offset = (h - new_h) // 2
        img = img.crop((0, offset, w, offset + new_h))
    img = img.resize((target_w, target_h), Image.LANCZOS)

    buffer = BytesIO()
    quality = 90
    while True:
        buffer.seek(0)
        buffer.truncate()
        img.save(buffer, format=format, quality=quality)

        size_kb = buffer.tell() / 1024
        if size_kb <= target_kb or quality <= 30:
            break
        quality -= 10

    buffer.seek(0)
    new_file = InMemoryUploadedFile(
        buffer,
        None,
        f"compressed.{format.lower()}",
        f"image/{format.lower()}",
        buffer.getbuffer().nbytes,
        None
    )
    return new_file
