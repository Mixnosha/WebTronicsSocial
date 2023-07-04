import uuid
import json
from requests import request
from fastapi_users import schemas
from  pydantic import EmailStr, ValidationError, validator
from config import HUNTER_KEY

HUNTER_URL = "https://api.hunter.io/v2/email-verifier?"
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr

    @validator('email')
    def hunter_validator(cls, email: EmailStr) -> EmailStr:
        if HUNTER_KEY is None: return email

        url = HUNTER_URL + f"email={email}&" + f"api_key={HUNTER_KEY}"
        res = request("get", url)
        res = json.loads(res.text).get("data")
        if res['status'] == "valid" and res['score'] > 70 and not res['disposable'] \
                and res['webmail']:
            return email
        raise ValueError("Email not verified by hunter") 
        



class UserUpdate(schemas.BaseUserUpdate):
    pass
