from pydantic import BaseModel

class Ingresar(BaseModel):
    patente:str

class Patente(BaseModel):
    id: int
    patente:str

class Config:
    orm_mode = True