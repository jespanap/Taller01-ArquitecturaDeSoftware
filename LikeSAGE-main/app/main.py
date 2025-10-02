from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.controllers import login_controller, register_controller, offers_controller, home_controller
from app.utils import auth

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="TU_SECRETO_AQUI")

app.mount("/static", StaticFiles(directory="app/views/static"), name="static")


templates = Jinja2Templates(directory="app/views/templates")

app.include_router(login_controller.router)
app.include_router(register_controller.router)
app.include_router(offers_controller.router)
app.include_router(home_controller.router)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    user = auth.get_current_user(request)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})
