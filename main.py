from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from service.item_service import save_item, get_items, remove_item, save_items, update_item, get_item_history
import os
import pandas as pd
import io
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel



app = FastAPI()
app_public = FastAPI(openapi_prefix='/public')
app_private = FastAPI(openapi_prefix='/api')

app.mount("/public", app_public)
app.mount("/api", app_private)

class ItemUpdate(BaseModel):
    nome: str
    data_nascimento: date 
    genero: str
    nacionalidade: str 

class HistoryItem(BaseModel):
    id: str
    item_id: str
    changed_fields: dict    
    timestamp: str      

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

@app_public.post("/items")
def create_item(item: ItemUpdate):
    item_data = item.model_dump(exclude_unset=True)
    if 'data_nascimento' in item_data and item_data['data_nascimento']:
        item_data['data_nascimento'] = item_data['data_nascimento'].isoformat()
    new_item = save_item(item_data)  
    return {"message": "Item created successfully", "item": new_item}

@app_public.post("/upload")
async def upload_file(file: UploadFile = File(...)):    
    contents = await file.read()    
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))        
    data = df.to_dict(orient="records")    
    save_items(data)    
    return {"message": "Data uploaded successfully", "data": get_items()}

@app_public.get("/items")
def read_items():
    return get_items()

@app_public.delete("/items/{item_id}")
def delete_item(item_id: str):
    return remove_item(item_id)

@app_public.put("/items/{item_id}")
def update_item_endpoint(item_id: str, item_update: ItemUpdate):
    item_data = item_update.model_dump(exclude_unset=True)        
    if 'data_nascimento' in item_data and item_data['data_nascimento']:
        item_data['data_nascimento'] = item_data['data_nascimento'].isoformat()    
    try:        
        updated_item = update_item(item_id, item_data)
        return {"message": "Item updated successfully", "item": updated_item}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app_public.get("/item/history/{item_id}", response_model=List[HistoryItem])
def read_item_history(item_id: str):
    history = get_item_history(item_id)
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    return history
    
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
