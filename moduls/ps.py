from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageEnhance
from moduls.gen import generador
from moduls.fund_n import formatear_nombre, generar_mrz_peru, convertir_fecha, validar_dni_peru_definitivo
from datetime import datetime
import math
import os

psd = PSDImage.open("plantillas/dni_a_f.psd")
psd2 = PSDImage.open("plantillas/dni_a_b.psd")


def convertir_a_negro(img):
    img = img.convert("RGBA")
    data = img.getdata()

    nueva = []
    for r, g, b, a in data:
        if a == 0:
            # mantener transparencia
            nueva.append((0, 0, 0, 0))
        else:
            # todo lo visible → negro sólido
            nueva.append((0, 0, 0, 255))

    img.putdata(nueva)
    return img

def _resolve_dni_data(dni, data=None):
    if data is not None:
        return data

    payload = generador(dni)
    if not isinstance(payload, dict):
        return None

    lista = payload.get("listaAni")
    if isinstance(lista, list) and len(lista) > 0 and isinstance(lista[0], dict):
        return lista[0]

    return None


def get_text_width_tracking(texto, font, tracking):
    total = 0
    stroke = 1

    for char in texto:
        bbox = font.getbbox(char)
        w = bbox[2] - bbox[0]
        total += w + tracking + stroke

    return total - tracking

def convertir_fecha(fecha_str):
    # Convertir string a fecha (formato día/mes/año)
    fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
    
    # Convertir a formato YYMMDD
    return fecha.strftime("%y%m%d")

def formatear_nombre(apellido, nombre, longitud_total=30):
    texto = f"{apellido.upper()}<<{nombre.upper()}"
    if len(texto) > longitud_total:
        texto = texto[:longitud_total]
    texto = texto.ljust(longitud_total, "<")
    return texto

def draw_text_tracking(draw, texto, x, y, font, fill, stroke_fill, tracking=0):

    cx = x
    stroke = 1

    for char in texto:

        # stroke
        for dx in range(-stroke, stroke+1):
            for dy in range(-stroke, stroke+1):
                if dx*dx + dy*dy <= stroke*stroke:
                    draw.text(
                        (cx + dx, y + dy),
                        char,
                        font=font,
                        fill=stroke_fill
                    )

        # texto
        draw.text((cx, y), char, font=font, fill=fill)

        bbox = font.getbbox(char)
        w = bbox[2] - bbox[0]

        cx += w + tracking + stroke

def draw_text_rotado_tracking(base_img, texto, x, y, font, fill, stroke_fill, angle, tracking=0):

    total_width = 0
    heights = []
    stroke = 1

    for char in texto:
        bbox = font.getbbox(char)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        total_width += w + tracking + stroke
        heights.append(h)

    total_width -= tracking
    max_height = max(heights)

    padding = 30

    temp = Image.new(
        "RGBA",
        (total_width + padding*2, max_height + padding*2),
        (0, 0, 0, 0)
    )

    draw_temp = ImageDraw.Draw(temp)

    cx = padding
    cy = padding

    for char in texto:

        # 🔥 stroke exterior
        for dx in range(-stroke, stroke+1):
            for dy in range(-stroke, stroke+1):
                if dx*dx + dy*dy <= stroke*stroke:
                    draw_temp.text(
                        (cx + dx, cy + dy),
                        char,
                        font=font,
                        fill=stroke_fill
                    )

        # 🔥 texto principal
        draw_temp.text((cx, cy), char, font=font, fill=fill)

        bbox = font.getbbox(char)
        w = bbox[2] - bbox[0]

        cx += w + tracking + stroke

    # 🔥 rotación limpia
    temp = temp.rotate(angle, resample=Image.NEAREST, expand=True)

    px = x - temp.width // 2
    py = y - temp.height // 2

    base_img.paste(temp, (px, py), temp)

    return base_img

