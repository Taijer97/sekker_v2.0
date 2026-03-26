from moduls.req import buscar_dni, buscar_cel, reniec_local
import os
import json

def _has_reniec_data(payload):
    if not isinstance(payload, dict):
        return False
    lista = payload.get("listaAni")
    return isinstance(lista, list) and len(lista) > 0 and isinstance(lista[0], dict)


def _has_osiptel_data(payload):
    if not isinstance(payload, dict):
        return False
    data = payload.get("data")
    return isinstance(data, list) and len(data) > 0


def sek_data_r_full(dni):

    base_dir = "data_img"
    dni_dir = os.path.join(base_dir, str(dni))
    json_path = os.path.join(dni_dir, f"{dni}.json")
    
    resut = None

    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                resut = json.load(f)
            return resut
        except Exception as e:
            print(f"Error al leer caché local: {e}")

    if not resut:
        print("Consultando API...")
        resut = buscar_dni(dni)
    
    if not _has_reniec_data(resut):
        print("Error: No se obtuvieron datos o el DNI no existe.")
        return None
    else:
        try:
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
                
            if not os.path.exists(dni_dir):
                os.makedirs(dni_dir)

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(resut, f, indent=4, ensure_ascii=False)
        
        except Exception as e:
            print(f"Error inesperado: {e}")
            
    return resut

def sek_data_r_basic(dni):
    base_dir = "data_img"
    dni_dir = os.path.join(base_dir, str(dni))
    json_path = os.path.join(dni_dir, f"{dni}.json")

    resut = None

    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                resut_o = json.load(f)
                lista = resut_o.get("listaAni")
                if isinstance(lista, list) and len(lista) > 0 and isinstance(lista[0], dict):
                    resut = lista[0]
                else:
                    return {"error": "sin_datos_cache"}
                fil_data = {
                    "apeMaterno": resut.get("apeMaterno"),
                    "apePaterno": resut.get("apePaterno"),
                    "depaDireccion": resut.get("depaDireccion"),
                    "departamento": resut.get("departamento"),
                    "desDireccion": resut.get("desDireccion"),
                    "digitoVerificacion": resut.get("digitoVerificacion"),
                    "distDireccion": resut.get("distDireccion"),
                    "distrito": resut.get("distrito"),
                    "estadoCivil": resut.get("estadoCivil"),
                    "feNacimiento": resut.get("feNacimiento"),
                    "nomMadre": resut.get("nomMadre"),
                    "nomPadre": resut.get("nomPadre"),
                    "nuDocMadre": resut.get("nuDocMadre"),
                    "nuDocPadre": resut.get("nuDocPadre"),
                    "nuEdad": resut.get("nuEdad"),
                    "preNombres": resut.get("preNombres"),
                    "provDireccion": resut.get("provDireccion"),
                    "provincia": resut.get("provincia"),
                    "sexo": resut.get("sexo")
                }

            print(f"Datos cargados desde caché local: {json_path}")
            return fil_data
        except Exception as e:
            print(f"Error al leer caché local: {e}")

    if not resut:
        print("Consultando en la API...")
        resut_o = buscar_dni(dni)
        lista = resut_o.get("listaAni") if isinstance(resut_o, dict) else None
        if isinstance(lista, list) and len(lista) > 0 and isinstance(lista[0], dict):
            resut = lista[0]
        else:
            return {"error": "sin_datos_api"}
        fil_data = {
                    "apeMaterno": resut.get("apeMaterno"),
                    "apePaterno": resut.get("apePaterno"),
                    "depaDireccion": resut.get("depaDireccion"),
                    "departamento": resut.get("departamento"),
                    "desDireccion": resut.get("desDireccion"),
                    "digitoVerificacion": resut.get("digitoVerificacion"),
                    "distDireccion": resut.get("distDireccion"),
                    "distrito": resut.get("distrito"),
                    "estadoCivil": resut.get("estadoCivil"),
                    "feNacimiento": resut.get("feNacimiento"),
                    "nomMadre": resut.get("nomMadre"),
                    "nomPadre": resut.get("nomPadre"),
                    "nuDocMadre": resut.get("nuDocMadre"),
                    "nuDocPadre": resut.get("nuDocPadre"),
                    "nuEdad": resut.get("nuEdad"),
                    "preNombres": resut.get("preNombres"),
                    "provDireccion": resut.get("provDireccion"),
                    "provincia": resut.get("provincia"),
                    "sexo": resut.get("sexo")
                }
        
    if not resut:
        print("Error: No se obtuvieron datos o el DNI no existe.")
        return None
    else:
        try:
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
                
            if not os.path.exists(dni_dir):
                os.makedirs(dni_dir)

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(resut_o, f, indent=4, ensure_ascii=False)
        
        except Exception as e:
            print(f"Error inesperado: {e}")
            
    return fil_data

