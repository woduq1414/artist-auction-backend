from datetime import datetime
from app.models.purchase_model import PurchaseBase
from app.utils.partial import optional
from uuid import UUID
from .user_schema import IUserReadWithoutGroups


class IPurchaseCreate(PurchaseBase):
    


    def __init__(self, **data):
        super().__init__(**data)
        self.status_log = '{"abc" : "def"}'
        self.product_image_list = '{"abc" : "def"}'
        
    

class IPurchaseRead(PurchaseBase):
    id: UUID

class IPurchaseReadWithUsers(PurchaseBase):
    id: UUID
    users: list[IUserReadWithoutGroups] | None = []


@optional
class IPurchaseUpdate(PurchaseBase):
    
    def __init__(self, **data):
        super().__init__(**data)
    

