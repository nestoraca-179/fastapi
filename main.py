from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel

from auth import create_token, get_current_user, get_user, verify_password

app = FastAPI(
    title="Authentication API",
    description="Backend académico con autenticación JWT y roles de usuario.",
    version="1.0.0",
)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login", response_model=TokenResponse, tags=["Authentication"])
def login(login_request: LoginRequest):
    user = get_user(login_request.username)
    if user is None or not verify_password(login_request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_token(user),
        "token_type": "bearer",
        "username": user["username"],
        "role": user["rol"],
    }


@app.get("/publico", tags=["Public"])
def public_endpoint():
    return {"mensaje": "Este es un endpoint público"}


@app.get("/privado", tags=["Private"])
def private_endpoint(current_user: dict = Depends(get_current_user)):
    return {
        "mensaje": "Acceso autorizado al endpoint privado",
        "usuario": current_user["username"],
        "rol": current_user["rol"],
    }


@app.get("/admin", tags=["Administration"])
def admin_endpoint(current_user: dict = Depends(get_current_user)):
    if current_user["rol"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )

    return {
        "mensaje": "Acceso autorizado al endpoint de administración",
        "usuario": current_user["username"],
        "rol": current_user["rol"],
    }
