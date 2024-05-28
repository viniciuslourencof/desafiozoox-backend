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

def get_item(item_id: str):
    try:
        doc_ref = db.collection('items').document(item_id)
        doc = doc_ref.get()
        if doc.exists:
            item = doc.to_dict()
            item['id'] = doc.id
            return item
        else:
            return None
    except Exception as e:
        raise ValueError(f"Error getting item: {e}") 

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
    
    return True

def update_item(item_id: str, item_data: dict):        
    item_ref = db.collection('items').document(item_id)
    item = item_ref.get()
    
    if not item.exists:
        raise ValueError("Item not found")    
    
    item_ref.update(item_data)
        
    updated_item = item_ref.get().to_dict()
    updated_item['id'] = item_id

    #history

    item_ref = db.collection('items').document(item_id)
    item_snapshot = item_ref.get()
    
    if not item_snapshot.exists:
        raise ValueError("Item not found")    
    
    old_data = item_snapshot.to_dict()    
    
    item_ref.update(item_data)    
    
    updated_item_snapshot = item_ref.get()
    updated_data = updated_item_snapshot.to_dict()    
    
    history_ref = db.collection('history').document()
    history_ref.set({
        'item_id': item_id,
        'old_data': old_data,
        'new_data': updated_data,
        'timestamp': firestore.SERVER_TIMESTAMP
    })

    #history

    return updated_item

def save_item(item_data: dict):
    item_ref = db.collection('items').add(item_data)
    new_item = item_ref[1].get().to_dict()
    new_item['id'] = item_ref[1].id
    return new_item

def get_item_history(item_id: str):
    history_list = []
    history_ref = db.collection('history').where('item_id', '==', item_id).order_by('timestamp', direction=firestore.Query.DESCENDING).get()
    for doc in history_ref:
        history_data = doc.to_dict()
        history_list.append({
            'id': doc.id,
            'item_id': history_data['item_id'],
            'old_data': history_data['old_data'],
            'new_data': history_data['new_data'],
            'timestamp': history_data['timestamp'].isoformat() 
        })
    return history_list
