#!/usr/bin/env python3
"""
Script per inizializzare il database PostgreSQL per l'app Finances.
Esegui questo script per creare le tabelle e inserire dati di esempio.
"""

import sys
import os
from datetime import date, timedelta

# Aggiungi il percorso dell'app al path Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.database import create_tables, engine
from app.models.db_models import (
    User, Category, Account, Transaction, RecurringTransaction,
    CatType, TranStatus, RecurrenceType
)
from app.services.database_service import DatabaseService


def main():
    """Funzione principale per inizializzare il database."""
    
    print("🏦 Inizializzazione Database Finances")
    print("=" * 40)
    
    try:
        # Test connessione database
        print("📡 Test connessione database...")
        engine.connect()
        print("✅ Connessione riuscita!")
        
        # Creazione tabelle
        print("🏗️  Creazione tabelle...")
        create_tables()
        print("✅ Tabelle create!")
        
        # Inserimento dati di esempio
        print("📊 Inserimento dati di esempio...")
        insert_sample_data()
        print("✅ Dati di esempio inseriti!")
        
        print("\n🎉 Database inizializzato con successo!")
        print("\n📝 Prossimi passi:")
        print("1. Aggiorna il file .env con le tue credenziali database")
        print("2. Installa le dipendenze: pip install -r requirements.txt")
        print("3. Avvia l'app: reflex run")
        
    except Exception as e:
        print(f"❌ Errore durante l'inizializzazione: {str(e)}")
        print("\n🔧 Verifica:")
        print("1. PostgreSQL è in esecuzione")
        print("2. Le credenziali nel file .env sono corrette")
        print("3. Il database 'finances_db' esiste")
        return 1
    
    return 0


