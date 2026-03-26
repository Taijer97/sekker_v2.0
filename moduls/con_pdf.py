import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
from moduls.gen import generador

def crear_pdf(imagen1_path, imagen2_path, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    page_width, page_height = letter

    def dibujar_imagen(path, x, y, max_width):
        img = Image.open(path)
        img_width, img_height = img.size

        # Mantener proporción
        ratio = img_height / img_width
        new_width = max_width
        new_height = new_width * ratio

        c.drawImage(path, x, y, width=new_width, height=new_height)

    # Dibujar imágenes centradas
    dibujar_imagen(imagen1_path, x=150, y=page_height - 300, max_width=300)
    dibujar_imagen(imagen2_path, x=150, y=page_height - 600, max_width=300)

    c.save()
    print(f"✅ PDF creado: {output_pdf}")


def generate_pdf(dni):

    base_path = f"data_img/{dni}/img_docs"
    
    img1 = os.path.join(base_path, f"dni_a_f_{dni}.png")
    img2 = os.path.join(base_path, f"dni_a_b_{dni}.png")
    
    output_dir = "dni_pdfs"
    output_pdf = os.path.join(output_dir, f"{dni}.pdf")

    # Crear carpeta de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    crear_pdf(img1, img2, output_pdf)
    return output_pdf

