from datetime import datetime
from app.models.project_model import ProjectBase
from app.utils.partial import optional
from uuid import UUID
from .user_schema import IUserReadWithoutGroups
import json
from datetime import datetime
import base64



class IProjectCreate(ProjectBase):
    
    project_users: list[UUID] | None = []

    def __init__(self, **data):
        super().__init__(**data)
        start_date = self.start_date.replace(tzinfo=None)
        self.start_date = datetime(start_date.year, start_date.month, start_date.day)
        end_date = self.end_date.replace(tzinfo=None)
        self.end_date = datetime(end_date.year, end_date.month, end_date.day)
    

class IProjectRead(ProjectBase):
    id: UUID

class IProjectReadWithUsers(ProjectBase):
    id: UUID
    users: list[IUserReadWithoutGroups] | None = []


@optional
class IProjectUpdate(ProjectBase):
    
    pre_content_json : dict | None = None


    def __init__(self, **data):
        super().__init__(**data)
        if self.pre_content_json:
            self.pre_content_json = validate_pre_content(self.pre_content_json)
           
            

def validate_pre_content(pre_content : dict):
    json_data = pre_content
    result = {}

    required_field_list = ["motive", "description_html_encoded"]
    for required_field in required_field_list:
        if required_field not in json_data or type(json_data[required_field]) != str:
            raise ValueError(f"pre_content must have {required_field} field")
        result[required_field] = json_data[required_field]

    if "description_html_encoded" in json_data:
        result["description"] =  base64.b64decode(json_data["description_html_encoded"]).decode("utf8")
        del result["description_html_encoded"]

    result["created_at"] = str(int(datetime.timestamp(datetime.now())))

    return result

    # result["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    