def gen_dni_f(dni, data=None):
    data = _resolve_dni_data(dni, data)
    if not data:
        print(f"Error: No se pudo generar el DNI para {dni}")
        return None

    fo = data["feNacimiento"]
    ff = fo.replace("/", " ")
    io = data["feInscripcion"]
    fi = io.replace("/", " ")
    fe = data["feEmision"].replace("/", " ")
    fc = data["feCaducidad"].replace("/", " ")
    genero = "M" if data["sexo"] == "MASCULINO" else "F"

    if data["estadoCivil"] == "SOLTERO":
        ec = "S"
    elif data["estadoCivil"] == "CASADO":
        ec = "C"
    else:
        ec = "V"

    dv = data["digitoVerificacion"]

    nombres = data["preNombres"]

    primer_nombre = nombres.strip().split()[0]

    nf = formatear_nombre(data["apePaterno"], primer_nombre)

    fff = convertir_fecha(fo)
    vf = convertir_fecha(data["feCaducidad"])

    f1, f2 = generar_mrz_peru(dni, fff, genero, vf)

    layers = list(psd.descendants())

    img_layer = None
    img_small_layer = None
    text_layers = {}
    firma_layer = None

    TEXTOS = {
        "primer apellido": data["apePaterno"],
        "SEGUNDO APELLIDO": data["apeMaterno"],
        "pre nombres": data["preNombres"],
        "NACIMIENTO": ff,
        "UBIGEO": data["UbigeoReniec"],
        "SEXO": genero,
        "ESTADO CIVIL": ec,
        "fecha inscripcion": fi,
        "fecha EMISION": fe,
        "fecha caducidad": fc,
        "71525264": dni,
        "dni nro": dni,
        "dig-verific": f"- {dv}",
        "TEXTO ABAJO1": f1,
        "TEXTO ABAJO2": f2,
        "TEXTO ABAJO3": nf,
        "NOMBRECITO": data["apePaterno"],
    }

    TRACKING = {
        "primer apellido": -1,
        "SEGUNDO APELLIDO":-1,
        "pre nombres": -1,
        "NACIMIENTO": 1,
        "UBIGEO": 2,
        "SEXO": 0,
        "ESTADO CIVIL": 0,
        "fecha inscripcion": 0,
        "fecha EMISION": 0,
        "fecha caducidad": 0,
        "71525264": 0,
        "dni nro": 28,
        "dig-verific": 0,
        "TEXTO ABAJO1": -1.5,
        "TEXTO ABAJO2": -1.5,
        "TEXTO ABAJO3": -1.5,
        "NOMBRECITO": 0,
    }

    for i, layer in enumerate(layers):

        if layer.name == "IM.GRANDE":
            img_layer = (i, layer)

        if layer.name == "IM.PEQUEÑA":
            img_small_layer = layer

        if layer.name == "firma": 
            firma_layer = layer

        if layer.name in TEXTOS:
            text_layers[layer.name] = layer

    if not img_layer or not text_layers:
        return

    index, layer_target = img_layer
    x1, y1, x2, y2 = layer_target.bbox

    for l in layers[index:]:
        l.visible = False
    fondo = psd.composite()

    for l in layers:
        l.visible = True

    for l in layers[:index+1]:
        l.visible = False

    if firma_layer:
        firma_layer.visible = False

    if img_small_layer:
        img_small_layer.visible = False

    overlay = psd.composite()

    for l in layers:
        l.visible = True

    nueva = Image.open(f"data_img/{dni}/foto.png")
    nueva = quitar_fondo_blanco(nueva, tolerancia=210)
    nueva = nueva.resize((x2 - x1, y2 - y1))

    resultado = fondo.copy()
    resultado.paste(nueva, (x1, y1), nueva)

    if firma_layer:

        fx1, fy1, fx2, fy2 = firma_layer.bbox

        firma = Image.open(f"data_img/{dni}/firma.png")
        firma = quitar_fondo_blanco(firma, tolerancia=230)
        firma = firma.convert("RGBA")

        scale = 2.0

        w = int((fx2 - fx1) * scale)
        h = int((fy2 - fy1) * scale)

        firma = firma.resize((w, h))

        offset_x = -110
        offset_y = -20

        px = fx1 + ((fx2 - fx1) - firma.width) // 2 + offset_x
        py = fy1 + ((fy2 - fy1) - firma.height) // 2 + offset_y

        resultado.paste(firma, (px, py), firma)

    if img_small_layer:

        sx1, sy1, sx2, sy2 = img_small_layer.bbox

        foto_small = Image.open(f"data_img/{dni}/foto.png")

        foto_small = foto_small.convert("L")

        enhancer = ImageEnhance.Contrast(foto_small)
        foto_small = enhancer.enhance(1.8)

        foto_small = foto_small.resize((sx2 - sx1, sy2 - sy1))

        foto_small = foto_small.convert("RGB")

        base = resultado.crop((sx1, sy1, sx2, sy2)).convert("RGB")

        combinado = ImageChops.multiply(base, foto_small)

        resultado.paste(combinado, (sx1, sy1))

    resultado = Image.alpha_composite(
        resultado.convert("RGBA"),
        overlay.convert("RGBA")
    )

    draw = ImageDraw.Draw(resultado)

    OFFSETS = {
        "primer apellido": (-2, -8),
        "SEGUNDO APELLIDO": (-1, -8),
        "pre nombres": (0, -8),
        "NACIMIENTO": (-2, -5),
        "UBIGEO": (-2, -5),
        "SEXO": (-2, -5),
        "ESTADO CIVIL": (0, -5),
        "fecha inscripcion": (-2, -10),
        "fecha EMISION":(-2, -6),
        "fecha caducidad": (-2, -7),
        "71525264": (-3, -9),
        "dni nro": (45, 2),
        "dig-verific": (0, -11),
        "TEXTO ABAJO1": (-14, 1),
        "TEXTO ABAJO2": (-7, 0),
        "TEXTO ABAJO3": (-11, -1),
        "NOMBRECITO": (1, -20),
    }

    FONTS = {
        "primer apellido": ImageFont.truetype("arial.ttf", 39),
        "SEGUNDO APELLIDO": ImageFont.truetype("arial.ttf", 39),
        "pre nombres": ImageFont.truetype("arial.ttf", 39),
        "NACIMIENTO": ImageFont.truetype("arial.ttf", 35),
        "UBIGEO": ImageFont.truetype("arial.ttf", 35),
        "SEXO": ImageFont.truetype("arial.ttf", 34),
        "ESTADO CIVIL": ImageFont.truetype("arial.ttf", 34),
        "fecha inscripcion": ImageFont.truetype("arial.ttf", 41),
        "fecha EMISION": ImageFont.truetype("arial.ttf", 41),
        "fecha caducidad": ImageFont.truetype("arialbd.ttf", 41),
        "71525264": ImageFont.truetype("arial.ttf", 65),
        "dni nro": ImageFont.truetype("arial.ttf", 70),
        "dig-verific": ImageFont.truetype("arial.ttf", 65),
        "TEXTO ABAJO1": ImageFont.truetype("fonts/OCR-B10PitchBT.ttf", 100),
        "TEXTO ABAJO2": ImageFont.truetype("fonts/OCR-B10PitchBT.ttf", 100),
        "TEXTO ABAJO3": ImageFont.truetype("fonts/OCR-B10PitchBT.ttf", 100),
        "NOMBRECITO": ImageFont.truetype("arial.ttf", 30),
    }

    COLORES = {
        "fecha caducidad": ((150, 53, 57), (255, 204, 0, 110)),
        "71525264": ((150, 53, 57), (150, 53, 57)),
        "dni nro": ((150, 53, 57), (150, 53, 57, 80)),
        "NOMBRECITO": ((150, 53, 57), (255, 204, 0, 80)),
    }

    for name, layer in text_layers.items():

        texto = TEXTOS[name]
        font = FONTS.get(name, ImageFont.truetype("arial.ttf", 40))

        tx1, ty1, tx2, ty2 = layer.bbox

        if name not in ["TEXTO ABAJO1", "TEXTO ABAJO2", "TEXTO ABAJO3"]:
            fondo_texto = fondo.crop((tx1, ty1, tx2, ty2))
            resultado.paste(fondo_texto, (tx1, ty1))

        bbox_text = draw.textbbox((0, 0), texto, font=font, stroke_width=1)
        h = bbox_text[3] - bbox_text[1]

        if name == "NOMBRECITO":

            w = get_text_width_tracking(texto, font, tracking_val)

            x_text = tx1 + (tx2 - tx1 - w) // 2
            y_text = ty1 + (ty2 - ty1 - h) // 2

        else:
            x_text = tx1
            y_text = ty1 + (ty2 - ty1 - h) // 2

        offset_x, offset_y = OFFSETS.get(name, (0, 0))

        color_texto, color_borde = COLORES.get(
            name,
            ((33, 32, 30), (33, 32, 30, 110))
        )

        tracking_val = TRACKING.get(name, 0)

        if name.strip().lower() == "dni nro":

            cx = tx1 + (tx2 - tx1) // 2 + offset_x
            cy = ty1 + (ty2 - ty1) // 2 + offset_y

            resultado = draw_text_rotado_tracking(
                resultado,
                texto,
                cx,
                cy,
                font,
                color_texto,
                color_borde,
                angle=-90,
                tracking=tracking_val
            )

        else:

            draw_text_tracking(
                draw,
                texto,
                x_text + offset_x,
                y_text + offset_y,
                font,
                color_texto,
                color_borde,
                tracking=tracking_val
            )

            ruta = f"data_img/{dni}/img_docs"
            archivo = os.path.join(ruta, f"dni_a_f_{dni}.png")

            # Crear carpeta si no existe
            os.makedirs(ruta, exist_ok=True)

            resultado.save(archivo)
            print(f"✅ Imagen guardada en: {archivo}")
    return True

