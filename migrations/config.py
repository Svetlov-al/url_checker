import os

from dotenv import load_dotenv
from app.infra.database import Base # noqa

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRES_URI", "").replace("+asyncpg", "")
