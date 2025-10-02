from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.models.offers_db import search_vacancies
from fastapi.responses import HTMLResponse
from app.utils import auth
from app.utils.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

# Vista para mostrar ofertas basadas en la búsqueda
@router.get("/offers/search", response_class=HTMLResponse)
async def search_offers(request: Request, page: int = 1, per_page: int = 5, query: str = None):
    user = auth.get_current_user(request)
    
    if query:  # Si hay una consulta, hacer búsqueda
        vacancies = search_vacancies(query)  # Función que buscará las vacantes basadas en el query
    else:  # Si no hay consulta, mostrar una respuesta vacía o alguna advertencia
        vacancies = []
    
    total = len(vacancies)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_vacancies = vacancies[start:end]

    return templates.TemplateResponse("offers_search.html", {
        "request": request,
        "offers": paginated_vacancies,
        "user": user,
        "page": page,
        "total_pages": (total + per_page - 1) // per_page,
        "query": query  # Pasar la consulta al template
    })

# Controlador para interactuar con las ofertas
@router.post("/offers/interact")
async def interact_with_offer(
    request: Request,
    titulo: str = Form(...),
    accion: str = Form(...),
    page: int = Form(1)
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    from app.models.offers import interact_with_vacancy
    interact_with_vacancy(user, titulo, accion)
    
    return RedirectResponse(f"/offers/search?query={titulo}&page={page}", status_code=303)

# Función para la búsqueda de vacantes (debido a que se usará en la búsqueda de ofertas)
from app.database.models.offers_db import search_vacancies
# Esto es solo un ejemplo. Tienes que definir esta función según tus necesidades.

@router.get("/offers/{titulo}", response_class=HTMLResponse)
async def offer_detail(request: Request, titulo: str):
    user = get_current_user(request)

    from app.database.models.offers_db import get_vacancy_by_title
    offer = get_vacancy_by_title(titulo)

    if not offer:
        return HTMLResponse(content="Oferta no encontrada", status_code=404)

    return templates.TemplateResponse("offer_detail.html", {
        "request": request,
        "user": user,
        "offer": offer
    })
