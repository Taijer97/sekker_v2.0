import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_RENIEC = os.getenv("API_RENIEC")
TOKEN_RENIEC = os.getenv("TOKEN_RENIEC")
API_OSIPTEL = os.getenv("API_OSIPTEL")
TOKEN_OSIPTEL = os.getenv("TOKEN_OSIPTEL")

def buscar_dni(dni):
    doc = requests.get(f'{API_RENIEC}{dni}?token={TOKEN_RENIEC}')
    if doc.status_code != 200:
        return False
    doc = doc.json()
    return doc

def buscar_cel(dni):
    cel = requests.get(f"{API_OSIPTEL}{dni}?token={TOKEN_OSIPTEL}")
    if cel.status_code != 200:
        return False
    cel = cel.json()
    return cel

URL_RENIEC_LOCAL = f"http://{os.getenv('HOST_API_LOCAL')}"

def login():
    url = f"{URL_RENIEC_LOCAL}/login"
    data = {
        "username": os.getenv("USER_API_LOCAL"),
        "password": os.getenv("PASSWORD_API_LOCAL")
    }

    response = requests.post(url, json=data)
    if response.status_code != 200:
        raise Exception(f"Error en login: {response.status_code} - {response.text}")
    response.raise_for_status()

    token = response.json().get("access_token")
    if not token:
        raise Exception("No se obtuvo token")

    return token

def reniec_local(dni):
    token = login()
    try:
        res = requests.get(
            f"{URL_RENIEC_LOCAL}/search/dni/{dni}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=8,
        )
        res.raise_for_status()
        return res.json()

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

