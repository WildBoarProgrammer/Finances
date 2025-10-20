import datetime
import random
from typing import Dict, List, Union

import reflex as rx
from dateutil.relativedelta import relativedelta

from app.models.models import (
    AccountCategory,
    AssetLiabilitySummaryItem,
    NetWorthDataPoint,
)
from app.states.data import account_categories_data


def generate_net_worth_data(
    num_points=365,
    start_value=600000,
    trend=200,
    volatility=1500,
) -> List[NetWorthDataPoint]:
    """Generates realistic net worth data points for the last year."""
    data = []
    today = datetime.date.today()
    current_value = start_value
    start_value -= trend * num_points * 0.5
    for i in range(num_points):
        current_date = today - datetime.timedelta(days=num_points - 1 - i)
        date_str = current_date.strftime("%Y-%m-%d")
        daily_change = random.gauss(trend / 365, volatility / 20)
        current_value += daily_change
        if random.random() < 0.02:
            current_value += random.uniform(-5000, 10000)
        current_value = max(0, current_value)
        data.append(
            {
                "date": date_str,
                "value": round(current_value, 2),
            }
        )
    data[-1]["value"] = 687041.79
    return data


INITIAL_NET_WORTH_DATA = generate_net_worth_data()


class AccountState(rx.State):
    """Holds the state for the financial dashboard."""

    sidebar_items: List[Dict[str, str]] = [
        {"name": "Dashboard", "icon": "home"},
        {"name": "Accounts", "icon": "credit_card"},
        {"name": "Transactions", "icon": "list"},
        {"name": "Cash Flow", "icon": "trending_up"},
        {"name": "Reports", "icon": "bar_chart"},
        {"name": "Budget", "icon": "pie_chart"},
        {"name": "Recurring", "icon": "repeat"},
        {"name": "Goals", "icon": "target"},
        {"name": "Investments", "icon": "dollar_sign"},
        {"name": "Advice", "icon": "message_circle"},
    ]
    active_page: str = "Accounts"
    user_name: str = "Melanie Smith"
    # I valori di net_worth verranno calcolati dal database
    selected_graph_range: str = "1 month"
    graph_ranges: List[str] = [
        "1 month",
        "3 months",
        "6 months",
        "1 year",
        "All time",
    ]
    selected_performance_type: str = "Net worth performance"
    # account_categories: List[AccountCategory] = account_categories_data  # Ora verrà dal database
    use_database: bool = True  # Flag per abilitare il database - SEMPRE ATTIVO
    db_connected: bool = False  # Stato della connessione database
    db_error: str = ""  # Errore di connessione
    
    # Compatibility attributes per i componenti esistenti
    _raw_net_worth_data: List[NetWorthDataPoint] = []  # Vuoto, non usato
    
    # Gli assets e liabilities verranno calcolati dinamicamente dal database
    summary_view: str = "Totals"

    @rx.var
    def assets_summary(self) -> List[AssetLiabilitySummaryItem]:
        """Calcola il summary degli assets dal database."""
        if not self.db_connected:
            return []
        
        # Calcola dai dati reali del database
        total_cash = 0.0
        total_investments = 0.0
        
        for category in self.account_categories:
            if category["category_name"] == "Cash":
                total_cash = category["total_balance"]
            elif category["category_name"] == "Investments": 
                total_investments = category["total_balance"]
        
        return [
            {
                "name": "Cash",
                "value": total_cash,
                "color": "bg-green-500",
            },
            {
                "name": "Investments", 
                "value": total_investments,
                "color": "bg-purple-500",
            }
        ]
    
    @rx.var
    def liabilities_summary(self) -> List[AssetLiabilitySummaryItem]:
        """Calcola il summary delle liabilities dal database."""
        if not self.db_connected:
            return []
            
        total_credit_cards = 0.0
        
        for category in self.account_categories:
            if category["category_name"] == "Credit Cards":
                total_credit_cards = abs(category["total_balance"])
        
        return [
            {
                "name": "Credit Cards",
                "value": total_credit_cards,
                "color": "bg-red-500",
            }
        ]

    @rx.var
    def account_categories(self) -> List[AccountCategory]:
        """Ottiene le categorie account SOLO dal database."""
        # Prova connessione automatica se non già connesso
        if not self.db_connected:
            self._attempt_database_connection()
        
        if self.db_connected:
            try:
                return self._get_accounts_from_database()
            except Exception as e:
                self.db_error = str(e)
                self.db_connected = False
                return []
        else:
            return []

    def _attempt_database_connection(self):
        """Prova a connettersi automaticamente al database."""
        try:
            from app.models.database import engine
            with engine.connect() as conn:
                pass  # Test connessione
            self.db_connected = True
            self.db_error = ""
        except Exception as e:
            self.db_error = str(e)
            self.db_connected = False

    @rx.var 
    def net_worth(self) -> float:
        """Calcola il net worth totale dal database."""
        if not self.db_connected:
            self._attempt_database_connection()
        
        if self.db_connected:
            try:
                from app.services.database_service import DatabaseService
                with DatabaseService() as db_service:
                    total_net_worth = 0.0
                    accounts = db_service.get_accounts_in_total()
                    for account in accounts:
                        balance = db_service.calculate_account_balance(account.ID)
                        total_net_worth += balance
                    return round(total_net_worth, 2)
            except Exception as e:
                print(f"Errore calcolo net worth: {e}")
                return 0.0
        return 0.0
    
    @rx.var
    def net_worth_change_amount(self) -> float:
        """Calcola la variazione del net worth (placeholder per ora).""" 
        return 100.0  # TODO: implementare calcolo reale
    
    @rx.var
    def net_worth_change_percent(self) -> float:
        """Calcola la percentuale di variazione del net worth (placeholder per ora)."""
        return 2.5  # TODO: implementare calcolo reale

    @rx.var
    def net_worth_performance_data(
        self,
    ) -> List[Dict[str, Union[str, float]]]:
        """Genera dati performance basati sul net worth corrente dal database."""
        if not self.db_connected:
            return []
        
        # Per ora generiamo dati basati sul net worth corrente
        current_net_worth = self.net_worth
        if current_net_worth == 0:
            return []
            
        # Genera alcuni punti dati per il grafico basati sul valore corrente
        today = datetime.date.today()
        data_points = []
        
        # Crea 30 punti per l'ultimo mese
        for i in range(30):
            date_point = today - datetime.timedelta(days=29-i)
            # Simula piccole variazioni attorno al valore corrente  
            variation = random.uniform(-0.02, 0.02)  # ±2%
            value = current_net_worth * (1 + variation * (i/30))
            
            data_points.append({
                "date": date_point.strftime("%b %d"),
                "value": round(value, 2)
            })
        
        # Assicurati che l'ultimo punto sia il valore corrente
        if data_points:
            data_points[-1]["value"] = current_net_worth
            
        return data_points

    @rx.var
    def total_assets(self) -> float:
        """Calculate total assets."""
        return round(
            sum((item["value"] for item in self.assets_summary)),
            2,
        )

    @rx.var
    def total_liabilities(self) -> float:
        """Calculate total liabilities."""
        cc_balance = next(
            (
                cat["total_balance"]
                for cat in self.account_categories
                if cat["category_name"] == "Credit Cards"
            ),
            0,
        )
        other_liabilities = sum(
            (
                item["value"]
                for item in self.liabilities_summary
                if item["name"] != "Credit Cards"
            )
        )
        return round(other_liabilities + abs(cc_balance), 2)

    @rx.var
    def asset_percentages(
        self,
    ) -> List[AssetLiabilitySummaryItem]:
        """Calculate asset percentages."""
        total = self.total_assets
        if total == 0:
            return [
                {
                    "name": item["name"],
                    "value": 0.0,
                    "color": item["color"],
                }
                for item in self.assets_summary
            ]
        return [
            {
                "name": item["name"],
                "value": round(item["value"] / total * 100, 1),
                "color": item["color"],
            }
            for item in self.assets_summary
        ]

    @rx.var
    def liability_percentages(
        self,
    ) -> List[AssetLiabilitySummaryItem]:
        """Calculate liability percentages."""
        total = self.total_liabilities
        if total == 0:
            return [
                {
                    "name": item["name"],
                    "value": 0.0,
                    "color": item["color"],
                }
                for item in self.liabilities_summary
            ]
        current_liability_summary = []
        for item in self.liabilities_summary:
            if item["name"] == "Credit Cards":
                cc_balance = next(
                    (
                        cat["total_balance"]
                        for cat in self.account_categories
                        if cat["category_name"] == "Credit Cards"
                    ),
                    0,
                )
                current_liability_summary.append({**item, "value": abs(cc_balance)})
            else:
                current_liability_summary.append(item)
        return [
            {
                "name": item["name"],
                "value": round(item["value"] / total * 100, 1),
                "color": item["color"],
            }
            for item in current_liability_summary
            if item["value"] > 0
        ]

    @rx.event
    def set_active_page(self, page_name: str):
        """Set the currently active page in the sidebar."""
        self.active_page = page_name

    @rx.event
    def toggle_account_category(self, category_index: int):
        """Toggle the open/closed state of an account category."""
        if 0 <= category_index < len(self.account_categories):
            new_categories = [dict(cat) for cat in self.account_categories]
            new_categories[category_index]["is_open"] = not new_categories[
                category_index
            ]["is_open"]
            self.account_categories = new_categories

    @rx.event
    def set_graph_range(self, value: str):
        """Set the time range for the net worth graph."""
        if value in self.graph_ranges:
            self.selected_graph_range = value
        else:
            pass

    @rx.event
    def set_summary_view(self, view: str):
        """Set the summary view to Totals or Percent."""
        if view in ["Totals", "Percent"]:
            self.summary_view = view

    def _get_accounts_from_database(self) -> List[AccountCategory]:
        """Ottiene i dati degli account dal database."""
        from app.services.database_service import DatabaseService
        
        with DatabaseService() as db_service:
            accounts = db_service.get_all_accounts()
            
            # Raggruppa per tipo (simuliamo le categorie)
            cash_accounts = []
            investment_accounts = []
            credit_accounts = []
            
            for account in accounts:
                balance = db_service.calculate_account_balance(account.ID)
                
                account_detail = {
                    "id": str(account.ID),
                    "name": account.name,
                    "type": self._get_account_type(account.name),
                    "balance": round(balance, 2),
                    "last_updated": "Aggiornato ora",
                    "logo_url": "/simple_logo_bank.png",
                    "sparkline_data": [{"value": balance} for _ in range(6)]
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
                    "one_month_change": 100.0,
                    "one_month_change_percent": 2.9,
                    "is_open": True,
                    "accounts": cash_accounts
                })
            
            if credit_accounts:
                total_credit = sum(acc["balance"] for acc in credit_accounts)
                categories.append({
                    "category_name": "Credit Cards",
                    "total_balance": round(total_credit, 2),
                    "one_month_change": -50.0,
                    "one_month_change_percent": -2.2,
                    "is_open": True,
                    "accounts": credit_accounts
                })
            
            if investment_accounts:
                total_investment = sum(acc["balance"] for acc in investment_accounts)
                categories.append({
                    "category_name": "Investments",
                    "total_balance": round(total_investment, 2),
                    "one_month_change": 1500.0,
                    "one_month_change_percent": 1.9,
                    "is_open": True,
                    "accounts": investment_accounts
                })
            
            return categories
    
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

    @rx.event
    def toggle_database_mode(self):
        """Forza connessione al database - modalità database sempre attiva."""
        self.use_database = True  # Sempre attivo
        # Prova a connettersi al database
        try:
            from app.models.database import engine
            # Test connessione
            engine.connect()
            self.db_connected = True
            self.db_error = ""
            yield rx.toast.success("Database collegato con successo!")
        except Exception as e:
            self.db_connected = False
            self.db_error = str(e)
            yield rx.toast.error(f"Errore database: {str(e)}. Controlla la connessione.")

    @rx.event
    def retry_database_connection(self):
        """Riprova la connessione al database."""
        try:
            from app.models.database import engine
            # Test connessione
            engine.connect()
            self.db_connected = True
            self.db_error = ""
            self.use_database = True
            yield rx.toast.success("Database collegato con successo!")
        except Exception as e:
            self.db_connected = False
            self.db_error = str(e)
            yield rx.toast.error(f"Errore database: {str(e)}")

    @rx.event
    def refresh_all(self):
        """Refreshes all account data SOLO dal database."""
        if not self.db_connected:
            yield rx.toast.error("Database non connesso. Impossibile aggiornare i dati.")
            return
            
        try:
            # Ricarica dal database
            # Forza aggiornamento delle variabili reactive
            self.db_connected = True  # Trigger per reactive updates
            yield rx.toast.success("Dati ricaricati dal database")
        except Exception as e:
            yield rx.toast.error(f"Errore nel refresh database: {str(e)}")

    @rx.event
    def add_account(self):
        """Placeholder for adding a new account."""
        yield rx.toast.warning("Add Account functionality not implemented yet.")