def gen_dni_b(dni, data=None):
    data = _resolve_dni_data(dni, data)
    if not data:
        print(f"Error: No se pudo generar el DNI para {dni}")
        return None

    layers = list(psd2.descendants())

    img_layer = None
    text_layers = {}

    TEXTOS = {
        "DEPARTAMENTO": data["depaDireccion"],
        "PROVINCIA": data["provDireccion"],
        "DISTRITO": data["distDireccion"],
        "DIRECCION": data["desDireccion"],
        "DONACION DE ORGANO": data["donaOrganos"],
        "GRUPO VOTACION": data["UbigeoReniec"],

        
    }

    TRACKING = {
        "DEPARTAMENTO": 0,
        "PROVINCIA": 0,
        "DISTRITO": 0,
        "DIRECCION": 0.6,
        "DONACION DE ORGANO": 0,
        "GRUPO VOTACION": 0.3
        
    }

    for i, layer in enumerate(layers):

        if layer.name == "HUELLA DIGITAL":
            img_layer = (i, layer)

        if layer.name in TEXTOS:
            text_layers[layer.name] = layer

    if not img_layer or not text_layers:
        return

    index, layer_target = img_layer
    x1, y1, x2, y2 = layer_target.bbox

    for l in layers[index:]:
        l.visible = False
    fondo = psd2.composite()

    for l in layers:
        l.visible = True

    for l in layers[:index+1]:
        l.visible = False

    overlay = psd2.composite()

    for l in layers:
        l.visible = True

    nueva = Image.open(f"data_img/{dni}/hDerecha.png")
    nueva = quitar_fondo_blanco(nueva, tolerancia=160)
    nueva = convertir_a_negro(nueva)
    nueva = nueva.resize((x2 - x1, y2 - y1))

    resultado = fondo.copy()
    resultado.paste(nueva, (x1, y1), nueva)

    draw = ImageDraw.Draw(resultado)

    OFFSETS = {
        "DEPARTAMENTO": (-1, -8),
        "PROVINCIA": (-1, -8),
        "DISTRITO": (-1, -8),
        "DIRECCION": (2, -8),
        "DONACION DE ORGANO": (-2, -8),
        "GRUPO VOTACION": (0, -9)
        
    }

    FONTS = {
        "DEPARTAMENTO": ImageFont.truetype("arial.ttf", 40),
        "PROVINCIA": ImageFont.truetype("arial.ttf", 40),
        "DISTRITO": ImageFont.truetype("arial.ttf", 40),
        "DIRECCION": ImageFont.truetype("arial.ttf", 40),
        "DONACION DE ORGANO": ImageFont.truetype("arial.ttf", 51),
        "GRUPO VOTACION": ImageFont.truetype("arial.ttf", 50),
        
    }

    COLORES = {
       
    }

    for name, layer in text_layers.items():

        texto = TEXTOS[name]
        font = FONTS.get(name, ImageFont.truetype("arial.ttf", 40))

        tx1, ty1, tx2, ty2 = layer.bbox

        fondo_texto = fondo.crop((tx1, ty1, tx2, ty2))
        resultado.paste(fondo_texto, (tx1, ty1))

        bbox_text = draw.textbbox((0, 0), texto, font=font, stroke_width=1)
        h = bbox_text[3] - bbox_text[1]

        x_text = tx1
        y_text = ty1 + (ty2 - ty1 - h) // 2

        offset_x, offset_y = OFFSETS.get(name, (0, 0))

        color_texto, color_borde = COLORES.get(
            name,
            ((33, 32, 30), (33, 32, 30, 110))
        )

        tracking_val = TRACKING.get(name, 0)

        draw_text_tracking(
            draw,
            texto,
            x_text + offset_x,
            y_text + offset_y,
            font,
            color_texto,
            color_borde,
            tracking=tracking_val
        )

        ruta = f"data_img/{dni}/img_docs"
        archivo = os.path.join(ruta, f"dni_a_b_{dni}.png")

        # Crear carpeta si no existe
        os.makedirs(ruta, exist_ok=True)

        resultado.save(archivo)
        print(f"✅ Imagen guardada en: {archivo}")
    return True

def quitar_fondo_blanco(img, tolerancia=200):
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for r, g, b, a in datas:
        if r > tolerancia and g > tolerancia and b > tolerancia:
            newData.append((255, 255, 255, 0))
        else:
            newData.append((r, g, b, a))

    img.putdata(newData)
    return img
