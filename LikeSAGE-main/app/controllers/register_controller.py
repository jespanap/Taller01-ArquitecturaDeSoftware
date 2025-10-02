from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.models import register
from app.utils.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/register")
async def show_register_form(request: Request):
    if get_current_user(request):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def do_register(
    request: Request,
    correo: str = Form(...),
    password: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    telefono: str = Form(...),
    pais: str = Form(...),
    sectores: list[str] = Form(...),
    cargo: str = Form(...),
    salario_minimo: int = Form(...),
    nivel_estudios: str = Form(...),
    lugar_trabajo: str = Form(...),
    trabajo_remoto: str = Form(...),
    viajar: str = Form(...),
    cambio_domicilio: str = Form(...),
    disponibilidad: str = Form(...),
    discapacidad: str = Form(...)
):
    if get_current_user(request):
        return RedirectResponse("/", status_code=303)

    # Validaciones
    if salario_minimo < 0:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "El salario mínimo no puede ser negativo",
            "form_data": locals()
        })

    if len(sectores) > 5:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "No puedes seleccionar más de 5 sectores laborales",
            "form_data": locals()
        })

    opciones_binarias = {"sí", "no", "si"}  # incluye sin tilde por si acaso
    if (trabajo_remoto.lower() not in opciones_binarias or
        viajar.lower() not in opciones_binarias or
        cambio_domicilio.lower() not in opciones_binarias):
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Las opciones de remoto, viaje y cambio de domicilio deben ser 'sí' o 'no'",
            "form_data": locals()
        })

    # Registro
    success = register.register_user(
        correo=correo,
        password=password,
        nombre=nombre,
        apellido=apellido,
        telefono=telefono,
        pais=pais,
        sectores=sectores,
        cargo=cargo,
        salario_minimo=salario_minimo,
        nivel_estudios=nivel_estudios,
        lugar_trabajo=lugar_trabajo,
        trabajo_remoto=trabajo_remoto,
        viajar=viajar,
        cambio_domicilio=cambio_domicilio,
        disponibilidad=disponibilidad,
        discapacidad=discapacidad
    )

    if success:
        return RedirectResponse("/login", status_code=303)
    else:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "El correo ya está registrado",
            "form_data": locals()
        })
