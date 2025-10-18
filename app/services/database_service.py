from datetime import date, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.database import get_db, SessionLocal
from app.models.db_models import (
    User, Category, Account, Transaction, RecurringTransaction,
    CatType, TranStatus, RecurrenceType
)


class DatabaseService:
    """Servizio per le operazioni database."""
    
    def __init__(self):
        self.db: Session = None
    
    def __enter__(self):
        self.db = SessionLocal()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()
    
    # === USERS ===
    def create_user(self, name: str, admin: bool = False) -> User:
        """Crea un nuovo utente."""
        user = User(name=name, admin=admin)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Ottiene un utente per ID."""
        return self.db.query(User).filter(User.ID == user_id).first()
    
    def get_all_users(self) -> List[User]:
        """Ottiene tutti gli utenti."""
        return self.db.query(User).all()
    
    # === CATEGORIES ===
    def create_category(self, name: str, cat_type: CatType) -> Category:
        """Crea una nuova categoria."""
        category = Category(name=name, type=cat_type)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def get_categories_by_type(self, cat_type: CatType) -> List[Category]:
        """Ottiene le categorie per tipo."""
        return self.db.query(Category).filter(Category.type == cat_type).all()
    
    def get_all_categories(self) -> List[Category]:
        """Ottiene tutte le categorie."""
        return self.db.query(Category).all()
    
    # === ACCOUNTS ===
    def create_account(self, name: str, initial_balance: float = 0.0, 
                      goal: str = "", need_admin: bool = False, 
                      in_tot: bool = True) -> Account:
        """Crea un nuovo account."""
        account = Account(
            name=name,
            initial_balance=initial_balance,
            goal=goal,
            need_admin=need_admin,
            in_tot=in_tot
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        """Ottiene un account per ID."""
        return self.db.query(Account).filter(Account.ID == account_id).first()
    
    def get_all_accounts(self) -> List[Account]:
        """Ottiene tutti gli account."""
        return self.db.query(Account).all()
    
    def get_accounts_in_total(self) -> List[Account]:
        """Ottiene gli account inclusi nel totale."""
        return self.db.query(Account).filter(Account.in_tot == True).all()
    
    def calculate_account_balance(self, account_id: int) -> float:
        """Calcola il saldo corrente di un account."""
        account = self.get_account_by_id(account_id)
        if not account:
            return 0.0
        
        # Saldo iniziale
        balance = account.initial_balance or 0.0
        
        # Somma tutte le entrate
        entrate = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.account_id == account_id,
                Transaction.type == 'ENTRATA'
            )
        ).scalar() or 0.0
        
        # Sottrai tutte le uscite
        uscite = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.account_id == account_id,
                Transaction.type == 'USCITA'
            )
        ).scalar() or 0.0
        
        return balance + entrate - uscite
    
    # === TRANSACTIONS ===
    def create_transaction(self, date: date, amount: float, description: str,
                          account_id: int, category_id: int, user_id: int,
                          transaction_type: CatType, 
                          status: TranStatus = TranStatus.SINGOLO) -> Transaction:
        """Crea una nuova transazione."""
        transaction = Transaction(
            date=date,
            type=transaction_type,
            status=status,
            amount=amount,
            description=description,
            account_id=account_id,
            category_id=category_id,
            user_id=user_id
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_transactions_by_account(self, account_id: int, 
                                   limit: Optional[int] = None) -> List[Transaction]:
        """Ottiene le transazioni per account."""
        query = self.db.query(Transaction).filter(Transaction.account_id == account_id)
        query = query.order_by(Transaction.date.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def get_transactions_by_date_range(self, start_date: date, 
                                     end_date: date) -> List[Transaction]:
        """Ottiene le transazioni in un range di date."""
        return self.db.query(Transaction).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).order_by(Transaction.date.desc()).all()
    
    def get_transactions_by_category(self, category_id: int) -> List[Transaction]:
        """Ottiene le transazioni per categoria."""
        return self.db.query(Transaction).filter(
            Transaction.category_id == category_id
        ).order_by(Transaction.date.desc()).all()
    
    # === RECURRING TRANSACTIONS ===
    def create_recurring_transaction(self, name: str, amount: float, 
                                   description: str, account_id: int, 
                                   category_id: int, user_id: int,
                                   transaction_type: CatType,
                                   recurrence: RecurrenceType,
                                   deadline: int = 0) -> RecurringTransaction:
        """Crea una transazione ricorrente."""
        recurring = RecurringTransaction(
            name=name,
            recursive=recurrence,
            deadline=deadline,
            type=transaction_type,
            status=TranStatus.RICORRENTE,
            amount=amount,
            description=description,
            account_id=account_id,
            category_id=category_id,
            user_id=user_id
        )
        self.db.add(recurring)
        self.db.commit()
        self.db.refresh(recurring)
        return recurring
    
    def get_active_recurring_transactions(self) -> List[RecurringTransaction]:
        """Ottiene le transazioni ricorrenti attive."""
        return self.db.query(RecurringTransaction).filter(
            or_(
                RecurringTransaction.deadline == 0,  # Infinito
                RecurringTransaction.deadline > 0   # Ancora attive
            )
        ).all()
    
    # === ANALYTICS ===
    def get_net_worth_by_date(self, target_date: date) -> float:
        """Calcola il patrimonio netto alla data specificata."""
        total = 0.0
        
        # Per ogni account incluso nel totale
        accounts = self.get_accounts_in_total()
        for account in accounts:
            # Saldo iniziale
            balance = account.initial_balance or 0.0
            
            # Transazioni fino alla data target
            transactions = self.db.query(Transaction).filter(
                and_(
                    Transaction.account_id == account.ID,
                    Transaction.date <= target_date
                )
            ).all()
            
            for transaction in transactions:
                if transaction.type == 'ENTRATA':
                    balance += transaction.amount
                else:
                    balance -= transaction.amount
            
            total += balance
        
        return total
    
    def get_monthly_summary(self, year: int, month: int) -> Dict[str, Any]:
        """Ottiene un riassunto mensile delle transazioni."""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        # Entrate del mese
        entrate = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date < end_date,
                Transaction.type == 'ENTRATA'
            )
        ).scalar() or 0.0
        
        # Uscite del mese
        uscite = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date < end_date,
                Transaction.type == 'USCITA'
            )
        ).scalar() or 0.0
        
        return {
            "entrate": entrate,
            "uscite": uscite,
            "saldo": entrate - uscite,
            "numero_transazioni": self.db.query(Transaction).filter(
                and_(
                    Transaction.date >= start_date,
                    Transaction.date < end_date
                )
            ).count()
        }
    
    def get_category_spending(self, category_id: int, 
                            start_date: Optional[date] = None,
                            end_date: Optional[date] = None) -> float:
        """Ottiene la spesa totale per una categoria in un periodo."""
        query = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.category_id == category_id
        )
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        
        return query.scalar() or 0.0


# Funzione di utilità per ottenere il servizio database
def get_database_service() -> DatabaseService:
    """Ottiene un'istanza del servizio database."""
    return DatabaseService()