import os
from app.infra.database import Base

from dotenv import load_dotenv

load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRES_URI", "").replace("+asyncpg", "")

Base = Base
