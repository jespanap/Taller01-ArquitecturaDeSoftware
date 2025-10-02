from passlib.context import CryptContext
from app.database.config.config import driver

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def register_user(
    correo: str,
    password: str,
    nombre: str,
    apellido: str,
    telefono: str,
    pais: str,
    sectores: list[str],
    cargo: str,
    salario_minimo: int,
    nivel_estudios: str,
    lugar_trabajo: str,
    trabajo_remoto: str,
    viajar: str,
    cambio_domicilio: str,
    disponibilidad: str,
    discapacidad: str
) -> bool:
    hashed_password = pwd_context.hash(password)

    with driver.session() as session:
        result = session.run("MATCH (c:Candidate {correo: $correo}) RETURN c", correo=correo)
        if result.single():
            return False  # Ya existe

        # 1. Crear nodo Candidate con datos personales
        session.run(
            """
            CREATE (c:Candidate {
                correo: $correo,
                password: $password,
                nombre: $nombre,
                apellido: $apellido,
                telefono: $telefono,
                pais: $pais,
                availability: $disponibilidad,
                disability: $discapacidad
            })
            """,
            correo=correo,
            password=hashed_password,
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            pais=pais,
            disponibilidad=disponibilidad,
            discapacidad=discapacidad
        )

        # 2. Sectores laborales
        for sector in sectores:
            session.run(
                """
                MERGE (s:Sector {name: $sector})
                WITH s
                MATCH (c:Candidate {correo: $correo})
                MERGE (c)-[:HAS_SECTOR]->(s)
                """,
                sector=sector,
                correo=correo
            )

        # 3. Cargo o empleo
        session.run(
            """
            MERGE (p:Position {name: $cargo})
            WITH p
            MATCH (c:Candidate {correo: $correo})
            MERGE (c)-[:SEEKS_POSITION]->(p)
            """,
            cargo=cargo,
            correo=correo
        )

        # 4. Salario mínimo
        session.run(
            """
            MERGE (s:Salary {amount: $salario})
            WITH s
            MATCH (c:Candidate {correo: $correo})
            MERGE (c)-[:WANTS_SALARY]->(s)
            """,
            salario=salario_minimo,
            correo=correo
        )

        # 5. Nivel de estudios
        session.run(
            """
            MERGE (e:Education {level: $nivel})
            WITH e
            MATCH (c:Candidate {correo: $correo})
            MERGE (c)-[:HAS_EDUCATION]->(e)
            """,
            nivel=nivel_estudios,
            correo=correo
        )

        # 6. Lugar de trabajo
        session.run(
            """
            MERGE (l:Workplace {name: $lugar})
            WITH l
            MATCH (c:Candidate {correo: $correo})
            MERGE (c)-[:PREFERS_WORKPLACE]->(l)
            """,
            lugar=lugar_trabajo,
            correo=correo
        )

        # 7. Trabajo remoto
        session.run(
            """
            MERGE (r:RemotePreference {value: $remoto})
            WITH r
            MATCH (c:Candidate {correo: $correo})
            MERGE (c)-[:WANTS_REMOTE]->(r)
            """,
            remoto=trabajo_remoto,
            correo=correo
        )

        # 8. Disponible para viajar
        session.run(
            """
            MERGE (v:TravelAvailability {value: $viajar})
            WITH v
            MATCH (c:Candidate {correo: $correo})
            MERGE (c)-[:CAN_TRAVEL]->(v)
            """,
            viajar=viajar,
            correo=correo
        )

        # 9. Cambio de domicilio
        session.run(
            """
            MERGE (m:RelocationAvailability {value: $mudarse})
            WITH m
            MATCH (c:Candidate {correo: $correo})
            MERGE (c)-[:CAN_RELOCATE]->(m)
            """,
            mudarse=cambio_domicilio,
            correo=correo
        )

        return True
