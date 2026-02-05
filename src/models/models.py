from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from src.config.db_config import Base


class MurphUsers(SQLAlchemyBaseUserTableUUID, Base):
    pass

