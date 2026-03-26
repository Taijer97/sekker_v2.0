from moduls.gen import generador
from moduls.ps import gen_dni_f, gen_dni_b
from moduls.con_pdf import generate_pdf
import os

def start(dni):
    datos_completos = generador(dni)
    
    if datos_completos:
        if isinstance(datos_completos, dict) and "listaAni" in datos_completos:
            return datos_completos["listaAni"][0]
        return datos_completos
    return None

def gen_dni_pdf(dni):
    datos = start(dni)
    if datos:
        gen_dni_f(dni, datos)
        gen_dni_b(dni, datos)
        output_pdf = generate_pdf(dni)
        if output_pdf and os.path.exists(output_pdf):
            return output_pdf
    return None
