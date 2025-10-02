from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils.auth import get_current_user
from app.database.models.offers_db import search_vacancies_by_text

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/buscar", response_class=HTMLResponse)
async def search(request: Request):
    user = get_current_user(request)
    query = request.query_params.get('q', '')
    print("🔍 Query recibida:", query)

    # Parámetro de la página actual (por defecto 1)
    page = int(request.query_params.get('page', 1))
    per_page = 10  # Número de resultados por página (ajustable)

    # Buscar ofertas
    all_offers = search_vacancies_by_text(query)
    total_offers = len(all_offers)
    total_pages = (total_offers + per_page - 1) // per_page

    # Obtener solo las ofertas para la página actual
    start = (page - 1) * per_page
    end = start + per_page
    offers = all_offers[start:end]
    

    return templates.TemplateResponse("offers_search.html", {
    "request": request,
    "user": user,
    "offers": offers,
    "query": query,
    "page": page,
    "total_pages": total_pages,
    "total_offers": total_offers
})
