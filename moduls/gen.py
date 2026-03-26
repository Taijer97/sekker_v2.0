from moduls.req import buscar_dni
import base64
import os
import json

def _has_reniec_data(payload):
    if not isinstance(payload, dict):
        return False
    lista = payload.get("listaAni")
    if isinstance(lista, list) and len(lista) > 0:
        return True
    image_keys = ("foto", "firma", "hDerecha", "hIzquierda")
    return any(payload.get(key) for key in image_keys)

def generador(dni):
    dni_str = str(dni)
    es_dni_valido = len(dni_str) == 8 and dni_str.isdigit()
    
    base_dir = "data_img"
    dni_dir = os.path.join(base_dir, dni_str)
    json_path = os.path.join(dni_dir, f"{dni_str}.json")
    
    resut = None

    if es_dni_valido and os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                resut = json.load(f)
            print(f"Datos cargados desde caché local: {json_path}")
            if es_dni_valido:
                try:
                    if not os.path.exists(base_dir):
                        os.makedirs(base_dir)
                        
                    if not os.path.exists(dni_dir):
                        os.makedirs(dni_dir)

                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(resut, f, indent=4, ensure_ascii=False)

                    campos = {
                        'foto': os.path.join(dni_dir, 'foto.png'),
                        'firma': os.path.join(dni_dir, 'firma.png'),
                        'hDerecha': os.path.join(dni_dir, 'hDerecha.png'),
                        'hIzquierda': os.path.join(dni_dir, 'hIzquierda.png')
                    }

                    contenido = resut
                    
                    for clave, nombre_archivo in campos.items():
                        base64_string = contenido.get(clave)
                        
                        if base64_string:
                            try:
                                imagen_bytes = base64.b64decode(base64_string)
                                
                                with open(nombre_archivo, 'wb') as img_file:
                                    img_file.write(imagen_bytes)
                                
                            except Exception as e:
                                print(f"Error al procesar '{clave}': {e}")
                        else:
                            print(f"Aviso: No se encontró la clave '{clave}' en los datos.")

                except Exception as e:
                    print(f"Error inesperado al guardar datos: {e}")
            else:
                print(f"Aviso: DNI '{dni}' no tiene 8 dígitos. Se devuelven los datos sin guardar en data_img.")
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
        if es_dni_valido:
            try:
                if not os.path.exists(base_dir):
                    os.makedirs(base_dir)
                    
                if not os.path.exists(dni_dir):
                    os.makedirs(dni_dir)

                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(resut, f, indent=4, ensure_ascii=False)

                campos = {
                    'foto': os.path.join(dni_dir, 'foto.png'),
                    'firma': os.path.join(dni_dir, 'firma.png'),
                    'hDerecha': os.path.join(dni_dir, 'hDerecha.png'),
                    'hIzquierda': os.path.join(dni_dir, 'hIzquierda.png')
                }

                contenido = resut
                
                for clave, nombre_archivo in campos.items():
                    base64_string = contenido.get(clave)
                    
                    if base64_string:
                        try:
                            imagen_bytes = base64.b64decode(base64_string)
                            
                            with open(nombre_archivo, 'wb') as img_file:
                                img_file.write(imagen_bytes)
                            
                        except Exception as e:
                            print(f"Error al procesar '{clave}': {e}")
                    else:
                        print(f"Aviso: No se encontró la clave '{clave}' en los datos.")

            except Exception as e:
                print(f"Error inesperado al guardar datos: {e}")
        else:
            print(f"Aviso: DNI '{dni}' no tiene 8 dígitos. Se devuelven los datos sin guardar en data_img.")
            
    return resut
