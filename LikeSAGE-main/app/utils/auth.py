import jwt
from datetime import datetime, timedelta
from fastapi import Request, Response

SECRET_KEY = "tu_secreto_super_secreto"
ALGORITHM = "HS256"
EXPIRATION_MINUTES = 60

def create_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=EXPIRATION_MINUTES)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None

def set_token_cookie(response: Response, token: str):
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="Lax")

def clear_token_cookie(response: Response):
    response.delete_cookie(key="access_token")
