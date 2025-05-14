from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str
    phone: str

class UserCreate(UserBase):
    password: str
    '''role:str="user" '''
    roleid:int

class UserUpdate(UserBase):
    id: int

class RoleBase(BaseModel):
    rolename: str

class ShowRole(RoleBase):
    roleid: int
    class Config:
        from_attributes = True
    
class ShowUser(UserBase):
    id: int
    role:ShowRole
    class Config:
        from_attributes = True
        
class LoginSchema(BaseModel):
    email: str
    password: str
    
class ForgotPasswordRequest(BaseModel):  
    email: str
    
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    
class AddressCreate(BaseModel):
    addressLine_1: str
    addressLine_2: str
    city: str
    state: str
    zipcode: str

class ShowAddress(AddressCreate):
    addressid: int
    class Config:
        from_attributes = True
       
class updateadd(AddressCreate):
    user_id:int
     

