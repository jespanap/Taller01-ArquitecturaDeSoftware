from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.models.auth_interface import UserAuthenticator
from app.utils.auth import (
    create_token,
    set_token_cookie,
    clear_token_cookie,
    get_current_user,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")


def get_authenticator() -> UserAuthenticator:
    from app.models.login import Neo4jUserAuthenticator

    return Neo4jUserAuthenticator()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if get_current_user(request):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def do_login(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    if get_current_user(request):
        return RedirectResponse("/", status_code=303)

    authenticator = get_authenticator()
    user = authenticator.authenticate(username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Credenciales inválidas"}
        )

    token = create_token(username)
    response = RedirectResponse(url="/", status_code=303)
    set_token_cookie(response, token)
    return response


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=303)
    clear_token_cookie(response)
    return response
