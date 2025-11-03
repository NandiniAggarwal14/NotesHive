# login_api.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from datetime import timedelta

app = FastAPI(title="NotesHive Login API")

user = "root"
password = "Nandini.14"
host = "localhost"
database = "notehive"

engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

class Settings(BaseModel):
    authjwt_secret_key: str = "notehive_secret_key"
    authjwt_access_token_expires: int = 7200  # 2 hours in seconds

@AuthJWT.load_config
def get_config():
    return Settings()

class LoginModel(BaseModel):
    email: str
    password: str

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

@app.post("/api/login")
def login(data: LoginModel, Authorize: AuthJWT = Depends()):
    email = data.email
    password = data.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    with engine.begin() as conn:
        query = text("SELECT user_id, name, role, password FROM User WHERE email = :email")
        user_result = conn.execute(query, {"email": email}).fetchone()

    if not user_result or password != user_result[3]:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id, name, role, _ = user_result

    access_token = Authorize.create_access_token(subject=str(user_id), user_claims={"role": role})

    return {
        "message": "Login successful",
        "token": access_token,
        "user": {
            "id": user_id,
            "name": name,
            "role": role
        }
    }

@app.get("/api/test")
def test_route(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user_claims = Authorize.get_raw_jwt()
    return {"message": "Token valid", "user_id": current_user, "claims": user_claims}