def sek_data_c_full(dni):
    base_dir = "data_img"
    cel_dir = os.path.join(base_dir, str(dni))
    json_path = os.path.join(cel_dir, f"{dni}-cel.json")

    resut = None

    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                resut = json.load(f)

                print(resut)
                return resut
        except Exception as e:
            print(f"Error al leer caché local: {e}")

    if not resut:
        print("buscando en la API")
        data_cel = buscar_cel(dni)
        
        def limpiar_valor(valor):
            if isinstance(valor, str):
                valor = valor.strip()  
                if valor.upper() == "NULL":
                    return None
            return valor

        def limpiar_dict(d):
            return {k: limpiar_valor(v) for k, v in d.items()}

        if not _has_osiptel_data(data_cel):
            print("Error: No se encontraron datos de telefonía para el DNI.")
            return None

        data_cel["data"] = [limpiar_dict(item) for item in data_cel["data"]]

        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)
        if not os.path.exists(cel_dir):
            os.makedirs(cel_dir, exist_ok=True)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data_cel, f, indent=4, ensure_ascii=False, sort_keys=True)

        print(f"✅ JSON guardado como {dni}-cel.json")
        return data_cel

def sek_data_c_basic(dni):
    base_dir = "data_img"
    cel_dir = os.path.join(base_dir, str(dni))
    json_path = os.path.join(cel_dir, f"{dni}-cel.json")

    resut = None

    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                resut = json.load(f)

                resultado = []

                for item in resut.get("data", []):
                    registro = {
                        "operador": item.get("operador"),
                        "periodo": item.get("periodo"),
                        "telefono": item.get("telefono"),
                        "estado": item.get("estado", "SIN ACTIVIDAD")  # si no existe → None
                    }
                    resultado.append(registro)

                return resultado
        except Exception as e:
            print(f"Error al leer caché local: {e}")

    if not resut:
        print("buscando en la API")
        data_cel = buscar_cel(dni)
        def limpiar_valor(valor):
            if isinstance(valor, str):
                valor = valor.strip()
                if valor.upper() == "NULL":
                    return None
            return valor

        def limpiar_dict(d):
            return {k: limpiar_valor(v) for k, v in d.items()}

        if not _has_osiptel_data(data_cel):
            print("Error: No se encontraron datos de telefonía para el DNI.")
            return []

        data_cel["data"] = [limpiar_dict(item) for item in data_cel["data"]]

        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)
        if not os.path.exists(cel_dir):
            os.makedirs(cel_dir, exist_ok=True)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data_cel, f, indent=4, ensure_ascii=False, sort_keys=True)

        print(f"✅ JSON guardado como {dni}-cel.json")
        resultado = []

        for item in data_cel.get("data", []):
            registro = {
                "operador": item.get("operador"),
                "periodo": item.get("periodo"),
                "telefono": item.get("telefono"),
                "estado": item.get("estado", "SIN ACTIVIDAD")  # si no existe → None
            }
            resultado.append(registro)

        return resultado

def sek_data_r_local(dni):
    datos = reniec_local(dni)
    d = datos.get("results")[0]
    return {
        "nombres": d.get("NOMBRES"),
        "apellido_paterno": d.get("AP_PAT"),
        "apellido_materno": d.get("AP_MAT"),
        "sexo": "M" if d.get("SEXO")==1 else "F",
        "fecha_nacimiento": d.get("FECHA_NAC"),
        "ubigeo_dir": d.get("UBIGEO_DIR"), 
        "direccion": d.get("DIRECCION"),
        "num_verific": d.get("DIG_RUC"),
    }
