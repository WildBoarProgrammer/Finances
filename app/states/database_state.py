import datetime
from typing import List, Dict, Optional
from datetime import date, timedelta

import reflex as rx
from dateutil.relativedelta import relativedelta

from app.models.models import (
    AccountCategory,
    AccountDetail,
    AssetLiabilitySummaryItem,
    NetWorthDataPoint,
    SparklinePoint
)
from app.models.db_models import (
    User, Account, Category, Transaction, RecurringTransaction,
    CatType, TranStatus, RecurrenceType
)
from app.services.database_service import DatabaseService
from app.models.database import create_tables


class DatabaseState(rx.State):
    """Stato per le operazioni database."""
    
    # Variabili di stato
    is_connected: bool = False
    current_user_id: int = 1  # Default user ID
    error_message: str = ""
    
    def initialize_database(self):
        """Inizializza il database creando le tabelle se necessario."""
        try:
            create_tables()
            self.is_connected = True
            self.error_message = ""
            
            # Crea dati di esempio se il database è vuoto
            with DatabaseService() as db_service:
                users = db_service.get_all_users()
                if not users:
                    self._create_sample_data(db_service)
                    
        except Exception as e:
            self.error_message = f"Errore connessione database: {str(e)}"
            self.is_connected = False
    
    def _create_sample_data(self, db_service: DatabaseService):
        """Crea dati di esempio per inizializzare il database."""
        
        # Crea utente di esempio
        user = db_service.create_user(name="Melanie Smith", admin=True)
        
        # Crea categorie
        categories = {
            "Stipendio": db_service.create_category("Stipendio", CatType.ENTRATA),
            "Cibo": db_service.create_category("Cibo", CatType.USCITA),
            "Trasporti": db_service.create_category("Trasporti", CatType.USCITA),
            "Casa": db_service.create_category("Casa", CatType.USCITA),
            "Svago": db_service.create_category("Svago", CatType.USCITA),
            "Investimenti": db_service.create_category("Investimenti", CatType.ENTRATA),
        }
        
        # Crea account
        checking_account = db_service.create_account(
            name="Melanie's Checking",
            initial_balance=1500.0,
            goal="Conto corrente principale",
            in_tot=True
        )
        
        savings_account = db_service.create_account(
            name="Joint Savings",
            initial_balance=15000.0,
            goal="Risparmi congiunti",
            in_tot=True
        )
        
        credit_card = db_service.create_account(
            name="Joint Credit Card",
            initial_balance=0.0,
            goal="Carta di credito",
            in_tot=True
        )
        
        investment_account = db_service.create_account(
            name="Jon's 401k",
            initial_balance=150000.0,
            goal="Piano pensionistico",
            in_tot=True
        )
        
        # Crea alcune transazioni di esempio degli ultimi 30 giorni
        today = date.today()
        for i in range(30):
            transaction_date = today - timedelta(days=i)
            
            # Transazioni casuali
            if i % 7 == 0:  # Stipendio settimanale
                db_service.create_transaction(
                    date=transaction_date,
                    amount=1200.0,
                    description="Stipendio settimanale",
                    account_id=checking_account.ID,
                    category_id=categories["Stipendio"].ID,
                    user_id=user.ID,
                    transaction_type=CatType.ENTRATA
                )
            
            if i % 3 == 0:  # Spese per cibo
                db_service.create_transaction(
                    date=transaction_date,
                    amount=45.50,
                    description="Spesa supermercato",
                    account_id=checking_account.ID,
                    category_id=categories["Cibo"].ID,
                    user_id=user.ID,
                    transaction_type=CatType.USCITA
                )
        
        # Crea transazioni ricorrenti
        db_service.create_recurring_transaction(
            name="Affitto",
            amount=800.0,
            description="Affitto mensile",
            account_id=checking_account.ID,
            category_id=categories["Casa"].ID,
            user_id=user.ID,
            transaction_type=CatType.USCITA,
            recurrence=RecurrenceType.OGNI_MESE,
            deadline=12  # 12 mesi
        )
    
    def get_accounts_data(self) -> List[AccountCategory]:
        """Ottiene i dati degli account dal database."""
        if not self.is_connected:
            return []
        
        try:
            with DatabaseService() as db_service:
                accounts = db_service.get_all_accounts()
                
                # Raggruppa per tipo (simuliamo le categorie)
                cash_accounts = []
                investment_accounts = []
                credit_accounts = []
                
                for account in accounts:
                    balance = db_service.calculate_account_balance(account.ID)
                    
                    # Genera sparkline data (ultimi 6 punti)
                    sparkline_data = self._generate_sparkline_for_account(
                        db_service, account.ID, balance
                    )
                    
                    account_detail: AccountDetail = {
                        "id": str(account.ID),
                        "name": account.name,
                        "type": self._get_account_type(account.name),
                        "balance": round(balance, 2),
                        "last_updated": "Aggiornato ora",
                        "logo_url": "/simple_logo_bank.png",
                        "sparkline_data": sparkline_data
                    }
                    
                    # Categorizza per tipo
                    if "401k" in account.name.lower() or "investment" in account.name.lower():
                        investment_accounts.append(account_detail)
                    elif "credit" in account.name.lower():
                        credit_accounts.append(account_detail)
                    else:
                        cash_accounts.append(account_detail)
                
                categories = []
                
                if cash_accounts:
                    total_cash = sum(acc["balance"] for acc in cash_accounts)
                    categories.append({
                        "category_name": "Cash",
                        "total_balance": round(total_cash, 2),
                        "one_month_change": 100.0,  # Placeholder
                        "one_month_change_percent": 2.9,  # Placeholder
                        "is_open": True,
                        "accounts": cash_accounts
                    })
                
                if credit_accounts:
                    total_credit = sum(acc["balance"] for acc in credit_accounts)
                    categories.append({
                        "category_name": "Credit Cards",
                        "total_balance": round(total_credit, 2),
                        "one_month_change": -50.0,  # Placeholder
                        "one_month_change_percent": -2.2,  # Placeholder
                        "is_open": True,
                        "accounts": credit_accounts
                    })
                
                if investment_accounts:
                    total_investment = sum(acc["balance"] for acc in investment_accounts)
                    categories.append({
                        "category_name": "Investments",
                        "total_balance": round(total_investment, 2),
                        "one_month_change": 1500.0,  # Placeholder
                        "one_month_change_percent": 1.9,  # Placeholder
                        "is_open": True,
                        "accounts": investment_accounts
                    })
                
                return categories
                
        except Exception as e:
            self.error_message = f"Errore nel caricamento dati: {str(e)}"
            return []
    
    def _generate_sparkline_for_account(self, db_service: DatabaseService, 
                                      account_id: int, current_balance: float) -> List[SparklinePoint]:
        """Genera i dati sparkline per un account."""
        sparkline = []
        today = date.today()
        
        # Calcola il saldo per gli ultimi 6 giorni
        for i in range(5, -1, -1):
            target_date = today - timedelta(days=i)
            
            # Saldo iniziale
            account = db_service.get_account_by_id(account_id)
            balance = account.initial_balance or 0.0
            
            # Transazioni fino alla data target
            transactions = db_service.get_transactions_by_account(account_id)
            for transaction in transactions:
                if transaction.date <= target_date:
                    if transaction.type == CatType.ENTRATA:
                        balance += transaction.amount
                    else:
                        balance -= transaction.amount
            
            sparkline.append({"value": round(balance, 2)})
        
        # Assicurati che l'ultimo valore sia il saldo corrente
        sparkline[-1]["value"] = current_balance
        
        return sparkline
    
    def _get_account_type(self, account_name: str) -> str:
        """Determina il tipo di account dal nome."""
        name_lower = account_name.lower()
        if "checking" in name_lower:
            return "Checking"
        elif "savings" in name_lower:
            return "Savings"
        elif "credit" in name_lower:
            return "Credit Card"
        elif "401k" in name_lower:
            return "401k"
        else:
            return "Account"
    
    def get_net_worth_data(self, days: int = 365) -> List[NetWorthDataPoint]:
        """Ottiene i dati del patrimonio netto dal database."""
        if not self.is_connected:
            return []
        
        try:
            with DatabaseService() as db_service:
                data = []
                today = date.today()
                
                # Calcola il patrimonio per gli ultimi N giorni
                # Per performance, campiona ogni 7 giorni se > 90 giorni
                step = 7 if days > 90 else 1
                
                for i in range(days, -1, -step):
                    target_date = today - timedelta(days=i)
                    net_worth = db_service.get_net_worth_by_date(target_date)
                    
                    data.append({
                        "date": target_date.strftime("%Y-%m-%d"),
                        "value": round(net_worth, 2)
                    })
                
                return data
                
        except Exception as e:
            self.error_message = f"Errore nel caricamento patrimonio: {str(e)}"
            return []
    
    @rx.event
    def refresh_data(self):
        """Ricarica i dati dal database."""
        self.initialize_database()
        yield rx.toast.info("Dati ricaricati dal database")
    
    @rx.event
    def add_sample_transaction(self):
        """Aggiunge una transazione di esempio."""
        try:
            with DatabaseService() as db_service:
                # Trova il primo account
                accounts = db_service.get_all_accounts()
                if not accounts:
                    yield rx.toast.error("Nessun account trovato")
                    return
                
                # Trova la categoria "Cibo"
                categories = db_service.get_all_categories()
                food_category = next((c for c in categories if c.name == "Cibo"), None)
                if not food_category:
                    yield rx.toast.error("Categoria Cibo non trovata")
                    return
                
                # Crea transazione
                db_service.create_transaction(
                    date=date.today(),
                    amount=25.50,
                    description="Pranzo di prova",
                    account_id=accounts[0].ID,
                    category_id=food_category.ID,
                    user_id=self.current_user_id,
                    transaction_type=CatType.USCITA
                )
                
                yield rx.toast.success("Transazione aggiunta!")
                
        except Exception as e:
            yield rx.toast.error(f"Errore: {str(e)}")


# Istanza globale dello stato database
database_state = DatabaseState()