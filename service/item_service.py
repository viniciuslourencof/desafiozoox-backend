from firebase_admin import credentials, initialize_app, firestore
from model.item_model import ItemModel
from utils.constants import FIRESTORE_PROJECT_ID

cred = credentials.ApplicationDefault()
initialize_app(cred, {
    'projectId': FIRESTORE_PROJECT_ID,
})

db = firestore.client()

def get_items():
    items = []
    docs = db.collection('items').stream()
    for doc in docs:
        item = doc.to_dict()
        item['id'] = doc.id  
        items.append(item)
    return items    

def save_item(id: str):
    doc_ref = db.collection(u'items').document(id)
    doc_ref.set({"item_id": id})
    return True

def remove_item(item_id: str):
    db.collection(u'items').document(item_id).delete()
    return True

def save_items(items: list):
    for item in items:
        nome = item.get("nome")
        birth_date = item.get("data_nascimento")        
        
        query = db.collection(u'items').where(u'nome', u'==', nome).where(u'data_nascimento', u'==', birth_date).limit(1).get()        
        
        if len(query) == 0:
            doc_ref = db.collection(u'items').document()
            doc_ref.set(item)
            print(f"Item '{nome}' adicionado ao Firestore.")
        else:
            print(f"Item '{nome}' com data de nascimento '{birth_date}' já existe no Firestore.")
    
    return True

def update_item(item_id: str, item_data: dict):
    items = get_items()
    for item in items:
        if item['id'] == item_id:
            item.update(item_data)
            save_items(items)
            return item
    raise ValueError("Item not found")


