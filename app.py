from typing import List
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse ,RedirectResponse
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from models import Patente
from fastapi.logger import logger
import uuid,models,schemas,re,logging
import numpy as np

# Create the database
Base.metadata.create_all(engine)


description = """
API Rest Falabella. 🚀

## Endpoint
**lista**          : Lista todas las entradas de Patenes almacenada en la bbdd SqlLite [OPCIONAL]

**patente_by_id**   : Entrada la patente segun el ID de ingreso

**ingresarPatente** : Ingrsa patente a la bbdd SqlLite via ORM 

**matriz**          : Endpoint Que suma las coordenadas (x,y), Segun la logica planteada en el desafio
"""

app = FastAPI(title="Prueba Técnica Falabella 2021",
              description=description,
              version="0.0.1",
              contact={
                  "name": "Cristian Moya G",
                  "url": "http://x-force.example.com/contact/",
                  "email": "cristian8x@gmail.com",
                                },
              license_info={
                  "name": "Apache 2.0",
                  "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
              },
          )

# Helper function to get database session
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@app.get("/")
async def docs_redirect():
  return RedirectResponse(url="/docs")

@app.get("/lista", response_model = List[schemas.Patente])
def lista_patentes(session: Session = Depends(get_session)):
    """
    Endpoint no solicitado ,pero sirve para validar la consitencia del ingreso de patentes.
    """
    result = session.query(models.Patente).all()
    json_result_data = jsonable_encoder(result)
    return JSONResponse(content=json_result_data)   

@app.get("/patente_by_id", response_model = List[schemas.Patente])
def buscar_patente_by_id(id:str,session: Session = Depends(get_session)):
    """
    Endpoint qur retorna una patente por su ID.
    """
    result = session.get(Patente, {"id":id})
    json_result_data = jsonable_encoder(result)
    if (result):
       return JSONResponse(content=json_result_data)
    else:
      raise HTTPException(status_code=404, detail=f"El registro {id} No Existe")


@app.post("/ingresarPatente",response_model=schemas.Patente,status_code=status.HTTP_201_CREATED)
def agregar_patente(var: schemas.Ingresar, session: Session = Depends(get_session)):
    """
    Endpoint encargado de ingresar patente a una bbdd via orm
    """   
    query = session.query(Patente).filter(Patente.patente == var.patente.upper()).all()

    #Validamos la existencia de la Patente en la bbdd
    if (query):
      raise HTTPException(status_code=404, detail=f"Patente {var.patente.upper()} Ya existe en la Base de Datos")

    especiales = re.compile('[\w.!#$%&+-?@ñÑ]')  

    if especiales.match(var.patente):
      raise HTTPException(status_code=404, detail=f"Solo se admiten caracteres alfanumericos con el formato ZZZZ999, sin acentos o Ñ")

    patron = re.compile('[A-Z]{4}[0-9]{3}')
    #Validacion de la consistencia del Patron
    if patron.match(var.patente.upper()):
      db = models.Patente(patente=var.patente.upper())
      session.add(db)
      session.commit()
      session.refresh(db)
      #Formato del retorno
      result ={"id":db.id,"sku":db.sku,"patente":db.patente}
      #Serializacion en JSON
      json_result_data = jsonable_encoder(result)
      return JSONResponse(content=json_result_data)

    else:
        raise HTTPException(status_code=404, detail=f"Formato de Patente invalid {var.patente} debes ingresar un formato ZZZZ999")


@app.post("/matriz",status_code=status.HTTP_201_CREATED)
def suma_matriz(r:int ,c:int,x:int,y:int,z:int,session: Session = Depends(get_session)):
  """
  Endpoint Que suma las Coordenasa (x,y), Segun la siguiente logica
  .   R > 0, C > 0, donde R y C son enteros.
  .    X >= 0, Y >= 0; X e Y son enteros.
  .   El llenado de la matriz esta dado por la variable Z, de tipo entero donde 0 < Z <= 1.000.000
  .   Donde sea R = 1 completar con Z.   Si R > 1 incrementar cada columna Rn con    Z + Rn -1

  """
  enteros = re.compile('[1-9]')
  if (enteros.match(str(r)) and enteros.match(str(c)) and enteros.match(str(z))):
    if(z >= 1000000):
     raise HTTPException(status_code=404, detail=f"EL valor de Z no puede superar el 1.000.000")  
    coor_x = x+1
    coor_y = y+1

    Matrix = [[0 for b in range(c)] for g in range(r)] 
    for i in range(r):
         for j in range(c):
            if(i == 0):
              Matrix[i][j]=z
            elif(1 > 0):
              Matrix[i][j]=(z+(i-1)+1)       
    mean_data = np.array(Matrix)      
    result = np.sum(mean_data[:coor_y, :coor_x])
    return int(result)

  else:
      raise HTTPException(status_code=422, detail=f"Solamente se admiten numeros enteros de un rango de [1-9]")  