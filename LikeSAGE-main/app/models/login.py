import json
from passlib.context import CryptContext
from pathlib import Path
from app.database.config.config import driver
from app.models.auth_interface import UserAuthenticator

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
USERS_FILE = Path("app/data/users.json")

# def load_users():
#     if USERS_FILE.exists():
#         with open(USERS_FILE, "r") as f:
#             return json.load(f)
#     return {}


class Neo4jUserAuthenticator(UserAuthenticator):
    def authenticate(self, username: str, password: str):
        print(f"[DEBUG] Intentando autenticar: {username}")
        with driver.session() as session:
            query = """
            MATCH (c:Candidate {correo: $username})
            RETURN c.password AS hashed_password
            """
            result = session.run(query, username=username)
            record = result.single()

            if record:
                hashed_password = record["hashed_password"]
                print(f"[DEBUG] Hash encontrado: {hashed_password}")
                if pwd_context.verify(password, hashed_password):
                    print(f"[DEBUG] Contraseña verificada con éxito.")
                    return {"username": username}
                else:
                    print(f"[DEBUG] Contraseña incorrecta.")
            else:
                print(f"[DEBUG] Usuario no encontrado en Neo4j.")

            return None


# def authenticate_user(username: str, password: str):
#     print(f"[DEBUG] Intentando autenticar: {username}")
#     with driver.session() as session:
#         query = """
#         MATCH (c:Candidate {correo: $username})
#         RETURN c.password AS hashed_password
#         """
#         result = session.run(query, username=username)
#         record = result.single()

#         if record:
#             hashed_password = record["hashed_password"]
#             print(f"[DEBUG] Hash encontrado: {hashed_password}")
#             if pwd_context.verify(password, hashed_password):
#                 print(f"[DEBUG] Contraseña verificada con éxito.")
#                 return {"username": username}
#             else:
#                 print(f"[DEBUG] Contraseña incorrecta.")
#         else:
#             print(f"[DEBUG] Usuario no encontrado en Neo4j.")

#         return None
