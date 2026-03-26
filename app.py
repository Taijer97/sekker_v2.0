from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.openapi.docs import get_swagger_ui_html
from moduls.consult_inf import sek_data_r_full, sek_data_r_basic, sek_data_c_full, sek_data_c_basic, sek_data_r_local
from moduls.cleanup import clean_old_generated_files, start_cleanup_scheduler
from dotenv import load_dotenv
import os
import time
from moduls.gen_pdf import gen_dni_pdf

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "3"))
CLEANUP_INTERVAL_SECONDS = int(os.getenv("CLEANUP_INTERVAL_SECONDS", str(3 * 24 * 60 * 60)))
LAST_CALLS = {}

app = FastAPI(
    docs_url="/docs-privado-cb",
    redoc_url=None,
    openapi_url="/hidden.json"
)


@app.on_event("startup")
def startup_tasks():
    clean_old_generated_files(CLEANUP_INTERVAL_SECONDS)
    start_cleanup_scheduler(CLEANUP_INTERVAL_SECONDS)


def create_access_token(data: dict, expires_days: int = 1):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=expires_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str = Query(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        key = payload.get("sub") or token
        now = time.time()
        prev = LAST_CALLS.get(key)
        if prev is not None and now - prev < RATE_LIMIT_SECONDS:
            remaining = int(RATE_LIMIT_SECONDS - (now - prev))
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit: espere {remaining} segundos"
            )
        LAST_CALLS[key] = now
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if (
        form_data.username != USER or
        form_data.password != PASSWORD
    ):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    token = create_access_token(
        {"sub": form_data.username},
        expires_days=int(os.getenv("VALUE_DAYS_TOKEN", "30"))
    )

    return {
        "access_token": token,
        "token_type": "query"
    }

@app.get("/token-info")
def token_info(token: str = Query(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        exp_timestamp = payload.get("exp")

        if not exp_timestamp:
            raise HTTPException(status_code=400, detail="Token sin expiración")

        # ⏱️ tiempo actual
        now = datetime.now(timezone.utc)

        # ⏳ tiempo de expiración
        exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        # ⏳ tiempo restante
        remaining = exp_time - now
        remaining_seconds = int(remaining.total_seconds())

        return {
            "valido": True,
            "expira_en_segundos": max(remaining_seconds, 0),
            "expira_en": exp_time.isoformat(),
            "hora_actual": now.isoformat()
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )


@app.get("/reniec-full/{dni}")
def consultar_reniec_full(dni: str, user=Depends(verify_token)):

    datos = sek_data_r_full(dni)
    return {
        "dni": dni,
        "datos": datos,
        
    }

@app.get("/reniec/{dni}")
def consultar_reniec_basic(dni: str, user=Depends(verify_token)):

    datos = sek_data_r_basic(dni)
    return {
        "dni": dni,
        "datos": datos,
        
    }

@app.get("/osiptel-full/{dni}")
def consultar_cel_full(dni: str, user=Depends(verify_token)):
    datos = sek_data_c_full(dni)
    return {
        "dni": dni,
        "datos": datos,
        
    }

@app.get("/osiptel_basic/{dni}")
def consultar_cel_basic(dni: str, user=Depends(verify_token)):
    datos = sek_data_c_basic(dni)
    return {
        "dni": dni,
        "datos": datos,
        
    }

@app.get("/reniec-local/{dni}")
def consultar_reniec_local(dni: str, user=Depends(verify_token)):
    datos = sek_data_r_local(dni)
    return {
        "dni": dni,
        "datos": datos,
    }

@app.get("/gen-dni_pdf/{dni}")
def generar_dni(dni: str, user=Depends(verify_token)):
    pdf_path = gen_dni_pdf(dni)
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="No se pudo generar el PDF")
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"dni_{dni}.pdf"
    )
