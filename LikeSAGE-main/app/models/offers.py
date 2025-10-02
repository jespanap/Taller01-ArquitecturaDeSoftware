import logging
from app.database.config.config import driver

# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def toggle_like(correo_candidato: str, titulo_vacante: str):
    _toggle_relationship(correo_candidato, titulo_vacante, "LIKES")

def toggle_save(correo_candidato: str, titulo_vacante: str):
    _toggle_relationship(correo_candidato, titulo_vacante, "SAVES")

def create_share(correo_candidato: str, titulo_vacante: str):
    with driver.session() as session:
        session.run("""
            MATCH (c:Candidate {correo: $correo}), (v:Vacancy {title: $titulo})
            MERGE (c)-[r:SHARES]->(v)
        """, correo=correo_candidato, titulo=titulo_vacante)
        logger.info(f"🔗 Relación SHARES creada entre {correo_candidato} y {titulo_vacante} (o ya existía)")

def _toggle_relationship(correo: str, titulo: str, rel: str):
    with driver.session() as session:
        # Verificar si ya existe la relación
        result = session.run(f"""
            MATCH (c:Candidate {{correo: $correo}})-[r:{rel}]->(v:Vacancy {{title: $titulo}})
            RETURN COUNT(r) AS rel_count
        """, correo=correo, titulo=titulo)

        rel_exists = result.single()["rel_count"] > 0

        if rel_exists:
            session.run(f"""
                MATCH (c:Candidate {{correo: $correo}})-[r:{rel}]->(v:Vacancy {{title: $titulo}})
                DELETE r
            """, correo=correo, titulo=titulo)
            logger.info(f"❌ Relación {rel} eliminada entre {correo} y {titulo}")
        else:
            session.run(f"""
                MATCH (c:Candidate {{correo: $correo}}), (v:Vacancy {{title: $titulo}})
                CREATE (c)-[:{rel}]->(v)
            """, correo=correo, titulo=titulo)
            logger.info(f"✅ Relación {rel} creada entre {correo} y {titulo}")

def interact_with_vacancy(correo_candidato: str, titulo_vacante: str, accion: str):
    logger.info(f"🔍 Interacción recibida: correo={correo_candidato}, titulo={titulo_vacante}, accion={accion}")
    if accion == "like":
        toggle_like(correo_candidato, titulo_vacante)
    elif accion == "save":
        toggle_save(correo_candidato, titulo_vacante)
    elif accion == "share":
        create_share(correo_candidato, titulo_vacante)
    else:
        logger.warning(f"⚠️ Acción desconocida: {accion}")
