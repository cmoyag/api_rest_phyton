import datetime ,uuid
from sqlalchemy import Column, Integer, String, DateTime ,Boolean
from database import Base
from sqlalchemy.sql import func 


class Patente(Base):
    __tablename__ = 'patente'
    id          = Column(Integer, primary_key=True ,autoincrement=True)
    sku         = Column(String(256),default=str(uuid.uuid4().hex))
    patente     = Column(String(8))
    created_at  = Column(DateTime(timezone=True), default=func.now())
    activo      = Column(Boolean, unique=False, default=True)