def insert_sample_data():
    """Inserisce dati di esempio nel database."""
    
    with DatabaseService() as db_service:
        
        # Verifica se esistono già dati
        existing_users = db_service.get_all_users()
        if existing_users:
            print("⚠️  Dati già presenti, saltando l'inserimento...")
            return
        
        # Crea utenti
        print("👤 Creazione utenti...")
        admin_user = db_service.create_user(name="Melanie Smith", admin=True)
        regular_user = db_service.create_user(name="John Doe", admin=False)
        
        # Crea categorie
        print("📁 Creazione categorie...")
        categories = {
            # Entrate
            "Stipendio": db_service.create_category("Stipendio", CatType.ENTRATA),
            "Freelance": db_service.create_category("Freelance", CatType.ENTRATA),
            "Investimenti": db_service.create_category("Investimenti", CatType.ENTRATA),
            "Bonus": db_service.create_category("Bonus", CatType.ENTRATA),
            
            # Uscite
            "Casa": db_service.create_category("Casa", CatType.USCITA),
            "Cibo": db_service.create_category("Cibo", CatType.USCITA),
            "Trasporti": db_service.create_category("Trasporti", CatType.USCITA),
            "Svago": db_service.create_category("Svago", CatType.USCITA),
            "Salute": db_service.create_category("Salute", CatType.USCITA),
            "Shopping": db_service.create_category("Shopping", CatType.USCITA),
            "Servizi": db_service.create_category("Servizi", CatType.USCITA),
        }
        
        # Crea account
        print("🏛️  Creazione account...")
        checking_account = db_service.create_account(
            name="Melanie's Checking",
            initial_balance=2500.00,
            goal="Conto corrente principale per spese quotidiane",
            need_admin=False,
            in_tot=True
        )
        
        savings_account = db_service.create_account(
            name="Joint Savings", 
            initial_balance=25000.00,
            goal="Risparmi per emergenze e obiettivi a medio termine",
            need_admin=False,
            in_tot=True
        )
        
        credit_card = db_service.create_account(
            name="Joint Credit Card",
            initial_balance=0.00,  # Saldo iniziale neutro per carta credito
            goal="Carta di credito per acquisti e cashback",
            need_admin=False,
            in_tot=True
        )
        
        investment_401k = db_service.create_account(
            name="Jon's 401k",
            initial_balance=185000.00,
            goal="Piano pensionistico aziendale",
            need_admin=True,
            in_tot=True
        )
        
        emergency_fund = db_service.create_account(
            name="Emergency Fund",
            initial_balance=15000.00,
            goal="Fondo di emergenza - 6 mesi di spese",
            need_admin=False,
            in_tot=True
        )
        
        # Crea transazioni degli ultimi 60 giorni
        print("💳 Creazione transazioni...")
        today = date.today()
        
        # Lista di transazioni realistiche
        sample_transactions = [
            # Entrate mensili
            {"days_ago": 1, "amount": 4200.00, "desc": "Stipendio Gennaio", "account": checking_account, "category": categories["Stipendio"], "type": CatType.ENTRATA},
            {"days_ago": 32, "amount": 4200.00, "desc": "Stipendio Dicembre", "account": checking_account, "category": categories["Stipendio"], "type": CatType.ENTRATA},
            {"days_ago": 15, "amount": 850.00, "desc": "Progetto freelance", "account": checking_account, "category": categories["Freelance"], "type": CatType.ENTRATA},
            
            # Spese casa (affitto, bollette)
            {"days_ago": 2, "amount": 1200.00, "desc": "Affitto Gennaio", "account": checking_account, "category": categories["Casa"], "type": CatType.USCITA},
            {"days_ago": 33, "amount": 1200.00, "desc": "Affitto Dicembre", "account": checking_account, "category": categories["Casa"], "type": CatType.USCITA},
            {"days_ago": 5, "amount": 145.30, "desc": "Bolletta elettricità", "account": checking_account, "category": categories["Servizi"], "type": CatType.USCITA},
            {"days_ago": 8, "amount": 89.50, "desc": "Internet fibra", "account": checking_account, "category": categories["Servizi"], "type": CatType.USCITA},
            
            # Spese cibo
            {"days_ago": 1, "amount": 67.45, "desc": "Spesa Esselunga", "account": checking_account, "category": categories["Cibo"], "type": CatType.USCITA},
            {"days_ago": 3, "amount": 23.80, "desc": "Pranzo ufficio", "account": credit_card, "category": categories["Cibo"], "type": CatType.USCITA},
            {"days_ago": 4, "amount": 89.30, "desc": "Spesa settimanale", "account": checking_account, "category": categories["Cibo"], "type": CatType.USCITA},
            {"days_ago": 7, "amount": 45.20, "desc": "Cena fuori", "account": credit_card, "category": categories["Svago"], "type": CatType.USCITA},
            {"days_ago": 10, "amount": 156.80, "desc": "Spesa grande", "account": checking_account, "category": categories["Cibo"], "type": CatType.USCITA},
            
            # Trasporti
            {"days_ago": 6, "amount": 65.00, "desc": "Rifornimento benzina", "account": credit_card, "category": categories["Trasporti"], "type": CatType.USCITA},
            {"days_ago": 12, "amount": 28.50, "desc": "Parcheggio centro", "account": checking_account, "category": categories["Trasporti"], "type": CatType.USCITA},
            {"days_ago": 25, "amount": 75.00, "desc": "Rifornimento", "account": credit_card, "category": categories["Trasporti"], "type": CatType.USCITA},
            
            # Shopping e svago
            {"days_ago": 9, "amount": 125.99, "desc": "Abbigliamento", "account": credit_card, "category": categories["Shopping"], "type": CatType.USCITA},
            {"days_ago": 14, "amount": 35.00, "desc": "Cinema", "account": checking_account, "category": categories["Svago"], "type": CatType.USCITA},
            {"days_ago": 18, "amount": 89.99, "desc": "Scarpe sportive", "account": credit_card, "category": categories["Shopping"], "type": CatType.USCITA},
            
            # Salute
            {"days_ago": 20, "amount": 85.00, "desc": "Visita medica", "account": checking_account, "category": categories["Salute"], "type": CatType.USCITA},
            {"days_ago": 22, "amount": 45.50, "desc": "Farmacia", "account": checking_account, "category": categories["Salute"], "type": CatType.USCITA},
            
            # Investimenti e risparmi
            {"days_ago": 1, "amount": 800.00, "desc": "Trasferimento risparmi", "account": savings_account, "category": categories["Investimenti"], "type": CatType.ENTRATA},
            {"days_ago": 32, "amount": 800.00, "desc": "Trasferimento risparmi", "account": savings_account, "category": categories["Investimenti"], "type": CatType.ENTRATA},
        ]
        
        # Inserisci le transazioni
        for transaction_data in sample_transactions:
            transaction_date = today - timedelta(days=transaction_data["days_ago"])
            
            db_service.create_transaction(
                date=transaction_date,
                amount=transaction_data["amount"],
                description=transaction_data["desc"],
                account_id=transaction_data["account"].ID,
                category_id=transaction_data["category"].ID,
                user_id=admin_user.ID,
                transaction_type=transaction_data["type"]
            )
        
        # Crea transazioni ricorrenti
        print("🔄 Creazione transazioni ricorrenti...")
        recurring_transactions = [
            {
                "name": "Affitto Mensile",
                "amount": 1200.00,
                "description": "Pagamento affitto appartamento",
                "account": checking_account,
                "category": categories["Casa"],
                "type": CatType.USCITA,
                "recurrence": RecurrenceType.OGNI_MESE,
                "deadline": 12  # 1 anno
            },
            {
                "name": "Stipendio",
                "amount": 4200.00,
                "description": "Stipendio mensile lordo",
                "account": checking_account,
                "category": categories["Stipendio"],
                "type": CatType.ENTRATA,
                "recurrence": RecurrenceType.OGNI_MESE,
                "deadline": 0  # Infinito
            },
            {
                "name": "Risparmio Automatico",
                "amount": 800.00,
                "description": "Trasferimento automatico su conto risparmio",
                "account": savings_account,
                "category": categories["Investimenti"],
                "type": CatType.ENTRATA,
                "recurrence": RecurrenceType.OGNI_MESE,
                "deadline": 0  # Infinito
            },
            {
                "name": "Assicurazione Auto",
                "amount": 450.00,
                "description": "Premio assicurativo annuale",
                "account": checking_account,
                "category": categories["Trasporti"],
                "type": CatType.USCITA,
                "recurrence": RecurrenceType.OGNI_ANNO,
                "deadline": 5  # 5 anni
            }
        ]
        
        for recurring_data in recurring_transactions:
            db_service.create_recurring_transaction(
                name=recurring_data["name"],
                amount=recurring_data["amount"],
                description=recurring_data["description"],
                account_id=recurring_data["account"].ID,
                category_id=recurring_data["category"].ID,
                user_id=admin_user.ID,
                transaction_type=recurring_data["type"],
                recurrence=recurring_data["recurrence"],
                deadline=recurring_data["deadline"]
            )
        
        print(f"✅ Inseriti {len(sample_transactions)} transazioni e {len(recurring_transactions)} transazioni ricorrenti")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)