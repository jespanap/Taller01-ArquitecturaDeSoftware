# offers_db.py
from app.database.config.config import driver


def get_all_vacancies():
    query = """
    MATCH (v:Vacancy)
    OPTIONAL MATCH (v)-[:PUBLISHED_BY]->(c:Company)
    OPTIONAL MATCH (v)-[:LOCATED_IN]->(ci:City)
    OPTIONAL MATCH (v)-[:REQUIRES_EDUCATION]->(e:EducationLevel)
    OPTIONAL MATCH (v)-[:REQUIRES_EXPERIENCE]->(x:ExperienceLevel)
    OPTIONAL MATCH (v)-[:REQUIRES_SKILL]->(s:Skill)
    RETURN 
        v.title AS titulo,
        COALESCE(c.name, 'No disponible') AS empresa,
        COALESCE(ci.name, 'No disponible') AS ciudad,
        COALESCE(e.level, 'No especificado') AS nivel_educativo,
        COALESCE(x.level, 'No especificado') AS nivel_experiencia,
        collect(DISTINCT s.name) AS habilidades
    """

    with driver.session() as session:
        result = session.run(query)
        return [
            {
                "titulo": record["titulo"],
                "empresa": record["empresa"],
                "ciudad": record["ciudad"],
                "nivel_educativo": record["nivel_educativo"],
                "nivel_experiencia": record["nivel_experiencia"],
                "habilidades": record["habilidades"]
            }
            for record in result
        ]


def get_vacancy_by_title(titulo: str):
    query = """
    MATCH (v:Vacancy {title: $titulo})
    OPTIONAL MATCH (v)-[:PUBLISHED_BY]->(c:Company)
    OPTIONAL MATCH (v)-[:LOCATED_IN]->(ci:City)
    OPTIONAL MATCH (v)-[:REQUIRES_EDUCATION]->(e:EducationLevel)
    OPTIONAL MATCH (v)-[:REQUIRES_EXPERIENCE]->(x:ExperienceLevel)
    OPTIONAL MATCH (v)-[:REQUIRES_SKILL]->(h:Skill)
    RETURN 
        v.title AS titulo, 
        COALESCE(c.name, 'No disponible') AS empresa, 
        COALESCE(ci.name, 'No disponible') AS ciudad,
        COALESCE(e.level, 'No especificado') AS nivel_educativo, 
        COALESCE(x.level, 'No especificado') AS nivel_experiencia,
        collect(DISTINCT h.name) AS habilidades
    """
    with driver.session() as session:
        record = session.run(query, titulo=titulo).single()

        if record:
            return {
                "titulo": record["titulo"],
                "empresa": record["empresa"],
                "ciudad": record["ciudad"],
                "nivel_educativo": record["nivel_educativo"],
                "nivel_experiencia": record["nivel_experiencia"],
                "habilidades": record["habilidades"]
            }
        return None


def search_vacancies_by_text(texto: str):
    query = """
    MATCH (v:Vacancy)
    WHERE toLower(v.title) CONTAINS toLower($texto)
    OPTIONAL MATCH (v)-[:PUBLISHED_BY]->(c:Company)
    OPTIONAL MATCH (v)-[:LOCATED_IN]->(ci:City)
    OPTIONAL MATCH (v)-[:REQUIRES_EDUCATION]->(edu:EducationLevel)
    OPTIONAL MATCH (v)-[:REQUIRES_EXPERIENCE]->(xp:ExperienceLevel)
    OPTIONAL MATCH (v)-[:REQUIRES_SKILL]->(s:Skill)
    RETURN 
        v.title AS titulo,
        COALESCE(c.name, 'No disponible') AS empresa,
        COALESCE(ci.name, 'No disponible') AS ciudad,
        COALESCE(edu.level, 'No especificado') AS nivel_educativo,
        COALESCE(xp.level, 'No especificado') AS nivel_experiencia,
        collect(DISTINCT s.name) AS habilidades
    """
    with driver.session() as session:
        result = session.run(query, texto=texto)
        resultados = [
            {
                "titulo": record["titulo"],
                "empresa": record["empresa"],
                "ciudad": record["ciudad"],
                "nivel_educativo": record["nivel_educativo"],
                "nivel_experiencia": record["nivel_experiencia"],
                "habilidades": record["habilidades"]
            }
            for record in result
        ]

        print(f"🔍 Resultados encontrados para '{texto}': {len(resultados)}")
        return resultados
