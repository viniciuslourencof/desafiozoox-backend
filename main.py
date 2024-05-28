from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from service.item_service import save_item, get_items, remove_item, save_items, update_item
import os
import pandas as pd
import io
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

app = FastAPI()
app_public = FastAPI(openapi_prefix='/public')
app_private = FastAPI(openapi_prefix='/api')

app.mount("/public", app_public)
app.mount("/api", app_private)

class ItemUpdate(BaseModel):
    nome: str = None
    data_nascimento: date = None
    genero: str = None
    nacionalidade: str = None
    data_atualizacao: Optional[datetime] = None

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_private.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_public.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app_public.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Read the uploaded file
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

    # Convert DataFrame to a list of dictionaries
    data = df.to_dict(orient="records")

    save_items(data)
    
    return {"message": "Data uploaded successfully", "data": get_items()}


@app.get("/")
def read_root():
    return {"teste"}

@app_private.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app_public.get("/items")
def read_items():
    return get_items()

@app_public.get("/items/add/{item_id}")
def add_item(item_id: str):
    return save_item(item_id)

@app_public.delete("/items/{item_id}")
def delete_item(item_id: str):
    return remove_item(item_id)

@app_private.put("/items/{item_id}")
def update_item_endpoint(item_id: str, item_update: ItemUpdate):
    item_data = item_update.dict(exclude_unset=True)
    try:
        updated_item = update_item(item_id, item_data)
        return {"message": "Item updated successfully", "item": updated_item}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == '__main__':
    if os.getenv('ENV') == 'prod':
        uvicorn.run("main:app",
                    host="0.0.0.0",
                    port=80,
                    reload=True,
                    ssl_keyfile=f"/code/certs/live/{os.getenv('API_DOMAIN')}/privkey.pem",
                    ssl_certfile=f"/code/certs/live/{os.getenv('API_DOMAIN')}/fullchain.pem"
                    )
    else:
        uvicorn.run("main:app",
                    host="0.0.0.0",
                    port=8000,
                    reload=True
                    )
