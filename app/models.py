from sqlalchemy import Column, ForeignKey, Integer, String
from .database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(50), unique=True)
    phone = Column(String(15))
    hashed_password = Column(String(100))
    '''role = Column(String(20), default="user")'''
    roleid=Column(Integer,ForeignKey("roles.roleid"))
    addresses=relationship("Address",back_populates="user")
    role=relationship("Role",back_populates="users")
     
class Address(Base):
    __tablename__ = "addresses"
    addressid = Column(Integer, primary_key=True, index=True)
    addressLine_1 = Column(String(100))
    addressLine_2=Column(String(100))
    city = Column(String(50))
    state = Column(String(50))
    zipcode = Column(String(20))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="addresses")

class Role(Base):
    __tablename__ = "roles"
    roleid = Column(Integer, primary_key=True, index=True)
    rolename = Column(String(20), unique=True)
    users = relationship("User", back_populates="role")



    