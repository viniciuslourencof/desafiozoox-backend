# model/item_model.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class ItemModel(BaseModel):
    nome: str
    data_nascimento: date
    genero: str
    nacionalidade: str
    data_criacao: Optional[datetime] = None 
    data_atualizacao: Optional[datetime] = None
