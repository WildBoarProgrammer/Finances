import enum
from datetime import date
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from app.models.database import Base


# Enums corrispondenti allo schema SQL
class CatType(enum.Enum):
    ENTRATA = "Entrata"
    USCITA = "Uscita"


class TranStatus(enum.Enum):
    SINGOLO = "Singolo"
    RICORRENTE = "Ricorrente"


class RecurrenceType(enum.Enum):
    OGNI_MESE = "Ogni mese"
    OGNI_ANNO = "Ogni anno"


# Definizioni ENUM PostgreSQL esplicite
cattype_enum = ENUM(CatType, name='CatType', create_constraint=True, validate_strings=True)
transtatus_enum = ENUM(TranStatus, name='TranStatus', create_constraint=True, validate_strings=True)
recurrencetype_enum = ENUM(RecurrenceType, name='RecurrenceType', create_constraint=True, validate_strings=True)


# Modelli delle tabelle
class User(Base):
    __tablename__ = "Users"
    __table_args__ = {'quote': True}  # Forza le virgolette per case sensitivity
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32))
    admin = Column(Boolean, default=False)
    
    # Relazioni
    transactions = relationship("Transaction", back_populates="user")
    recurring_transactions = relationship("RecurringTransaction", back_populates="user")


class Category(Base):
    __tablename__ = "Category" 
    __table_args__ = {'quote': True}
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32))
    type = Column(cattype_enum)
    
    # Relazioni
    transactions = relationship("Transaction", back_populates="category")
    recurring_transactions = relationship("RecurringTransaction", back_populates="category")


class Account(Base):
    __tablename__ = "Account"
    __table_args__ = {'quote': True}
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    need_admin = Column(Boolean, default=False)
    name = Column(String(32))
    goal = Column(String(128))
    initial_balance = Column(Float(precision=2))
    in_tot = Column(Boolean, default=True)
    
    # Relazioni
    transactions = relationship("Transaction", back_populates="account")
    recurring_transactions = relationship("RecurringTransaction", back_populates="account")


class Transaction(Base):
    __tablename__ = "Transactions"
    __table_args__ = {'quote': True}
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    type = Column(cattype_enum)
    status = Column(transtatus_enum)
    amount = Column(Float(precision=2))
    description = Column(String(256))
    account_id = Column(Integer, ForeignKey("Account.ID"))
    category_id = Column(Integer, ForeignKey("Category.ID"))
    user_id = Column(Integer, ForeignKey("Users.ID"))
    
    # Relazioni
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    user = relationship("User", back_populates="transactions")


class RecurringTransaction(Base):
    __tablename__ = "Recurring_Transactions"
    __table_args__ = {'quote': True}
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32))
    recursive = Column(recurrencetype_enum)
    deadline = Column(Integer)
    type = Column(cattype_enum)
    status = Column(transtatus_enum)
    amount = Column(Float(precision=2))
    description = Column(String(256))
    account_id = Column(Integer, ForeignKey("Account.ID"))
    category_id = Column(Integer, ForeignKey("Category.ID"))
    user_id = Column(Integer, ForeignKey("Users.ID"))
    
    # Relazioni
    account = relationship("Account", back_populates="recurring_transactions")
    category = relationship("Category", back_populates="recurring_transactions")
    user = relationship("User", back_populates="recurring_transactions")