from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.models.offers_db import get_all_vacancies
from fastapi.responses import HTMLResponse, JSONResponse
from app.database.config.config import driver
from app.utils import auth
from app.utils.auth import get_current_user


router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/offers", response_class=HTMLResponse)
async def show_offers(request: Request, page: int = 1, per_page: int = 5):
    user = auth.get_current_user(request)
    all_vacancies = get_all_vacancies()

    total = len(all_vacancies)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_vacancies = all_vacancies[start:end]

    # Obtener el estado de "me gusta" y "guardar" para cada oferta
    if user:
        with driver.session() as session:
            for vacancy in paginated_vacancies:
                # Verificar si el usuario ya ha marcado esta oferta como "me gusta"
                like_result = session.run("""
                    MATCH (c:Candidate {correo: $correo})-[:LIKES]->(v:Vacancy {title: $title})
                    RETURN count(v) > 0 AS liked
                """, correo=user, title=vacancy['titulo'])
                vacancy['liked'] = like_result.single()['liked']

                # Verificar si el usuario ya ha marcado esta oferta como "guardar"
                save_result = session.run("""
                    MATCH (c:Candidate {correo: $correo})-[:SAVES]->(v:Vacancy {title: $title})
                    RETURN count(v) > 0 AS saved
                """, correo=user, title=vacancy['titulo'])
                vacancy['saved'] = save_result.single()['saved']

    return templates.TemplateResponse("offers.html", {
        "request": request,
        "vacancy": paginated_vacancies,
        "user": user,
        "page": page,
        "total_pages": (total + per_page - 1) // per_page,
        "query": None
    })


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
    
    return RedirectResponse(f"/offers?page={page}", status_code=303)


@router.post("/offers/like")
async def like_offer(request: Request, vacancy_title: str = Form(...)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    with driver.session() as session:
        session.run("""
            MATCH (c:Candidate {correo: $correo}), (v:Vacancy {title: $title})
            MERGE (c)-[:LIKES]->(v)
        """, correo=user, title=vacancy_title)

    return RedirectResponse("/offers", status_code=303)


@router.post("/offers/save")
async def save_offer(request: Request, vacancy_title: str = Form(...)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    with driver.session() as session:
        session.run("""
            MATCH (c:Candidate {correo: $correo}), (v:Vacancy {title: $title})
            MERGE (c)-[:SAVES]->(v)
        """, correo=user, title=vacancy_title)

    return RedirectResponse("/offers", status_code=303)


@router.post("/offers/share")
async def share_offer(request: Request, vacancy_title: str = Form(...)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    with driver.session() as session:
        session.run("""
            MATCH (c:Candidate {correo: $correo}), (v:Vacancy {title: $title})
            MERGE (c)-[:SHARES]->(v)
        """, correo=user, title=vacancy_title)

    return RedirectResponse("/offers", status_code=303)

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

@router.get("/api/offers")
async def api_offers(page: int = 1, per_page: int = 5):
    all_vacancies = get_all_vacancies()
    start = (page - 1) * per_page
    end = start + per_page
    paginated = all_vacancies[start:end]
    return JSONResponse(content={"offers": paginated})