# model/item_model.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class ItemModel(BaseModel):
    nome: str
    data_nascimento: Optional[date] = None 
    genero: str
    nacionalidade: str
    data_criacao: Optional[date] = None 
    data_atualizacao: Optional[date] = None

class HistoryItem(BaseModel):
    id: str
    item_id: str
    changed_fields: dict    
    timestamp: str   
