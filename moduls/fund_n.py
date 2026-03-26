import re
from datetime import datetime

def valor_icao(char):
    if char.isdigit(): return int(char)
    if char.isalpha(): return ord(char.upper()) - 55
    return 0

def calcular_dc(cadena):
    pesos = [7, 3, 1]
    suma = 0
    for i, char in enumerate(cadena):
        suma += valor_icao(char) * pesos[i % 3]
    return suma % 10

def validar_dni_peru_definitivo(l1, l2):
    # Forzamos 30 caracteres exactos
    l1 = l1.replace(" ", "").upper().ljust(30, '<')
    l2 = l2.replace(" ", "").upper().ljust(30, '<')

    try:
        
        dni_bloque = l1[5:14]  # Ejemplo: "80677311<"
        # El DC del DNI está en la posición 14 (índice 14)
        dni_dc_real = l1[14]
        # Línea 2: Nacimiento(0-5), DC(6), Sexo(7), Caducidad(8-13), DC(14)
        nac_str = l2[0:6]
        nac_dc_real = l2[6]
        cad_str = l2[8:14]
        cad_dc_real = l2[14]
        # El Global es el último carácter de la línea 2
        global_real = l2[29]


        errores = 0
        # 1. Validar DNI (usando los 9 caracteres del bloque)
        c_dni = calcular_dc(dni_bloque)
        if c_dni == valor_icao(dni_dc_real): print(f"[OK] DNI: {c_dni}")
        else: 
            print(f"[ERR] DNI: Calc {c_dni} / Real {dni_dc_real}"); errores += 1

        # 2. Validar Nacimiento
        c_nac = calcular_dc(nac_str)
        if c_nac == valor_icao(nac_dc_real): print(f"[OK] NAC: {c_nac}")
        else: 
            print(f"[ERR] NAC: Calc {c_nac} / Real {nac_dc_real}"); errores += 1

        # 3. Validar Caducidad
        c_cad = calcular_dc(cad_str)
        if c_cad == valor_icao(cad_dc_real): print(f"[OK] CAD: {c_cad}")
        else: 
            print(f"[ERR] CAD: Calc {c_cad} / Real {cad_dc_real}"); errores += 1

        cadena_global = f"{l1[5:15]}{l2[0:7]}{l2[8:15]}"
        c_global = calcular_dc(cadena_global)

        if c_global == valor_icao(global_real):
            print(f"[OK] GLOBAL: {c_global}")
        else:
            # Prueba con el bloque opcional de la línea 2 (posiciones 15 a 28)
            cadena_global_completa = f"{l1[5:15]}{l2[0:15]}{l2[18:29]}"
            c_global = calcular_dc(cadena_global_completa)
            if c_global == valor_icao(global_real):
                print(f"[OK] GLOBAL: {c_global}")
            else:
                print(f"[ERR] GLOBAL: Calc {c_global} / Real {global_real}"); errores += 1

        print("="*45)
        print("RESULTADO: DOCUMENTO VÁLIDO" if errores == 0 else "RESULTADO: INVÁLIDO")
        print("="*45 + "\n")

    except Exception as e:
        print(f"[ERROR]: {e}")

def formatear_nombre(apellido, nombre, longitud_total=30):
        texto = f"{apellido.upper()}<<{nombre.upper()}"
        if len(texto) > longitud_total:
            texto = texto[:longitud_total]
        texto = texto.ljust(longitud_total, "<")
        return texto

def convertir_fecha(fecha_str):
    # Convertir string a fecha (formato día/mes/año)
    fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
    
    # Convertir a formato YYMMDD
    return fecha.strftime("%y%m%d")

def generar_mrz_peru(dni, f_nac, sexo, f_cad):
    # 1. Bloque DNI (9 chars) + DC
    dni_bloque = dni.ljust(9, '<')
    dni_dc = calcular_dc(dni_bloque)
    linea1 = f"I<PER{dni_bloque}{dni_dc}".ljust(30, '<')
    
    # 2. DCs de fechas
    nac_dc = calcular_dc(f_nac)
    cad_dc = calcular_dc(f_cad)
    
    # 3. Construir cadena para el DIGITO GLOBAL
    # Esta es la cadena exacta que espera el validador:
    # DNI_BLOQUE(9) + DNI_DC(1) + NAC(6) + NAC_DC(1) + CAD(6) + CAD_DC(1)
    # IMPORTANTE: Sin el '<' extra en el medio para que coincida con tu validador
    cadena_para_global = f"{dni_bloque}{dni_dc}{f_nac}{nac_dc}{f_cad}{cad_dc}"
    global_dc = calcular_dc(cadena_para_global)
    
    # 4. Línea 2 final (30 chars)
    linea2_base = f"{f_nac}{nac_dc}{sexo.upper()}{f_cad}{cad_dc}PER".ljust(29, '<')
    linea2 = f"{linea2_base}{global_dc}"
    
    return linea1, linea2

